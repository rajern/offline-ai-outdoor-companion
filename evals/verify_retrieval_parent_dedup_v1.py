"""Audit saved artifacts only: no retrieval, tokenization or generation calls."""
import ast
from dataclasses import asdict
from datetime import datetime, timezone
import json
import shutil

import run_retrieval_parent_dedup_v1 as experiment
import run_retrieval_eval_v1 as prior


def main():
    root, base, output = experiment.ROOT, experiment.BASE, experiment.OUTPUT
    frozen = json.loads((output / "frozen-run.json").read_text(encoding="utf-8"))
    records = json.loads((output / "retrieved-all.json").read_text(encoding="utf-8"))
    old = [r for r in json.loads((base / "retrieved-all.json").read_text(encoding="utf-8"))
           if r["configuration"] == "C8"]
    assert len(records) == 30 and records[:15] == old
    assert len({(r["configuration"], r["case_id"]) for r in records}) == 30
    children = {c["child_id"]: c for c in json.loads((base / "children.json").read_text(encoding="utf-8"))}
    parents = {p.id: p for p in prior.load_knowledge_items(prior.CORPUS)}
    scores = json.loads((output / "scoring.json").read_text(encoding="utf-8"))
    offsets = json.loads((output / "scoring-with-offsets.json").read_text(encoding="utf-8"))
    assert scores["C8"] == json.loads((base / "scoring.json").read_text(encoding="utf-8"))["C8"]
    caches = [base, root / "knowledge/local/diagnostics/retrieval-topk-ablation-v1-2026-10-07",
              root / "knowledge/local/diagnostics/retrieval-eval-v1-2026-10-07"]
    copied_caches, keys = 0, set()

    def token_ids(key):
        nonlocal copied_caches
        target = output / "tokenization" / key
        if not target.exists():
            saved = next(cache / "tokenization" / key for cache in caches
                         if (cache / "tokenization" / key).exists())
            assert prior.hashlib.sha256((saved / "input.txt").read_text(encoding="utf-8").encode()).hexdigest() == key
            shutil.copytree(saved, target)
            copied_caches += 1
        assert prior.hashlib.sha256((target / "input.txt").read_text(encoding="utf-8").encode()).hexdigest() == key
        ids = json.loads((target / "stdout.txt").read_text(encoding="utf-8"))
        assert isinstance(ids, list) and all(isinstance(t, int) for t in ids)
        assert json.loads((target / "process.json").read_text(encoding="utf-8"))["returncode"] == 0
        keys.add(key)
        return ids

    for row in records:
        mode, cid = row["configuration"], row["case_id"]
        directory = output / mode / cid
        assert json.loads((directory / "retrieved.json").read_text(encoding="utf-8")) == row
        context = (directory / "context.txt").read_text(encoding="utf-8")
        prompt = (directory / "prompt-not-executed.txt").read_text(encoding="utf-8")
        excerpts = [prior.RetrievedKnowledgeItem(parents[r["item"]["id"]], r["score"]) for r in row["excerpts"]]
        assert [asdict(r) for r in excerpts] == row["excerpts"]
        assert context == prior.context_for(excerpts)
        assert prompt == prior._build_grounded_prompt(row["question"], excerpts)
        assert prior.hashlib.sha256(context.encode()).hexdigest() == row["context_sha256"]
        assert prior.hashlib.sha256(prompt.encode()).hexdigest() == row["prompt_tokenization_key"]
        assert len(token_ids(row["context_tokenization_key"])) == row["context_tokens"]
        assert len(token_ids(row["prompt_tokenization_key"])) == row["prompt_tokens"] <= 2000
        for trace in row["trace"]:
            if "tokenization_key" in trace:
                assert len(token_ids(trace["tokenization_key"])) == trace["prompt_tokens"]
        text = {e["item"]["id"]: e["item"]["text"] for e in row["excerpts"]}
        annotation = offsets[mode][cid]
        groups = [*[i["evidence"] for i in annotation["items"]], annotation["irrelevant"],
                  annotation["potentially_misleading"], annotation["jurisdiction_leakage"]]
        for group in groups:
            for evidence in group:
                assert text[evidence["id"]][evidence["start_char"]:evidence["end_char"]] == evidence["quote"]
        assert all(e["item"]["metadata"]["jurisdiction"] in ["NO", "general"] for e in row["excerpts"])
        if mode == "C8U8":
            ranking = json.loads((directory / "all-candidates.json").read_text(encoding="utf-8"))
            assert ranking == json.loads((base / "C8" / cid / "all-candidates.json").read_text(encoding="utf-8"))
            chosen = experiment.select_unique(ranking, children, parents)
            assert [s["child"]["child_id"] for s in row["child_seeds"]] == [s["child_id"] for s in chosen]
            assert [s["score"] for s in row["child_seeds"]] == [s["score"] for s in chosen]
            assert len({s["item"]["id"] for s in row["seeds"]}) == len(row["seeds"]) <= 8
            control = next(r for r in old if r["case_id"] == cid)
            assert row["excerpts"][:control["chunk_count"]] == control["excerpts"]

    assert prior.protected_hashes() == frozen["protected_before"]
    assert experiment.baseline_hashes() == frozen["baseline_inputs_before"]
    assert prior.sha(experiment.PROTOCOL) == frozen["experiment_sha256"]
    assert prior.sha(root / "evals/run_retrieval_parent_dedup_v1.py") == frozen["runner_sha256"]
    assert prior.sha(root / "evals/score_retrieval_parent_dedup_v1.py") == (output / "scoring-authoring.sha256").read_text().strip()
    artifacts = ["score_retrieval_parent_dedup_v1.py", "verify_retrieval_parent_dedup_v1.py",
                 "retrieval_parent_dedup.v1.2026-10-07.md"]
    for name in artifacts:
        source = root / "evals" / name
        if source.suffix == ".py":
            ast.parse(source.read_text(encoding="utf-8"))
        shutil.copyfile(source, output / name)
    ast.parse((root / "evals/run_retrieval_parent_dedup_v1.py").read_text(encoding="utf-8"))
    shutil.copyfile(base / "chunk-statistics.json", output / "unchanged-child-chunk-statistics.json")
    verification = {"checked_at": datetime.now(timezone.utc).isoformat(), "saved_rows": 30,
                    "baseline_raw_and_scoring_unchanged": True, "rankings_and_scores_unchanged": True,
                    "unique_parent_selection_verified": True, "old_context_exact_prefix": True,
                    "source_text_provenance_verified": True, "prompt_context_reconstructed_exactly": True,
                    "token_counts_verified_from_saved_ids": True, "tokenization_keys": len(keys),
                    "missing_control_tokenization_caches_copied": copied_caches,
                    "all_prompt_tokens_at_most_2000": True, "scoring_quote_offsets_valid": True,
                    "protected_inputs_unchanged": True, "prior_baseline_inputs_unchanged": True,
                    "frozen_protocol_runner_and_scorer_unchanged": True, "python_syntax_valid": True,
                    "retrieval_embedding_tokenization_generation_calls_during_verification": 0,
                    "report_sha256": prior.sha(root / "evals/retrieval_parent_dedup.v1.2026-10-07.md")}
    prior.write_json(output / "final-verification.json", verification)
    hashes = {str(p.relative_to(output)): prior.sha(p) for p in sorted(output.rglob("*"))
              if p.is_file() and p.name != "artifact-hashes.json"}
    prior.write_json(output / "artifact-hashes.json", hashes)
    print(json.dumps(verification, indent=2))
    print(f"Artifact hashes saved: {len(hashes)}")


if __name__ == "__main__":
    main()
