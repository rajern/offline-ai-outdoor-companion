"""Offline, isolated chunking comparison; never writes production assets.

Run from backend with .venv/Scripts/python.exe ../evals/compare_token_chunking.py.
Uses the frozen corpus, locked embedder, production scoring/filtering and 15
existing questions. Outputs include exact child/parent spans and full rankings.
No generation, source refresh, model download or production change.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, replace
from datetime import datetime, timezone
from importlib.metadata import version
import json
from pathlib import Path
import re
import shutil
import socket
import sys

import numpy as np
from tokenizers import Tokenizer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from outwise.knowledge.ingestion import digest, write_json
from outwise.services.semantic_retrieval import SemanticRetrievalService, allowed_in_jurisdiction


def no_network(*args, **kwargs):
    raise AssertionError("Network is forbidden during this experiment")


def context_view(item, text=None):
    return f"{item.title}. {item.section or ''}. {item.text if text is None else text}"


def split_item(item, tokenizer, limit):
    """Lossless, nonoverlapping substrings. Prefer paragraph then sentence ends.

    Both production embedding views must fit INCLUDING special tokens and the
    unchanged title/section prefix. Existing chunk boundaries remain intact.
    Token offsets are used only when an entire sentence exceeds the budget.
    """
    text = item.text
    paragraphs = {m.end() for m in re.finditer(r"\n+", text)} | {len(text)}
    sentences = {m.end() for m in re.finditer(r"[.!?](?:\s+|$)", text)}
    offsets = {end for _, end in tokenizer.encode(text, add_special_tokens=False).offsets}
    candidates = sorted(paragraphs | sentences | offsets)
    if len(tokenizer.encode(context_view(item, "")).ids) >= limit:
        raise ValueError(f"Metadata alone exhausts token budget: {item.id}")

    def fits(start, end):
        piece = text[start:end]
        return (len(tokenizer.encode(piece).ids) <= limit
                and len(tokenizer.encode(context_view(item, piece)).ids) <= limit)

    result, spans = [], []
    start = 0
    while start < len(text):
        # Check every candidate, rather than assume token count is monotone
        # under substring retokenization. Corpus is small and frozen.
        valid = [end for end in candidates if end > start and fits(start, end)]
        if not valid:
            raise ValueError(f"Cannot fit any source text: {item.id}:{start}")
        preferred = [end for end in valid if end in paragraphs]
        if not preferred:
            preferred = [end for end in valid if end in sentences]
        end = max(preferred or valid)
        number = len(result) + 1
        child = replace(item, id=f"{item.id}~t{number:02d}", text=text[start:end])
        result.append(child)
        spans.append({"id": child.id, "parent_id": item.id, "start": start, "end": end,
                      "text_tokens": len(tokenizer.encode(child.text).ids),
                      "context_tokens": len(tokenizer.encode(context_view(child)).ids)})
        start = end
    assert "".join(child.text for child in result) == text
    assert all(s["text_tokens"] <= limit and s["context_tokens"] <= limit for s in spans)
    return result, spans


def covered_fraction(text, intervals):
    meaningful = {i for i, char in enumerate(text) if not char.isspace()}
    covered = {i for start, end in intervals for i in range(start, end)}
    return len(meaningful & covered) / len(meaningful) if meaningful else 1.0


def measure(case, top, mapping, parents):
    selected = {mapping[row["item"]["id"]]["parent_id"] for row in top}
    intervals = {parent: [] for parent in case["gold_ids"]}
    for row in top:
        span = mapping[row["item"]["id"]]
        if span["parent_id"] in intervals:
            intervals[span["parent_id"]].append((span["start"], span["end"]))
    fractions = {parent: covered_fraction(parents[parent].text, spans)
                 for parent, spans in intervals.items()}
    return {"any_gold_parent": bool(selected & set(case["gold_ids"])),
            "all_gold_parents_hit": bool(case["gold_ids"]) and set(case["gold_ids"]) <= selected,
            "all_gold_text_present": bool(fractions) and all(v == 1 for v in fractions.values()),
            "gold_parent_text_fraction": fractions}


def evaluate(service, cases, mapping, parents, query_vectors):
    rows = []
    for case, query in zip(cases, query_vectors, strict=True):
        scores = service._vectors @ query
        ranked = sorted(zip(service._items, scores, strict=True), key=lambda pair: (-float(pair[1]), pair[0].id))
        all_ranking = []
        eligible_rank = 0
        for rank, (item, score) in enumerate(ranked, 1):
            allowed = allowed_in_jurisdiction(item, "NO")
            eligible_rank += int(allowed)
            all_ranking.append({**mapping[item.id], "score": float(score), "rank_unfiltered": rank,
                                "eligible_rank": eligible_rank if allowed else None,
                                "allowed_in_NO": allowed, "above_threshold": bool(score >= .35),
                                "document_id": item.document_id, "section": item.section,
                                "source_name": item.source_name, "source_url": item.source_url})
        eligible = [(item, float(score)) for item, score in ranked
                    if score >= .35 and allowed_in_jurisdiction(item, "NO")]
        top5 = [{"rank": rank, "score": score, "span": mapping[item.id], "item": asdict(item)}
                for rank, (item, score) in enumerate(eligible[:5], 1)]
        # Cross-check independently against the unchanged production service.
        actual = service.retrieve(case["question"], top_k=5)
        assert [r.item.id for r in actual] == [r["item"]["id"] for r in top5]
        gold_ranking = [r for r in all_ranking if r["parent_id"] in case["gold_ids"]]
        row = {**case, "top5": top5, "gold_ranking": gold_ranking, "all_ranking": all_ranking,
               "at3": measure(case, top5[:3], mapping, parents),
               "at5": measure(case, top5, mapping, parents)}
        rows.append(row)
        print(case["id"], [(r["item"]["id"], round(r["score"], 4)) for r in top5], flush=True)
    return rows


def summarize(rows):
    actionable = [row for row in rows if row["coverage"] != "gap"]
    return {"actionable_cases": len(actionable), **{
        k: {metric: sum(row[k][metric] for row in actionable)
            for metric in ["any_gold_parent", "all_gold_parents_hit", "all_gold_text_present"]}
        for k in ["at3", "at5"]}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "knowledge/local/diagnostics/token-chunking-2026-10-07")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    socket.socket.connect = no_network
    socket.create_connection = no_network
    args.output = args.output.resolve()
    permitted = (ROOT / "knowledge/local/diagnostics").resolve()
    if not args.output.is_relative_to(permitted) or args.output.exists():
        raise ValueError("Output must be a NEW directory under ignored knowledge/local/diagnostics")
    previous = ROOT / "knowledge/local/diagnostics/m2-06-2026-10-07"
    protected = json.loads((previous / "protected-baseline.json").read_text(encoding="utf-8"))
    def fingerprints():
        return {name: digest((ROOT / name).read_bytes()) for name in protected}
    before = fingerprints()
    assert before == protected, "Protected inputs changed since earlier diagnosis"
    config = ROOT / "evals/m2-06-diagnostic-cases.json"
    cases = json.loads(config.read_text(encoding="utf-8"))["cases"]
    baseline = SemanticRetrievalService.from_json(ROOT / "knowledge/local/knowledge.json")
    tokenizer = Tokenizer.from_file(str(ROOT / "knowledge/local/embedding-model/tokenizer.json"))
    tokenizer.no_padding()
    tokenizer.no_truncation()
    truncation = baseline._embedder._model.model.tokenizer.truncation
    limit = truncation["max_length"]
    assert limit == 128
    parents = {item.id: item for item in baseline._items}
    children, spans = [], []
    for item in baseline._items:
        new_items, new_spans = split_item(item, tokenizer, limit)
        children.extend(new_items)
        spans.extend(new_spans)
    args.output.mkdir(parents=True)
    write_json(args.output / "protected-baseline.json", before)
    write_json(args.output / "candidate-knowledge.json", {"schema_version": 1, "items": [asdict(i) for i in children]})
    write_json(args.output / "child-parent-spans.json", spans)
    for name in ["knowledge.json", "index.json", "embeddings.npy", "build.json", "snapshots.json"]:
        shutil.copyfile(ROOT / "knowledge/local" / name, args.output / f"baseline-{name}")
    shutil.copyfile(config, args.output / config.name)
    shutil.copyfile(Path(__file__), args.output / Path(__file__).name)
    shutil.copyfile(ROOT / "knowledge/manifests/approved-sources.json", args.output / "approved-sources.json")
    shutil.copyfile(ROOT / "knowledge/local/embedding-model/outwise-model.json", args.output / "embedding-model-lock.json")
    for name in ["backend/outwise/knowledge/embeddings.py", "backend/outwise/services/semantic_retrieval.py"]:
        destination = args.output / "code-snapshot" / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, destination)
    write_json(args.output / "parameters.json", {
        "utc_started": datetime.now(timezone.utc).isoformat(), "python": sys.version,
        "packages": {p: version(p) for p in ["fastembed", "onnxruntime", "numpy", "tokenizers"]},
        "model_lock": baseline._embedder.lock, "runtime_truncation": truncation,
        "chunking": "split existing parent only; nonoverlap; prefer paragraph then sentence ends; exact substrings",
        "unchanged": ["corpus content and metadata", "title/section embedding prefix", "two-view normalized mean",
                      "embedding model/tokenizer/runtime", "NO geography filter", ".35 threshold", "top_k 3 and 5", "questions"],
        "baseline_items": len(parents), "candidate_items": len(children),
        "candidate_max_context_tokens": max(s["context_tokens"] for s in spans),
        "candidate_max_text_tokens": max(s["text_tokens"] for s in spans),
        "baseline_truncated_context_views": sum(len(tokenizer.encode(context_view(i)).ids) > limit for i in parents.values()),
        "baseline_truncated_text_views": sum(len(tokenizer.encode(i.text).ids) > limit for i in parents.values()),
        "network": "Python connections denied; local_files_only; no OS-wide network isolation",
        "metric_caveat": "Parent hit does NOT mean all instructions retrieved. Text presence is strict coverage of selected original gold text, not answer sufficiency or clinical gold."})
    print(f"Embedding {len(children)} token-aligned children from {len(parents)} frozen parents", flush=True)
    embedder = baseline._embedder
    context_vectors = embedder.embed([context_view(i) for i in children])
    text_vectors = embedder.embed([i.text for i in children])
    vectors = (context_vectors + text_vectors) / 2
    vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)
    np.save(args.output / "candidate-embeddings.npy", vectors, allow_pickle=False)
    candidate = SemanticRetrievalService(children, vectors, embedder)
    query_vectors = embedder.embed([case["question"] for case in cases])
    np.save(args.output / "query-embeddings.npy", query_vectors, allow_pickle=False)
    original_map = {i.id: {"id": i.id, "parent_id": i.id, "start": 0, "end": len(i.text)} for i in parents.values()}
    baseline_rows = evaluate(baseline, cases, original_map, parents, query_vectors)
    original = json.loads((previous / "retrieval.json").read_text(encoding="utf-8"))["cases"]
    for current, old in zip(baseline_rows, original, strict=True):
        assert current["id"] == old["id"]
        assert [r["item"]["id"] for r in current["top5"]] == [r["item"]["id"] for r in old["top5"]]
        assert np.allclose([r["score"] for r in current["top5"]], [r["score"] for r in old["top5"]], atol=1e-6, rtol=0)
    candidate_rows = evaluate(candidate, cases, {s["id"]: s for s in spans}, parents, query_vectors)
    write_json(args.output / "retrieval-comparison.json", {"baseline": baseline_rows, "token_aligned": candidate_rows,
               "summary": {"baseline": summarize(baseline_rows), "token_aligned": summarize(candidate_rows)}})
    after = fingerprints()
    write_json(args.output / "integrity.json", {"protected_files_unchanged": before == after,
               "baseline_matches_previous_diagnosis": True, "hashes": after})
    assert after == before, "Protected inputs changed during diagnostic"
    print(json.dumps({"baseline": summarize(baseline_rows), "token_aligned": summarize(candidate_rows)}, indent=2), flush=True)


if __name__ == "__main__":
    main()
