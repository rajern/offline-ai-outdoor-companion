"""Coordinate grounded retrieval and local model generation for one request."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from outwise.knowledge.models import RetrievedKnowledgeItem


DEFAULT_KNOWLEDGE_PATH = (
    Path(__file__).resolve().parents[3]
    / "knowledge"
    / "fixtures"
    / "development-knowledge.json"
)
NO_GROUNDED_ANSWER = (
    "Jeg fant ingen relevant informasjon i den lokale kunnskapsbasen. "
    "Jeg kan derfor ikke gi et kildebasert svar på dette spørsmålet."
)


class ModelGenerator(Protocol):
    def generate(self, prompt: str) -> str: ...


class KnowledgeRetriever(Protocol):
    def retrieve(
        self, query: str, *, top_k: int = 3
    ) -> list[RetrievedKnowledgeItem]: ...


@dataclass(frozen=True)
class AnswerSource:
    title: str
    source_name: str
    source_url: str


@dataclass(frozen=True)
class GroundedAnswer:
    answer: str
    sources: tuple[AnswerSource, ...]


class Orchestrator:
    """Run retrieval before generation and keep citations outside the model."""

    def __init__(
        self,
        retrieval_service: KnowledgeRetriever,
        model_service: ModelGenerator,
        *,
        top_k: int = 3,
    ) -> None:
        if top_k <= 0:
            raise ValueError("top_k must be positive")
        self._retrieval_service = retrieval_service
        self._model_service = model_service
        self._top_k = top_k

    def answer(self, message: str) -> GroundedAnswer:
        results = self._retrieval_service.retrieve(message, top_k=self._top_k)
        if not results:
            return GroundedAnswer(answer=NO_GROUNDED_ANSWER, sources=())

        prompt = _build_grounded_prompt(message, results)
        answer = self._model_service.generate(prompt)
        return GroundedAnswer(answer=answer, sources=_sources_from(results))


def knowledge_path_from_environment() -> Path:
    """Return normalized knowledge path without coupling retrieval to its source."""

    return Path(os.environ.get("OUTWISE_KNOWLEDGE_PATH", DEFAULT_KNOWLEDGE_PATH))


def _build_grounded_prompt(
    message: str, results: list[RetrievedKnowledgeItem]
) -> str:
    context_blocks = []
    for index, result in enumerate(results, start=1):
        item = result.item
        context_blocks.append(
            f"[KUNNSKAPSUTDRAG {index}]\n"
            f"Tittel: {item.title}\n"
            f"Tema: {item.topic}\n"
            f"Innhold: {item.text}"
        )

    context = "\n\n".join(context_blocks)
    return (
        "You are Outwise, a local outdoor assistant. Answer briefly and "
        "practically in the same language as the user. Use only the knowledge "
        "extracts below as factual grounding. Do not fill gaps with your own "
        "knowledge. If the extracts do not support a necessary claim, clearly "
        "say that the available knowledge does not cover it. Do not create or "
        "repeat URLs or citations; the application adds stored sources "
        "separately.\n\n"
        f"{context}\n\n"
        f"[BRUKERSPØRSMÅL]\n{message}\n\n"
        "[SVAR]"
    )


def _sources_from(
    results: list[RetrievedKnowledgeItem],
) -> tuple[AnswerSource, ...]:
    sources: list[AnswerSource] = []
    seen: set[tuple[str, str]] = set()
    for result in results:
        item = result.item
        identity = (item.source_name, item.source_url)
        if identity in seen:
            continue
        seen.add(identity)
        sources.append(
            AnswerSource(
                title=item.title,
                source_name=item.source_name,
                source_url=item.source_url,
            )
        )
    return tuple(sources)
