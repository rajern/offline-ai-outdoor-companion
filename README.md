# Outwise

**Offline AI Outdoor Companion**

Outwise is a local-first AI project exploring whether a small language model combined with a curated knowledge base can provide useful outdoor guidance entirely offline.

The first MVP runs locally on Windows with a mobile-first interface.

## What it does

Outwise is designed for situations where internet access is unavailable and the user needs practical information quickly.

Initial use cases include:

- basic first aid and injuries
- getting lost
- cold exposure and sudden weather changes
- shelter and warmth
- water and hygiene
- emergency signalling
- other basic outdoor emergency situations

The user describes the situation in natural language. Outwise retrieves relevant local knowledge and generates a concise, source-grounded response.

## Stack

- **Frontend:** Expo, React Native, TypeScript
- **Backend:** Python, FastAPI
- **Local model:** Qwen3.5-2B, Q4_K_M, GGUF
- **Inference:** llama.cpp
- **Knowledge:** local RAG with source metadata
- **Cloud dependency:** none for the core product flow

## Project status

Milestone 1 is complete: the mobile-first web UI, FastAPI backend and local Qwen
inference work end to end. The project owner approved 22 real knowledge URLs
on 2026-10-06. Their text is ingested locally with frozen snapshots, provenance,
licence metadata and multilingual retrieval. The normal RAG flow uses these
assets; synthetic fixtures remain available for tests.

M2-05 is complete. M2-06 integration is implemented, but answer-quality checks
found irrelevant context and unsupported or garbled Norwegian advice. It is
not complete or suitable for real outdoor decisions. Milestone 2 also requires
an owner quality review before Milestone 3. Safety policy, final product
messaging and release approval remain separate checkpoints.

## Local setup

Follow `backend/README.md`, `frontend/README.md` and `docs/MODEL_SETUP.md`.
Then run `.\scripts\setup-knowledge.ps1` from the repository root to prepare
the approved offline knowledge assets. `docs/KNOWLEDGE_SETUP.md` explains
offline rebuilds, source reuse requirements and quality review.

The project is planned in three milestones:

1. Foundation + Local AI
2. RAG + Real Knowledge Base
3. Safety + Finished MVP

## Documentation

- [`docs/PRODUCT.md`](docs/PRODUCT.md) — product scope
- [`docs/DECISIONS.md`](docs/DECISIONS.md) — locked decisions
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — system architecture
- [`docs/DATA.md`](docs/DATA.md) — knowledge and data strategy
- [`docs/PLAN.md`](docs/PLAN.md) — milestone plan
- [`docs/MODEL_SETUP.md`](docs/MODEL_SETUP.md) — local model installation and prompt test
- [`docs/KNOWLEDGE_SETUP.md`](docs/KNOWLEDGE_SETUP.md) — approved sources, ingestion and offline retrieval
- [`TASKS.md`](TASKS.md) — implementation tasks
- [`AGENTS.md`](AGENTS.md) — instructions for coding agents

## Safety

Outwise is an information and preparedness tool.

It is not a replacement for emergency services, professional medical care or expert judgement.

## Mobile

The first MVP runs locally on PC, but the interface is designed for phone-sized screens using React Native so the project can later be adapted for iOS or Android.
