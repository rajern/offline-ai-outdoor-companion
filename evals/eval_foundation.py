"""Source-only preparation / saved-context helpers, never a retrieval runner.

Public evaluators use load_development(). The control set has no public loader;
authoring QA is deliberately separate. This is a process gate, not a sandbox.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re

import yaml

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "evals/retrieval_cases.v1.yaml"
ADDITIONS = ROOT / "evals/retrieval_development_additions.v2.yaml"
DEVELOPMENT = ROOT / "evals/retrieval_development.v2.yaml"
CONTROL = ROOT / "evals/holdout/retrieval_control.v1.yaml"
CORPUS = ROOT / "knowledge/local/knowledge.json"
MANIFEST = ROOT / "knowledge/manifests/approved-sources.json"
LOCK = ROOT / "evals/retrieval_foundation.lock.json"
BASE_HASH = "04ad519f56cfff4fc4158af1975363a142b06d84c84d8f7e842a1095d07868c4"
CORPUS_HASH = "bd954cd27111854db2a54a8b05335dac8be7776301060da2cce3dfedb2a33d20"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_yaml(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def normalized(text):
    # Only whitespace is relaxed: preserve numbers, punctuation and negations.
    return re.sub(r"\s+", " ", text).strip()


def assert_historical_base():
    if sha(BASE) != BASE_HASH or sha(CORPUS) != CORPUS_HASH:
        raise ValueError("Historical gold/corpus identity changed; stop for owner review")


def development_definition():
    """Mechanical composition; first 15 dictionaries are copied verbatim."""
    assert_historical_base()
    original = read_yaml(BASE)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    new = read_yaml(ADDITIONS)
    result = deepcopy(original)
    result.update(set_id="outwise-retrieval-development-v2", set_version="2.0.0",
                  created_at="2026-10-08", status="pending_owner_review",
                  partition="development", legacy_base={"path": "evals/retrieval_cases.v1.yaml",
                  "sha256": BASE_HASH, "cases": 15},
                  review={"legacy": "Existing 15 definitions retained exactly, including review labels",
                          "new": "10 source-authored proposals; no retrieval runs; pending owner review"})
    for s in manifest["sources"]:
        p = manifest["publishers"][s["publisher"]]
        result["sources"].setdefault(s["id"], {"title": s["title"], "url": s["url"],
                                              "publisher": p["name"], "language": p["language"]})
    result["cases"].extend(new["cases"])
    assert result["cases"][:15] == original["cases"] and len(result["cases"]) == 25
    return result


def load_development():
    definition = read_yaml(DEVELOPMENT)
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    assert_historical_base()
    if sha(DEVELOPMENT) != lock["files"]["evals/retrieval_development.v2.yaml"]["sha256"]:
        raise ValueError("Development set hash differs from review lock")
    if definition != development_definition():
        raise ValueError("Development set is not exact historical-plus-additions composition")
    return definition


def require_development_cases(case_ids):
    permitted = {c["id"] for c in load_development()["cases"]}
    if set(case_ids) - permitted:
        raise ValueError("Unknown/holdout cases forbidden in development scoring")


def source_evidence_locations(evidence, corpus):
    """Exact source QA, not a required chunk-ID retrieval gold."""
    matches = []
    for p in corpus:
        if p["document_id"] != evidence["source_id"] or p["section"] != evidence["section"]:
            continue
        field = "section" if evidence.get("location") == "section_heading" else "text"
        start = p[field].find(evidence["quote"])
        if start >= 0:
            matches.append({"locator_id": p["id"], "field": field, "start_char": start,
                            "end_char": start + len(evidence["quote"]),
                            "passage_sha256": hashlib.sha256(p["text"].encode()).hexdigest(),
                            "source_url": p["source_url"], "jurisdiction": p["metadata"]["jurisdiction"]})
    if not matches:
        raise ValueError(f"Unsupported evidence span: {evidence}")
    return matches


def validate_new_cases(cases, corpus, source_ids):
    required = {"question", "areas", "difficulty", "jurisdiction", "expected_result",
                "relevant_sources", "preferred_source_sections", "supporting_sources",
                "must_have_information", "must_have_evidence", "acceptable_source_sections_or_chunks",
                "optional_useful_information", "irrelevant_or_potentially_misleading_information",
                "knowledge_gap", "gold_uncertainty", "why_this_case_is_useful"}
    resolved = {}
    for c in cases:
        assert required <= c.keys(), (c["id"], required - c.keys())
        assert set(c["relevant_sources"]) <= source_ids
        assert c["expected_result"] in ["supported_context", "insufficient_coverage"]
        assert (c["expected_result"] == "insufficient_coverage") == (c["knowledge_gap"]["status"] == "insufficient_coverage")
        assert sorted(e["item"] for e in c["must_have_evidence"]) == list(range(1, len(c["must_have_information"]) + 1))
        resolved[c["id"]] = []
        for e in c["must_have_evidence"]:
            assert e["all_of"]
            entries = []
            for atom in e["all_of"]:
                locations = source_evidence_locations(atom, corpus)
                assert any(p["jurisdiction"] in ["general", c["jurisdiction"]] for p in locations)
                entries.append({"evidence": atom, "locations": locations})
            resolved[c["id"]].append({"item": e["item"], "source_support": entries})
        for s in c["preferred_source_sections"] + c["supporting_sources"]:
            assert s["source_id"] in source_ids
            for section in s["sections"]:
                assert any(p["document_id"] == s["source_id"] and p["section"] == section for p in corpus)
    return resolved


def duplicate_question_audit(cases):
    """Descriptive lexical overlap only; semantic overlap requires author review."""
    rows = []
    for i, a in enumerate(cases):
        words_a = set(re.findall(r"\w+", a["question"].lower()))
        for b in cases[i+1:]:
            words_b = set(re.findall(r"\w+", b["question"].lower()))
            assert normalized(a["question"].lower()) != normalized(b["question"].lower())
            overlap = len(words_a & words_b) / len(words_a | words_b)
            rows.append({"a": a["id"], "b": b["id"], "word_jaccard": overlap})
    return sorted(rows, key=lambda r: -r["word_jaccard"])
