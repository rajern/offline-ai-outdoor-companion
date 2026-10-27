from typing import Literal

from fastapi import APIRouter, Request
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: Literal["ok"]


router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get('/api/status')
def local_status(request: Request):
    """Passive file availability, not a quality or OS-offline certification."""
    from outwise.services.orchestrator import knowledge_path_from_environment
    from outwise.services.model import ModelServiceError
    model = request.app.state.model_service
    if not request.app.state.prototype:
        return {'mode': 'fixtures', 'assets_present': False, 'knowledge_present': True,
                'model_present': False, 'message': 'Syntetiske utviklingsdata. Ikke ekte turveiledning.'}
    local = knowledge_path_from_environment().parent
    knowledge = all((local / name).is_file() for name in
                    ('knowledge.json', 'prototype-index.json', 'prototype-embeddings.npy', 'embedding-model/outwise-model.json'))
    available = model.settings.model_path.is_file()
    try:
        model.runtime('llama-server'); model.runtime('llama-tokenize')
    except ModelServiceError:
        available = False
    return {'mode': 'local', 'assets_present': knowledge and available,
            'knowledge_present': knowledge, 'model_present': available,
            'message': 'Lokale filer finnes. Kontrolleres ved bruk.' if knowledge and available
                       else 'Lokalt oppsett mangler filer. Se installasjonsveiledningen.'}
