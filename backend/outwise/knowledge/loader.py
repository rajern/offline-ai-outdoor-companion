"""Load and validate normalized Outwise knowledge and retrieval evaluations."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from outwise.knowledge.models import KnowledgeItem, RetrievalEvaluation, SourceIdentity


SCHEMA_VERSION = 1
REQUIRED_ITEM_FIELDS = (
    "id",
    "text",
    "title",
    "source_name",
    "source_url",
    "license",
    "language",
    "topic",
)
OPTIONAL_ITEM_FIELDS = (
    "section",
    "published_at",
    "updated_at",
    "document_id",
)
ALLOWED_ITEM_FIELDS = set(REQUIRED_ITEM_FIELDS + OPTIONAL_ITEM_FIELDS + ("metadata",))


class KnowledgeValidationError(ValueError):
    """Raised when normalized knowledge or an evaluation set is invalid."""


def load_knowledge_items(path: str | Path) -> list[KnowledgeItem]:
    document = _load_json_object(Path(path))
    _validate_schema_version(document, Path(path))
    raw_items = document.get("items")
    if not isinstance(raw_items, list):
        raise KnowledgeValidationError(f"{path}: 'items' must be a list")

    items = [_parse_knowledge_item(value, index) for index, value in enumerate(raw_items)]
    _reject_duplicate_values([item.id for item in items], "knowledge item id")
    return items


def load_retrieval_evaluations(
    path: str | Path,
    knowledge_items: list[KnowledgeItem],
) -> list[RetrievalEvaluation]:
    document = _load_json_object(Path(path))
    _validate_schema_version(document, Path(path))
    raw_cases = document.get("cases")
    if not isinstance(raw_cases, list):
        raise KnowledgeValidationError(f"{path}: 'cases' must be a list")

    cases = [_parse_evaluation(value, index) for index, value in enumerate(raw_cases)]
    _reject_duplicate_values([case.id for case in cases], "retrieval evaluation id")
    _validate_evaluation_references(cases, knowledge_items)
    return cases


def _load_json_object(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as fixture_file:
            document = json.load(fixture_file)
    except (OSError, json.JSONDecodeError) as exc:
        raise KnowledgeValidationError(f"Could not load valid JSON from {path}: {exc}") from exc
    if not isinstance(document, dict):
        raise KnowledgeValidationError(f"{path}: root must be an object")
    return document


def _validate_schema_version(document: dict[str, Any], path: Path) -> None:
    if document.get("schema_version") != SCHEMA_VERSION:
        raise KnowledgeValidationError(
            f"{path}: 'schema_version' must be {SCHEMA_VERSION}"
        )


def _parse_knowledge_item(value: Any, index: int) -> KnowledgeItem:
    location = f"items[{index}]"
    if not isinstance(value, dict):
        raise KnowledgeValidationError(f"{location} must be an object")

    unknown_fields = set(value) - ALLOWED_ITEM_FIELDS
    if unknown_fields:
        raise KnowledgeValidationError(
            f"{location} has unknown fields: {', '.join(sorted(unknown_fields))}"
        )

    required = {field: _required_text(value, field, location) for field in REQUIRED_ITEM_FIELDS}
    _validate_source_url(required["source_url"], location)

    optional = {
        field: _optional_text(value, field, location) for field in OPTIONAL_ITEM_FIELDS
    }
    for date_field in ("published_at", "updated_at"):
        if optional[date_field] is not None:
            _validate_iso_date(optional[date_field], date_field, location)

    metadata = value.get("metadata", {})
    if not isinstance(metadata, dict) or not all(
        isinstance(key, str) for key in metadata
    ):
        raise KnowledgeValidationError(
            f"{location}.metadata must be an object with string keys"
        )

    return KnowledgeItem(**required, **optional, metadata=metadata)


def _parse_evaluation(value: Any, index: int) -> RetrievalEvaluation:
    location = f"cases[{index}]"
    if not isinstance(value, dict):
        raise KnowledgeValidationError(f"{location} must be an object")

    expected_fields = {"id", "question", "relevant_item_ids", "expected_sources"}
    unknown_fields = set(value) - expected_fields
    if unknown_fields:
        raise KnowledgeValidationError(
            f"{location} has unknown fields: {', '.join(sorted(unknown_fields))}"
        )

    case_id = _required_text(value, "id", location)
    question = _required_text(value, "question", location)
    item_ids = _required_text_list(value, "relevant_item_ids", location)
    _reject_duplicate_values(item_ids, f"{location} relevant item id")

    raw_sources = value.get("expected_sources")
    if not isinstance(raw_sources, list) or not raw_sources:
        raise KnowledgeValidationError(
            f"{location}.expected_sources must be a non-empty list"
        )
    sources: list[SourceIdentity] = []
    for source_index, raw_source in enumerate(raw_sources):
        source_location = f"{location}.expected_sources[{source_index}]"
        if not isinstance(raw_source, dict) or set(raw_source) != {
            "source_name",
            "source_url",
        }:
            raise KnowledgeValidationError(
                f"{source_location} must contain only source_name and source_url"
            )
        source_name = _required_text(raw_source, "source_name", source_location)
        source_url = _required_text(raw_source, "source_url", source_location)
        _validate_source_url(source_url, source_location)
        sources.append(SourceIdentity(source_name=source_name, source_url=source_url))

    return RetrievalEvaluation(
        id=case_id,
        question=question,
        relevant_item_ids=tuple(item_ids),
        expected_sources=tuple(sources),
    )


def _required_text(value: dict[str, Any], field: str, location: str) -> str:
    field_value = value.get(field)
    if not isinstance(field_value, str) or not field_value.strip():
        raise KnowledgeValidationError(f"{location}.{field} must be a non-empty string")
    return field_value.strip()


def _optional_text(value: dict[str, Any], field: str, location: str) -> str | None:
    field_value = value.get(field)
    if field_value is None:
        return None
    if not isinstance(field_value, str) or not field_value.strip():
        raise KnowledgeValidationError(
            f"{location}.{field} must be a non-empty string when present"
        )
    return field_value.strip()


def _required_text_list(value: dict[str, Any], field: str, location: str) -> list[str]:
    field_value = value.get(field)
    if not isinstance(field_value, list) or not field_value:
        raise KnowledgeValidationError(f"{location}.{field} must be a non-empty list")
    if not all(isinstance(item, str) and item.strip() for item in field_value):
        raise KnowledgeValidationError(
            f"{location}.{field} must contain non-empty strings"
        )
    return [item.strip() for item in field_value]


def _validate_source_url(source_url: str, location: str) -> None:
    if not urlparse(source_url).scheme:
        raise KnowledgeValidationError(f"{location}.source_url must be an absolute URL")


def _validate_iso_date(value: str, field: str, location: str) -> None:
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise KnowledgeValidationError(
            f"{location}.{field} must use YYYY-MM-DD format"
        ) from exc


def _reject_duplicate_values(values: list[str], label: str) -> None:
    seen: set[str] = set()
    for value in values:
        if value in seen:
            raise KnowledgeValidationError(f"Duplicate {label}: {value}")
        seen.add(value)


def _validate_evaluation_references(
    cases: list[RetrievalEvaluation],
    knowledge_items: list[KnowledgeItem],
) -> None:
    items_by_id = {item.id: item for item in knowledge_items}
    for case in cases:
        missing_ids = set(case.relevant_item_ids) - set(items_by_id)
        if missing_ids:
            raise KnowledgeValidationError(
                f"Evaluation '{case.id}' references unknown knowledge items: "
                f"{', '.join(sorted(missing_ids))}"
            )

        actual_sources = {
            SourceIdentity(
                source_name=items_by_id[item_id].source_name,
                source_url=items_by_id[item_id].source_url,
            )
            for item_id in case.relevant_item_ids
        }
        if set(case.expected_sources) != actual_sources:
            raise KnowledgeValidationError(
                f"Evaluation '{case.id}' expected_sources do not match its knowledge items"
            )
