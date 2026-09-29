from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from outwise.routes.chat import router as chat_router
from outwise.routes.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(title="Outwise API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type"],
    )
    app.include_router(health_router)
    app.include_router(chat_router)
    return app


app = create_app()
