"""Validate source-authored proposals / calibrate on saved historical contexts.

No retrieval or model imports. Default QA cannot open the control set. This task's
authoring-only flag is not a final holdout-run authorization.
"""
import argparse
import hashlib
import json
from pathlib import Path

import eval_foundation as f
from automatic_retrieval_scoring import score_saved, bounds, CERTIFICATES


def write_json(path, value):
    if path.exists():
        raise ValueError(f"Refusing to overwrite preserved result: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def qa(authoring_control=False):
    f.assert_historical_base()
    dev = f.read_yaml(f.DEVELOPMENT)
    assert dev == f.development_definition()
    base = f.read_yaml(f.BASE)
    corpus = json.loads(f.CORPUS.read_text(encoding="utf-8"))["items"]
    manifest = json.loads(f.MANIFEST.read_text(encoding="utf-8"))
    assert len(manifest["sources"]) == len({p["document_id"] for p in corpus}) == 22
    source_ids = {s["id"] for s in manifest["sources"]}
    assert dev["cases"][:15] == base["cases"] and len(dev["cases"]) == 25
    additions = dev["cases"][15:]
    evidence = f.validate_new_cases(additions, corpus, source_ids)
    certificates = json.loads(CERTIFICATES.read_text(encoding="utf-8"))
    assert certificates["base_gold_sha256"] == f.BASE_HASH
    assert certificates["corpus_sha256"] == f.CORPUS_HASH
    for c in base["cases"]:
        assert len(certificates["rules"][c["id"]]) == len(c["must_have_information"])
        for r in certificates["rules"][c["id"]]:
            for route in r["alternatives"]:
                assert route["all_of"]
                for atom in route["all_of"]:
                    f.source_evidence_locations(atom, corpus)
    dev_pairs = f.duplicate_question_audit(dev["cases"])
    result = {"status": "source_and_schema_checks_passed_pending_owner_review",
              "development_case_count": 25, "unchanged_legacy_cases": 15,
              "new_development_cases": 10,
              "development_supported": sum(c["expected_result"] == "supported_context" for c in dev["cases"]),
              "development_gaps": sum(c["expected_result"] == "insufficient_coverage" for c in dev["cases"]),
              "new_required_items": sum(len(c["must_have_information"]) for c in additions),
              "source_document_count": 22, "base_gold_sha256": f.sha(f.BASE),
              "corpus_sha256": f.sha(f.CORPUS), "manifest_sha256": f.sha(f.MANIFEST),
              "development_sha256": f.sha(f.DEVELOPMENT), "certificates_sha256": f.sha(CERTIFICATES),
              "source_support": evidence, "top_lexical_overlap_pairs_development_only": dev_pairs[:12],
              "similarity_limit": "Word Jaccard is only descriptive; semantic distinctness manually reviewed, not statistically guaranteed",
              "control_read_for_authoring_qa_only": authoring_control, "retrieval_calls": 0, "generation_calls": 0}
    if authoring_control:
        control = f.read_yaml(f.CONTROL)
        assert len(control["cases"]) == 10
        assert not ({c["id"] for c in control["cases"]} & {c["id"] for c in dev["cases"]})
        control_evidence = f.validate_new_cases(control["cases"], corpus, source_ids)
        pairs = f.duplicate_question_audit(dev["cases"] + control["cases"])
        write_json(f.ROOT / "evals/holdout/authoring_qa.v1.json", {
            "purpose": "Authoring/source QA only; NEVER use for optimization or judge calibration",
            "control_sha256": f.sha(f.CONTROL), "set_version": control["set_version"],
            "control_cases": 10, "supported": sum(c["expected_result"] == "supported_context" for c in control["cases"]),
            "gaps": sum(c["expected_result"] == "insufficient_coverage" for c in control["cases"]),
            "required_items": sum(len(c["must_have_information"]) for c in control["cases"]),
            "source_support": control_evidence, "top_question_overlap_pairs": pairs[:20],
            "no_exact_question_duplicates": True, "retrieval_calls": 0, "scoring_calls": 0,
            "semantic_overlap_review": "Different information needs; owner review required. No source/ranking-driven gold changes."})
    write_json(f.ROOT / "evals/retrieval_development_qa.v2.json", result)
    # Public lock reveals only control hash/version/count, never its questions/gold.
    files = [f.BASE, f.ADDITIONS, f.DEVELOPMENT, CERTIFICATES,
             f.ROOT / "evals/automatic_retrieval_scoring.py", f.ROOT / "evals/eval_foundation.py",
             f.ROOT / "evals/retrieval_judge_rubric.v1.md"]
    if authoring_control:
        files += [f.CONTROL]
    lock = {"schema_version": 1, "version": "1.0.0", "status": "pending_owner_review",
            "gold_legacy_immutable": f.BASE_HASH, "corpus_sha256": f.CORPUS_HASH,
            "source_manifest_sha256": f.sha(f.MANIFEST), "development_count": 25,
            "control_count": 10, "control_version": "1.0.0",
            "holdout_process": "Author-created; no retrieval run; later optimizer cannot read; explicit final-run authorization required",
            "files": {str(p.relative_to(f.ROOT)).replace('\\', '/'): {"sha256": f.sha(p)} for p in files}}
    write_json(f.LOCK, lock)
    print(json.dumps({k: v for k, v in result.items() if k not in ["source_support", "top_lexical_overlap_pairs_development_only"]}, indent=2))


def calibrate():
    dev = f.load_development()
    cases = {c["id"]: c for c in dev["cases"][:15]}
    corpus = json.loads(f.CORPUS.read_text(encoding="utf-8"))["items"]
    legacy = json.loads(CERTIFICATES.read_text(encoding="utf-8"))
    runs = [("retrieval-eval-v1-2026-10-07", ["A", "B"]),
            ("retrieval-topk-ablation-v1-2026-10-07", ["B8"]),
            ("retrieval-child-search-v1-2026-10-07", ["C8"]),
            ("retrieval-parent-dedup-v1-2026-10-07", ["C8U8"])]
    inputs, per_case, summary = {}, [], {}
    for directory, modes in runs:
        base = f.ROOT / "knowledge/local/diagnostics" / directory
        rows = json.loads((base / "retrieved-all.json").read_text(encoding="utf-8"))
        manual = json.loads((base / "scoring.json").read_text(encoding="utf-8"))
        for path in [base / "retrieved-all.json", base / "scoring.json"]:
            inputs[str(path.relative_to(f.ROOT)).replace('\\', '/')] = f.sha(path)
        for mode in modes:
            results, tp, fp, unresolved_yes, unresolved_no, manual_found = [], 0, 0, 0, 0, 0
            for row in [r for r in rows if r["configuration"] == mode]:
                c = cases[row["case_id"]]
                assert row["gold_hash"] == f.BASE_HASH and row["corpus_hash"] == f.CORPUS_HASH
                text_path = base / mode / c["id"] / "context.txt"
                context = text_path.read_text(encoding="utf-8")
                assert hashlib.sha256(context.encode()).hexdigest() == row["context_sha256"]
                for kind in ["context", "prompt"]:
                    key = row[kind + "_tokenization_key"]
                    token_dir = base / "tokenization" / key
                    assert hashlib.sha256((token_dir / "input.txt").read_text(encoding="utf-8").encode()).hexdigest() == key
                    assert len(json.loads((token_dir / "stdout.txt").read_text(encoding="utf-8"))) == row[kind + "_tokens"]
                actual = score_saved(c, row, context, corpus, legacy)
                results.append(actual)
                human = manual[mode][c["id"]]
                assert len(actual["items"]) == len(human["items"])
                comparison = []
                for i, (auto, reference) in enumerate(zip(actual["items"], human["items"]), 1):
                    positive = auto["decision"] == "covered"
                    comparison.append({"item": i, "manual_covered": reference["covered"], **auto})
                    if c["expected_result"] == "supported_context":
                        manual_found += reference["covered"]
                        if positive and reference["covered"]: tp += 1
                        elif positive: fp += 1
                        elif reference["covered"]: unresolved_yes += 1
                        else: unresolved_no += 1
                per_case.append({"configuration": mode, "case_id": c["id"], "expected_result": c["expected_result"],
                                 "manual_found": sum(i["covered"] for i in human["items"]),
                                 "automatic_certified": actual["certified_found"], "items": comparison,
                                 "manual_noise_flags": {k: bool(human[k]) for k in ["irrelevant", "potentially_misleading", "jurisdiction_leakage"]},
                                 "automatic_noise_and_geography": "needs_review for nonempty contexts; no final classification calibrated",
                                 "context_sha256": row["context_sha256"]})
            assert len(results) == 15
            supported = [r for r in results if r["expected_result"] == "supported_context"]
            summary[mode] = {"supported_item_decisions": 51, "correct_positive_certificates": tp,
                             "false_positive_certificates": fp, "unresolved_manual_positive": unresolved_yes,
                             "unresolved_manual_negative": unresolved_no, "manual_covered": manual_found,
                             "resolution_rate": (tp + fp) / 51,
                             "precision_of_certified_positives": tp / (tp + fp) if tp + fp else None,
                             "recall_of_manual_positives": tp / manual_found if manual_found else None,
                             "manual_complete_passes": sum(all(i["covered"] for i in manual[mode][r["case_id"]]["items"]) for r in supported),
                             "automatic_complete_pass_lower_bound": sum(r["complete_pass_lower_bound"] for r in supported),
                             "manual_irrelevant_cases": sum(bool(manual[mode][r["case_id"]]["irrelevant"]) for r in supported),
                             "manual_potentially_misleading_cases": sum(bool(manual[mode][r["case_id"]]["potentially_misleading"]) for r in supported),
                             "manual_jurisdiction_leakage_cases": sum(bool(manual[mode][r["case_id"]]["jurisdiction_leakage"]) for r in supported),
                             "bounds": {k:v for k,v in bounds(results).items() if k not in ["results", "insufficient_coverage"]}}
    output = {"status": "not_ready_for_unattended_full_scoring", "date": "2026-10-08",
              "method": "Frozen source-authored positive certificates; no gold/output-based certificate tuning",
              "rules_sha256": f.sha(CERTIFICATES), "development_set_sha256": f.sha(f.DEVELOPMENT),
              "historical_gold_sha256": f.sha(f.BASE), "corpus_sha256": f.sha(f.CORPUS),
              "inputs_sha256": inputs, "configurations": summary, "per_case": per_case,
              "holdout_accessed": False, "new_questions_retrieved": 0, "retrieval_calls": 0,
              "generation_judge_calls": 0, "optimization_iterations": 0,
              "limits": ["Same previously seen 15 cases and correlated contexts; not independent accuracy validation",
                         "Positive certificates incomplete; no automatic negative, noise or geography-zero certification",
                         "No paraphrase/unit-conversion entailment model, judge calibration or inter-rater study",
                         "Certificates frozen before comparison; do not tune against mismatches in this task"]}
    write_json(f.ROOT / "evals/retrieval_scoring_calibration.v1.json", output)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["qa", "calibrate"])
    parser.add_argument("--authoring-control-qa", action="store_true",
                        help="Source-only QA authorized solely for this authoring task; NEVER a retrieval/optimizer permission")
    args = parser.parse_args()
    if args.authoring_control_qa and args.command != "qa":
        parser.error("Holdout authoring cannot be used during calibration")
    qa(args.authoring_control_qa) if args.command == "qa" else calibrate()
