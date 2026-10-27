# Outwise evaluation lock v1

Owner authorization, 2026-10-25: "ok kjør begge de trinnene takk" after the
six-step execution plan for locking evaluation and re-assessing saved retrieval.

The approved development rubric is the unchanged `answer_rubric.v1.json`, SHA256
`6333f84d343c529009b0f319a1119edb9437f8b6a047c07325bd4201658b5d1f`.
The evaluator is `gpt-6.1-sol`, requested effort `medium`, using the existing
ChatGPT-authenticated Codex CLI, isolated read-only/no-tools ephemeral sessions.
High produced no clear overall evaluation advantage in the completed paired
review and had approximately twice the median latency. This is a practical
development choice, not proof of evaluator accuracy or clinical validity.

Use the 63 required criteria of the 22 supported development cases as the common
fixed denominator. Four conditional criteria are inventoried separately; assess
whether their branch information is available without depending on a future
model answer. Five optional criteria never replace required information.
The three corpus gaps, including case14's two supported-subset criteria, remain
separate. Empty criteria are never an automatic success.

Equivalent meaning and unambiguous question context are valid. One complete valid
alternative is enough where the criterion permits alternatives. Preserve decisive
conditions, negations, ordering, time, units, actor and jurisdiction. A broad
instruction can cover a clearly included instance. Do not require word repetition
or infer substantial absent procedures. Positive coverage and erroneous additions
are separate dimensions.

This lock changes no historical rubric, prompt or raw score. The former answer
assessments are reused with their recorded interpretation caveats. Retention must
be computed by criterion identity: requirements full in BOTH actual retrieval
and answer / requirements full in retrieval, rather than dividing unrelated totals.
Answer coverage from outside the delivered context is reported separately.

This owner task authorizes only the saved-context assessment described in
`retrieval_rubric_rescore_protocol.v1.md`. No source ingestion, new retrieval,
embedding/model changes, local product answers, GPT answer generation, holdout,
production/safety-policy changes or M3. Those later steps require separate tasks.
