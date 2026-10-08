"""Isolated retrieval-context experiment, not a production retriever.

Reuse frozen child/query vectors from compare_token_chunking.py. Compare direct
child context, restoring original parents, unique parents and unique section
roots. Count complete prompts with the LOCKED GGUF's existing llama-tokenize;
never run generation, rebuild production assets or access external sources.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from outwise.knowledge.ingestion import digest, write_json
from outwise.knowledge.loader import load_knowledge_items
from outwise.knowledge.models import RetrievedKnowledgeItem
from outwise.services.orchestrator import _build_grounded_prompt
from outwise.services.semantic_retrieval import allowed_in_jurisdiction

INPUT = ROOT / "knowledge/local/diagnostics/token-chunking-2026-10-07"


def section_key(item):
    # A heading root and all of its descendants in the SAME frozen document.
    # No fuzzy heading match, medical rules, gold-based expansion or source URLs.
    return (item.document_id or item.source_url, (item.section or item.id).split(" / ")[0])


def packet_members(seed, mode, parents):
    if mode != "section_unique":
        return [seed]
    key = section_key(seed)
    return [item for item in parents.values()
            if section_key(item) == key and allowed_in_jurisdiction(item, "NO")]


def prompt_for(question, excerpts):
    return _build_grounded_prompt(question, [RetrievedKnowledgeItem(row["item"], row["score"]) for row in excerpts])


class TokenCounter:
    def __init__(self, executable, model, output):
        self.executable, self.model = executable, model
        self.directory = output / "tokenization"
        self.directory.mkdir()
        self.cache = {}

    def count(self, prompt):
        key = digest(prompt.encode("utf-8"))
        if key not in self.cache:
            command = [str(self.executable), "-m", str(self.model), "--stdin", "--ids", "--offline"]
            started = time.monotonic()
            result = subprocess.run(command, input=prompt, capture_output=True, text=True, encoding="utf-8", timeout=30)
            directory = self.directory / key
            directory.mkdir()
            (directory / "prompt.txt").write_text(prompt, encoding="utf-8")
            (directory / "stdout.txt").write_text(result.stdout, encoding="utf-8")
            (directory / "stderr.txt").write_text(result.stderr, encoding="utf-8")
            write_json(directory / "process.json", {"argv": command, "returncode": result.returncode,
                       "elapsed_seconds": time.monotonic() - started, "purpose": "tokenization ONLY; no generation"})
            if result.returncode != 0:
                raise RuntimeError(f"Tokenizer failed: {directory}")
            tokens = json.loads(result.stdout)
            assert isinstance(tokens, list) and all(isinstance(i, int) for i in tokens)
            self.cache[key] = len(tokens)
        return self.cache[key], key


def pack(question, seeds, mode, top_k, parents, counter, budget):
    """Atomic packets; deduplicate, never truncate instructions to fit budget.

    parent_restore consumes exactly the first K child hits (control). Unique
    modes continue through the fixed eligible child ranking until K unique
    packets fit, or candidates are exhausted. All skipped packets are recorded.
    """
    scan = seeds[:top_k] if mode in {"current", "child", "parent_restore"} else seeds
    accepted, excerpts, seen_groups, seen_ids, trace = [], [], set(), set(), []
    for seed in scan:
        item = seed["item"]
        group = section_key(parents[seed["parent_id"]]) if mode == "section_unique" else seed["parent_id"]
        entry = {"child_rank": seed["rank"], "seed_id": item.id, "score": seed["score"], "group": group}
        if group in seen_groups and mode != "child":
            trace.append({**entry, "status": "duplicate_group"})
            continue
        seen_groups.add(group)
        members = [item] if mode in {"current", "child"} else packet_members(parents[seed["parent_id"]], mode, parents)
        added = [{"item": member, "score": seed["score"],
                  "span": seed["span"] if mode in {"current", "child"}
                  else {"id": member.id, "parent_id": member.id, "start": 0, "end": len(member.text)},
                  "packet_rank": len(accepted) + 1, "seed_id": item.id}
                 for member in members if member.id not in seen_ids]
        if not added:
            trace.append({**entry, "status": "already_in_context"})
            continue
        candidate_count, key = counter.count(prompt_for(question, excerpts + added))
        if candidate_count > budget:
            trace.append({**entry, "status": "over_budget", "candidate_prompt_tokens": candidate_count,
                          "tokenization_key": key, "would_add": [row["item"].id for row in added]})
            continue
        accepted.append({**entry, "packet_rank": len(accepted) + 1, "member_ids": [row["item"].id for row in added]})
        excerpts.extend(added)
        seen_ids.update(row["item"].id for row in added)
        trace.append({**entry, "status": "accepted", "candidate_prompt_tokens": candidate_count, "tokenization_key": key})
        if mode in {"parent_unique", "section_unique"} and len(accepted) == top_k:
            break
    prompt = prompt_for(question, excerpts)
    count, key = counter.count(prompt)
    assert count <= budget
    return {"packets": accepted, "excerpts": [{**row, "item": asdict(row["item"])} for row in excerpts],
            "trace": trace, "prompt": prompt, "prompt_tokens": count, "tokenization_key": key,
            "distinct_parent_count": len({row["span"]["parent_id"] for row in excerpts})}


def fact_coverage(case_id, excerpts, definitions, parents):
    if case_id not in definitions:
        return {"not_scored": "knowledge gap / negative control"}
    intervals = {}
    for row in excerpts:
        span = row["span"]
        intervals.setdefault(span["parent_id"], []).append((span["start"], span["end"]))
    def present(reference):
        covered = {i for start, end in intervals.get(reference["parent_id"], []) for i in range(start, end)}
        text = parents[reference["parent_id"]].text
        return all(all(i in covered for i in range(span["start"], span["end"]) if not text[i].isspace())
                   for span in reference["spans"])
    facts = [{"label": unit["label"], "present": any(all(present(reference) for reference in option)
              for option in unit["alternatives"])} for unit in definitions[case_id]]
    return {"facts_total": len(facts), "facts_present": sum(f["present"] for f in facts),
            "complete": all(f["present"] for f in facts), "facts": facts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "knowledge/local/diagnostics/parent-context-2026-10-07")
    parser.add_argument("--prompt-budget", type=int, default=2000)
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to((ROOT / "knowledge/local/diagnostics").resolve()) or output.exists():
        raise ValueError("Output must be a NEW directory under ignored knowledge/local/diagnostics")
    if not 1000 <= args.prompt_budget <= 3000:
        raise ValueError("Diagnostic prompt budget must be between 1000 and 3000 tokens")
    sys.stdout.reconfigure(encoding="utf-8")
    def no_network(*args, **kwargs):
        raise AssertionError("Python network forbidden")
    socket.socket.connect = no_network
    socket.create_connection = no_network
    read = lambda path: json.loads(path.read_text(encoding="utf-8"))
    protected = read(INPUT / "protected-baseline.json")
    fingerprint = lambda: {name: digest((ROOT / name).read_bytes()) for name in protected}
    before = fingerprint()
    assert before == protected, "Protected production inputs changed"
    lock = read(INPUT / "embedding-model-lock.json")
    embedding_hashes = lambda: {name: digest((ROOT / "knowledge/local/embedding-model" / name).read_bytes()) for name in lock["files"]}
    assert embedding_hashes() == lock["files"]
    old_environment = read(ROOT / "knowledge/local/diagnostics/m2-06-2026-10-07/environment.json")
    model = Path(old_environment["model_path"])
    with model.open("rb") as stream:
        model_hash = hashlib.file_digest(stream, "sha256").hexdigest()
    assert model_hash == old_environment["model_sha256"]
    tokenizer_exe = Path(old_environment["runtime"][0]).with_name("llama-tokenize.exe")
    assert tokenizer_exe.is_file()
    previous = read(INPUT / "retrieval-comparison.json")
    instructions = read(INPUT / "instruction-coverage.json")
    parents_list = load_knowledge_items(INPUT / "baseline-knowledge.json")
    parents = {item.id: item for item in parents_list}
    children = load_knowledge_items(INPUT / "candidate-knowledge.json")
    children_by_id = {item.id: item for item in children}
    spans = {row["id"]: row for row in read(INPUT / "child-parent-spans.json")}
    vectors = np.load(INPUT / "candidate-embeddings.npy", allow_pickle=False)
    queries = np.load(INPUT / "query-embeddings.npy", allow_pickle=False)
    vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
    source_files = ["baseline-knowledge.json", "baseline-embeddings.npy", "candidate-knowledge.json",
                    "candidate-embeddings.npy", "query-embeddings.npy", "child-parent-spans.json",
                    "retrieval-comparison.json", "instruction-coverage.json", "parameters.json",
                    "embedding-model-lock.json", "approved-sources.json", "protected-baseline.json"]
    output.mkdir(parents=True)
    for name in source_files:
        shutil.copyfile(INPUT / name, output / name)
    shutil.copyfile(Path(__file__), output / Path(__file__).name)
    write_json(output / "parameters-parent-context.json", {
        "utc_started": datetime.now(timezone.utc).isoformat(), "prompt_budget_qwen_tokens": args.prompt_budget,
        "production_context_size": 4096, "production_max_answer_tokens": 256,
        "token_count_note": "Complete unmodified grounded prompt; chat-template overhead excluded; at least 1840 tokens of margin. No inference.",
        "tokenizer_exe": str(tokenizer_exe), "tokenizer_exe_sha256": digest(tokenizer_exe.read_bytes()),
        "model_path": str(model), "model_sha256": model_hash,
        "source_input_hashes": {name: digest((INPUT / name).read_bytes()) for name in source_files},
        "threshold": .35, "jurisdiction": "NO", "top_k_packets": [3, 5],
        "section_rule": "Exact first heading component before ' / ', same document; every expanded member filtered independently for NO eligibility",
        "budget_rule": "Atomic whole packets; skip over-budget packet, never truncate; unique modes continue to next eligible distinct packet",
        "ranking_rule": "Fixed previous child cosine ranking; packet score is highest triggering child score, NOT expanded-text similarity",
        "modes": {"current": "original production top K, budget checked",
                  "child": "previous token-adapted top K, budget checked",
                  "parent_restore": "first K child hits restored to whole original parent; dedup without refill",
                  "parent_unique": "top K distinct original parents using child ranking; refill duplicates/budget skips",
                  "section_unique": "top K distinct section roots using child ranking; full eligible section expansion"},
        "generation": "None; llama-tokenize only", "network": "Python connections denied and tokenizer --offline"})
    counter = TokenCounter(tokenizer_exe, model, output)
    results = {mode: [] for mode in ["current", "child", "parent_restore", "parent_unique", "section_unique"]}
    for index, case in enumerate(previous["baseline"]):
        scores = vectors @ queries[index]
        ranked = sorted(zip(children, scores, strict=True), key=lambda pair: (-float(pair[1]), pair[0].id))
        eligible = [(item, float(score)) for item, score in ranked if score >= .35 and allowed_in_jurisdiction(item, "NO")]
        seeds = [{"rank": rank, "item": item, "parent_id": spans[item.id]["parent_id"], "score": score, "span": spans[item.id]}
                 for rank, (item, score) in enumerate(eligible, 1)]
        assert [s["item"].id for s in seeds[:5]] == [r["item"]["id"] for r in previous["token_aligned"][index]["top5"]]
        assert np.allclose([s["score"] for s in seeds[:5]], [r["score"] for r in previous["token_aligned"][index]["top5"]], atol=1e-6, rtol=0)
        write_json(output / f"child-ranking-{case['id']}.json", previous["token_aligned"][index]["all_ranking"])
        current_seeds = [{"rank": match["rank"], "item": parents[match["item"]["id"]],
                          "parent_id": match["item"]["id"], "score": match["score"], "span": match["span"]} for match in case["top5"]]
        for mode in results:
            row = {"id": case["id"], "question": case["question"], "coverage": case["coverage"],
                   "gold_ids": case["gold_ids"], "owner_review": case.get("owner_review")}
            for k in [3, 5]:
                packed = pack(case["question"], current_seeds if mode == "current" else seeds,
                              mode, k, parents, counter, args.prompt_budget)
                packed["instruction_coverage"] = fact_coverage(case["id"], packed["excerpts"], instructions["definitions"], parents)
                row[f"at{k}"] = packed
                directory = output / "contexts" / mode / case["id"] / f"top-{k}"
                directory.mkdir(parents=True)
                (directory / "prompt.txt").write_text(packed["prompt"], encoding="utf-8")
                write_json(directory / "context.json", packed)
            results[mode].append(row)
            print(case["id"], mode, {f"at{k}": (row[f"at{k}"]["instruction_coverage"].get("facts_present"),
                                                   row[f"at{k}"]["prompt_tokens"]) for k in [3, 5]}, flush=True)
        write_json(output / "results-partial.json", results)
    summary = {}
    for mode, rows in results.items():
        summary[mode] = {}
        for k in [3, 5]:
            contexts = [r[f"at{k}"] for r in rows]
            scored = [c["instruction_coverage"] for c in contexts if "facts_total" in c["instruction_coverage"]]
            summary[mode][f"at{k}"] = {
                "actionable_cases": len(scored), "facts_total": sum(c["facts_total"] for c in scored),
                "facts_present": sum(c["facts_present"] for c in scored), "complete_cases": sum(c["complete"] for c in scored),
                "prompt_tokens_mean_all_cases": float(np.mean([c["prompt_tokens"] for c in contexts])),
                "prompt_tokens_max": max(c["prompt_tokens"] for c in contexts),
                "expanded_parents_mean_all_cases": float(np.mean([c["distinct_parent_count"] for c in contexts])),
                "over_budget_packet_skips": sum(t["status"] == "over_budget" for c in contexts for t in c["trace"])}
    write_json(output / "results.json", {"definitions": instructions["definitions"], "results": results, "summary": summary})
    command = [sys.executable, "-m", "pytest", "tests/test_semantic_retrieval.py", "../evals/test_parent_context.py", "-q"]
    check = subprocess.run(command, cwd=ROOT / "backend", capture_output=True, text=True, encoding="utf-8")
    shutil.copyfile(ROOT / "evals/test_parent_context.py", output / "test_parent_context.py")
    after = fingerprint()
    with model.open("rb") as stream:
        after_model_hash = hashlib.file_digest(stream, "sha256").hexdigest()
    write_json(output / "verification.json", {"protected_file_count": len(after), "protected_files_unchanged": before == after,
               "embedding_model_assets_unchanged": embedding_hashes() == lock["files"], "qwen_gguf_unchanged": after_model_hash == model_hash,
               "input_artifacts_unchanged": all(digest((INPUT / name).read_bytes()) == digest((output / name).read_bytes()) for name in source_files),
               "pytest_command": command, "returncode": check.returncode, "stdout": check.stdout, "stderr": check.stderr,
               "tokenization_calls": len(counter.cache), "generation_calls": 0, "hashes": after})
    assert before == after and after_model_hash == model_hash and embedding_hashes() == lock["files"] and check.returncode == 0
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
