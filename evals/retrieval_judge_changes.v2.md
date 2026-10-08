# Judge v2 changes — bounded owner-authorized validation

The owner selected GPT-6.1 Sol / Codex CLI / Medium / ChatGPT subscription on
2026-10-08. This changes the provisional choice from the v1 recommendation;
it authorizes judge stress testing and the nine remaining historical questions,
not retrieval optimization, new development gold, production or holdout use.

V1 prompt, schema, runner, gold, references and pilot results remain unchanged.
V2 distinguishes relevant/optional, irrelevant, potentially misleading and
directly contradictory advice. Preserved other-age/severity/scenario headings
make advice ordinarily irrelevant rather than automatically risky. Misleading
requires a concrete wrong current-scenario action, lost condition or applicable
conflict. A missing must-have alone is a coverage failure, not a noise finding.
Contradiction is an explicit subset of misleading; categories can overlap.
Actual foreign law/service/procedure is distinct from foreign publisher identity.
Case 07's cream/ointment exception and corpus-gap handling remain intact.

Whole-conjunction coverage explicitly includes the distinction between calling
113 and receiving guidance. Separate applicable contradictory advice does not
erase a genuinely present required fact; conflict remains a separate safety
metric. Genuine unresolved meaning/applicability blocks final scoring.

These are evaluation classification rules, not a new product safety policy.
Old noise labels were written under broader wrong-scenario-risk interpretations;
disagreement with those references does not automatically show a v2 error.
Stress examples used for prompt design/calibration are not independent validation.

The CLI runtime uses a process-released file lock, pre-call intent, durable JSONL
stdout/stderr, recorded usage from every completed turn and recovery without
new inference. An incomplete call never becomes an automatic retry. One global
active-call journal prevents a crashed call being forgotten by another v2 run.
The archived v1 runner has no lock and must not be launched alongside v2.

Before historical validation, prompt/schema/settings/code/test and source hashes
are frozen. No changes from validation outcomes are allowed in the same version.
CLI server model/revision remains unavailable in JSONL: explicit requested ID,
catalog support, Medium setting, CLI version and ChatGPT auth are verified.
No OpenAI API calls or key loading are part of v2.
