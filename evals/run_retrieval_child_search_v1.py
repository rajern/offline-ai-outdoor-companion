"""One frozen C8 child-search experiment against saved B8; no production writes.

run creates one isolated index and 15 contexts. summarize consumes manual
scoring without retrieval. Queries, full parent context and packer stay unchanged.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
from importlib.metadata import version
import json
from pathlib import Path
import re
import shutil
import socket
import statistics
import sys

import numpy as np
from tokenizers import Tokenizer
import yaml

import run_retrieval_eval_v1 as prior
from outwise.knowledge.embeddings import LocalEmbedder

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "knowledge/local/diagnostics/retrieval-topk-ablation-v1-2026-10-07"
ORIGINAL = ROOT / "knowledge/local/diagnostics/retrieval-eval-v1-2026-10-07"
LANDSCAPE = ROOT / "knowledge/local/diagnostics/retrieval-failure-landscape-v1-2026-10-07"
OUTPUT = ROOT / "knowledge/local/diagnostics/retrieval-child-search-v1-2026-10-07"
PROTOCOL = ROOT / "evals/retrieval_child_search.v1.json"


def view(parent, text):
    return f"{parent.title}. {parent.section or ''}. {text}"


def split(parent, tokenizer, limit=128, overlap=16):
    """Exact character spans; both original embedding views must fit completely."""
    text = parent.text
    def fits(start, end):
        return max(len(tokenizer.encode(text[start:end]).ids),
                   len(tokenizer.encode(view(parent, text[start:end])).ids)) <= limit
    if fits(0, len(text)):
        return [(0, len(text), 0)]
    assert len(tokenizer.encode(view(parent, "")).ids) < limit, parent.id
    natural = {m.end() for m in re.finditer(r"\n+|[.!?](?:\s+|$)", text)} | {len(text)}
    words = {m.end() for m in re.finditer(r"\S+\s*", text)} | {len(text)}
    offsets = {e for _, e in tokenizer.encode(text, add_special_tokens=False).offsets}
    result = []
    start = 0
    previous_end = 0
    while start < len(text):
        valid = [e for e in sorted(natural | words | offsets) if e > start and fits(start, e)]
        assert valid, (parent.id, start)
        natural_fit = [e for e in valid if e in natural and e > previous_end]
        word_fit = [e for e in valid if e in words and e > previous_end]
        end = max(natural_fit or word_fit or valid)
        if end <= previous_end:
            # Fixed forward-progress rule, not parameter tuning.
            start = previous_end
            continue
        overlap_tokens = len(tokenizer.encode(text[start:previous_end], add_special_tokens=False).ids) if result else 0
        assert overlap_tokens <= overlap
        result.append((start, end, overlap_tokens))
        if end == len(text):
            break
        next_starts = [m.start() for m in re.finditer(r"\S+", text) if start < m.start() < end
                       and len(tokenizer.encode(text[m.start():end], add_special_tokens=False).ids) <= overlap]
        start = min(next_starts) if next_starts else end
        previous_end = end
    covered = set()
    for s, e, _ in result:
        assert fits(s, e)
        covered.update(range(s, e))
    assert covered == set(range(len(text))), parent.id
    return result


class Counter(prior.Counter):
    def count(self, text):
        key = prior.hashlib.sha256(text.encode()).hexdigest()
        for directory in [BASE, ORIGINAL]:
            saved = directory / "tokenization" / key
            if key not in self.cache and saved.exists():
                assert (saved / "input.txt").read_text(encoding="utf-8") == text
                ids = json.loads((saved / "stdout.txt").read_text(encoding="utf-8"))
                assert all(isinstance(i, int) for i in ids)
                shutil.copytree(saved, OUTPUT / "tokenization" / key)
                self.cache[key] = len(ids)
        return super().count(text)


def rank_targets():
    """Evidence locations fixed before C8 results; not an exhaustive gold whitelist."""
    from diagnose_retrieval_failures_v1 import mapping
    originals = mapping()
    scores = json.loads((BASE / "scoring.json").read_text(encoding="utf-8"))["B8"]
    targets = {}
    for cid, annotation in scores.items():
        targets[cid] = []
        for n, item in enumerate(annotation["items"], 1):
            old = next((p for p in originals.get(cid, []) if p["gold_item_index"] == n), None)
            if old:
                targets[cid].append(old)
            elif item["covered"]:
                by_parent = {}
                for ev in item["evidence"]:
                    by_parent.setdefault(ev["id"], []).append(ev["quote"])
                targets[cid].append({"gold_item_index": n, "sufficient_sets": [[{"id": id, "quotes": q} for id, q in by_parent.items()]]})
    return targets


def rankings(cid, candidates, targets, children, parents, old_b8):
    baseline_path = LANDSCAPE / cid / "all-candidates.json"
    baseline = {r["id"]: r for r in json.loads(baseline_path.read_text(encoding="utf-8"))} if baseline_path.exists() else {}
    for n, seed in enumerate(old_b8["seeds"], 1):
        baseline.setdefault(seed["item"]["id"], {"jurisdiction_rank": n, "cosine": seed["score"]})
    by_parent = {}
    for row in candidates:
        if row["jurisdiction_rank"] is not None:
            by_parent.setdefault(row["parent_id"], []).append(row)
    audit = []
    for target in targets[cid]:
        sets = []
        for parts in target["sufficient_sets"]:
            entries = []
            for part in parts:
                pid = part["id"]
                original = parents[pid]
                choices = by_parent.get(pid, [])
                quote_rows = []
                for quote in part["quotes"]:
                    assert quote in original.text
                    start = original.text.index(quote)
                    end = start + len(quote)
                    containing = [r for r in choices if r["start_char"] <= start and r["end_char"] >= end]
                    fragments = [r for r in choices if r["start_char"] < end and r["end_char"] > start]
                    quote_rows.append({"quote": quote, "start_char": start, "end_char": end,
                                       "best_full_quote_child": containing[0] if containing else None,
                                       "fragment_children": fragments,
                                       "all_fragments_untruncated": all(children[r["child_id"]]["truncated_inputs"] == 0 for r in fragments)})
                entries.append({"parent_id": pid, "title": original.title, "section": original.section,
                                "source_url": original.source_url, "baseline": baseline.get(pid),
                                "best_parent_child": choices[0] if choices else None, "quotes": quote_rows})
            sets.append(entries)
        audit.append({"gold_item_index": target["gold_item_index"], "sufficient_sets": sets})
    return audit


def run():
    if OUTPUT.exists():
        raise RuntimeError(f"Refusing to overwrite existing run: {OUTPUT}")
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    old = json.loads((BASE / "frozen-run.json").read_text(encoding="utf-8"))
    before = prior.protected_hashes()
    assert before == old["protected_before"]
    assert prior.sha(prior.GOLD) == protocol["gold_sha256"]
    assert prior.sha(prior.CORPUS) == protocol["corpus_sha256"]
    assert prior.sha(Path(prior.__file__)) == protocol["packing_script_sha256"]
    def deny_network(*args, **kwargs):
        raise RuntimeError("Frozen offline child-search experiment: network disabled")
    socket.socket.connect = deny_network
    socket.create_connection = deny_network
    parents_list = prior.load_knowledge_items(prior.CORPUS)
    parents = {p.id: p for p in parents_list}
    targets = rank_targets()
    gold = yaml.safe_load(prior.GOLD.read_text(encoding="utf-8"))
    baseline_raw = json.loads((BASE / "retrieved-all.json").read_text(encoding="utf-8"))
    baseline_rows = [r for r in baseline_raw if r["configuration"] == "B8"]
    assert len(baseline_rows) == len(gold["cases"]) == 15
    OUTPUT.mkdir()
    frozen = {"experiment": protocol, "experiment_sha256": prior.sha(PROTOCOL),
              "runner_sha256": prior.sha(Path(__file__)), "created_at": datetime.now(timezone.utc).isoformat(),
              "protected_before": before, "gold_version": gold["set_version"], "gold_hash": prior.sha(prior.GOLD),
              "corpus_hash": prior.sha(prior.CORPUS), "baseline_raw_hash": prior.sha(BASE / "retrieved-all.json"),
              "baseline_scoring_hash": prior.sha(BASE / "scoring.json"), "baseline_retrieval_calls": 0,
              "generation_calls": 0, "query_embedding_calls": 0,
              "runtime": {"python": sys.version, "executable": sys.executable,
                          "packages": {n: version(n) for n in ["numpy", "fastembed", "tokenizers", "onnxruntime", "PyYAML"]}}}
    prior.write_json(OUTPUT / "frozen-run.json", frozen)
    prior.write_json(OUTPUT / "ranking-evidence-targets.json", targets)
    for source in [PROTOCOL, prior.GOLD, prior.PROTOCOL, Path(__file__), Path(prior.__file__)]:
        shutil.copyfile(source, OUTPUT / source.name)
    for name in ["knowledge.json", "index.json", "embeddings.npy"]:
        shutil.copyfile(ROOT / "knowledge/local" / name, OUTPUT / f"original-{name}")
    shutil.copyfile(ROOT / "knowledge/manifests/approved-sources.json", OUTPUT / "source-manifest.json")
    shutil.copytree(BASE / "B8", OUTPUT / "B8")
    prior.write_json(OUTPUT / "baseline-B8-raw.json", baseline_rows)
    embedder = LocalEmbedder(ROOT / "knowledge/local/embedding-model")
    actual_tokenizer = embedder._model.model.tokenizer
    tokenizer = Tokenizer.from_str(actual_tokenizer.to_str())
    tokenizer.no_padding()
    tokenizer.no_truncation()
    assert actual_tokenizer.truncation["max_length"] == 128
    prior.write_json(OUTPUT / "embedding-tokenizer-config.json", {"truncation": actual_tokenizer.truncation,
                     "padding": actual_tokenizer.padding, "model_lock": embedder.lock,
                     "embedding_views": ["text", "title + '. ' + section + '. ' + text"]})
    original_vectors = np.load(ROOT / "knowledge/local/embeddings.npy", allow_pickle=False)
    children = []
    baseline_lengths = []
    for index, parent in enumerate(parents_list):
        baseline_lengths.append({"parent_id": parent.id, "text_tokens": len(tokenizer.encode(parent.text).ids),
                                 "metadata_text_tokens": len(tokenizer.encode(view(parent, parent.text)).ids)})
        spans = split(parent, tokenizer, 128, 16)
        for n, (start, end, overlap) in enumerate(spans, 1):
            body = parent.text[start:end]
            inputs = {}
            for label, text in [("text", body), ("metadata_text", view(parent, body))]:
                full = tokenizer.encode(text)
                actual = actual_tokenizer.encode(text)
                actual_ids = [id for id, mask in zip(actual.ids, actual.attention_mask) if mask]
                assert len(full.ids) <= 128 and full.ids == actual_ids, (parent.id, start, label)
                inputs[label] = {"input": text, "token_ids": full.ids, "token_count": len(full.ids), "truncated": False}
            children.append({"child_id": f"{parent.id}~c{n:03d}", "parent_id": parent.id,
                             "parent_index": index, "document_id": parent.document_id,
                             "section": parent.section, "source_url": parent.source_url,
                             "source_name": parent.source_name, "metadata": parent.metadata,
                             "title": parent.title, "text": body, "start_char": start, "end_char": end,
                             "overlap_body_tokens": overlap, "inputs": inputs, "truncated_inputs": 0,
                             "reuse_original_vector": len(spans) == 1 and start == 0 and end == len(parent.text)})
    prior.write_json(OUTPUT / "children.json", children)
    prior.write_json(OUTPUT / "original-input-lengths.json", baseline_lengths)
    def stats(values):
        return {"min": min(values), "median": statistics.median(values), "mean": statistics.mean(values), "max": max(values)}
    input_stats = {"child_count": len(children), "parent_count": len(parents_list),
                   "split_parent_count": len({c["parent_id"] for c in children if not c["reuse_original_vector"]}),
                   "reused_original_vectors": sum(c["reuse_original_vector"] for c in children),
                   "body_input_tokens": stats([c["inputs"]["text"]["token_count"] for c in children]),
                   "metadata_body_input_tokens": stats([c["inputs"]["metadata_text"]["token_count"] for c in children]),
                   "all_input_tokens": stats([v["token_count"] for c in children for v in c["inputs"].values()]),
                   "overlap_tokens": stats([c["overlap_body_tokens"] for c in children]),
                   "truncated_input_count": 0,
                   "baseline_truncated_body_inputs": sum(r["text_tokens"] > 128 for r in baseline_lengths),
                   "baseline_truncated_metadata_body_inputs": sum(r["metadata_text_tokens"] > 128 for r in baseline_lengths)}
    prior.write_json(OUTPUT / "chunk-statistics.json", input_stats)
    print(f"Frozen chunking: {len(children)} children; {input_stats['split_parent_count']} split parents; zero truncated inputs", flush=True)
    vectors = np.zeros((len(children), original_vectors.shape[1]), dtype=np.float32)
    changed = [n for n, c in enumerate(children) if not c["reuse_original_vector"]]
    for n, child in enumerate(children):
        if child["reuse_original_vector"]:
            vectors[n] = original_vectors[child["parent_index"]]
    # Exactly the unchanged two-view production embedding/normalisation formula.
    contextual = embedder.embed([children[n]["inputs"]["metadata_text"]["input"] for n in changed])
    body = embedder.embed([children[n]["inputs"]["text"]["input"] for n in changed])
    merged = (contextual + body) / 2
    merged /= np.linalg.norm(merged, axis=1, keepdims=True)
    vectors[changed] = merged
    np.save(OUTPUT / "child-metadata-vectors.npy", contextual, allow_pickle=False)
    np.save(OUTPUT / "child-body-vectors.npy", body, allow_pickle=False)
    np.save(OUTPUT / "child-embeddings.npy", vectors, allow_pickle=False)
    prior.write_json(OUTPUT / "child-index.json", {"child_ids": [c["child_id"] for c in children],
                     "embedding_format": "text-context-mean-v1", "dimensions": int(vectors.shape[1]),
                     "model_lock": embedder.lock, "vectors_sha256": prior.sha(OUTPUT / "child-embeddings.npy"),
                     "inputs_sha256": prior.sha(OUTPUT / "children.json"), "new_embedding_input_count": 2*len(changed)})
    vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
    prior.OUTPUT = OUTPUT
    counter = Counter()
    by_child = {c["child_id"]: c for c in children}
    records = []
    for case in gold["cases"]:
        cid, question = case["id"], case["question"]
        qpath = ORIGINAL / f"{cid}-query-vector.npy"
        q = np.load(qpath, allow_pickle=False)[0]
        shutil.copyfile(qpath, OUTPUT / qpath.name)
        scores = vectors @ q
        order = sorted(range(len(children)), key=lambda n: (-float(scores[n]), children[n]["child_id"]))
        eligible = [n for n in order if prior.allowed_in_jurisdiction(parents[children[n]["parent_id"]], "NO")]
        ranks = {n: r for r, n in enumerate(eligible, 1)}
        unique_rank = {}
        for n in eligible:
            unique_rank.setdefault(children[n]["parent_id"], len(unique_rank) + 1)
        selected = [n for n in eligible if scores[n] >= .35][:8]
        candidates = [{"child_id": children[n]["child_id"], "parent_id": children[n]["parent_id"],
                       "start_char": children[n]["start_char"], "end_char": children[n]["end_char"],
                       "score": float(scores[n]), "global_rank": r,
                       "jurisdiction_rank": ranks.get(n), "projected_unique_parent_rank": unique_rank.get(children[n]["parent_id"]),
                       "above_threshold": bool(scores[n] >= .35), "selected": n in selected,
                       "body_tokens": children[n]["inputs"]["text"]["token_count"],
                       "metadata_body_tokens": children[n]["inputs"]["metadata_text"]["token_count"]}
                      for r, n in enumerate(order, 1)]
        seeds = [prior.RetrievedKnowledgeItem(parents[children[n]["parent_id"]], float(scores[n])) for n in selected]
        results, packets, trace = prior.packed_b(question, seeds, parents_list, counter, 2000)
        for t in trace:
            t["child_id"] = children[selected[t["seed_rank"] - 1]]["child_id"]
        context = prior.context_for(results)
        prompt = prior._build_grounded_prompt(question, results)
        pt, pk = counter.count(prompt)
        ct, ck = counter.count(context)
        assert pt <= 2000
        directory = OUTPUT / "C8" / cid
        directory.mkdir(parents=True)
        row = {"configuration": "C8", "case_id": cid, "question": question,
               "expected_result": case["expected_result"], "gold_hash": frozen["gold_hash"],
               "corpus_hash": frozen["corpus_hash"], "experiment_sha256": frozen["experiment_sha256"],
               "context_budget": 2000, "semantic_seed_top_k": 8,
               "query_vector_sha256": prior.sha(qpath), "seeds": [asdict(s) for s in seeds],
               "child_seeds": [{"child": children[n], "score": float(scores[n]), "rank": ranks[n]} for n in selected],
               "unique_seed_parents": len({s.item.id for s in seeds}),
               "excerpts": [asdict(r) for r in results], "packets": packets, "trace": trace,
               "chunk_count": len(results), "section_count": len({(r.item.document_id, r.item.section) for r in results}),
               "packet_count": len(packets), "context_tokens": ct, "prompt_tokens": pt,
               "prompt_tokenization_key": pk, "context_tokenization_key": ck,
               "budget_excluded_packets": sum(t["status"] == "over_budget" for t in trace),
               "duplicate_packets": sum(t["status"] == "duplicate_branch" for t in trace),
               "context_sha256": prior.hashlib.sha256(context.encode()).hexdigest()}
        (directory / "context.txt").write_text(context, encoding="utf-8")
        (directory / "prompt-not-executed.txt").write_text(prompt, encoding="utf-8")
        prior.write_json(directory / "retrieved.json", row)
        prior.write_json(directory / "all-candidates.json", candidates)
        old_b8 = next(r for r in baseline_rows if r["case_id"] == cid)
        prior.write_json(directory / "gold-ranking-audit.json", rankings(cid, candidates, targets, by_child, parents, old_b8))
        records.append(row)
        print(f"{cid}: {len(selected)} child hits / {row['unique_seed_parents']} parents; {len(results)} excerpts; {ct} context / {pt} prompt tokens; {row['budget_excluded_packets']} budget skips", flush=True)
    prior.write_json(OUTPUT / "retrieved-all.json", baseline_rows + records)
    after = prior.protected_hashes()
    prior.write_json(OUTPUT / "integrity-after.json", {"protected_unchanged": before == after, "protected_after": after,
                     "baseline_raw_unchanged": frozen["baseline_raw_hash"] == prior.sha(BASE / "retrieved-all.json"),
                     "baseline_scoring_unchanged": frozen["baseline_scoring_hash"] == prior.sha(BASE / "scoring.json"),
                     "experiment_unchanged": frozen["experiment_sha256"] == prior.sha(PROTOCOL),
                     "runner_unchanged": frozen["runner_sha256"] == prior.sha(Path(__file__))})
    assert before == after


def summarize():
    frozen = json.loads((OUTPUT / "frozen-run.json").read_text(encoding="utf-8"))
    gold = yaml.safe_load((OUTPUT / prior.GOLD.name).read_text(encoding="utf-8"))
    assert prior.sha(prior.GOLD) == frozen["gold_hash"]
    scores = json.loads((OUTPUT / "scoring.json").read_text(encoding="utf-8"))
    baseline_scores = json.loads((BASE / "scoring.json").read_text(encoding="utf-8"))["B8"]
    assert scores["B8"] == baseline_scores
    rows = json.loads((OUTPUT / "retrieved-all.json").read_text(encoding="utf-8"))
    summary = {}
    for mode in ["B8", "C8"]:
        supported, gaps = [], []
        for case in gold["cases"]:
            cid = case["id"]
            row = next(r for r in rows if r["configuration"] == mode and r["case_id"] == cid)
            annotation = scores[mode][cid]
            assert len(annotation["items"]) == len(case["must_have_information"])
            text = {e["item"]["id"]: e["item"]["text"] for e in row["excerpts"]}
            for item in annotation["items"]:
                assert isinstance(item["covered"], bool) and item["reason"]
                assert not item["covered"] or item["evidence"]
                for ev in item["evidence"]:
                    assert ev["quote"] in text[ev["id"]], (mode, cid, ev)
            for label in ["irrelevant", "potentially_misleading", "jurisdiction_leakage"]:
                for ev in annotation[label]:
                    assert ev["quote"] in text[ev["id"]], (mode, cid, ev)
            found = sum(i["covered"] for i in annotation["items"])
            total = len(annotation["items"])
            gap = case["expected_result"] == "insufficient_coverage"
            result = {"case_id": cid, "title": case["title"], "expected_result": case["expected_result"],
                      "found": found, "total": total, "coverage": found/total if total else None,
                      "complete_pass": not gap and found == total, "scoring": annotation,
                      **{key: row[key] for key in ["context_tokens", "prompt_tokens", "chunk_count", "section_count", "packet_count", "budget_excluded_packets"]},
                      "raw_path": f"{mode}/{cid}/retrieved.json"}
            (gaps if gap else supported).append(result)
        aggregate = {"covered_cases": len(supported), "must_have_found": sum(r["found"] for r in supported),
                     "must_have_total": sum(r["total"] for r in supported),
                     "must_have_micro_coverage": sum(r["found"] for r in supported)/sum(r["total"] for r in supported),
                     "average_per_case_macro_coverage": statistics.mean(r["coverage"] for r in supported),
                     "complete_passes": sum(r["complete_pass"] for r in supported)}
        for label in ["irrelevant", "potentially_misleading", "jurisdiction_leakage"]:
            aggregate[label + "_cases"] = sum(bool(r["scoring"][label]) for r in supported)
        aggregate["either_noise_cases"] = sum(bool(r["scoring"]["irrelevant"] or r["scoring"]["potentially_misleading"]) for r in supported)
        for key in ["context_tokens", "prompt_tokens", "chunk_count", "section_count", "packet_count"]:
            values = [r[key] for r in supported]
            aggregate[key] = {"min": min(values), "median": statistics.median(values), "mean": statistics.mean(values), "max": max(values)}
        aggregate["budget_excluded_packets"] = sum(r["budget_excluded_packets"] for r in supported)
        aggregate["budget_affected_cases"] = sum(r["budget_excluded_packets"] > 0 for r in supported)
        prior.write_json(OUTPUT / mode / "results.json", {"configuration": mode, "aggregate": aggregate,
                         "per_case": supported, "insufficient_coverage": gaps, "frozen_run": frozen,
                         "scoring_sha256": prior.sha(OUTPUT / "scoring.json"),
                         "raw_results_sha256": prior.sha(OUTPUT / "retrieved-all.json")})
        summary[mode] = aggregate
    prior.write_json(OUTPUT / "aggregate.json", summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["run", "summarize"])
    args = parser.parse_args()
    run() if args.command == "run" else summarize()
