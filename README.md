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

Completed:

**Milestone 1 — Foundation + Local AI**

The mobile-first web UI, FastAPI backend and local Qwen inference now work end
to end. Milestone 2 (local RAG and the real knowledge base) has not started.

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
- [`TASKS.md`](TASKS.md) — implementation tasks
- [`AGENTS.md`](AGENTS.md) — instructions for coding agents

## Safety

Outwise is an information and preparedness tool.

It is not a replacement for emergency services, professional medical care or expert judgement.

## Mobile

The first MVP runs locally on PC, but the interface is designed for phone-sized screens using React Native so the project can later be adapted for iOS or Android.
