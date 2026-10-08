import os

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
from outwise.services.semantic_retrieval import LocalKnowledgeRetriever


def create_app(
    model_service: ModelGenerator | None = None,
    retrieval_service: KnowledgeRetriever | None = None,
) -> FastAPI:
    app = FastAPI(title="Outwise API", version="0.1.0")
    resolved_model_service = model_service or ModelService()
    if retrieval_service is not None:
        resolved_retrieval_service = retrieval_service
    elif os.environ.get("OUTWISE_KNOWLEDGE_MODE", "real") == "real":
        resolved_retrieval_service = LocalKnowledgeRetriever(knowledge_path_from_environment())
    elif os.environ.get("OUTWISE_KNOWLEDGE_MODE") == "fixtures":
        resolved_retrieval_service = RetrievalService.from_json(knowledge_path_from_environment())
    else:
        raise ValueError("OUTWISE_KNOWLEDGE_MODE must be real or fixtures")
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
