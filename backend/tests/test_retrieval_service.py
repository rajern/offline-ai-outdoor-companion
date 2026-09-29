from __future__ import annotations

from pathlib import Path

import pytest

from outwise.knowledge.loader import (
    load_knowledge_items,
    load_retrieval_evaluations,
)
from outwise.knowledge.models import KnowledgeItem, SourceIdentity
from outwise.services.retrieval import RetrievalService


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIRECTORY = REPOSITORY_ROOT / "knowledge" / "fixtures"
KNOWLEDGE_PATH = FIXTURE_DIRECTORY / "development-knowledge.json"
EVALUATIONS_PATH = FIXTURE_DIRECTORY / "retrieval-evals.json"


def fixture_retriever() -> RetrievalService:
    return RetrievalService.from_json(KNOWLEDGE_PATH)


def test_all_retrieval_evaluations_find_expected_items_and_sources() -> None:
    items = load_knowledge_items(KNOWLEDGE_PATH)
    cases = load_retrieval_evaluations(EVALUATIONS_PATH, items)
    retriever = RetrievalService(items)

    for case in cases:
        results = retriever.retrieve(case.question, top_k=len(case.relevant_item_ids))

        assert {result.item.id for result in results} == set(case.relevant_item_ids), case.id
        assert {
            SourceIdentity(result.item.source_name, result.item.source_url)
            for result in results
        } == set(case.expected_sources), case.id
        assert all(result.score > 0 for result in results)


def test_result_preserves_complete_original_knowledge_item() -> None:
    items = load_knowledge_items(KNOWLEDGE_PATH)
    expected = next(item for item in items if item.id == "fixture-water-001")

    [result] = RetrievalService(items).retrieve("treat drinking water", top_k=1)

    assert result.item is expected
    assert result.item == KnowledgeItem(
        id="fixture-water-001",
        text=expected.text,
        title=expected.title,
        source_name="Outwise synthetic development fixtures",
        source_url="fixture://outwise/water/treatment",
        license="CC0-1.0",
        language="en",
        topic="water-hygiene",
        section="Treatment and storage",
        document_id="outwise-fixtures-v1",
        metadata={"synthetic": True},
    )


def test_results_are_ranked_and_limited_by_top_k() -> None:
    results = fixture_retriever().retrieve(
        "I am lost, wet and cold outdoors", top_k=2
    )

    assert {result.item.id for result in results} == {
        "fixture-lost-001",
        "fixture-cold-exposure-001",
    }
    assert results[0].score >= results[1].score


@pytest.mark.parametrize("query", ["", "   "])
def test_blank_query_is_rejected(query: str) -> None:
    with pytest.raises(ValueError, match="query must be a non-empty string"):
        fixture_retriever().retrieve(query)


@pytest.mark.parametrize("top_k", [0, -1, True, 1.5])
def test_invalid_top_k_is_rejected(top_k: object) -> None:
    with pytest.raises(ValueError, match="top_k must be a positive integer"):
        fixture_retriever().retrieve("water", top_k=top_k)  # type: ignore[arg-type]


def test_no_relevant_result_returns_empty_list() -> None:
    assert fixture_retriever().retrieve("quantum microprocessor warranty") == []


def test_empty_store_returns_empty_list() -> None:
    assert RetrievalService([]).retrieve("water") == []


def test_generic_outdoors_word_does_not_add_unrelated_results() -> None:
    results = fixture_retriever().retrieve(
        "I twisted my ankle outdoors. What should I do first?"
    )

    assert [result.item.id for result in results] == ["fixture-first-aid-ankle-001"]
