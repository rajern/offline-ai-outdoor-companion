# Outwise backend

Python/FastAPI owns retrieval, context packing and local generation. The normal
application is a **learning prototype**, not a safety-approved outdoor assistant.
See [scope](../docs/PROTOTYPE.md) and [results](../docs/RESULTS.md).

## Setup and run (PowerShell, repository root)

```powershell
python -m venv backend/.venv
backend/.venv/Scripts/python.exe -m pip install -e './backend[dev]'
.\scripts\setup-local-model.ps1
.\scripts\setup-knowledge.ps1
.\scripts\start-outwise.ps1
```

The startup script serves the exported frontend and API at
`http://127.0.0.1:8000`. Models and knowledge load only on a live question.
`/?demo=1` replays selected saved tests without loading those assets.
For API-only development:

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn outwise.main:app --host 127.0.0.1 --port 8000
```

Stop with Ctrl+C; the backend closes its owned llama.cpp process. The subprocess
binds numeric loopback and uses CPU inference, local assets and offline flags.

## Request and response

`GET /health` reports API liveness only. `GET /api/status` checks whether expected
local files/runtime executables are present; their integrity is checked when
used. Neither endpoint certifies answer quality or physical offline operation.

`POST /api/chat` accepts `{"message":"..."}`. Each question is independent; the
backend receives no chat history. The response contains:

- `answer`: the generated interpretation, or an explicit unavailability message.
- `sources`: stored title/publisher/URL/reuse metadata and exact excerpt IDs,
  text, section and language. These do not come from generated citations.
- Optional `generation_error`: interpretation could not be generated.
- Optional `context_notice`: raw hits are shown because packing could not be
  completed; the model was not run. This is not mislabeled as a knowledge gap.

A missing knowledge store returns an explicit503 setup error without fixture
fallback. Generation failures after retrieval preserve source access. Empty
retrieval skips generation. A nonempty search can still be irrelevant: the
measured top-16/no-threshold profile does not solve safe abstention.

## Application components

- `knowledge/window_index.py`: portable full-body MiniLM window index.
- `services/context.py`: original P3 expansion/deduplication and fixed budget.
- `services/native_model.py`: owned llama.cpp server, native prompt serialization,
  input limit and later Qwen baseline generation settings.
- `services/orchestrator.py`: coordinates the request and keeps source provenance.

The original `SemanticRetrievalService`, lexical fixture retriever, legacy
`ModelService` and legacy prompt remain for existing tests and historical
reference. They are not the normal prototype profile. Evaluation runners are
archived and are not application dependencies.

Settings still support `OUTWISE_MODEL_PATH`, `OUTWISE_LLAMA_CLI` and
`OUTWISE_KNOWLEDGE_PATH`. The pinned llama.cpp installation must contain
`llama-cli`, `llama-server` and `llama-tokenize` beside each other. Knowledge setup
creates both the original index and the separate `prototype-index.json` /
`prototype-embeddings.npy`; existing original files are not silently replaced.
For explicit synthetic fixture development, use `OUTWISE_KNOWLEDGE_MODE=fixtures`.
This is not real advice or the measured profile.

## Checks

```powershell
backend/.venv/Scripts/python.exe -m pytest backend/tests -q
backend/.venv/Scripts/python.exe scripts/verify-prototype.py
```

The second command is an optional comparison with the original private frozen
inputs. It requires that evidence, generates no answers and reads no holdout.
A fresh clone can run unit tests without private sources/models. See
[verification](../docs/VERIFICATION.md) for performed checks and their limits.
