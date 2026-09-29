# Outwise backend

The backend exposes the local HTTP API used by the Outwise frontend. Model,
retrieval, and safety integrations are intentionally not part of this initial
scaffold.

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

## Test

```powershell
.\.venv\Scripts\python -m pytest
```
