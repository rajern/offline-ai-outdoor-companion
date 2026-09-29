# Outwise backend

The backend exposes the local HTTP API used by the Outwise frontend. It also
contains a dedicated `ModelService` for local Qwen inference through llama.cpp.
Retrieval and safety integrations are not part of this milestone.

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

The temporary chat boundary is `POST /api/chat`:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/chat `
  -ContentType "application/json" -Body '{"message":"Jeg har gått meg vill."}'
```

The response contains an `answer` field. The mock implementation is replaced by local model inference in a later task while retaining this HTTP contract.

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

The HTTP chat route is connected to this service in M1-06.

## Test

```powershell
.\.venv\Scripts\python -m pytest
```
