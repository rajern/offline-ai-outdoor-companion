from typing import Protocol

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field, field_validator

from outwise.services.model import (
    ModelGenerationError,
    ModelLoadError,
    ModelNotFoundError,
    ModelRuntimeNotFoundError,
    ModelTimeoutError,
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)

    @field_validator("message")
    @classmethod
    def normalize_message(cls, value: str) -> str:
        message = value.strip()
        if not message:
            raise ValueError("message must not be blank")
        return message


class ChatResponse(BaseModel):
    answer: str


class ModelGenerator(Protocol):
    def generate(self, prompt: str) -> str: ...


router = APIRouter(prefix="/api", tags=["chat"])


def get_model_service(request: Request) -> ModelGenerator:
    return request.app.state.model_service


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    model_service: ModelGenerator = Depends(get_model_service),
) -> ChatResponse:
    try:
        answer = model_service.generate(request.message)
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

    return ChatResponse(answer=answer)
