"""Conservative saved-context scoring prototype, not an optimizer or semantic judge.

Only sufficient positive certificates are automatic. Unknown is never a zero
semantic score. Full scoring of novel context requires a calibrated judge or
human review, particularly for noise/conflict/jurisdiction. No model APIs.
"""
from __future__ import annotations

import json
import statistics
from eval_foundation import ROOT, normalized, require_development_cases, load_development

CERTIFICATES = ROOT / "evals/retrieval_evidence_certificates.v1.json"


def rendered_context(excerpts):
    return "\n\n".join(f"[KUNNSKAPSUTDRAG {n}]\nTittel: {e['item']['title']}\nTema: {e['item']['topic']}\nInnhold: {e['item']['text']}"
                      for n, e in enumerate(excerpts, 1))


def certified_item(context, definition):
    """No ID, source-count or ranking lookup; all textual conditions must occur.

This function assumes provenance/applicability was verified upstream. It is a
positive recognizer, not a general semantic classifier or contradiction detector.
"""
    text = normalized(context)
    for route in definition["alternatives"]:
        if all(normalized(atom["quote"]) in text for atom in route["all_of"]):
            return {"decision": "covered", "evidence": [atom["quote"] for atom in route["all_of"]]}
    return {"decision": "needs_review", "evidence": [],
            "reason": "No complete registered sufficient route; equivalent/partial/missing content requires semantic review"}


def case_rules(case, legacy):
    if case["id"] in legacy["rules"]:
        return legacy["rules"][case["id"]]
    return [{"alternatives": [{"all_of": e["all_of"]}]} for e in case["must_have_evidence"]]


def score_saved(case, row, actual_context, corpus, legacy):
    require_development_cases([case["id"]])
    assert row["case_id"] == case["id"] and row["question"] == case["question"]
    assert rendered_context(row["excerpts"]) == actual_context, "Score delivered text, not hidden metadata or discarded packets"
    definitions = case_rules(case, legacy)
    assert len(definitions) == len(case["must_have_information"])
    usable, provenance_issues, geography_candidates = [], [], []
    # Validation accepts exact source substrings, including re-chunked excerpts;
    # IDs can be arbitrary. Larger cross-section representations require review.
    for e in row["excerpts"]:
        item = e["item"]
        parents = [p for p in corpus if p["document_id"] == item.get("document_id") and
                   normalized(item["text"]) in normalized(p["text"]) and
                   item["title"] == p["title"] and item["topic"] == p["topic"] and
                   item.get("source_url") == p["source_url"] and
                   item.get("metadata", {}).get("jurisdiction") == p["metadata"]["jurisdiction"]]
        if not parents:
            provenance_issues.append(item.get("id"))
        elif any(p["metadata"]["jurisdiction"] in ["general", case["jurisdiction"]] for p in parents):
            usable.append(e)
        else:
            geography_candidates.append(item.get("id"))
    context = rendered_context(usable)
    decisions = [certified_item(context, r) for r in definitions]
    found = sum(d["decision"] == "covered" for d in decisions)
    gap = case["expected_result"] == "insufficient_coverage"
    empty = not row["excerpts"]
    return {"case_id": case["id"], "expected_result": case["expected_result"],
            "items": decisions, "certified_found": found, "total": len(decisions),
            "coverage_lower_bound": found / len(decisions) if decisions else None,
            "complete_pass_lower_bound": not gap and bool(decisions) and found == len(decisions),
            "requires_semantic_review": any(d["decision"] == "needs_review" for d in decisions) or not empty,
            "irrelevant_context": "none" if empty else "needs_review",
            "potentially_misleading_context": "none" if empty else "needs_review",
            "jurisdiction_leakage": "none" if empty else "needs_review",
            "jurisdiction_metadata_candidates": geography_candidates, "provenance_issues": provenance_issues,
            "optional_information": "not_scored_as_required; needs_review",
            "context_tokens": row["context_tokens"], "prompt_tokens": row["prompt_tokens"],
            "token_count_status": "Recorded counts; caller must verify tokenizer/input hashes and saved IDs",
            "budget_excluded_packets": row.get("budget_excluded_packets", 0),
            "prompt_within_recorded_budget": row["prompt_tokens"] <= row["context_budget"],
            "chunk_count": row["chunk_count"], "section_count": row["section_count"],
            "knowledge_gap": case["knowledge_gap"] if gap else None,
            "gap_full_answer_pass": False if gap else None,
            "status": "partial_automation_not_a_final_semantic_score"}


def bounds(results):
    supported = [r for r in results if r["expected_result"] == "supported_context"]
    gaps = [r for r in results if r["expected_result"] == "insufficient_coverage"]
    total = sum(r["total"] for r in supported)
    found = sum(r["certified_found"] for r in supported)
    return {"covered_cases": len(supported), "must_have_total": total, "certified_found": found,
            "must_have_coverage_lower_bound": found / total if total else None,
            "must_have_coverage_upper_bound": 1.0 if total else None,
            "average_case_coverage_lower_bound": statistics.mean(r["coverage_lower_bound"] for r in supported) if supported else None,
            "complete_case_pass_lower_bound": sum(r["complete_pass_lower_bound"] for r in supported),
            "unknown_items": total - found,
            "noise_and_geography_final_metrics": "unavailable_without_semantic_review; not zero",
            "context_tokens": {"median": statistics.median(r["context_tokens"] for r in supported)} if supported else None,
            "complete_prompt_tokens": {"median": statistics.median(r["prompt_tokens"] for r in supported)} if supported else None,
            "budget_rejected_packets": sum(r["budget_excluded_packets"] for r in supported),
            "insufficient_coverage": gaps, "results": results}


def development_rules():
    return load_development(), json.loads(CERTIFICATES.read_text(encoding="utf-8"))
