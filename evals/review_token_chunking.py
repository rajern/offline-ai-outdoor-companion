"""Audit exact source-instruction presence in the isolated chunking experiment.

This is a textual coverage check, NOT safety-policy approval or answer scoring.
Selectors refer to frozen source lines and are saved with resolved char spans.
Equivalent text elsewhere may exist; only explicitly listed alternatives count.
Run from backend AFTER compare_token_chunking.py.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from outwise.knowledge.ingestion import digest, write_json

OUTPUT = ROOT / "knowledge/local/diagnostics/token-chunking-2026-10-07"


def ref(parent, *lines, first_sentences=None):
    return {"parent_id": parent, "lines": list(lines), "first_sentences": first_sentences}


def fact(label, *alternatives):
    return {"label": label, "alternatives": [list(option) for option in alternatives]}


def selectors():
    sprain = [fact(label, [ref("source-04-003", line)]) for label, line in
              [("Rest/protection without load", 1), ("Cooling with protective layer", 2),
               ("Compression without stopping circulation", 3), ("Elevation", 4)]]
    water = [fact("Clear water may be unsafe", [ref("source-21-005", 0)]),
             fact("Rolling boil 1 minute / 3 above 6500 feet", [ref("source-21-010", 0)]),
             fact("Filter THEN disinfect", [ref("source-21-009", 0)], [ref("source-21-002", 2)]),
             fact("Chemical contamination not fixed by boiling/disinfection", [ref("source-21-009", 3)])]
    return {
        "sprain-nb": sprain, "sprain-en": sprain,
        "fracture-nb": [fact("Suspect fracture from inability to stand; uncertainty", [ref("source-04-005", 0)]),
                        fact("Doctor/urgent care if suspected fracture", [ref("source-04-005", 0)]),
                        fact("Keep injured area still", [ref("source-04-006", 0)])],
        "cold-nb": [fact("Wet clothing instruction AND conditional no-insulation fallback", [ref("source-05-004", 0, 6)]),
                    fact("Wind/vapour-tight insulating wrapping", [ref("source-05-004", 1)]),
                    fact("Heat source not directly on skin", [ref("source-05-004", 2)]),
                    fact("Monitor consciousness/breathing; call 113", [ref("source-05-004", 3, 5)])],
        "lost-nb": [fact("Stop; stay unless certain of route", [ref("source-09-007", 1)]),
                    fact("Make group safe/warm", [ref("source-09-007", 2)]),
                    fact("Call for help and become visible", [ref("source-09-007", 3)])],
        "warmth-nb": [fact("Wind/vapour-tight insulating wrapping", [ref("source-05-004", 1)]),
                      fact("Heat source not directly on skin", [ref("source-05-004", 2)]),
                      fact("Conditional no-insulation fallback", [ref("source-05-004", 6)])],
        "water-nb": water, "water-en": water,
        "lightning-nb": [fact("Safe building/enclosed metal-topped vehicle, windows up", [ref("source-22-002", 2)]),
                         fact("No safe outdoor place; leave high terrain with outdoor fallback condition", [ref("source-22-002", 0), ref("source-22-004", 0, 1)]),
                         fact("Wait 30 minutes after last thunder", [ref("source-22-002", 3)])],
        "rescue-nb": [fact("Early beacon activation in life-threatening situation", [ref("source-11-003", 0)]),
                      fact("Activate/get help when unsure", [ref("source-11-003", 1)])],
        "preparedness-nb": [fact("Warm clothes/extra food; bad weather/unexpected night (uses section title)", [ref("source-10-004", 0)]),
                            fact("Survival kit and emergency shelter", [ref("source-12-002", 8, 9)]),
                            fact("First aid, navigation, torch and distress beacon", [ref("source-12-002", 3, 4, 5, 7)])],
        "river-nb": [fact("Fast/murky/debris/loud warning signs and do-not-cross instruction", [ref("source-14-005", 0, 2, 3, 4, 5)]),
                     fact("Do not cross on warning signs/doubt", [ref("source-14-006", 0, 2, 5)])],
        "ice-nb": [fact("Avoid second victim; keep distance/use aids", [ref("source-19-001", 2, first_sentences=2)]),
                   fact("Conditional call 113 before rescue", [ref("source-19-001", 1)]),
                   fact("Throw rope OR extend branch/ladder", [ref("source-19-001", 4)], [ref("source-19-002", 0)])],
    }


def main():
    global OUTPUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    OUTPUT = args.output.resolve()
    if not OUTPUT.is_relative_to((ROOT / "knowledge/local/diagnostics").resolve()):
        raise ValueError("Output must be under ignored knowledge/local/diagnostics")
    data = json.loads((OUTPUT / "retrieval-comparison.json").read_text(encoding="utf-8"))
    parents = {i["id"]: i for i in json.loads((OUTPUT / "baseline-knowledge.json").read_text(encoding="utf-8"))["items"]}
    definitions = selectors()
    for facts in definitions.values():
        for unit in facts:
            for option in unit["alternatives"]:
                for reference in option:
                    text = parents[reference["parent_id"]]["text"]
                    lines = text.splitlines(keepends=True)
                    spans = []
                    for line_number in reference["lines"]:
                        line = lines[line_number].rstrip()
                        if reference["first_sentences"] is not None:
                            # Only used for the two introductory ice-rescue sentences.
                            line = ". ".join(line.split(". ")[:reference["first_sentences"]]) + "."
                        start = sum(len(part) for part in lines[:line_number])
                        assert text[start:start + len(line)] == line
                        spans.append({"start": start, "end": start + len(line)})
                    reference["spans"] = spans
    results = {}
    for variant in ["baseline", "token_aligned"]:
        rows = []
        for case in data[variant]:
            if case["id"] not in definitions:
                rows.append({"id": case["id"], "coverage": case["coverage"], "not_scored": "coverage gap / negative control"})
                continue
            row = {"id": case["id"], "facts_total": len(definitions[case["id"]])}
            for k in [3, 5]:
                intervals = {}
                for match in case["top5"][:k]:
                    span = match["span"]
                    intervals.setdefault(span["parent_id"], []).append((span["start"], span["end"]))
                def present(reference):
                    covered = {i for a, b in intervals.get(reference["parent_id"], []) for i in range(a, b)}
                    text = parents[reference["parent_id"]]["text"]
                    return all(all(i in covered for i in range(s["start"], s["end"]) if not text[i].isspace())
                               for s in reference["spans"])
                scored = [{"label": unit["label"], "present": any(all(present(r) for r in option) for option in unit["alternatives"])}
                          for unit in definitions[case["id"]]]
                row[f"at{k}"] = {"facts_present": sum(u["present"] for u in scored), "facts": scored}
            rows.append(row)
        results[variant] = rows
    summary = {}
    for variant, rows in results.items():
        scored = [row for row in rows if "facts_total" in row]
        summary[variant] = {"facts_total": sum(row["facts_total"] for row in scored), **{
            f"at{k}": {"facts_present": sum(row[f"at{k}"]["facts_present"] for row in scored),
                       "cases_all_checked_facts_present": sum(row[f"at{k}"]["facts_present"] == row["facts_total"] for row in scored)}
            for k in [3, 5]}}
    write_json(OUTPUT / "instruction-coverage.json", {"scope": "Exact textual diagnostic coverage, not clinical approval; grouped facts equally weighted; equivalent text not exhaustively labelled; language controls duplicate two fact sets; selectors annotated after rankings were observed.",
               "definitions": definitions, "results": results, "summary": summary})
    shutil.copyfile(Path(__file__), OUTPUT / Path(__file__).name)
    shutil.copyfile(ROOT / "evals/test_token_chunking.py", OUTPUT / "test_token_chunking.py")
    command = [sys.executable, "-m", "pytest", "tests/test_semantic_retrieval.py", "../evals/test_token_chunking.py", "-q"]
    check = subprocess.run(command, cwd=ROOT / "backend", capture_output=True, text=True, encoding="utf-8")
    baseline_hashes = json.loads((OUTPUT / "protected-baseline.json").read_text(encoding="utf-8"))
    current_hashes = {name: digest((ROOT / name).read_bytes()) for name in baseline_hashes}
    lock = json.loads((OUTPUT / "embedding-model-lock.json").read_text(encoding="utf-8"))
    model_hashes = {name: digest((ROOT / "knowledge/local/embedding-model" / name).read_bytes()) for name in lock["files"]}
    children = json.loads((OUTPUT / "candidate-knowledge.json").read_text(encoding="utf-8"))["items"]
    spans = {s["id"]: s for s in json.loads((OUTPUT / "child-parent-spans.json").read_text(encoding="utf-8"))}
    parent_indices = {parent: index for index, parent in enumerate(parents)}
    old_vectors = np.load(OUTPUT / "baseline-embeddings.npy", allow_pickle=False)
    new_vectors = np.load(OUTPUT / "candidate-embeddings.npy", allow_pickle=False)
    unchanged = [(index, parent_indices[spans[child["id"]]["parent_id"]])
                 for index, child in enumerate(children)
                 if child["text"] == parents[spans[child["id"]]["parent_id"]]["text"]]
    max_difference = max(float(np.max(np.abs(new_vectors[i] - old_vectors[j]))) for i, j in unchanged)
    write_json(OUTPUT / "verification.json", {"pytest_command": command, "returncode": check.returncode,
               "stdout": check.stdout, "stderr": check.stderr,
               "protected_file_count": len(current_hashes), "protected_files_unchanged": current_hashes == baseline_hashes,
               "embedding_model_assets_unchanged": model_hashes == lock["files"], "embedding_asset_hashes": model_hashes,
               "unsplit_chunk_count": len(unchanged), "unsplit_vectors_max_absolute_difference": max_difference})
    assert check.returncode == 0 and current_hashes == baseline_hashes and model_hashes == lock["files"]
    assert max_difference < 1e-6, "Reembedding changed unsplit vectors"
    print(json.dumps({"summary": summary, "results": {v: [{k: r[k] for k in ["id", "facts_total"] if k in r} | {s: r[s]["facts_present"] for s in ["at3", "at5"] if s in r} for r in rows] for v, rows in results.items()}}, indent=2))


if __name__ == "__main__":
    main()
