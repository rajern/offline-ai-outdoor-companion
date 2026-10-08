from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field, field_validator
from outwise.knowledge.embeddings import KnowledgeAssetsError

from outwise.services.model import (
    ModelGenerationError,
    ModelLoadError,
    ModelNotFoundError,
    ModelRuntimeNotFoundError,
    ModelTimeoutError,
)
from outwise.services.orchestrator import Orchestrator


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)

    @field_validator("message")
    @classmethod
    def normalize_message(cls, value: str) -> str:
        message = value.strip()
        if not message:
            raise ValueError("message must not be blank")
        return message


class ChatSource(BaseModel):
    title: str
    name: str
    url: str
    license: str
    content_owner: str | None = None
    licence_url: str | None = None
    retrieved_at: str | None = None
    source_updated_at: str | None = None
    notice: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource] = Field(default_factory=list)


router = APIRouter(prefix="/api", tags=["chat"])


def get_orchestrator(request: Request) -> Orchestrator:
    return request.app.state.orchestrator


@router.post("/chat", response_model=ChatResponse, response_model_exclude_none=True)
def chat(
    request: ChatRequest,
    orchestrator: Orchestrator = Depends(get_orchestrator),
) -> ChatResponse:
    try:
        result = orchestrator.answer(request.message)
    except KnowledgeAssetsError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Den lokale kunnskapsbasen er ikke klar. Kjør scripts/setup-knowledge.ps1 og start backend på nytt.") from exc
    except (ModelNotFoundError, ModelRuntimeNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Den lokale modellen er ikke klar. "
                "Kjør modelloppsettet og start backend på nytt."
            ),
        ) from exc
    except ModelTimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Den lokale modellen brukte for lang tid. Prøv igjen.",
        ) from exc
    except (ModelLoadError, ModelGenerationError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Den lokale modellen kunne ikke lage et svar. "
                "Kontroller modelloppsettet og prøv igjen."
            ),
        ) from exc

    return ChatResponse(
        answer=result.answer,
        sources=[
            ChatSource(
                title=source.title,
                name=source.source_name,
                url=source.source_url,
                license=source.license,
                content_owner=source.content_owner,
                licence_url=source.licence_url,
                retrieved_at=source.retrieved_at,
                source_updated_at=source.source_updated_at,
                notice=source.notice,
            )
            for source in result.sources
        ],
    )
