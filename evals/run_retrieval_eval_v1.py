"""One frozen A/B retrieval experiment, with offline tokenization only.

Run: backend/.venv/Scripts/python.exe evals/run_retrieval_eval_v1.py run
Then manually annotate scoring.json and run the `summarize` command, which
never retrieves or embeds. Raw copyrighted source text stays in ignored local
diagnostics. This module imports no generation/model service.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import shutil
import socket
import statistics
import subprocess
import sys

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from outwise.knowledge.loader import load_knowledge_items
from outwise.knowledge.models import RetrievedKnowledgeItem
from outwise.services.orchestrator import _build_grounded_prompt
from outwise.services.semantic_retrieval import SemanticRetrievalService, allowed_in_jurisdiction

OUTPUT = ROOT / "knowledge/local/diagnostics/retrieval-eval-v1-2026-10-07"
GOLD = ROOT / "evals/retrieval_cases.v1.yaml"
PROTOCOL = ROOT / "evals/retrieval_protocol.v1.yaml"
CORPUS = ROOT / "knowledge/local/knowledge.json"
MODEL = ROOT / "models/Qwen_Qwen3.5-2B-Q4_K_M.gguf"
TOKENIZER = Path(r"C:\Users\rajvi\AppData\Local\Microsoft\WinGet\Packages\ggml.llamacpp_Microsoft.Winget.Source_8wekyb3d8bbwe\llama-tokenize.exe")


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def protected_hashes():
    paths = [GOLD, CORPUS, MODEL, TOKENIZER, ROOT / "knowledge/manifests/approved-sources.json",
             ROOT / "knowledge/local/index.json", ROOT / "knowledge/local/embeddings.npy",
             ROOT / "TASKS.md", ROOT / "AGENTS.md", ROOT / "backend/pyproject.toml"]
    paths += list((ROOT / "backend/outwise").rglob("*.py"))
    paths += list((ROOT / "docs").rglob("*.md"))
    paths += [p for p in (ROOT / "knowledge/local/embedding-model").rglob("*") if p.is_file()]
    return {str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p): sha(p) for p in sorted(set(paths))}


def context_for(results):
    return "\n\n".join(f"[KUNNSKAPSUTDRAG {n}]\nTittel: {r.item.title}\nTema: {r.item.topic}\nInnhold: {r.item.text}"
                        for n, r in enumerate(results, 1))


class Counter:
    def __init__(self):
        self.cache = {}
        (OUTPUT / "tokenization").mkdir()

    def count(self, text):
        key = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if key not in self.cache:
            command = [str(TOKENIZER), "-m", str(MODEL), "--stdin", "--ids", "--offline"]
            proc = subprocess.run(command, input=text, capture_output=True, text=True, encoding="utf-8", timeout=30)
            target = OUTPUT / "tokenization" / key
            target.mkdir()
            (target / "input.txt").write_text(text, encoding="utf-8")
            (target / "stdout.txt").write_text(proc.stdout, encoding="utf-8")
            (target / "stderr.txt").write_text(proc.stderr, encoding="utf-8")
            write_json(target / "process.json", {"argv": command, "returncode": proc.returncode,
                                                "purpose": "tokenization only; no generation"})
            if proc.returncode:
                raise RuntimeError(f"Tokenization failed: {target}")
            tokens = json.loads(proc.stdout)
            assert isinstance(tokens, list) and all(isinstance(t, int) for t in tokens)
            self.cache[key] = len(tokens)
        return self.cache[key], key


def section_path(item):
    return tuple((item.section or item.id).split(" / "))


def narrow_members(seed, parents):
    """Identical generic branch rule to compare_retrieval_refinement.narrow_members."""
    document = seed.document_id or seed.source_url
    eligible = [item for item in parents if (item.document_id or item.source_url) == document
                and allowed_in_jurisdiction(item, "NO")]
    heading = section_path(seed)
    descendants = [item for item in eligible if len(section_path(item)) > len(heading)
                   and section_path(item)[:len(heading)] == heading]
    anchor = heading
    if not descendants and len(heading) > 1:
        ancestor = heading[:-1]
        branches = {section_path(item)[len(ancestor)] for item in eligible
                    if len(section_path(item)) > len(ancestor) and section_path(item)[:len(ancestor)] == ancestor}
        if len(ancestor) > 1 or len(branches) <= 1:
            anchor = ancestor
    branches = {section_path(item)[len(anchor)] for item in eligible
                if len(section_path(item)) > len(anchor) and section_path(item)[:len(anchor)] == anchor}
    exact_only = len(anchor) == 1 and len(branches) > 1
    members = [item for item in eligible if section_path(item) == anchor or
               (not exact_only and len(section_path(item)) > len(anchor)
                and section_path(item)[:len(anchor)] == anchor)]
    assert seed.id in {item.id for item in members}
    return (document, anchor, exact_only), members


def packed_b(question, seeds, parents, counter, budget):
    results, packets, trace, seen_groups, seen_ids = [], [], [], set(), set()
    for rank, seed in enumerate(seeds, 1):
        group, members = narrow_members(seed.item, parents)
        entry = {"seed_rank": rank, "seed_id": seed.item.id, "seed_score": seed.score, "group": group}
        if group in seen_groups or seed.item.id in seen_ids:
            trace.append({**entry, "status": "duplicate_branch"})
            continue
        seen_groups.add(group)
        added = [RetrievedKnowledgeItem(item, seed.score) for item in members if item.id not in seen_ids]
        count, key = counter.count(_build_grounded_prompt(question, results + added))
        if count > budget:
            trace.append({**entry, "status": "over_budget", "prompt_tokens": count,
                          "tokenization_key": key, "would_add": [r.item.id for r in added]})
            continue
        results.extend(added)
        seen_ids.update(r.item.id for r in added)
        packets.append({**entry, "member_ids": [r.item.id for r in added]})
        trace.append({**entry, "status": "accepted", "prompt_tokens": count, "tokenization_key": key})
    return results, packets, trace


def freeze_run():
    if OUTPUT.exists():
        raise RuntimeError(f"Refusing to overwrite a previous run: {OUTPUT}")
    protocol = yaml.safe_load(PROTOCOL.read_text(encoding="utf-8"))
    gold = yaml.safe_load(GOLD.read_text(encoding="utf-8"))
    assert sha(GOLD) == protocol["gold"]["sha256"]
    assert sha(CORPUS) == protocol["corpus"]["sha256"]
    assert len(gold["cases"]) == 15
    assert sha(TOKENIZER) == "466fa920e21d85bfc8a2977e724d5ef332074aa11839278f3ae3fe2fbf6a11af"
    assert sha(MODEL) == "57a1085840f497d764a7fc5d346922dbde961efb54cc792ea81d694fd846a1d8"
    OUTPUT.mkdir()
    before = protected_hashes()
    controls = protocol["controls"]
    config = {"created_at": datetime.now(timezone.utc).isoformat(), "gold_version": gold["set_version"],
              "gold_hash": sha(GOLD), "corpus_hash": sha(CORPUS), "protocol_hash": sha(PROTOCOL),
              "runner_hash": sha(Path(__file__)), "controls": controls,
              "configurations": protocol["configurations"], "protected_before": before,
              "runtime": {name: version(name) for name in ["numpy", "fastembed", "onnxruntime", "PyYAML"]},
              "python": sys.version, "generation_calls": 0}
    write_json(OUTPUT / "frozen-run.json", config)
    shutil.copyfile(GOLD, OUTPUT / GOLD.name)
    shutil.copyfile(PROTOCOL, OUTPUT / PROTOCOL.name)
    shutil.copyfile(Path(__file__), OUTPUT / Path(__file__).name)
    shutil.copyfile(ROOT / "knowledge/local/index.json", OUTPUT / "production-index.json")
    shutil.copyfile(CORPUS, OUTPUT / "corpus-snapshot.json")
    shutil.copyfile(ROOT / "knowledge/manifests/approved-sources.json", OUTPUT / "source-manifest.json")
    subprocess.run(["git", "status", "--short"], cwd=ROOT, stdout=(OUTPUT / "git-status-before.txt").open("w", encoding="utf-8"), check=True)

    def deny_network(*args, **kwargs):
        raise RuntimeError("Network disabled for frozen local retrieval evaluation")
    socket.socket.connect = deny_network
    socket.create_connection = deny_network
    service = SemanticRetrievalService.from_json(CORPUS)
    parents = load_knowledge_items(CORPUS)
    counter = Counter()
    underlying = service._embedder

    class CaptureEmbedder:
        def embed(self, texts):
            value = underlying.embed(texts)
            self.last = value.copy()
            return value
    capture = CaptureEmbedder()
    service._embedder = capture
    records = []
    for case in gold["cases"]:
        question, case_id = case["question"], case["id"]
        seeds = service.retrieve(question, top_k=controls["semantic_seeds"])
        np.save(OUTPUT / f"{case_id}-query-vector.npy", capture.last, allow_pickle=False)
        b_results, packets, trace = packed_b(question, seeds, parents, counter, controls["budget_tokens"])
        for mode, results, packet_rows, trace_rows in [
            ("A", seeds, [{"seed_id": s.item.id, "member_ids": [s.item.id]} for s in seeds], []),
            ("B", b_results, packets, trace),
        ]:
            directory = OUTPUT / mode / case_id
            directory.mkdir(parents=True)
            context = context_for(results)
            prompt = _build_grounded_prompt(question, results)
            prompt_tokens, prompt_key = counter.count(prompt)
            context_tokens, context_key = counter.count(context)
            assert prompt_tokens <= controls["budget_tokens"], "Baseline exceeds frozen common budget; stop, do not alter A"
            assert all(allowed_in_jurisdiction(r.item, case["jurisdiction"]) for r in results)
            (directory / "context.txt").write_text(context, encoding="utf-8")
            (directory / "prompt-not-executed.txt").write_text(prompt, encoding="utf-8")
            row = {"configuration": mode, "case_id": case_id, "question": question,
                   "expected_result": case["expected_result"], "gold_version": gold["set_version"],
                   "gold_hash": config["gold_hash"], "corpus_hash": config["corpus_hash"],
                   "protocol_hash": config["protocol_hash"], "context_budget": controls["budget_tokens"],
                   "seeds": [asdict(r) for r in seeds], "excerpts": [asdict(r) for r in results],
                   "packets": packet_rows, "trace": trace_rows, "context_tokens": context_tokens,
                   "prompt_tokens": prompt_tokens, "prompt_tokenization_key": prompt_key,
                   "context_tokenization_key": context_key, "chunk_count": len(results),
                   "section_count": len({(r.item.document_id, r.item.section) for r in results}),
                   "packet_count": len(packet_rows), "context_sha256": hashlib.sha256(context.encode()).hexdigest()}
            write_json(directory / "retrieved.json", row)
            records.append(row)
        print(f"{case_id}: A={len(seeds)} chunks; B={len(b_results)} chunks", flush=True)
    write_json(OUTPUT / "retrieved-all.json", records)
    after = protected_hashes()
    write_json(OUTPUT / "integrity-after.json", {"unchanged": before == after, "protected_after": after,
                                               "protocol_unchanged": config["protocol_hash"] == sha(PROTOCOL),
                                               "runner_unchanged": config["runner_hash"] == sha(Path(__file__))})
    assert before == after


def summarize():
    frozen = json.loads((OUTPUT / "frozen-run.json").read_text(encoding="utf-8"))
    gold = yaml.safe_load((OUTPUT / GOLD.name).read_text(encoding="utf-8"))
    assert sha(GOLD) == frozen["gold_hash"]
    scores = json.loads((OUTPUT / "scoring.json").read_text(encoding="utf-8"))
    records = json.loads((OUTPUT / "retrieved-all.json").read_text(encoding="utf-8"))
    summaries = {}
    for mode in ["A", "B"]:
        cases, gaps = [], []
        for case in gold["cases"]:
            raw = next(r for r in records if r["configuration"] == mode and r["case_id"] == case["id"])
            score = scores[mode][case["id"]]
            assert len(score["items"]) == len(case["must_have_information"])
            for item in score["items"]:
                assert isinstance(item["covered"], bool)
                assert item["reason"]
                assert not item["covered"] or item["evidence"]
                for evidence in item["evidence"]:
                    passage = next(r["item"]["text"] for r in raw["excerpts"] if r["item"]["id"] == evidence["id"])
                    assert evidence["quote"] in passage, (mode, case["id"], evidence)
                    evidence["start"] = passage.index(evidence["quote"])
                    evidence["end"] = evidence["start"] + len(evidence["quote"])
            for label in ["irrelevant", "potentially_misleading", "jurisdiction_leakage"]:
                for finding in score[label]:
                    passage = next(r["item"]["text"] for r in raw["excerpts"] if r["item"]["id"] == finding["id"])
                    assert finding["quote"] in passage
            found = sum(item["covered"] for item in score["items"])
            total = len(score["items"])
            gap = case["expected_result"] == "insufficient_coverage"
            result = {"case_id": case["id"], "title": case["title"], "expected_result": case["expected_result"],
                      "found": found, "total": total, "coverage": found / total if total else None,
                      "complete_pass": not gap and found == total, "scoring": score,
                      "context_tokens": raw["context_tokens"], "prompt_tokens": raw["prompt_tokens"],
                      "chunk_count": raw["chunk_count"], "section_count": raw["section_count"],
                      "packet_count": raw["packet_count"], "raw_path": f"{mode}/{case['id']}/retrieved.json"}
            (gaps if gap else cases).append(result)
        total = sum(r["total"] for r in cases)
        found = sum(r["found"] for r in cases)
        aggregate = {"covered_cases": len(cases), "must_have_found": found, "must_have_total": total,
                     "must_have_micro_coverage": found / total,
                     "average_per_case_macro_coverage": statistics.mean(r["coverage"] for r in cases),
                     "complete_passes": sum(r["complete_pass"] for r in cases),
                     "irrelevant_cases": sum(bool(r["scoring"]["irrelevant"]) for r in cases),
                     "potentially_misleading_cases": sum(bool(r["scoring"]["potentially_misleading"]) for r in cases),
                     "either_noise_cases": sum(bool(r["scoring"]["irrelevant"] or r["scoring"]["potentially_misleading"]) for r in cases),
                     "jurisdiction_leakage_cases": sum(bool(r["scoring"]["jurisdiction_leakage"]) for r in cases),
                     "jurisdiction_leakage_passages": sum(len(r["scoring"]["jurisdiction_leakage"]) for r in cases)}
        for measure in ["context_tokens", "prompt_tokens", "chunk_count", "section_count", "packet_count"]:
            values = [r[measure] for r in cases]
            aggregate[measure] = {"mean": statistics.mean(values), "median": statistics.median(values), "max": max(values), "min": min(values)}
        summary = {"configuration": mode, "frozen_run": frozen, "aggregate": aggregate,
                   "per_case": cases, "insufficient_coverage": gaps,
                   "scoring_sha256": sha(OUTPUT / "scoring.json"),
                   "raw_results_sha256": sha(OUTPUT / "retrieved-all.json")}
        write_json(OUTPUT / mode / "results.json", summary)
        summaries[mode] = aggregate
    write_json(OUTPUT / "aggregate.json", summaries)
    write_json(OUTPUT / "scoring-with-offsets.json", scores)
    print(json.dumps(summaries, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["run", "summarize"])
    args = parser.parse_args()
    freeze_run() if args.command == "run" else summarize()
