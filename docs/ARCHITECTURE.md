# Outwise — Architecture

## Goal

Outwise should be simple to develop quickly, while keeping the AI, retrieval, safety and UI layers clearly separated.

The first MVP runs locally on a Windows PC, but the frontend is designed mobile-first and the core boundaries should make a later mobile implementation possible without redesigning the product.

## High-level flow

    User
      ↓
    Mobile-first UI
      ↓
    Application API
      ↓
    Orchestrator
      ├── Safety
      ├── Retrieval
      └── Local Model
      ↓
    Response + Sources

## Frontend

**Technology**
- Expo
- React Native
- TypeScript
- Web target for the PC MVP

Responsibilities:
- chat interface
- scenario shortcuts
- follow-up interaction
- source display
- offline-ready/status UI
- loading and error states

The frontend should not contain model, retrieval or safety logic.

It communicates with the backend through a small, explicit API.

## Backend

**Technology**
- Python
- FastAPI

The backend owns all AI-related behaviour for the PC MVP.

Main logical components:

### Orchestrator

Coordinates one user request.

Responsibilities:
1. Receive the user message and relevant conversation context.
2. Run required safety checks.
3. Request relevant knowledge from retrieval.
4. Construct model context.
5. Call the local model.
6. Return the final answer and source metadata.

The orchestrator should contain workflow logic, not low-level implementation details.

### Model service

Responsibilities:
- load and manage the local model
- call llama.cpp
- generate responses
- expose a simple inference interface to the orchestrator

Initial model:
- Qwen3.5-2B
- Q4_K_M
- GGUF
- llama.cpp

The rest of the application should not depend directly on llama.cpp-specific details.

### Retrieval service

Responsibilities:
- accept a search/query
- retrieve relevant knowledge chunks
- return the most relevant content together with source metadata

The retrieval implementation should remain replaceable without changing the UI or model service.

### Knowledge store

Stores normalized knowledge used by retrieval.

Each knowledge item must follow the common data contract defined in `DATA.md`.

The store may contain:
- text chunks
- embeddings
- source metadata
- search indexes

Exact storage implementation can be chosen during implementation as long as it remains fully local.

### Safety layer

Safety is separate from the LLM itself.

Responsibilities include:
- detecting situations requiring stronger safety handling
- prioritizing emergency/professional assistance where appropriate
- preventing unsupported high-risk guidance
- ensuring uncertainty is surfaced when reliable grounding is unavailable

Safety rules may influence both the context given to the model and the final response.

The MVP should keep this layer simple and explicit rather than building a complex rules engine.

## Knowledge ingestion

Knowledge ingestion happens outside the normal user request flow.

    Approved source
      ↓
    Ingestion
      ↓
    Normalize
      ↓
    Chunk
      ↓
    Generate embeddings
      ↓
    Local knowledge store

Source-specific ingestion logic should only be responsible for converting source data into the common Outwise data format.

Retrieval should not care whether a source originally came from JSON, PDF, API or another supported format.

## Local assets

The application depends on local assets such as:
- GGUF model
- embedding model if required
- knowledge database
- generated embeddings/indexes

Large generated assets should not be committed directly to Git.

Setup scripts should make it possible to prepare the required local environment.

For a future mobile version, these assets should be downloadable as a separate offline package after initial app installation.

## Future device tools

Future mobile capabilities should be exposed through simple interfaces such as:
- `LocationProvider`
- `CompassProvider`
- `BatteryProvider`

These are not part of the MVP.

The orchestrator may later consume information from these providers without changing the rest of the architecture.

## Mobile transition

The React Native frontend should remain reusable for a later iOS or Android version.

The current FastAPI/Python backend is specific to the PC MVP.

A future mobile version would replace the backend implementation with local mobile equivalents for:
- model inference
- retrieval
- storage
- safety/orchestration

The interfaces and expected behaviour should remain conceptually the same.

## Architecture principles

- Keep the system local-first.
- No cloud dependency for the core user flow.
- Prefer simple modules over unnecessary abstraction.
- Keep implementation details behind clear interfaces.
- Avoid coupling the UI directly to AI infrastructure.
- Avoid coupling retrieval directly to specific data sources.
- Do not introduce distributed services or complex infrastructure.
- Optimize for rapid agentic development and easy replacement of individual components.