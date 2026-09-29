from __future__ import annotations

import json
from pathlib import Path

import pytest

from outwise.knowledge.loader import (
    KnowledgeValidationError,
    load_knowledge_items,
    load_retrieval_evaluations,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIRECTORY = REPOSITORY_ROOT / "knowledge" / "fixtures"


def write_json(path: Path, value: object) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def valid_item(**overrides: object) -> dict[str, object]:
    item: dict[str, object] = {
        "id": "fixture-test-001",
        "text": "Synthetic test guidance.",
        "title": "Synthetic test item",
        "source_name": "Outwise test fixtures",
        "source_url": "fixture://outwise/test/item",
        "license": "CC0-1.0",
        "language": "en",
        "topic": "test",
    }
    item.update(overrides)
    return item


def test_repository_fixtures_load_with_required_metadata() -> None:
    items = load_knowledge_items(FIXTURE_DIRECTORY / "development-knowledge.json")

    assert len(items) == 8
    assert len({item.topic for item in items}) >= 6
    for item in items:
        assert item.id
        assert item.text
        assert item.title
        assert item.source_name
        assert item.source_url
        assert item.license == "CC0-1.0"
        assert item.language
        assert item.topic
        assert item.metadata["synthetic"] is True


@pytest.mark.parametrize(
    "missing_field",
    [
        "id",
        "text",
        "title",
        "source_name",
        "source_url",
        "license",
        "language",
        "topic",
    ],
)
def test_required_item_metadata_is_enforced(
    tmp_path: Path, missing_field: str
) -> None:
    item = valid_item()
    del item[missing_field]
    path = write_json(
        tmp_path / "knowledge.json", {"schema_version": 1, "items": [item]}
    )

    with pytest.raises(KnowledgeValidationError, match=missing_field):
        load_knowledge_items(path)


def test_duplicate_item_ids_are_rejected(tmp_path: Path) -> None:
    path = write_json(
        tmp_path / "knowledge.json",
        {"schema_version": 1, "items": [valid_item(), valid_item(title="Second")]},
    )

    with pytest.raises(KnowledgeValidationError, match="Duplicate knowledge item id"):
        load_knowledge_items(path)


@pytest.mark.parametrize(
    "override, expected_error",
    [
        ({"text": "  "}, "text must be a non-empty string"),
        ({"source_url": "not-absolute"}, "source_url must be an absolute URL"),
        ({"published_at": "15 March 2026"}, "published_at must use YYYY-MM-DD"),
        ({"metadata": []}, "metadata must be an object"),
        ({"unexpected": "typo"}, "unknown fields"),
    ],
)
def test_invalid_item_data_is_rejected(
    tmp_path: Path, override: dict[str, object], expected_error: str
) -> None:
    path = write_json(
        tmp_path / "knowledge.json",
        {"schema_version": 1, "items": [valid_item(**override)]},
    )

    with pytest.raises(KnowledgeValidationError, match=expected_error):
        load_knowledge_items(path)


def test_retrieval_eval_set_references_fixture_items_and_sources() -> None:
    items = load_knowledge_items(FIXTURE_DIRECTORY / "development-knowledge.json")

    cases = load_retrieval_evaluations(
        FIXTURE_DIRECTORY / "retrieval-evals.json", items
    )

    assert len(cases) == 4
    assert all(case.relevant_item_ids for case in cases)
    assert all(case.expected_sources for case in cases)


def test_eval_unknown_item_reference_is_rejected(tmp_path: Path) -> None:
    eval_document = {
        "schema_version": 1,
        "cases": [
            {
                "id": "eval-invalid",
                "question": "Test question?",
                "relevant_item_ids": ["missing-item"],
                "expected_sources": [
                    {
                        "source_name": "Outwise test fixtures",
                        "source_url": "fixture://outwise/test/item",
                    }
                ],
            }
        ],
    }

    with pytest.raises(KnowledgeValidationError, match="unknown knowledge items"):
        load_retrieval_evaluations(
            write_json(tmp_path / "evals.json", eval_document), []
        )


def test_eval_source_identity_must_match_referenced_items(tmp_path: Path) -> None:
    eval_document = {
        "schema_version": 1,
        "cases": [
            {
                "id": "eval-invalid-source",
                "question": "Test question?",
                "relevant_item_ids": ["fixture-test-001"],
                "expected_sources": [
                    {
                        "source_name": "Invented source",
                        "source_url": "fixture://outwise/invented",
                    }
                ],
            }
        ],
    }
    knowledge_path = write_json(
        tmp_path / "knowledge.json",
        {"schema_version": 1, "items": [valid_item()]},
    )

    with pytest.raises(KnowledgeValidationError, match="expected_sources do not match"):
        load_retrieval_evaluations(
            write_json(tmp_path / "evals.json", eval_document),
            load_knowledge_items(knowledge_path),
        )
