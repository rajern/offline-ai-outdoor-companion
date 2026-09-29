# Outwise — Plan

## Goal

Build a working offline MVP as quickly as possible while keeping the architecture clean enough for later mobile deployment.

The project is divided into three milestones.

---

## Milestone 1 — Foundation + Local AI

Build the basic application and prove that local inference works end to end.

Scope:
- scaffold Expo + React Native + TypeScript frontend
- scaffold FastAPI + Python backend
- establish the frontend/backend API boundary
- integrate Qwen3.5-2B Q4_K_M through llama.cpp
- run inference fully locally
- build a simple mobile-first chat interface
- handle basic loading and error states
- create scripts/instructions for local model setup

### Exit criteria

- frontend and backend start locally
- user can send a message through the UI
- local Qwen model generates the response
- no cloud AI/API is used
- core flow works without internet once the model is installed

---

## Milestone 2 — RAG + Real Knowledge Base

Add grounded retrieval and replace development fixtures with the real Outwise knowledge base.

Scope:
- implement the common knowledge data contract
- create a small fixture dataset first
- implement local retrieval and source metadata
- connect retrieval to the orchestrator and local model
- return natural answers with supporting sources
- research and approve the real datasets/documents
- verify licences and attribution requirements
- build automated ingestion for approved sources
- generate the production local knowledge assets

### Exit criteria

- questions retrieve relevant local knowledge
- Qwen uses retrieved context when answering
- responses display real source metadata
- the final MVP knowledge sources are documented and licence-checked
- ingestion is reproducible without manual copy/paste
- the full RAG flow works offline

---

## Milestone 3 — Safety + Finished MVP

Turn the working technical system into a coherent and demonstrable Outwise MVP.

Scope:
- implement the initial safety layer
- prioritize emergency/professional help where appropriate
- handle unsupported or uncertain questions safely
- add product disclaimers and safety/legal messaging
- refine the mobile-first user experience
- add scenario shortcuts
- add clear offline-ready/status behaviour
- test complete offline operation
- fix major reliability and usability issues
- prepare the public GitHub project and demo

### Exit criteria

- the main product scenarios work end to end
- the application remains usable with internet disabled
- safety behaviour is explicit and testable
- unsupported answers do not silently fabricate guidance
- users can inspect supporting sources
- the UI is usable at phone-sized dimensions
- README contains working setup and demo instructions
- the MVP is ready to show publicly

---

## Post-MVP

Do not add these unless the completed MVP provides a clear reason:

- larger local models
- fine-tuning
- improved retrieval or reranking
- GPS and location context
- compass and battery information
- offline maps
- live or cached weather
- camera/image capabilities
- additional languages
- native iOS/Android deployment

Post-MVP work should be driven by observed limitations or real user interest rather than by adding features for their own sake.