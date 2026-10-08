"""Control: SAME section expansion, but ORIGINAL production search ranking.

Run after compare_parent_context.py. No inference or production changes.
Keeps context budget/section rule constant to distinguish search from expansion.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import sys

import numpy as np

from compare_parent_context import INPUT, ROOT, TokenCounter, fact_coverage, pack
from outwise.knowledge.ingestion import digest, write_json
from outwise.knowledge.loader import load_knowledge_items


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    main_output = ROOT / "knowledge/local/diagnostics/parent-context-2026-10-07"
    output = main_output / "original-ranking-control"
    if output.exists():
        raise ValueError("Control output already exists")
    read = lambda path: json.loads(path.read_text(encoding="utf-8"))
    parameters = read(main_output / "parameters-parent-context.json")
    parent_list = load_knowledge_items(INPUT / "baseline-knowledge.json")
    parents = {item.id: item for item in parent_list}
    cases = read(INPUT / "retrieval-comparison.json")["baseline"]
    definitions = read(INPUT / "instruction-coverage.json")["definitions"]
    protected = read(INPUT / "protected-baseline.json")
    fingerprint = lambda: {name: digest((ROOT / name).read_bytes()) for name in protected}
    assert fingerprint() == protected
    output.mkdir()
    shutil.copyfile(Path(__file__), output / Path(__file__).name)
    counter = TokenCounter(Path(parameters["tokenizer_exe"]), Path(parameters["model_path"]), output)
    rows = []
    for case in cases:
        eligible = [r for r in case["all_ranking"] if r["allowed_in_NO"] and r["above_threshold"]]
        seeds = [{"rank": rank, "item": parents[r["id"]], "parent_id": r["id"], "score": r["score"],
                  "span": {"id": r["id"], "parent_id": r["id"], "start": 0, "end": len(parents[r["id"]].text)}}
                 for rank, r in enumerate(eligible, 1)]
        assert [s["item"].id for s in seeds[:5]] == [r["item"]["id"] for r in case["top5"]]
        row = {"id": case["id"], "question": case["question"]}
        for k in [3, 5]:
            context = pack(case["question"], seeds, "section_unique", k, parents, counter,
                           parameters["prompt_budget_qwen_tokens"])
            context["instruction_coverage"] = fact_coverage(case["id"], context["excerpts"], definitions, parents)
            row[f"at{k}"] = context
            directory = output / "contexts" / case["id"] / f"top-{k}"
            directory.mkdir(parents=True)
            (directory / "prompt.txt").write_text(context["prompt"], encoding="utf-8")
            write_json(directory / "context.json", context)
        rows.append(row)
        print(case["id"], {f"at{k}": (row[f"at{k}"]["instruction_coverage"].get("facts_present"),
                                         row[f"at{k}"]["prompt_tokens"]) for k in [3, 5]}, flush=True)
    summary = {}
    for k in [3, 5]:
        contexts = [r[f"at{k}"] for r in rows]
        scored = [c["instruction_coverage"] for c in contexts if "facts_total" in c["instruction_coverage"]]
        summary[f"at{k}"] = {"actionable_cases": len(scored), "complete_cases": sum(c["complete"] for c in scored),
                             "facts_total": sum(c["facts_total"] for c in scored), "facts_present": sum(c["facts_present"] for c in scored),
                             "prompt_tokens_mean_all_cases": float(np.mean([c["prompt_tokens"] for c in contexts])),
                             "prompt_tokens_max": max(c["prompt_tokens"] for c in contexts),
                             "over_budget_packet_skips": sum(t["status"] == "over_budget" for c in contexts for t in c["trace"])}
    write_json(output / "results.json", {"purpose": "Same expansion and budget as child section experiment; only search ranking changes",
               "parameters": parameters, "results": rows, "summary": summary})
    with Path(parameters["model_path"]).open("rb") as stream:
        model_hash = hashlib.file_digest(stream, "sha256").hexdigest()
    lock = read(INPUT / "embedding-model-lock.json")
    model_assets = {name: digest((ROOT / "knowledge/local/embedding-model" / name).read_bytes()) for name in lock["files"]}
    write_json(output / "verification.json", {"protected_files_unchanged": fingerprint() == protected,
               "qwen_gguf_unchanged": model_hash == parameters["model_sha256"], "embedding_model_assets_unchanged": model_assets == lock["files"],
               "generation_calls": 0, "tokenization_calls": len(counter.cache)})
    assert fingerprint() == protected and model_hash == parameters["model_sha256"] and model_assets == lock["files"]
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
