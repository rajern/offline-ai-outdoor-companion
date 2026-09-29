import asyncio

import httpx

from outwise.main import create_app


def test_chat_endpoint_returns_mock_answer() -> None:
    async def post_message() -> httpx.Response:
        transport = httpx.ASGITransport(app=create_app())
        async with httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        ) as client:
            return await client.post(
                "/api/chat", json={"message": "  Jeg har gått meg vill.  "}
            )

    response = asyncio.run(post_message())

    assert response.status_code == 200
    assert response.json() == {
        "answer": (
            "Meldingen din ble mottatt av Outwise. "
            "Dette er et midlertidig svar mens den lokale modellen kobles til."
        )
    }


def test_chat_endpoint_rejects_blank_message() -> None:
    async def post_message() -> httpx.Response:
        transport = httpx.ASGITransport(app=create_app())
        async with httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        ) as client:
            return await client.post("/api/chat", json={"message": "   "})

    response = asyncio.run(post_message())

    assert response.status_code == 422


def test_chat_endpoint_allows_local_frontend_origin() -> None:
    async def preflight() -> httpx.Response:
        transport = httpx.ASGITransport(app=create_app())
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
