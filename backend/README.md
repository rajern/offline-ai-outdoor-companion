# Outwise backend

The backend exposes the local HTTP API used by the Outwise frontend. It also
contains dedicated services for local Qwen inference and local knowledge
retrieval, coordinated by a small RAG orchestrator. Safety integration is a
separate later task.

## Setup (Windows PowerShell)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
```

## Run

```powershell
.\.venv\Scripts\python -m uvicorn outwise.main:app --reload
```

Verify the API from another PowerShell window:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

The response should be `{"status":"ok"}`.

The local chat boundary is `POST /api/chat`:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/chat `
  -ContentType "application/json" -Body '{"message":"Jeg har gått meg vill."}'
```

The response contains an `answer` and a `sources` list. Source titles, names and
URLs come directly from retrieved knowledge metadata, never from model output.
If retrieval finds no relevant fixture, the API returns an explicit unsupported
answer with no sources and does not call the model. Model setup, loading, timeout
and generation failures are returned as explicit HTTP errors.

## Local model service

First complete the model setup described in `../docs/MODEL_SETUP.md`. Backend
code can then call the local model without depending on llama.cpp command-line
details:

```python
from outwise.services.model import ModelService

answer = ModelService().generate("Reply briefly: what should I prioritize?")
```

The defaults use `../models/Qwen_Qwen3.5-2B-Q4_K_M.gguf` and discover the
installed llama.cpp runtime. `OUTWISE_MODEL_PATH` and `OUTWISE_LLAMA_CLI` can
override those paths. Missing assets, model loading failures, timeouts and
generation failures are exposed as distinct `ModelServiceError` subclasses.

The HTTP chat route uses this service while keeping llama.cpp details outside the
route and frontend.

## Local retrieval service

`RetrievalService` loads the normalized JSON knowledge contract and ranks chunks
with a deterministic BM25-style lexical score. It has no model, UI, source-format
or network dependency:

```python
from outwise.services.retrieval import RetrievalService

retriever = RetrievalService.from_json("../knowledge/fixtures/development-knowledge.json")
results = retriever.retrieve("How should I treat drinking water?", top_k=3)
```

Each result contains the original `KnowledgeItem` with all source metadata plus
its score. Blank queries and non-positive `top_k` values raise `ValueError`; a
query with no lexical overlap returns an empty list. The current lexical method
is intentionally small and replaceable, and may miss cross-language queries or
semantic matches that use entirely different vocabulary.

The normal request flow currently loads
`../knowledge/fixtures/development-knowledge.json`. Set
`OUTWISE_KNOWLEDGE_PATH` to another normalized version-1 knowledge JSON file to
override it locally. Fixture content is development data, not production advice.

## Test

```powershell
.\.venv\Scripts\python -m pytest
```
