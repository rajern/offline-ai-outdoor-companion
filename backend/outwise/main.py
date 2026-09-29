from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from outwise.routes.chat import router as chat_router
from outwise.routes.health import router as health_router
from outwise.services.model import ModelService
from outwise.services.orchestrator import (
    KnowledgeRetriever,
    ModelGenerator,
    Orchestrator,
    knowledge_path_from_environment,
)
from outwise.services.retrieval import RetrievalService


def create_app(
    model_service: ModelGenerator | None = None,
    retrieval_service: KnowledgeRetriever | None = None,
) -> FastAPI:
    app = FastAPI(title="Outwise API", version="0.1.0")
    resolved_model_service = model_service or ModelService()
    resolved_retrieval_service = retrieval_service or RetrievalService.from_json(
        knowledge_path_from_environment()
    )
    app.state.orchestrator = Orchestrator(
        resolved_retrieval_service, resolved_model_service
    )
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
