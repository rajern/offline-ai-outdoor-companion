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
    / "local"
    / "knowledge.json"
)
FIXTURE_KNOWLEDGE_PATH = DEFAULT_KNOWLEDGE_PATH.parent.parent / "fixtures/development-knowledge.json"
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
    license: str
    content_owner: str | None = None
    licence_url: str | None = None
    retrieved_at: str | None = None
    source_updated_at: str | None = None
    notice: str | None = None


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

    default = FIXTURE_KNOWLEDGE_PATH if os.environ.get("OUTWISE_KNOWLEDGE_MODE") == "fixtures" else DEFAULT_KNOWLEDGE_PATH
    return Path(os.environ.get("OUTWISE_KNOWLEDGE_PATH", default))


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
        "Du er Outwise. Svar på norsk bokmål, kort og konkret, med høyst tre "
        "korte punkter. Bruk bare fakta fra kunnskapsutdragene som faktisk "
        "besvarer spørsmålet. Ikke legg til egne råd eller bland inn andre "
        "situasjoner. Hvis utdragene ikke gir nok informasjon, si tydelig hva "
        "kunnskapsbasen ikke dekker. Ikke oppgi nettadresser eller kildehenvisninger; "
        "appen viser kildene separat. Brukeren er i Norge. Kildens tittel angir "
        "artikkelens opphav, ikke brukerens sted.\n\n"
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
                license=item.license,
                content_owner=item.metadata.get("content_owner"),
                licence_url=item.metadata.get("licence_url"),
                retrieved_at=item.metadata.get("retrieved_at"),
                source_updated_at=item.metadata.get("source_updated_at"),
                notice=_reuse_notice(item.metadata.get("licence_url", "")),
            )
        )
    return tuple(sources)


def _reuse_notice(licence_url: str) -> str | None:
    if "doc.govt.nz" in licence_url:
        return ("Source: Department of Conservation (NZ). CC BY 4.0. "
                "Kildeteksten er normalisert og delt i utdrag; svaret er sammenfattet av Outwise.")
    if "cdc.gov" in licence_url:
        return ("Source: CDC. Materialet er tilgjengelig gratis på CDCs nettsted. "
                "Bruken innebærer ingen godkjenning fra CDC, ATSDR, HHS eller USAs regjering. "
                "Outwise-sammendrag er ikke offisielt CDC-innhold.")
    if "weather.gov" in licence_url:
        return ("Source: NOAA/National Weather Service. Bruken innebærer ingen godkjenning "
                "fra NOAA/NWS. Outwise-sammendrag er ikke offisielt myndighetsinnhold.")
    return None
