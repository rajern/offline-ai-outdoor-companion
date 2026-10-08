"""Run exactly B3/B8 with the frozen prior packer and original query vectors.

Commands: run; summarize. No embedding inference, rebuild, Qwen generation or
production edits. summarize consumes manual scoring without rerunning retrieval.
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
import statistics
import sys

import numpy as np
import yaml

import run_retrieval_eval_v1 as prior

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "knowledge/local/diagnostics/retrieval-eval-v1-2026-10-07"
OUTPUT = ROOT / "knowledge/local/diagnostics/retrieval-topk-ablation-v1-2026-10-07"
PROTOCOL = ROOT / "evals/retrieval_topk_ablation.v1.json"


class Counter(prior.Counter):
    def count(self, text):
        key = hashlib.sha256(text.encode("utf-8")).hexdigest()
        original = BASE / "tokenization" / key
        if key not in self.cache and original.exists():
            assert (original / "input.txt").read_text(encoding="utf-8") == text
            ids = json.loads((original / "stdout.txt").read_text(encoding="utf-8"))
            assert all(isinstance(t, int) for t in ids)
            shutil.copytree(original, OUTPUT / "tokenization" / key)
            self.cache[key] = len(ids)
        return super().count(text)


def run():
    if OUTPUT.exists():
        raise RuntimeError(f"Refusing to overwrite existing experiment: {OUTPUT}")
    config = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    old = json.loads((BASE / "frozen-run.json").read_text(encoding="utf-8"))
    before = prior.protected_hashes()
    assert before == old["protected_before"], "Protected inputs differ from the baseline"
    for path, digest in [(prior.GOLD, config["gold_sha256"]), (prior.CORPUS, config["corpus_sha256"]),
                         (prior.PROTOCOL, config["inherited_protocol_sha256"]),
                         (Path(prior.__file__), config["packing_script_sha256"])]:
        assert prior.sha(path) == digest
    assert prior.sha(prior.TOKENIZER) == before[str(prior.TOKENIZER)]
    assert prior.sha(prior.MODEL) == before[str(prior.MODEL.relative_to(ROOT))]
    gold = yaml.safe_load(prior.GOLD.read_text(encoding="utf-8"))
    assert len(gold["cases"]) == 15
    parents = prior.load_knowledge_items(prior.CORPUS)
    index = json.loads((ROOT / "knowledge/local/index.json").read_text(encoding="utf-8"))
    assert index["item_ids"] == [i.id for i in parents]
    vectors = np.asarray(np.load(ROOT / "knowledge/local/embeddings.npy", allow_pickle=False), dtype=np.float32)
    vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
    original = json.loads((BASE / "retrieved-all.json").read_text(encoding="utf-8"))
    OUTPUT.mkdir()
    frozen = {"experiment": config, "experiment_sha256": prior.sha(PROTOCOL),
              "runner_sha256": prior.sha(Path(__file__)), "created_at": datetime.now(timezone.utc).isoformat(),
              "gold_version": gold["set_version"], "gold_hash": prior.sha(prior.GOLD),
              "corpus_hash": prior.sha(prior.CORPUS), "protected_before": before,
              "query_vector_source": str(BASE), "embedding_calls": 0, "generation_calls": 0,
              "configurations": config["configurations"], "controls": config["controls"],
              "baseline_raw_sha256": prior.sha(BASE / "retrieved-all.json"),
              "baseline_scoring_sha256": prior.sha(BASE / "scoring.json"),
              "runtime": {"python": sys.version, "executable": sys.executable,
                          "numpy": np.__version__, "numpy_path": np.__file__,
                          "yaml": yaml.__version__, "yaml_path": yaml.__file__},
              "runtime_note": "Old venv launcher has a missing base Python. Existing bundled runtime used without installing or modifying dependencies. Original production top-3 scores/ranks and full B3 contexts must reproduce exactly."}
    prior.write_json(OUTPUT / "frozen-run.json", frozen)
    for source in [PROTOCOL, prior.GOLD, prior.PROTOCOL, Path(__file__), Path(prior.__file__)]:
        shutil.copyfile(source, OUTPUT / source.name)
    shutil.copyfile(prior.CORPUS, OUTPUT / "corpus-snapshot.json")
    shutil.copyfile(ROOT / "knowledge/local/index.json", OUTPUT / "production-index.json")
    shutil.copyfile(ROOT / "knowledge/local/embeddings.npy", OUTPUT / "production-embeddings.npy")
    shutil.copyfile(ROOT / "knowledge/manifests/approved-sources.json", OUTPUT / "source-manifest.json")

    def no_network(*args, **kwargs):
        raise RuntimeError("Frozen offline experiment; network disabled")
    socket.socket.connect = no_network
    socket.create_connection = no_network
    prior.OUTPUT = OUTPUT  # Evaluation module's diagnostic output ONLY; no file/production change.
    counter = Counter()
    records = []
    for case in gold["cases"]:
        cid, question = case["id"], case["question"]
        vector_path = BASE / f"{cid}-query-vector.npy"
        q = np.load(vector_path, allow_pickle=False)[0]
        scores = vectors @ q
        eligible = sorted([n for n, item in enumerate(parents)
                           if scores[n] >= .35 and prior.allowed_in_jurisdiction(item, "NO")],
                          key=lambda n: (-float(scores[n]), parents[n].id))
        old_a = next(r for r in original if r["case_id"] == cid and r["configuration"] == "A")
        assert [parents[n].id for n in eligible[:3]] == [r["item"]["id"] for r in old_a["seeds"]]
        for n, old_seed in zip(eligible[:3], old_a["seeds"], strict=True):
            assert abs(float(scores[n]) - old_seed["score"]) < 1e-7
        shutil.copyfile(vector_path, OUTPUT / vector_path.name)
        for mode, k in [("B3", 3), ("B8", 8)]:
            seeds = [prior.RetrievedKnowledgeItem(parents[n], float(scores[n])) for n in eligible[:k]]
            results, packets, trace = prior.packed_b(question, seeds, parents, counter, 2000)
            context = prior.context_for(results)
            prompt = prior._build_grounded_prompt(question, results)
            prompt_tokens, prompt_key = counter.count(prompt)
            context_tokens, context_key = counter.count(context)
            assert prompt_tokens <= 2000
            if mode == "B3":
                old_b = next(r for r in original if r["case_id"] == cid and r["configuration"] == "B")
                assert [asdict(r) for r in results] == old_b["excerpts"]
                assert json.loads(json.dumps(packets)) == old_b["packets"]
                assert json.loads(json.dumps(trace)) == old_b["trace"]
                assert prompt_tokens == old_b["prompt_tokens"] and context_tokens == old_b["context_tokens"]
                assert context == (BASE / "B" / cid / "context.txt").read_text(encoding="utf-8")
            else:
                control = next(r for r in records if r["configuration"] == "B3" and r["case_id"] == cid)
                assert [asdict(r) for r in results][:control["chunk_count"]] == control["excerpts"]
            directory = OUTPUT / mode / cid
            directory.mkdir(parents=True)
            (directory / "context.txt").write_text(context, encoding="utf-8")
            (directory / "prompt-not-executed.txt").write_text(prompt, encoding="utf-8")
            row = {"configuration": mode, "semantic_seed_top_k": k, "case_id": cid, "question": question,
                   "expected_result": case["expected_result"], "gold_version": gold["set_version"],
                   "gold_hash": frozen["gold_hash"], "corpus_hash": frozen["corpus_hash"],
                   "experiment_sha256": frozen["experiment_sha256"], "context_budget": 2000,
                   "query_vector_sha256": prior.sha(vector_path),
                   "seeds": [asdict(r) for r in seeds], "excerpts": [asdict(r) for r in results],
                   "packets": packets, "trace": trace, "context_tokens": context_tokens,
                   "prompt_tokens": prompt_tokens, "prompt_tokenization_key": prompt_key,
                   "context_tokenization_key": context_key, "chunk_count": len(results),
                   "section_count": len({(r.item.document_id, r.item.section) for r in results}),
                   "packet_count": len(packets), "budget_excluded_packets": sum(t["status"] == "over_budget" for t in trace),
                   "context_sha256": hashlib.sha256(context.encode()).hexdigest()}
            prior.write_json(directory / "retrieved.json", row)
            records.append(row)
        a, b = records[-2:]
        print(f"{cid}: B3={a['chunk_count']}/{a['context_tokens']} tokens; B8={b['chunk_count']}/{b['context_tokens']} tokens; budget skips={b['budget_excluded_packets']}", flush=True)
    prior.write_json(OUTPUT / "retrieved-all.json", records)
    after = prior.protected_hashes()
    prior.write_json(OUTPUT / "integrity-after.json", {"protected_unchanged": before == after,
                     "protected_after": after, "experiment_unchanged": frozen["experiment_sha256"] == prior.sha(PROTOCOL),
                     "runner_unchanged": frozen["runner_sha256"] == prior.sha(Path(__file__))})
    assert before == after


def summarize():
    frozen = json.loads((OUTPUT / "frozen-run.json").read_text(encoding="utf-8"))
    assert prior.sha(prior.GOLD) == frozen["gold_hash"]
    gold = yaml.safe_load((OUTPUT / prior.GOLD.name).read_text(encoding="utf-8"))
    scores = json.loads((OUTPUT / "scoring.json").read_text(encoding="utf-8"))
    records = json.loads((OUTPUT / "retrieved-all.json").read_text(encoding="utf-8"))
    old_scores = json.loads((BASE / "scoring.json").read_text(encoding="utf-8"))
    assert scores["B3"] == old_scores["B"], "Baseline manual scoring must not change"
    summary = {}
    for mode in ["B3", "B8"]:
        covered, gaps = [], []
        for case in gold["cases"]:
            cid = case["id"]
            row = next(r for r in records if r["configuration"] == mode and r["case_id"] == cid)
            annotation = scores[mode][cid]
            assert len(annotation["items"]) == len(case["must_have_information"])
            text = {r["item"]["id"]: r["item"]["text"] for r in row["excerpts"]}
            for item in annotation["items"]:
                assert isinstance(item["covered"], bool) and item["reason"]
                assert not item["covered"] or item["evidence"]
                for ev in item["evidence"]:
                    assert ev["quote"] in text[ev["id"]]
            for label in ["irrelevant", "potentially_misleading", "jurisdiction_leakage"]:
                for ev in annotation[label]:
                    assert ev["quote"] in text[ev["id"]]
            found = sum(p["covered"] for p in annotation["items"])
            total = len(annotation["items"])
            gap = case["expected_result"] == "insufficient_coverage"
            result = {"case_id": cid, "title": case["title"], "expected_result": case["expected_result"],
                      "found": found, "total": total, "coverage": found/total if total else None,
                      "complete_pass": not gap and found == total, "scoring": annotation,
                      **{key: row[key] for key in ["context_tokens", "prompt_tokens", "chunk_count", "section_count", "packet_count", "budget_excluded_packets"]},
                      "raw_path": f"{mode}/{cid}/retrieved.json"}
            (gaps if gap else covered).append(result)
        aggregate = {"covered_cases": len(covered), "must_have_found": sum(r["found"] for r in covered),
                     "must_have_total": sum(r["total"] for r in covered),
                     "must_have_micro_coverage": sum(r["found"] for r in covered)/sum(r["total"] for r in covered),
                     "average_per_case_macro_coverage": statistics.mean(r["coverage"] for r in covered),
                     "complete_passes": sum(r["complete_pass"] for r in covered)}
        for label in ["irrelevant", "potentially_misleading", "jurisdiction_leakage"]:
            aggregate[label + "_cases"] = sum(bool(r["scoring"][label]) for r in covered)
        aggregate["either_noise_cases"] = sum(bool(r["scoring"]["irrelevant"] or r["scoring"]["potentially_misleading"]) for r in covered)
        for measure in ["context_tokens", "prompt_tokens", "chunk_count", "section_count", "packet_count"]:
            values = [r[measure] for r in covered]
            aggregate[measure] = {"mean": statistics.mean(values), "median": statistics.median(values), "max": max(values), "min": min(values)}
        aggregate["budget_excluded_packets"] = sum(r["budget_excluded_packets"] for r in covered)
        aggregate["budget_affected_cases"] = sum(r["budget_excluded_packets"] > 0 for r in covered)
        prior.write_json(OUTPUT / mode / "results.json", {"configuration": mode, "frozen_run": frozen,
                         "aggregate": aggregate, "per_case": covered, "insufficient_coverage": gaps,
                         "scoring_sha256": prior.sha(OUTPUT / "scoring.json"),
                         "raw_results_sha256": prior.sha(OUTPUT / "retrieved-all.json")})
        summary[mode] = aggregate
    prior.write_json(OUTPUT / "aggregate.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["run", "summarize"])
    args = parser.parse_args()
    run() if args.command == "run" else summarize()
