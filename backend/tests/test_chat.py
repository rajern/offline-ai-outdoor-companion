import asyncio

import httpx
import pytest

from outwise.main import create_app
from outwise.knowledge.models import KnowledgeItem, RetrievedKnowledgeItem
from outwise.services.model import (
    ModelGenerationError,
    ModelLoadError,
    ModelNotFoundError,
    ModelRuntimeNotFoundError,
    ModelTimeoutError,
)


class StubModelService:
    def __init__(self, answer: str = "Prioriter varme og finn ly.") -> None:
        self.answer = answer
        self.prompt: str | None = None
        self.error: Exception | None = None

    def generate(self, prompt: str) -> str:
        self.prompt = prompt
        if self.error:
            raise self.error
        return self.answer


class StubRetrievalService:
    def __init__(self, results: list[RetrievedKnowledgeItem] | None = None) -> None:
        item = KnowledgeItem(
            id="fixture-lost",
            text="Stop moving and assess your last known location.",
            title="Synthetic lost guidance",
            source_name="Stored fixture source",
            source_url="fixture://outwise/navigation/lost",
            license="CC0-1.0",
            language="en",
            topic="navigation",
        )
        self.results = results if results is not None else [
            RetrievedKnowledgeItem(item=item, score=1.0)
        ]

    def retrieve(
        self, query: str, *, top_k: int = 3
    ) -> list[RetrievedKnowledgeItem]:
        return self.results[:top_k]


def test_chat_endpoint_returns_model_answer() -> None:
    model_service = StubModelService()

    async def post_message() -> httpx.Response:
        transport = httpx.ASGITransport(
            app=create_app(model_service, StubRetrievalService())
        )
        async with httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        ) as client:
            return await client.post(
                "/api/chat", json={"message": "  Jeg har gått meg vill.  "}
            )

    response = asyncio.run(post_message())

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Prioriter varme og finn ly.",
        "sources": [
            {
                "title": "Synthetic lost guidance",
                "name": "Stored fixture source",
                "url": "fixture://outwise/navigation/lost",
                "license": "CC0-1.0",
            }
        ],
    }
    assert model_service.prompt is not None
    assert "Jeg har gått meg vill." in model_service.prompt
    assert "Stop moving and assess your last known location." in model_service.prompt


def test_chat_endpoint_rejects_blank_message() -> None:
    async def post_message() -> httpx.Response:
        transport = httpx.ASGITransport(
            app=create_app(StubModelService(), StubRetrievalService())
        )
        async with httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        ) as client:
            return await client.post("/api/chat", json={"message": "   "})

    response = asyncio.run(post_message())

    assert response.status_code == 422


def test_chat_endpoint_allows_local_frontend_origin() -> None:
    async def preflight() -> httpx.Response:
        transport = httpx.ASGITransport(
            app=create_app(StubModelService(), StubRetrievalService())
        )
        async with httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        ) as client:
            return await client.options(
                "/api/chat",
                headers={
                    "Origin": "http://localhost:8081",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "content-type",
                },
            )

    response = asyncio.run(preflight())

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:8081"


@pytest.mark.parametrize(
    ("error", "expected_status", "expected_detail"),
    [
        (
            ModelNotFoundError("missing model"),
            503,
            "Den lokale modellen er ikke klar.",
        ),
        (
            ModelRuntimeNotFoundError("missing runtime"),
            503,
            "Den lokale modellen er ikke klar.",
        ),
        (
            ModelTimeoutError("timed out"),
            504,
            "Den lokale modellen brukte for lang tid.",
        ),
        (
            ModelLoadError("load failed"),
            503,
            "Den lokale modellen kunne ikke lage et svar.",
        ),
        (
            ModelGenerationError("generation failed"),
            503,
            "Den lokale modellen kunne ikke lage et svar.",
        ),
    ],
)
def test_chat_endpoint_maps_model_errors(
    error: Exception, expected_status: int, expected_detail: str
) -> None:
    model_service = StubModelService()
    model_service.error = error

    async def post_message() -> httpx.Response:
        transport = httpx.ASGITransport(
            app=create_app(model_service, StubRetrievalService())
        )
        async with httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        ) as client:
            return await client.post("/api/chat", json={"message": "Hjelp"})

    response = asyncio.run(post_message())

    assert response.status_code == expected_status
    assert response.json()["detail"].startswith(expected_detail)


def test_chat_endpoint_returns_no_sources_and_skips_model_on_no_match() -> None:
    model_service = StubModelService()

    async def post_message() -> httpx.Response:
        transport = httpx.ASGITransport(
            app=create_app(model_service, StubRetrievalService([]))
        )
        async with httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        ) as client:
            return await client.post("/api/chat", json={"message": "Ukjent tema"})

    response = asyncio.run(post_message())

    assert response.status_code == 200
    assert response.json()["sources"] == []
    assert "ingen relevant informasjon" in response.json()["answer"]
    assert model_service.prompt is None


def test_missing_real_knowledge_returns_setup_error_without_fixture_fallback(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("OUTWISE_KNOWLEDGE_PATH", str(tmp_path / "missing.json"))
    monkeypatch.setenv("OUTWISE_KNOWLEDGE_MODE", "real")
    model = StubModelService()

    async def post_message():
        transport = httpx.ASGITransport(app=create_app(model))
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.post("/api/chat", json={"message": "Jeg har gått meg vill"})

    response = asyncio.run(post_message())
    assert response.status_code == 503
    assert "kunnskapsbasen" in response.json()["detail"]
    assert model.prompt is None


def test_real_source_owner_license_and_reuse_notice_survive_api():
    retriever = StubRetrievalService()
    from dataclasses import replace
    item = replace(retriever.results[0].item, source_name="CDC", source_url="https://www.cdc.gov/example",
                   license="CDC public domain", metadata={"content_owner": "CDC", "retrieved_at": "2026-10-06",
                   "licence_url": "https://www.cdc.gov/other/agencymaterials.html"})
    retriever.results = [RetrievedKnowledgeItem(item=item, score=1)]

    async def post_message():
        transport = httpx.ASGITransport(app=create_app(StubModelService(), retriever))
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.post("/api/chat", json={"message": "Vann"})

    source = asyncio.run(post_message()).json()["sources"][0]
    assert source["content_owner"] == "CDC"
    assert source["retrieved_at"] == "2026-10-06"
    assert source["license"] == "CDC public domain"
    assert "gratis" in source["notice"] and "HHS" in source["notice"]
