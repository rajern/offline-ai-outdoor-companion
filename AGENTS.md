# Outwise — Agent Instructions

## Purpose

This file defines how coding agents should work in the Outwise repository.

Agents are expected to make implementation decisions independently within the boundaries already defined in the project documentation.

Do not redesign the product or architecture unless a concrete blocker makes the current decision impossible.

## Read before working

Before starting a task, read the relevant project files:

- `docs/PRODUCT.md`
- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/DATA.md`
- `docs/PLAN.md`
- `TASKS.md`

`docs/DECISIONS.md` contains decisions that should be treated as locked unless explicitly changed by the project owner.

## Working principles

- Prefer the simplest implementation that satisfies the task.
- Optimize for a working end-to-end product rather than unnecessary abstraction.
- Do not introduce new infrastructure, frameworks or dependencies without a concrete need.
- Keep frontend, model, retrieval, safety and data-ingestion concerns separated according to `ARCHITECTURE.md`.
- Keep the core product fully local and offline-capable.
- Do not introduce cloud AI APIs into the core product.
- Do not silently change product scope.
- Do not implement post-MVP features unless explicitly requested.
- Do not optimize prematurely.

## Task workflow

Work from `TASKS.md`.

For each task:

1. Confirm its dependencies are complete.
2. Inspect the existing implementation before changing code.
3. Implement only the task and closely related fixes required to make it work.
4. Run relevant tests, builds or checks.
5. Fix failures caused by the change.
6. Report what changed, what was tested and any remaining blocker.
7. Mark the task complete only when its acceptance criteria are satisfied.

If the task reveals a decision that is not covered by the existing documentation and materially affects architecture or product behaviour, stop and surface the decision instead of choosing silently.

## Human approval checkpoints

Some tasks contain decisions that must be approved by the project owner before work continues.

When a task is marked as a **Human approval checkpoint**:

- complete only the work explicitly allowed before the checkpoint
- stop before making or implementing the protected decision
- clearly summarize what requires approval
- wait for explicit approval from the project owner
- do not continue to dependent tasks until approval is given
- do not treat existing documentation, silence or previous general approval as approval for the checkpoint

Human approval is required for decisions involving:
- final knowledge sources and licensing
- safety policy and high-risk behaviour
- final safety/legal messaging
- final MVP readiness and public release

## Parallel work

Tasks may be developed in parallel when they do not depend on each other and do not require editing the same core files.

Prefer separate branches or Git worktrees for parallel agents.

Each parallel task should have clear ownership of the files or module it changes.

Avoid parallel work when:
- one task depends on output from another
- several agents would modify the same core implementation
- architecture is still unresolved
- integration risk is larger than the expected speed gain

## Code quality

- Keep code readable and straightforward.
- Use clear names.
- Add comments only where behaviour is not obvious.
- Avoid large abstractions before they are needed.
- Remove dead code created during implementation.
- Keep dependencies minimal.
- Follow existing project conventions once they exist.

## Testing

Tests should focus on behaviour that matters to the product.

Prioritize:
- core request flow
- local model integration
- retrieval correctness
- source preservation
- ingestion validation
- safety behaviour
- offline operation

Do not create large test suites for trivial implementation details.

Every meaningful feature should have enough automated or reproducible verification to detect obvious regressions.

## Data and licensing

Do not add real external source material to the public repository unless its redistribution rights have been verified.

Do not assume that publicly accessible content is freely redistributable.

Preserve provenance and licence metadata according to `docs/DATA.md`.

Use fixtures or synthetic data while developing RAG functionality before production sources are approved.

## Repository safety

Never commit:
- secrets or credentials
- `.env` files containing secrets
- model binaries
- large generated embeddings or indexes
- generated databases
- copyrighted source material without verified redistribution rights
- local build artifacts or caches

## Internet use

Agents may use the internet for:
- official documentation
- dependency documentation
- technical troubleshooting
- verifying implementation approaches

Prefer primary documentation and official repositories.

Do not change a locked project decision solely because another library or approach appears newer or more fashionable.

## Documentation updates

Update documentation only when implementation materially changes something documented there.

Do not rewrite project documentation for stylistic reasons.

If a locked decision must change because of a verified technical blocker:
1. explain the blocker
2. propose the smallest viable alternative
3. wait for approval before changing `DECISIONS.md`

## Definition of done

A task is done when:

- its acceptance criteria are satisfied
- the relevant flow works
- relevant tests/checks pass
- no known regression has been introduced
- documentation is updated if necessary
- the implementation still respects the locked product and architecture decisions
