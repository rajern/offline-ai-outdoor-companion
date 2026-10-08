"""One selection-unit ablation on saved C8; no embeddings or generation.

run packs only C8U8, from frozen saved child scores. summarize reads manual
annotations. All original production and previous experiment files are read-only.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import socket
import statistics
import sys

import yaml
import run_retrieval_eval_v1 as prior

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "knowledge/local/diagnostics/retrieval-child-search-v1-2026-10-07"
OUTPUT = ROOT / "knowledge/local/diagnostics/retrieval-parent-dedup-v1-2026-10-07"
PROTOCOL = ROOT / "evals/retrieval_parent_dedup.v1.json"


class Counter(prior.Counter):
    def count(self, text):
        key = prior.hashlib.sha256(text.encode()).hexdigest()
        caches = [BASE, ROOT / "knowledge/local/diagnostics/retrieval-topk-ablation-v1-2026-10-07",
                  ROOT / "knowledge/local/diagnostics/retrieval-eval-v1-2026-10-07"]
        for cache in caches:
            saved = cache / "tokenization" / key
            if key not in self.cache and saved.exists():
                assert (saved / "input.txt").read_text(encoding="utf-8") == text
                ids = json.loads((saved / "stdout.txt").read_text(encoding="utf-8"))
                assert all(isinstance(id, int) for id in ids)
                shutil.copytree(saved, OUTPUT / "tokenization" / key)
                self.cache[key] = len(ids)
        return super().count(text)


def baseline_hashes():
    paths = ["frozen-run.json", "children.json", "child-index.json", "child-embeddings.npy",
             "scoring.json", "aggregate.json", "retrieved-all.json", "ranking-evidence-targets.json"]
    paths += [str(p.relative_to(BASE)) for p in (BASE / "C8").rglob("*") if p.is_file()]
    paths += [str(p.relative_to(BASE)) for p in BASE.glob("case-*-query-vector.npy")]
    return {path: prior.sha(BASE / path) for path in sorted(set(paths))}


def select_unique(candidates, children, parents):
    # First eligible hit for a parent is its best child. Ties use saved child-ID order.
    selected, seen = [], set()
    for row in candidates:
        child = children[row["child_id"]]
        parent = parents[child["parent_id"]]
        assert row["parent_id"] == parent.id
        if row["score"] < .35 or not prior.allowed_in_jurisdiction(parent, "NO"):
            continue
        if parent.id in seen:
            continue
        seen.add(parent.id)
        selected.append(row)
        if len(selected) == 8:
            break
    return selected


def run():
    if OUTPUT.exists():
        raise RuntimeError(f"Refusing to overwrite existing experiment: {OUTPUT}")
    config = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    old_frozen = json.loads((BASE / "frozen-run.json").read_text(encoding="utf-8"))
    protected = prior.protected_hashes()
    assert protected == old_frozen["protected_before"]
    for path, key in [(prior.GOLD, "gold_sha256"), (prior.CORPUS, "corpus_sha256"),
                      (BASE / "children.json", "child_inputs_sha256"),
                      (BASE / "child-embeddings.npy", "child_vectors_sha256"),
                      (Path(prior.__file__), "packing_script_sha256")]:
        assert prior.sha(path) == config[key]
    gold = yaml.safe_load(prior.GOLD.read_text(encoding="utf-8"))
    old_rows = json.loads((BASE / "retrieved-all.json").read_text(encoding="utf-8"))
    control = [r for r in old_rows if r["configuration"] == "C8"]
    assert len(control) == len(gold["cases"]) == 15
    children = {c["child_id"]: c for c in json.loads((BASE / "children.json").read_text(encoding="utf-8"))}
    parents_list = prior.load_knowledge_items(prior.CORPUS)
    parents = {p.id: p for p in parents_list}
    inputs = baseline_hashes()
    OUTPUT.mkdir()
    frozen = {"experiment": config, "experiment_sha256": prior.sha(PROTOCOL),
              "runner_sha256": prior.sha(Path(__file__)), "created_at": datetime.now(timezone.utc).isoformat(),
              "protected_before": protected, "baseline_inputs_before": inputs,
              "gold_version": gold["set_version"], "gold_hash": prior.sha(prior.GOLD),
              "corpus_hash": prior.sha(prior.CORPUS), "python": sys.version,
              "python_executable": sys.executable, "baseline_retrieval_calls": 0,
              "embedding_calls": 0, "generation_calls": 0,
              "scores": "Exact saved C8 scores; no dot-product recalculation, reranking or embedding inference"}
    prior.write_json(OUTPUT / "frozen-run.json", frozen)
    for source in [PROTOCOL, prior.GOLD, prior.PROTOCOL, Path(__file__), Path(prior.__file__)]:
        shutil.copyfile(source, OUTPUT / source.name)
    shutil.copytree(BASE / "C8", OUTPUT / "C8")
    shutil.copyfile(BASE / "C8/results.json", OUTPUT / "baseline-original-C8-results.json")
    for name in ["children.json", "child-index.json", "child-embeddings.npy", "ranking-evidence-targets.json"]:
        shutil.copyfile(BASE / name, OUTPUT / name)
    shutil.copyfile(prior.CORPUS, OUTPUT / "corpus-snapshot.json")
    shutil.copyfile(ROOT / "knowledge/manifests/approved-sources.json", OUTPUT / "source-manifest.json")
    def no_network(*args, **kwargs):
        raise RuntimeError("Offline parent-dedup experiment; network denied")
    socket.socket.connect = no_network
    socket.create_connection = no_network
    prior.OUTPUT = OUTPUT
    counter = Counter()
    records = list(control)
    for case in gold["cases"]:
        cid, question = case["id"], case["question"]
        old = next(r for r in control if r["case_id"] == cid)
        ranking = json.loads((BASE / "C8" / cid / "all-candidates.json").read_text(encoding="utf-8"))
        assert len(ranking) == len(children)
        assert ranking == sorted(ranking, key=lambda r: (-r["score"], r["child_id"]))
        eligible = [r for r in ranking if r["score"] >= .35 and prior.allowed_in_jurisdiction(parents[r["parent_id"]], "NO")]
        assert [r["child_id"] for r in eligible[:8]] == [s["child"]["child_id"] for s in old["child_seeds"]]
        for r, saved in zip(eligible[:8], old["child_seeds"], strict=True):
            assert r["score"] == saved["score"]
        selected = select_unique(ranking, children, parents)
        seeds = [prior.RetrievedKnowledgeItem(parents[r["parent_id"]], r["score"]) for r in selected]
        assert len(seeds) == len({s.item.id for s in seeds}) <= 8
        results, packets, trace = prior.packed_b(question, seeds, parents_list, counter, 2000)
        # Removing repeated parent hits cannot remove any old context; additions
        # happen after the original distinct parents, with unchanged atomic packing.
        assert [asdict(r) for r in results][:old["chunk_count"]] == old["excerpts"]
        for t in trace:
            hit = selected[t["seed_rank"]-1]
            t["child_id"] = hit["child_id"]
            t["original_child_rank"] = hit["jurisdiction_rank"]
        context = prior.context_for(results)
        prompt = prior._build_grounded_prompt(question, results)
        pt, pk = counter.count(prompt)
        ct, ck = counter.count(context)
        assert pt <= 2000
        directory = OUTPUT / "C8U8" / cid
        directory.mkdir(parents=True)
        qpath = BASE / f"{cid}-query-vector.npy"
        shutil.copyfile(qpath, OUTPUT / qpath.name)
        old_ids = {e["item"]["id"] for e in old["excerpts"]}
        row = {"configuration": "C8U8", "case_id": cid, "question": question,
               "expected_result": case["expected_result"], "gold_hash": frozen["gold_hash"],
               "corpus_hash": frozen["corpus_hash"], "experiment_sha256": frozen["experiment_sha256"],
               "context_budget": 2000, "parent_top_k": 8,
               "query_vector_sha256": prior.sha(qpath), "seeds": [asdict(s) for s in seeds],
               "child_seeds": [{"child": children[r["child_id"]], "score": r["score"], "rank": r["jurisdiction_rank"]} for r in selected],
               "selected_parent_count": len(seeds),
               "excerpts": [asdict(r) for r in results], "packets": packets, "trace": trace,
               "chunk_count": len(results), "section_count": len({(r.item.document_id, r.item.section) for r in results}),
               "packet_count": len(packets), "context_tokens": ct, "prompt_tokens": pt,
               "prompt_tokenization_key": pk, "context_tokenization_key": ck,
               "budget_excluded_packets": sum(t["status"] == "over_budget" for t in trace),
               "duplicate_packets": sum(t["status"] == "duplicate_branch" for t in trace),
               "added_excerpt_ids": [r.item.id for r in results if r.item.id not in old_ids],
               "context_sha256": prior.hashlib.sha256(context.encode()).hexdigest()}
        (directory / "context.txt").write_text(context, encoding="utf-8")
        (directory / "prompt-not-executed.txt").write_text(prompt, encoding="utf-8")
        prior.write_json(directory / "retrieved.json", row)
        prior.write_json(directory / "all-candidates.json", ranking)
        prior.write_json(directory / "selection-audit.json", {"old_child_ids": [s["child"]["child_id"] for s in old["child_seeds"]],
                         "old_distinct_parent_count": old["unique_seed_parents"], "selected_best_children": selected,
                         "newly_selected_parent_ids": [s.item.id for s in seeds if s.item.id not in {r["item"]["id"] for r in old["seeds"]}],
                         "scores_unchanged": True, "prior_context_is_exact_prefix": True})
        records.append(row)
        print(f"{cid}: {old['unique_seed_parents']} -> {len(seeds)} unique parents; added={row['added_excerpt_ids']}; context={ct}, prompt={pt}; budget rejects={row['budget_excluded_packets']}", flush=True)
    prior.write_json(OUTPUT / "retrieved-all.json", records)
    after = prior.protected_hashes()
    unchanged = baseline_hashes() == inputs
    prior.write_json(OUTPUT / "integrity-after.json", {"protected_unchanged": protected == after,
                     "baseline_inputs_unchanged": unchanged, "protected_after": after,
                     "experiment_unchanged": frozen["experiment_sha256"] == prior.sha(PROTOCOL),
                     "runner_unchanged": frozen["runner_sha256"] == prior.sha(Path(__file__))})
    assert protected == after and unchanged


def summarize():
    frozen = json.loads((OUTPUT / "frozen-run.json").read_text(encoding="utf-8"))
    assert prior.sha(prior.GOLD) == frozen["gold_hash"]
    gold = yaml.safe_load((OUTPUT / prior.GOLD.name).read_text(encoding="utf-8"))
    scores = json.loads((OUTPUT / "scoring.json").read_text(encoding="utf-8"))
    assert scores["C8"] == json.loads((BASE / "scoring.json").read_text(encoding="utf-8"))["C8"]
    records = json.loads((OUTPUT / "retrieved-all.json").read_text(encoding="utf-8"))
    summaries = {}
    for mode in ["C8", "C8U8"]:
        supported, gaps = [], []
        for case in gold["cases"]:
            cid = case["id"]
            row = next(r for r in records if r["configuration"] == mode and r["case_id"] == cid)
            score = scores[mode][cid]
            text = {r["item"]["id"]: r["item"]["text"] for r in row["excerpts"]}
            assert len(score["items"]) == len(case["must_have_information"])
            for item in score["items"]:
                assert isinstance(item["covered"], bool) and item["reason"]
                assert not item["covered"] or item["evidence"]
                for ev in item["evidence"]:
                    assert ev["quote"] in text[ev["id"]]
            for label in ["irrelevant", "potentially_misleading", "jurisdiction_leakage"]:
                for ev in score[label]:
                    assert ev["quote"] in text[ev["id"]]
            found, total = sum(p["covered"] for p in score["items"]), len(score["items"])
            gap = case["expected_result"] == "insufficient_coverage"
            result = {"case_id": cid, "title": case["title"], "expected_result": case["expected_result"],
                      "found": found, "total": total, "coverage": found/total if total else None,
                      "complete_pass": not gap and found == total, "scoring": score,
                      **{key: row[key] for key in ["context_tokens", "prompt_tokens", "chunk_count", "section_count", "packet_count", "budget_excluded_packets", "duplicate_packets"]},
                      "raw_path": f"{mode}/{cid}/retrieved.json"}
            (gaps if gap else supported).append(result)
        aggregate = {"covered_cases": len(supported), "must_have_found": sum(r["found"] for r in supported),
                     "must_have_total": sum(r["total"] for r in supported),
                     "must_have_micro_coverage": sum(r["found"] for r in supported)/sum(r["total"] for r in supported),
                     "average_per_case_macro_coverage": statistics.mean(r["coverage"] for r in supported),
                     "complete_passes": sum(r["complete_pass"] for r in supported)}
        for label in ["irrelevant", "potentially_misleading", "jurisdiction_leakage"]:
            aggregate[label+"_cases"] = sum(bool(r["scoring"][label]) for r in supported)
        aggregate["either_noise_cases"] = sum(bool(r["scoring"]["irrelevant"] or r["scoring"]["potentially_misleading"]) for r in supported)
        for key in ["context_tokens", "prompt_tokens", "chunk_count", "section_count", "packet_count"]:
            values = [r[key] for r in supported]
            aggregate[key] = {"min": min(values), "median": statistics.median(values), "mean": statistics.mean(values), "max": max(values)}
        aggregate["budget_excluded_packets"] = sum(r["budget_excluded_packets"] for r in supported)
        aggregate["budget_affected_cases"] = sum(r["budget_excluded_packets"] > 0 for r in supported)
        aggregate["duplicate_packets"] = sum(r["duplicate_packets"] for r in supported)
        prior.write_json(OUTPUT / mode / "results.json", {"configuration": mode, "aggregate": aggregate,
                         "per_case": supported, "insufficient_coverage": gaps, "frozen_run": frozen,
                         "scoring_sha256": prior.sha(OUTPUT / "scoring.json"), "raw_results_sha256": prior.sha(OUTPUT / "retrieved-all.json")})
        summaries[mode] = aggregate
    prior.write_json(OUTPUT / "aggregate.json", summaries)
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["run", "summarize"])
    args = parser.parse_args()
    run() if args.command == "run" else summarize()
