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

## Test

```powershell
.\.venv\Scripts\python -m pytest
```
