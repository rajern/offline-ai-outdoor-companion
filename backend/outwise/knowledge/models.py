"""Source-independent data structures used by knowledge ingestion and retrieval."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypeAlias


JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]


@dataclass(frozen=True)
class KnowledgeItem:
    id: str
    text: str
    title: str
    source_name: str
    source_url: str
    license: str
    language: str
    topic: str
    section: str | None = None
    published_at: str | None = None
    updated_at: str | None = None
    document_id: str | None = None
    metadata: dict[str, JsonValue] = field(default_factory=dict)


@dataclass(frozen=True)
class SourceIdentity:
    source_name: str
    source_url: str


@dataclass(frozen=True)
class RetrievalEvaluation:
    id: str
    question: str
    relevant_item_ids: tuple[str, ...]
    expected_sources: tuple[SourceIdentity, ...]
