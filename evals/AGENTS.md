# Evaluation evidence boundaries

Owner-authorized closeout,26 October 2026: finish a documented learning prototype,
show source excerpts and AI interpretation automatically, port the selected
measured profile into app code, perform necessary integration checks, and archive
obsolete public experiment files after a verified restorable snapshot. This
supersedes old stop instructions only for this bounded closeout, not for new
experimentation or safety approval. See ../docs/PROTOTYPE.md and ../TASKS.md.

- Do not open or recursively read/search evals/holdout/. No holdout run is authorized.
- Do not run new optimization, judges, rubric changes, model comparisons or paid APIs.
- Preserve retained result/rubric/protocol files and original private raw evidence.
- Historical scripts/reports/stops are archived with original paths and hashes;
  see README.md. Restore separately for historical reproduction; do not alter
  frozen scripts or raw scores to make checks pass against changed application code.
- Keep25-case and8-case populations and all denominators explicit. Coverage,
  retention and safe abstention are different measures; none is clinical safety.
- No independent clinical validation, mobile-device validation, M2 quality pass,
  completed safety layer or final public-release approval may be inferred.

Latest results: retrieval55/63 full,4partial/4absent; historical Qwen13/63,
retaining13/55 fully delivered. Screening8 contains6 supported cases/15core:
Qwen baseline8/15, Gemma6/15, GPT reference13/15. Context fully delivered13/15;
GPT retained13/13. Local A/B changes gave no clear overall gain. Medium remains
the locked judge after no clear Medium/High winner. Full methods and caveats
are in the retained final reports and ../docs/RESULTS.md.
