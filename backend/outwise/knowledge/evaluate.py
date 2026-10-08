"""Reproducible real-KB retrieval checks without copying source text to Git."""

import argparse
import json
import socket
from pathlib import Path

from outwise.knowledge.ingestion import DEFAULT_LOCAL, ROOT, write_json
from outwise.services.semantic_retrieval import SemanticRetrievalService


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local", type=Path, default=DEFAULT_LOCAL)
    parser.add_argument("--cases", type=Path, default=ROOT / "evals/real-knowledge.json")
    parser.add_argument("--answers", action="store_true", help="Also run local Qwen; save answers for owner review")
    parser.add_argument("--offline-check", action="store_true", help="Reject Python network connections during evaluation")
    args = parser.parse_args()
    if args.offline_check:
        def reject_network(*args, **kwargs):
            raise AssertionError("Network connection forbidden during offline evaluation")
        socket.socket.connect = reject_network
        socket.create_connection = reject_network
    service = SemanticRetrievalService.from_json(args.local / "knowledge.json")
    if args.answers:
        from outwise.services.model import ModelService
        from outwise.services.orchestrator import Orchestrator
        orchestrator = Orchestrator(service, ModelService())
    rows = []
    for case in json.loads(args.cases.read_text(encoding="utf-8"))["cases"]:
        results = service.retrieve(case["question"])
        found = {result.item.document_id for result in results}
        expected = set(case["expected_documents"])
        passed = bool(found & expected) if expected else not found
        row = {**case, "retrieval_passed": passed, "results": [{"id": r.item.id, "document_id": r.item.document_id,
                "score": round(r.score, 4), "section": r.item.section, "source_url": r.item.source_url} for r in results]}
        if args.answers:
            from dataclasses import asdict
            answer = orchestrator.answer(case["question"])
            row["answer"] = answer.answer
            row["answer_quality"] = "requires_manual_review"
            row["sources"] = [asdict(source) for source in answer.sources]
            assert {s.source_url for s in answer.sources} == {r.item.source_url for r in results}
            assert answer.answer.strip() and "(truncated)" not in answer.answer
        rows.append(row)
        print(f"{case['id']}: retrieval {'PASS' if passed else 'FAIL'} {[(r.item.id, round(r.score, 3)) for r in results]}", flush=True)
    write_json(args.local / ("answer-report.json" if args.answers else "retrieval-report.json"),
               {"scope": "Expected document in top 3; not factual answer validation", "cases": rows})
    if not all(row["retrieval_passed"] for row in rows):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
