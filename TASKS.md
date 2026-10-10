# Outwise — Tasks

This file contains the active implementation tasks.

Only near-term work should live here.  
Completed work may be archived or removed as the project progresses.

---

# Milestone 1 — Foundation + Local AI

## M1-01 — Scaffold frontend

**Dependencies:** None

Create the Expo + React Native + TypeScript frontend with web support.

Requirements:
- project runs locally on Windows
- mobile-first layout
- basic placeholder chat screen
- no AI logic in the frontend

**Done when:**
- frontend starts successfully
- app renders in the browser
- layout works at phone-sized width

---

## M1-02 — Scaffold backend

**Dependencies:** None

Create the Python + FastAPI backend.

Requirements:
- simple health endpoint
- basic project structure following `ARCHITECTURE.md`
- no model integration yet

**Done when:**
- backend starts locally
- health endpoint responds successfully

---

## M1-03 — Connect frontend and backend

**Dependencies:** M1-01, M1-02

Create the minimal API boundary between the frontend and backend.

Requirements:
- frontend can send a message
- backend can return a temporary/mock response
- loading and basic error states work

**Done when:**
- a message entered in the UI reaches FastAPI
- the returned response appears in the chat

---

## M1-04 — Local model setup

**Dependencies:** None

Set up local inference with:

- Qwen3.5-2B
- Q4_K_M
- GGUF
- llama.cpp

Create the minimum scripts/instructions required to obtain and run the model locally.

Do not commit the model file to Git.

**Done when:**
- the model can be downloaded/setup reproducibly
- a local prompt produces a valid response without internet access

---

## M1-05 — Implement ModelService

**Dependencies:** M1-04

Connect the backend to the local model through a dedicated model service.

Requirements:
- llama.cpp-specific logic remains behind the model service
- backend can submit a prompt and receive generated text
- useful model/loading errors are surfaced

**Done when:**
- FastAPI can obtain a real response from the local Qwen model

---

## M1-06 — Complete local AI vertical slice

**Dependencies:** M1-03, M1-05

Replace the mock response with real local inference.

Flow:

    User
      ↓
    Mobile-first UI
      ↓
    FastAPI
      ↓
    ModelService
      ↓
    Local Qwen model
      ↓
    Response in UI

**Done when:**
- user can chat with the local model through the frontend
- the full flow works with internet disabled after setup
- no cloud AI/API is used
- major setup and runtime errors are handled clearly


# Milestone 2 — RAG + Real Knowledge Base

## M2-01 — Define knowledge fixtures and data contract

**Dependencies:** M1-06

Create a small development knowledge set using synthetic or clearly reusable fixture content.

Requirements:
- follow the common structure defined in `docs/DATA.md`
- include source metadata with every item
- cover several MVP knowledge areas
- keep fixture data intentionally small

**Done when:**
- fixture knowledge can be loaded reproducibly
- every item contains the required source metadata
- no unverified external copyrighted content is committed

---

## M2-02 — Implement local retrieval

**Dependencies:** M2-01

Implement the local retrieval layer.

Requirements:
- retrieve relevant knowledge chunks from the local knowledge store
- keep retrieval logic separate from the model service
- return both retrieved text and source metadata
- remain fully local and offline

**Done when:**
- a query returns relevant fixture chunks
- source identity is preserved
- retrieval can be called independently from the LLM

---

## M2-03 — Integrate RAG into the request flow

**Dependencies:** M2-02, M1-06

Connect retrieval to the orchestrator and local model.

Expected flow:

    User
      ↓
    Orchestrator
      ↓
    Retrieval
      ↓
    Relevant chunks + source metadata
      ↓
    Local Qwen model
      ↓
    Natural answer + sources

Requirements:
- the model receives only the relevant retrieved context
- the model may combine several retrieved chunks into one natural response
- displayed sources must come from stored metadata, not generated URLs or citations

**Done when:**
- the user can ask a question through the UI
- relevant local knowledge is retrieved
- Qwen uses the retrieved context
- the UI displays the supporting sources
- the full flow works offline

---

## M2-04 — Approve real knowledge sources

**Status:** Complete — owner approved the 22-URL source manifest on 2026-10-06.

**Dependencies:** M2-03

**Human approval checkpoint**

The final knowledge sources must be researched, reviewed and approved by the project owner before ingestion work begins.

Do not autonomously select or approve the final source set.

The approved source documentation should record:
- source and URL
- intended knowledge coverage
- authority/reliability
- licence and redistribution rights
- attribution requirements
- language
- ingestion method

Codex must not begin M2-05 until the project owner has explicitly approved and documented the final source set.

Prefer:
- downloadable datasets
- structured APIs
- manuals or document collections
- sources that can be ingested automatically

Avoid large manual copy/paste or article-by-article scraping workflows.

**Done when:**
- the final source set for the MVP is documented
- licence/usage status is recorded for every selected source
- required attribution is known
- the selected sources cover the intended MVP knowledge areas sufficiently
- the project owner has explicitly approved the documented source set

---

## M2-05 — Build ingestion for approved sources

**Status:** Complete — frozen ingestion, local embedding assets and offline rebuild verified on 2026-10-06.

**Dependencies:** M2-04

Create reproducible ingestion pipelines for the approved real sources.

Requirements:
- convert each source into the common Outwise data contract
- preserve provenance and licence metadata
- automate parsing, normalization and chunking
- generate the required local retrieval assets
- keep source-specific logic outside the retrieval layer

**Done when:**
- the real knowledge base can be rebuilt from approved sources without manual copy/paste
- the output follows the Outwise data contract
- provenance is preserved throughout the pipeline

---

## M2-06 — Replace fixtures with the real knowledge base

**Dependencies:** M2-05

**Status:** In progress — real-KB integration is implemented, but answer-quality
validation is blocked. Technical tests pass; manual checks found irrelevant
retrieved context and unsupported or garbled Norwegian answers. See
`docs/KNOWLEDGE_SETUP.md`. Do not mark complete or begin M3 yet.

Judge validation subtask completed on 2026-10-08: v2 rules, locking/recovery,
15 synthetic stress examples and 45 saved historical contexts. See
`evals/retrieval_judge_validation_report.v2.md`. Owner review of remaining
scoring issues is required before retrieval optimization; M2-06 remains open.

The owner subsequently authorized the unchanged 25-case optimization foundation
and scorer corrections. V3 targeted calibration passed (22 rows, 19 unique judge
calls, three cache hits). Optimization stopped before phase A because Qwen Q4's
local runtime did not pass embedding repeatability. No configurations were run;
full experiment execution remains unfinished. See
`evals/retrieval_optimization_report.v1.md`. M2-06 is not complete.

Bounded Qwen stability follow-up passed with explicit CPU isolation, including the
unchanged original check in a new process and stable synthetic top-k membership.
See `evals/qwen_embedding_stability_report.v1.md`. No optimization was started;
full orchestration and resources remain unverified. M2-06 stays open.

The owner then authorized resuming all 31 configurations after technical checks.
A/B/C orchestration, memory guards and checked resume are implemented; 43 local
tests pass, including a mocked exact-31 driver. Real execution stopped before
phase A when MiniLM left only 244.6 MiB available RAM, below the frozen 256 MiB
reserve. No new judge calls or configurations were run. See
`evals/retrieval_optimization_report.v2.md`. Live full-flow validation, resource
capacity and finalist source review remain unverified; M2-06 stays open.

After the owner freed RAM, all three sequential model/resource/input probes
passed with the original limits. The 25 MiniLM contexts are saved; a one-line
source-default comparison correction preserves all 980 result-file hashes and
the original freeze in a separate audit layer. Thirteen orchestration tests
pass, including default/mutation checks. Phase A resumed without repeating
model probes/retrieval. No scoring, gold or model setting changed; M2-06 remains
open pending actual results and source review.

Phase A is now complete: 3/31 configurations, 25 cases each, 75 successful judge
calls and 714,931 reported subscription tokens. MiniLM/Gemma/Qwen micro25 is
77.8%/70.8%/51.4%, with 14/13/10 complete supported cases. Final integrity checks
of all 75 cached results passed without inference. Stage choice stopped because
per-item safety tradeoffs prevent a dominating model; case 13 also needs semantic
review. B/C are not run, numeric thresholds are not calculated, and no production
model/configuration is selected. See `evals/retrieval_optimization_report.v3.md`.
Owner review and a provisional phase B model choice are required. M2-06 remains
open; do not repeat completed A calls or start M3.

  On 2026-10-09 the owner selected MiniLM for B/C and approved exact-context
  adjudications for Gemma case 13 and MiniLM case 20/1. Original gold, judges,
  score files and all 309 phase-A artifacts remain unchanged. The separate
  continuation has 34 relevant passing tests and froze the four thresholds
  from 400 saved MiniLM scores. B-k3-none completed 25 judgments (22 new calls,
  three cache hits): 40/72 requirements, 8/22 complete, two misleading flags.
  Execution stopped at the original RAM guard: only 5.65 MiB available during
  scoring, versus a 256 MiB reserve. Integrity audit passes all 82 frozen files
  and the 25 new input/result/token bindings. 27 B/C configurations remain;
  no winner is selected. See `evals/retrieval_optimization_report.v4.md`.
  Resume completed calls from cache after the resource blocker is resolved.
  M2-06 remains open; holdout, production changes and answer generation excluded.

  Latest continuation, 2026-10-09: all 25 MiniLM B configurations / 625 judgments
  are complete; A+B totals 28/31. The original dominance gate blocks C. Best
  coverage is 58/72, macro 79.09%, 15/22 complete at k12/16 without threshold,
  versus adjusted A's 57/72, macro 77.95%, 15/22. Gain: adult breathing check
  08/2; full monitoring/CPR 08/4 and anaphylaxis 17/1–2 remain missing. Source
  review identifies unresolved case13/P70 risk negatives and case19 risk
  variability. Recommend k16/no threshold provisionally for C, subject to owner
  resolution of those findings and the protected experimental choice. One quota
  rejection was archived; resume followed natural renewal and a new owner
  instruction. Original limits, raw A/B results, gold, judge and production are
  preserved. See `evals/retrieval_optimization_report.v5.md`; only the three
  planned C configurations remain. M2-06 is still open.

  Current C stop, 2026-10-09: owner authorized MiniLM/k16/no threshold and the
  limited B-to-C dominance override. Three exact-input risk adjudications resolve
  case13/P70 and case19 in six B rows without coverage/gold/raw changes. All 25
  C-P1 judgments are saved: 24 new calls, one cache hit, 63/72 requirements,
  macro 85.23%, 17/22 complete. Original RAM guard failed after scoring: host
  available memory 52.42 MiB versus 256 MiB reserve; judge-tree peak 231.53 MiB
  versus 4 GiB limit. C-P2/P3 are not started; 29/31 configurations fully scored.
  P1 gains eight items but loses burn-treatment 07/1-3 and introduces a concrete
  anaphylaxis contact conflict. No final winner or control-test readiness. See
  `evals/retrieval_optimization_report.v6.md`. Resolve RAM and resume the same C
  continuation when instructed; preserve failed samples and reuse all completed
  calls. Six C tests and nine continuation tests passed. Offline audit passed
  all 725 results, 82 frozen identities and 2,912 protected A/B files; see
  `evals/retrieval_optimization_final_audit.v2.json`. M2-06 remains open;
  production, holdout, generation and extra experiments are excluded.

  Final development report, 2026-10-10: all 31 planned configurations / 775
  judgments completed on 2026-10-09. P1 was preserved; P2 reused 25 exact B16
  results, P3 used 15 new calls / ten cache hits. P2/P3 resources passed;
  P1's historical RAM failure remains failed. Audit v3 verifies all 775 inputs,
  82 identities, 2,912 A/B files and 103 unchanged P1 files. Provisional
  development recommendation: MiniLM/k16/no threshold/P3, 59/72, macro 80.23%,
  15/22 complete. P1's 63/72 aggregate conceals burn regressions and anaphylaxis
  conflict. P3 still lacks 13 supported requirements, so further retrieval
  improvement is recommended before the control test. No production winner
  or automatic C dominance choice. Total: 228 successful new judge calls,
  547 cache hits, 2,126,482 reported subscription tokens; one historical failed
  attempt has unknown usage. See `evals/retrieval_optimization_report.v7.md`.
  Stop at the agreed 31 configurations. M2-06 remains open for product/safety
  acceptance; new experiments, holdout, production and generation need separate
  authorization. Older execution statuses above remain historical.

Replace development fixtures in the main RAG flow with the approved Outwise knowledge base.

Requirements:
- keep fixtures available for testing
- use the real knowledge base in the normal application flow
- verify retrieval across the main MVP knowledge areas
- verify that source metadata is shown correctly

**Done when:**
- the application answers using the real local knowledge base
- sources are displayed correctly
- the knowledge base and retrieval flow work with internet disabled
- no unapproved source material is required for the MVP

### Human quality review

After the technical implementation is complete, stop for a manual product review before Milestone 3 begins.

The project owner should test representative real-world questions and review:
- retrieval relevance
- answer quality
- source correctness
- obvious knowledge gaps

Do not begin Milestone 3 until this review has been explicitly approved.

---

# Milestone 3 — Safety + Finished MVP

## M3-01 — Implement the safety layer

**Dependencies:** M2-06

**Human approval checkpoint**

Before implementing the safety layer, define the proposed safety rules and behaviour for the main high-risk situations.

Present the proposed rules to the project owner for review.

Do not implement the final safety behaviour until the project owner has explicitly approved the policy.

Implement the first explicit safety layer outside the LLM itself.

Requirements:
- detect situations that require stronger safety handling
- prioritize emergency or professional help where appropriate
- avoid unsupported high-risk guidance
- surface uncertainty when reliable grounding is missing
- keep safety logic separate from model and retrieval implementations

**Done when:**
- safety handling can be triggered independently of the LLM prompt
- high-risk scenarios receive the intended safety treatment
- unsupported answers are not silently presented as confident guidance

---

## M3-02 — Add safety and legal messaging

**Dependencies:** M3-01

**Human approval checkpoint**

Codex may draft the safety and legal messaging, but the final wording must be reviewed and explicitly approved by the project owner before it is treated as complete or shown as final product copy.

Add clear product messaging about the intended use and limitations of Outwise.

Requirements:
- explain that Outwise is an information and preparedness tool
- clarify that it is not a replacement for emergency services or professional medical help
- make important limitations visible without blocking normal use
- include appropriate source and attribution information where required

**Done when:**
- safety/legal messaging is visible in the relevant parts of the product
- the wording is consistent with `docs/PRODUCT.md` and `docs/DECISIONS.md`
- no feature is presented as providing guaranteed medical or emergency outcomes

---

## M3-03 — Refine the mobile-first product experience

**Dependencies:** M2-06

Turn the technical application into a coherent Outwise experience.

Requirements:
- refine the phone-sized layout
- add the agreed scenario shortcuts
- improve chat, source display, loading and error states
- keep the interface simple and usable under stress
- avoid adding post-MVP features

**Done when:**
- the main user flows are clear without explanation
- the UI works well at phone-sized dimensions
- answers and supporting sources are easy to inspect

---

## M3-04 — Add offline readiness and reliability checks

**Dependencies:** M3-01, M3-03

Make offline operation explicit and testable.

Requirements:
- clearly indicate whether required local assets are available
- fail clearly if model or knowledge assets are missing
- verify that the normal user flow has no hidden internet dependency
- test the application with internet access disabled

**Done when:**
- the application clearly reports its offline-ready state
- the full core flow works with internet disabled
- missing assets produce understandable errors rather than silent failures

---

## M3-05 — Validate core MVP scenarios

**Dependencies:** M3-01, M3-04

Run the completed system through representative scenarios from the MVP scope.

Include examples covering:
- injury / basic first aid
- getting lost
- cold or exposure
- shelter / warmth
- water / hygiene
- emergency signalling
- unsupported or uncertain questions

Focus on:
- retrieval relevance
- grounding
- source correctness
- safety behaviour
- clarity of the final response

**Done when:**
- the main MVP scenarios work end to end
- obvious retrieval or safety failures are fixed
- sources shown to the user match the retrieved source metadata
- known limitations are documented

### Human product review

After automated and technical validation, the project owner should manually test the finished core scenarios and review the product from an end-user perspective.

Any major issues found should be resolved before M3-06 is completed.

---

## M3-06 — Prepare the public MVP

**Dependencies:** M3-05

Prepare Outwise as a complete public learning project.

Requirements:
- clean up setup and run instructions
- update README with the final MVP behaviour
- document model and knowledge setup
- document important limitations
- ensure the public repository contains no prohibited or unlicensed assets
- add a simple demo or screenshots if useful

**Done when:**
- a new developer can understand and run the project from the repository
- the repository accurately reflects the finished MVP
- the MVP is ready to demonstrate publicly
- all three milestones are complete

### Final approval

**Human approval checkpoint**

Codex may prepare the repository and MVP for release, but must not treat the project as finally approved or release-ready until the project owner has completed the final review and explicitly approved it.


---
# Parallelization

The following work can initially run in parallel:

- `M1-01` Frontend
- `M1-02` Backend
- `M1-04` Local model setup

After these are complete:

- `M1-03` depends on frontend + backend
- `M1-05` depends on model setup
- `M1-06` integrates both tracks

Do not begin Milestone 2 tasks until the Milestone 1 vertical slice works end to end.
