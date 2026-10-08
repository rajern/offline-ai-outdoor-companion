"""Diagnostic-only 2x2 comparison: semantic/hybrid and broad/narrow context.

Fixed BM25+RRF, no medical rules, query translations, model change or generation.
23 questions; 15 existing and 8 fresh probes. Same corpus, vectors and geography.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys

import numpy as np

from compare_parent_context import INPUT, ROOT, TokenCounter, fact_coverage, pack, prompt_for
from outwise.knowledge.embeddings import LocalEmbedder
from outwise.knowledge.ingestion import digest, write_json
from outwise.knowledge.loader import load_knowledge_items
from outwise.services.semantic_retrieval import allowed_in_jurisdiction


STOPWORDS = set("""a an the and or but if is are was were be been being do does did
to of in on at for from with as by it its this that these those i me my we us our
you your he she they them their can could should would will how what which who
where when why please have has had not
og eller men hvis er var være blir blitt å i på til av fra med som det den de
en et jeg meg min mitt vi oss vår du deg din ditt dere sin sitt sine kan kunne
skal skulle bør vil ville har hadde hva hvem hvor når hvordan hvorfor ikke
dette denne disse noe noen etter før så om enn må også hva gjør gjøre""".split())


def terms(text):
    return [word for word in re.findall(r"[^\W\d_]+", text.casefold(), flags=re.UNICODE)
            if len(word) > 1 and word not in STOPWORDS]


class BM25:
    def __init__(self, parents):
        self.documents = {item.id: Counter(terms(f"{item.title} {item.title} {item.section or ''} {item.section or ''} {item.text}"))
                          for item in parents.values() if allowed_in_jurisdiction(item, "NO")}
        self.lengths = {id: sum(words.values()) for id, words in self.documents.items()}
        self.average_length = sum(self.lengths.values()) / len(self.lengths)
        df = Counter(word for words in self.documents.values() for word in words)
        self.idf = {word: math.log(1 + (len(self.documents) - frequency + .5) / (frequency + .5)) for word, frequency in df.items()}

    def score(self, question):
        query = set(terms(question))
        return {id: sum(self.idf.get(word, 0) * count * 2.2 /
                       (count + 1.2 * (.25 + .75 * self.lengths[id] / self.average_length))
                       for word in query if (count := document.get(word, 0)))
                for id, document in self.documents.items()}


def rank_parents(parents, children, spans, cosine_scores, lexical_scores):
    best = {}
    for child, cosine in zip(children, cosine_scores, strict=True):
        if not allowed_in_jurisdiction(child, "NO"):
            continue
        id = spans[child.id]["parent_id"]
        candidate = (float(cosine), child.id)
        if id not in best or candidate[0] > best[id][0] or (candidate[0] == best[id][0] and child.id < best[id][1]):
            best[id] = candidate
    ordered = sorted(best, key=lambda id: (-best[id][0], id))
    eligible = [id for id in ordered if best[id][0] >= .35]
    semantic_rank = {id: rank for rank, id in enumerate(ordered, 1)}
    lexical_order = sorted([id for id in eligible if lexical_scores.get(id, 0) > 0], key=lambda id: (-lexical_scores[id], id))
    lexical_rank = {id: rank for rank, id in enumerate(lexical_order, 1)}
    fused = {id: 1 / (60 + semantic_rank[id]) + (1 / (60 + lexical_rank[id]) if id in lexical_rank else 0)
             for id in eligible}
    hybrid_order = sorted(eligible, key=lambda id: (-fused[id], -best[id][0], id))
    def seeds(order):
        return [{"rank": rank, "item": parents[id], "parent_id": id, "score": best[id][0],
                 "best_child_id": best[id][1], "semantic_rank": semantic_rank[id],
                 "lexical_score": lexical_scores.get(id, 0), "lexical_rank": lexical_rank.get(id), "rrf_score": fused[id],
                 "span": {"id": id, "parent_id": id, "start": 0, "end": len(parents[id].text)}}
                for rank, id in enumerate(order, 1)]
    all_rows = [{"parent_id": id, "best_child_id": best[id][1], "cosine": best[id][0],
                 "semantic_rank": semantic_rank[id], "above_threshold": best[id][0] >= .35,
                 "lexical_score": lexical_scores.get(id, 0), "lexical_rank": lexical_rank.get(id),
                 "rrf_score": fused.get(id), "section": parents[id].section, "source_url": parents[id].source_url,
                 "document_id": parents[id].document_id} for id in ordered]
    return seeds(eligible), seeds(hybrid_order), all_rows


def path(item):
    return tuple((item.section or item.id).split(" / "))


def narrow_members(seed, parents):
    """Nearest branch, not all descendants of a multi-branch article root.

    Expand a heading with descendants; otherwise its immediate ancestor when
    non-root, or a root with only one direct branch. Keeps exact-heading split
    continuations together. Never uses questions, topics, sources or gold IDs.
    """
    document = seed.document_id or seed.source_url
    eligible = [item for item in parents.values() if (item.document_id or item.source_url) == document
                and allowed_in_jurisdiction(item, "NO")]
    heading = path(seed)
    descendants = [item for item in eligible if len(path(item)) > len(heading) and path(item)[:len(heading)] == heading]
    anchor = heading
    if not descendants and len(heading) > 1:
        ancestor = heading[:-1]
        branches = {path(item)[len(ancestor)] for item in eligible
                    if len(path(item)) > len(ancestor) and path(item)[:len(ancestor)] == ancestor}
        if len(ancestor) > 1 or len(branches) <= 1:
            anchor = ancestor
    branches = {path(item)[len(anchor)] for item in eligible
                if len(path(item)) > len(anchor) and path(item)[:len(anchor)] == anchor}
    exact_only = len(anchor) == 1 and len(branches) > 1
    members = [item for item in eligible if path(item) == anchor or
               (not exact_only and len(path(item)) > len(anchor) and path(item)[:len(anchor)] == anchor)]
    assert seed.id in {item.id for item in members}
    return (document, anchor, exact_only), members


def pack_narrow(question, seeds, k, parents, counter, budget):
    excerpts, packets, trace, seen_groups, seen_ids = [], [], [], set(), set()
    for seed in seeds:
        group, members = narrow_members(seed["item"], parents)
        entry = {key: seed[key] for key in ["rank", "parent_id", "score", "best_child_id", "semantic_rank", "lexical_score", "lexical_rank", "rrf_score"]}
        if group in seen_groups or seed["parent_id"] in seen_ids:
            trace.append({**entry, "status": "duplicate_branch"})
            continue
        seen_groups.add(group)
        added = [{"item": item, "score": seed["score"], "packet_rank": len(packets) + 1, "seed_id": seed["item"].id,
                  "span": {"id": item.id, "parent_id": item.id, "start": 0, "end": len(item.text)}}
                 for item in members if item.id not in seen_ids]
        count, key = counter.count(prompt_for(question, excerpts + added))
        if count > budget:
            trace.append({**entry, "status": "over_budget", "candidate_prompt_tokens": count,
                          "tokenization_key": key, "would_add": [r["item"].id for r in added]})
            continue
        excerpts.extend(added)
        seen_ids.update(row["item"].id for row in added)
        packets.append({**entry, "group": group, "member_ids": [r["item"].id for r in added]})
        trace.append({**entry, "status": "accepted", "tokenization_key": key, "candidate_prompt_tokens": count})
        if len(packets) == k:
            break
    prompt = prompt_for(question, excerpts)
    count, key = counter.count(prompt)
    assert count <= budget
    return {"packets": packets, "excerpts": [{**row, "item": asdict(row["item"])} for row in excerpts], "trace": trace,
            "prompt": prompt, "prompt_tokens": count, "tokenization_key": key, "distinct_parent_count": len(seen_ids)}


class CachedCounter(TokenCounter):
    def __init__(self, executable, model, output, old_directories):
        super().__init__(executable, model, output)
        self.old = {directory.name: directory for root in old_directories for directory in root.iterdir() if directory.is_dir()}
        self.reused = set()

    def count(self, prompt):
        key = digest(prompt.encode("utf-8"))
        if key not in self.cache and key in self.old:
            source = self.old[key]
            assert (source / "prompt.txt").read_text(encoding="utf-8") == prompt
            ids = json.loads((source / "stdout.txt").read_text(encoding="utf-8"))
            self.cache[key] = len(ids)
            self.reused.add(key)
            shutil.copytree(source, self.directory / key)
        return super().count(prompt)


def summarize(rows, cohort):
    selected = [row for row in rows if row["cohort"] == cohort]
    result = {}
    for k in [3, 5]:
        contexts = [row[f"at{k}"] for row in selected]
        scored = [c["instruction_coverage"] for c in contexts if "facts_total" in c["instruction_coverage"]]
        result[f"at{k}"] = {"scored_cases": len(scored), "complete_cases": sum(c["complete"] for c in scored),
                            "facts_present": sum(c["facts_present"] for c in scored), "facts_total": sum(c["facts_total"] for c in scored),
                            "prompt_tokens_mean_all_cases": float(np.mean([c["prompt_tokens"] for c in contexts])),
                            "prompt_tokens_max": max(c["prompt_tokens"] for c in contexts),
                            "known_intrusion_cases": sum(bool(c["known_intrusions"]) for c in contexts),
                            "over_budget_packet_skips": sum(t["status"] == "over_budget" for c in contexts for t in c["trace"])}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "knowledge/local/diagnostics/retrieval-refinement-2026-10-07")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or not output.is_relative_to((ROOT / "knowledge/local/diagnostics").resolve()):
        raise ValueError("Output must be a NEW directory inside ignored knowledge/local/diagnostics")
    sys.stdout.reconfigure(encoding="utf-8")
    def no_network(*args, **kwargs):
        raise AssertionError("Python network forbidden")
    socket.socket.connect = no_network
    socket.create_connection = no_network
    read = lambda p: json.loads(p.read_text(encoding="utf-8"))
    previous_output = ROOT / "knowledge/local/diagnostics/parent-context-2026-10-07"
    protected = read(INPUT / "protected-baseline.json")
    fingerprint = lambda: {name: digest((ROOT / name).read_bytes()) for name in protected}
    assert fingerprint() == protected
    previous_parameters = read(previous_output / "parameters-parent-context.json")
    model = Path(previous_parameters["model_path"])
    with model.open("rb") as stream:
        assert hashlib.file_digest(stream, "sha256").hexdigest() == previous_parameters["model_sha256"]
    config_path = ROOT / "evals/retrieval-refinement-cases.json"
    probes = read(config_path)
    originals = read(INPUT / "retrieval-comparison.json")["baseline"]
    instructions = read(INPUT / "instruction-coverage.json")
    templates = {case["id"]: case for case in originals}
    cases = [{**c, "cohort": "original", "template": c["id"]} for c in originals]
    for probe in probes["cases"]:
        template = templates[probe["template"]]
        case = {**template, **probe, "cohort": "fresh"}
        for key in ["top5", "gold_ranking", "all_ranking"]:
            case.pop(key, None)
        cases.append(case)
    output.mkdir(parents=True)
    for name in ["baseline-knowledge.json", "baseline-embeddings.npy", "candidate-knowledge.json", "candidate-embeddings.npy",
                 "query-embeddings.npy", "child-parent-spans.json", "instruction-coverage.json", "embedding-model-lock.json", "approved-sources.json"]:
        shutil.copyfile(INPUT / name, output / name)
    for script in [Path(__file__), config_path, ROOT / "evals/compare_parent_context.py", ROOT / "evals/test_retrieval_refinement.py"]:
        shutil.copyfile(script, output / script.name)
    write_json(output / "cases-frozen.json", cases)
    write_json(output / "parameters.json", {"utc_started": datetime.now(timezone.utc).isoformat(),
               "models": previous_parameters, "budget_full_prompt_qwen_tokens": 2000, "cosine_gate": .35,
               "bm25": {"k1": 1.2, "b": .75, "title_weight": 2, "section_weight": 2, "text_weight": 1,
                        "tokenization": "Unicode whole words lowercased; fixed NB/EN stopwords; no stemming/translation/aliases", "stopwords": sorted(STOPWORDS)},
               "rrf": {"constant": 60, "weights": [1, 1], "candidate_gate": "Only same-model cosine >= .35, NO-eligible parents; BM25 cannot bypass gate"},
               "parameters_frozen_before_outcomes": True, "probes_config_sha256": digest(config_path.read_bytes()),
               "cohort_note": probes["scope"], "generation_calls": 0,
               "ranking_independence": "Ranking/packing receive no case ID, gold annotation or clinical safety rule"})
    parents = {item.id: item for item in load_knowledge_items(INPUT / "baseline-knowledge.json")}
    children = load_knowledge_items(INPUT / "candidate-knowledge.json")
    spans = {row["id"]: row for row in read(INPUT / "child-parent-spans.json")}
    child_vectors = np.load(INPUT / "candidate-embeddings.npy", allow_pickle=False)
    child_vectors /= np.linalg.norm(child_vectors, axis=1, keepdims=True)
    original_vectors = np.load(INPUT / "baseline-embeddings.npy", allow_pickle=False)
    original_vectors /= np.linalg.norm(original_vectors, axis=1, keepdims=True)
    embedder = LocalEmbedder(ROOT / "knowledge/local/embedding-model")
    fresh_queries = embedder.embed([probe["question"] for probe in probes["cases"]])
    queries = np.concatenate([np.load(INPUT / "query-embeddings.npy", allow_pickle=False), fresh_queries])
    np.save(output / "all-query-embeddings.npy", queries, allow_pickle=False)
    lexical = BM25(parents)
    counter = CachedCounter(Path(previous_parameters["tokenizer_exe"]), model, output,
                            [previous_output / "tokenization", previous_output / "original-ranking-control/tokenization"])
    modes = ["current", "semantic_broad", "semantic_narrow", "hybrid_broad", "hybrid_narrow"]
    results = {mode: [] for mode in modes}
    prior_results = read(previous_output / "results.json")
    for index, case in enumerate(cases):
        semantic, hybrid, ranking = rank_parents(parents, children, spans, child_vectors @ queries[index], lexical.score(case["question"]))
        write_json(output / f"ranking-{case['id']}.json", {"question": case["question"], "parents": ranking,
                   "semantic_order": [s["parent_id"] for s in semantic], "hybrid_order": [s["parent_id"] for s in hybrid]})
        original_scores = original_vectors @ queries[index]
        original_order = sorted(zip(parents.values(), original_scores, strict=True), key=lambda pair: (-float(pair[1]), pair[0].id))
        current = [{"rank": rank, "item": item, "parent_id": item.id, "score": float(score),
                    "span": {"id": item.id, "parent_id": item.id, "start": 0, "end": len(item.text)}}
                   for rank, (item, score) in enumerate([(i, s) for i, s in original_order if s >= .35 and allowed_in_jurisdiction(i, "NO")], 1)]
        for mode in modes:
            row = {"id": case["id"], "question": case["question"], "cohort": case["cohort"], "template": case["template"],
                   "coverage": case["coverage"], "owner_review": case.get("owner_review")}
            seeds = current if mode == "current" else semantic if mode.startswith("semantic") else hybrid
            for k in [3, 5]:
                context = pack_narrow(case["question"], seeds, k, parents, counter, 2000) if mode.endswith("narrow") else pack(
                    case["question"], seeds, "current" if mode == "current" else "section_unique", k, parents, counter, 2000)
                context["instruction_coverage"] = fact_coverage(case["template"], context["excerpts"], instructions["definitions"], parents)
                intrusions = {"cold-nb": {"source-04-003"}, "warmth-nb": {"source-04-003"},
                              "water-nb": {"source-20-003", "source-20-004"}, "river-nb": {"source-20-003", "source-20-004"}}
                context["known_intrusions"] = sorted({r["item"]["id"] for r in context["excerpts"]} & intrusions.get(case["template"], set()))
                row[f"at{k}"] = context
                directory = output / "contexts" / mode / case["id"] / f"top-{k}"
                directory.mkdir(parents=True)
                (directory / "prompt.txt").write_text(context["prompt"], encoding="utf-8")
                write_json(directory / "context.json", context)
                if index < len(originals) and mode in {"current", "semantic_broad"}:
                    old = prior_results["results"]["current" if mode == "current" else "section_unique"][index][f"at{k}"]
                    assert [r["item"]["id"] for r in context["excerpts"]] == [r["item"]["id"] for r in old["excerpts"]]
                    assert context["instruction_coverage"] == old["instruction_coverage"]
                    assert context["prompt_tokens"] == old["prompt_tokens"]
            results[mode].append(row)
            print(case["id"], mode, {f"at{k}": (row[f"at{k}"]["instruction_coverage"].get("facts_present"),
                                                row[f"at{k}"]["prompt_tokens"]) for k in [3, 5]}, flush=True)
        write_json(output / "results-partial.json", results)
    summary = {mode: {cohort: summarize(rows, cohort) for cohort in ["original", "fresh"]} for mode, rows in results.items()}
    write_json(output / "results.json", {"definitions": instructions["definitions"], "results": results, "summary": summary})
    command = [sys.executable, "-m", "pytest", "tests/test_semantic_retrieval.py", "../evals/test_parent_context.py", "../evals/test_retrieval_refinement.py", "-q"]
    check = subprocess.run(command, cwd=ROOT / "backend", capture_output=True, text=True, encoding="utf-8")
    with model.open("rb") as stream:
        model_hash = hashlib.file_digest(stream, "sha256").hexdigest()
    lock = read(INPUT / "embedding-model-lock.json")
    embedding_hashes = {name: digest((ROOT / "knowledge/local/embedding-model" / name).read_bytes()) for name in lock["files"]}
    write_json(output / "verification.json", {"protected_file_count": len(protected), "protected_files_unchanged": fingerprint() == protected,
               "embedding_assets_unchanged": embedding_hashes == lock["files"], "qwen_gguf_unchanged": model_hash == previous_parameters["model_sha256"],
               "original_controls_reproduced": True, "cases_config_unchanged": digest(config_path.read_bytes()) == read(output / "parameters.json")["probes_config_sha256"],
               "prompt_counts_cached": len(counter.reused), "prompt_counts_new": len(counter.cache) - len(counter.reused),
               "generation_calls": 0, "pytest_command": command, "returncode": check.returncode, "stdout": check.stdout, "stderr": check.stderr,
               "hashes": fingerprint()})
    assert check.returncode == 0 and fingerprint() == protected and embedding_hashes == lock["files"] and model_hash == previous_parameters["model_sha256"]
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
