# Outwise — Decisions

This file records the main project decisions that should not be changed casually during implementation.

## Product

- Product name: **Outwise**
- Description: **Offline AI Outdoor Companion**
- Primary use case: help users handle unexpected outdoor situations when internet access is unavailable.
- Initial focus: injuries, getting lost, cold/exposure, shelter, water, emergency signalling and similar outdoor situations.
- The first MVP is a learning-focused local PC application with a mobile-first interface.
- Mobile deployment is a later option, not an MVP requirement.

## Platform and application structure

- First development environment: **Windows PC**
- Frontend: **Expo + React Native + TypeScript**
- The frontend runs as a web application for the PC MVP.
- UI must remain mobile-first so it can later be reused for iOS/Android.
- PC backend: **FastAPI + Python**
- The UI and AI/backend layers must be separated through clear interfaces.

## Local AI

- Main model: **Qwen3.5-2B**
- Quantization: **Q4_K_M**
- Model format: **GGUF**
- Runtime: **llama.cpp**
- The model runs locally.
- No cloud LLM/API is required for the core product.
- Users do not choose between models in the MVP.

## Retrieval and knowledge

- The MVP uses **local RAG**.
- Safety-critical factual knowledge should come from curated sources rather than relying on model memory alone.
- Retrieved content must preserve source metadata so answers can show real supporting sources.
- The knowledge system must be source-independent through a common data contract.
- Exact production datasets and documents are selected later through a dedicated data step.
- Large model files, generated knowledge databases and copyrighted source material should not be committed to the public repository unless their licences explicitly allow it.

## Safety and legal

- Outwise is an information and preparedness tool, not a medical professional or emergency service.
- Safety logic is a separate system concern and must not rely solely on the LLM prompt.
- Potential emergencies should prioritize professional/emergency assistance where available.
- The app should communicate uncertainty rather than invent unsupported guidance.
- Legal/licensing review is required before public distribution of real knowledge content.

## Installation and offline behaviour

- The final mobile concept uses a two-stage installation:
  1. Small application install.
  2. Separate offline package containing model and knowledge assets.
- The product must clearly indicate whether it is **offline ready**.
- For the PC MVP, all core functionality must work without internet once local assets are installed.

## MVP scope

The MVP is built in three milestones:

1. **Foundation + Local AI**
2. **RAG + Real Knowledge Base**
3. **Safety + Finished MVP**

## Deferred until after MVP

The following are intentionally postponed:

- fine-tuning
- larger models such as 4B
- GPS
- compass
- battery/device tools
- offline maps
- live weather
- camera/image analysis
- plant/mushroom identification
- satellite communication
- multiple user-selectable models
- Android/iOS distribution

These should only be added if the completed MVP gives a concrete reason to add them.

## Development philosophy

- Prefer the simplest implementation that satisfies the architecture.
- Do not redesign locked decisions during implementation unless a concrete technical blocker is discovered.
- Keep components replaceable where practical, especially model inference, retrieval and future mobile implementations.
- Optimize for rapid agentic development and a working end-to-end system rather than unnecessary abstraction.