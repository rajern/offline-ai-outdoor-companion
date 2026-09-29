import asyncio

import httpx
import pytest

from outwise.main import create_app
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


def test_chat_endpoint_returns_model_answer() -> None:
    model_service = StubModelService()

    async def post_message() -> httpx.Response:
        transport = httpx.ASGITransport(app=create_app(model_service))
        async with httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        ) as client:
            return await client.post(
                "/api/chat", json={"message": "  Jeg har gått meg vill.  "}
            )

    response = asyncio.run(post_message())

    assert response.status_code == 200
    assert response.json() == {"answer": "Prioriter varme og finn ly."}
    assert model_service.prompt == "Jeg har gått meg vill."


def test_chat_endpoint_rejects_blank_message() -> None:
    async def post_message() -> httpx.Response:
        transport = httpx.ASGITransport(app=create_app(StubModelService()))
        async with httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        ) as client:
            return await client.post("/api/chat", json={"message": "   "})

    response = asyncio.run(post_message())

    assert response.status_code == 422


def test_chat_endpoint_allows_local_frontend_origin() -> None:
    async def preflight() -> httpx.Response:
        transport = httpx.ASGITransport(app=create_app(StubModelService()))
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
        transport = httpx.ASGITransport(app=create_app(model_service))
        async with httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        ) as client:
            return await client.post("/api/chat", json={"message": "Hjelp"})

    response = asyncio.run(post_message())

    assert response.status_code == expected_status
    assert response.json()["detail"].startswith(expected_detail)
