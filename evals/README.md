# Evaluation evidence

Start with [Results](../docs/RESULTS.md), [Research](../docs/RESEARCH.md) and the
[evidence guide](../docs/EVIDENCE.md). You do not need to read the development history.

This directory retains the final methods, criterion definitions, reports,
results and review decisions behind the conclusions. The current
application is a learning prototype; these are development measurements, not a
medical safety approval or an independent holdout result.

## Historical archive

[development-2026-10-26.zip](archive/development-2026-10-26.zip) contains a verified
snapshot of the public project immediately before closeout, including earlier
reports, runners and technical stops. Original repo-relative paths and a SHA-256
manifest are inside it. It includes the previously uncommitted evaluation work.
No model binaries, secrets, private knowledge snapshots or holdout files were added.

215 obsolete flat evaluation files and two superseded planning/history documents
were removed from the active tree after archiving. The selected final evidence
remains directly readable. Some **historical links and commands inside immutable
reports refer to the archived layout**; restore the archive before using those.
Curated links in README and `docs/` point to active evidence.

From the repository root:

```powershell
python scripts/evidence_archive.py
python scripts/evidence_archive.py --restore-to knowledge/local/restored-development
```

Restoration requires a new or empty directory and does not run anything. The
snapshot records the original Git HEAD and working diff. Full historical audit
execution additionally requires the matching private frozen evidence, original
dependencies and expected Git state; a current clone plus today's downloaded
webpages is not equivalent. Do not modify frozen scripts to make an audit pass.

Private raw logs and original source snapshots remain under ignored
`knowledge/local/diagnostics/`. Technical facts affecting interpretation remain
in the final reports: for example, the 4B memory exclusion and interrupted GPT
attempt of unknown token usage. Other debugging history is available in the
archive rather than the introductory reading path.

`real-knowledge.json` is retained because the knowledge setup smoke check uses
it. `holdout/` is outside this closeout and has not been opened or evaluated.
