# Cycle 115 Experience Handoff: Maintenance Guidance Crystallization

Date: 2026-05-16
Scope: experience capture only. This file is the only file edited by this handoff.

## Decision Record

Cycle 115 proved that AiPresenter maintenance guidance should graduate into repo
knowledge before it becomes any kind of active skill.

- Durable, repo-wide maintenance guidance belongs in `docs/knowledge/` when it is
  meant to help future agents choose artifacts without changing runtime behavior.
- A runbook belongs in `docs/runbooks/` when the main value is repeatable human
  procedure. A checklist is not evidence until a dated run is recorded in the
  proper evidence log.
- An active presenter skill belongs under `presenter/skills/` and the mirrored
  `src/ai_presenter/presenter/skills/` only when the presenter should receive
  new runtime prompt context through profile `narration.skillPaths`.
- A real Codex skill belongs outside the repo only after an explicit design,
  install path, rollback story, privacy review, and verification plan. It is not
  the first move for AiPresenter-specific maintenance rules.
- Cycle-local lessons still belong in `docs/agent-handoffs/`. They can explain
  why a decision was made, but future agents should verify them against current
  source, tests, and durable docs before treating them as policy.

The implemented Cycle 115 playbook, `docs/knowledge/ai-presenter-maintenance.md`,
is the right layer because it is reviewable in the repo, discoverable from
README, and does not activate provider prompts, package facts, profiles, tests,
or global Codex behavior.

## Artifact Choice Heuristics

Use this quick filter before creating a new maintenance artifact.

| Need | Better artifact | Reason |
| --- | --- | --- |
| Decide what the next slice should be | Demand analysis handoff | Captures priority and non-goals without pretending implementation happened. |
| Identify file boundaries or risk before editing | Technical scan or risk scan | Keeps advice separate from production changes. |
| Preserve cross-cycle repo practice | `docs/knowledge/` | Durable and reviewable without changing runtime behavior. |
| Tell a human how to perform a manual check | Runbook | Procedure is useful even before evidence exists. |
| Record a completed manual or live RingCentral run | `docs/knowledge/ringcentral-video/acceptance-runs.md` | Acceptance evidence needs date, environment, route, and result. |
| Change what the presenter says or receives as prompt context | Active presenter skill, soul, or memory | This is runtime behavior and needs packaging/profile verification. |
| Share agent behavior across repositories | Codex skill candidate first, installed skill later | Global behavior needs explicit approval and a separate verification story. |

If the guidance is "future agents should remember this while working in this
repo," start with repo knowledge. If it is "the live presenter should behave
differently," it is not a docs-only crystallization slice.

## RingCentral Evidence Precision

Cycle 115 reinforced that RingCentral wording must preserve evidence level.

- Keep `answerOnly`, blocked, observed, repo-tested, and live accepted as
  separate states. Do not flatten them into "validated" or "supported."
- Treat runbooks as procedure. Treat `acceptance-runs.md` entries as evidence
  only when they include date, environment, source path, command or manual route,
  and result.
- Link to canonical RingCentral docs such as runtime safety routing, privacy,
  locator, state, evidence, and acceptance files instead of copying their tables
  into broad repo-wide guidance.
- Avoid raw meeting IDs, invite links, participant names, chat text,
  transcripts, notes, recordings, screenshots of private content, or generated
  answer bodies in handoffs.
- When a docs-only cycle mentions RingCentral, say what was checked: markdown
  path/content checks, source review, offline tests, or dated live observation.
  A docs-only playbook does not create new live RingCentral acceptance.

The practical phrasing test: a reviewer should be able to tell whether a claim
came from current source, a current automated test, a runbook procedure, a prior
handoff, or a dated live artifact.

## Safe Staging With `.coverage` Dirty

`.coverage` was already dirty during Cycle 115. Treat that as someone else's
local/generated state unless explicitly told otherwise.

Use exact-path staging:

```powershell
git status --short --untracked-files=all
git add -- docs/agent-handoffs/cycle-115-experience.md
git diff --cached --name-status
git diff --cached -- .coverage
git status --short --untracked-files=all
```

Do not use `git add .`, `git add -A`, or broad docs staging in a shared dirty
worktree. If `.coverage` appears in `git diff --cached --name-status`, unstage
only that path with `git restore --staged -- .coverage`; do not delete, reset,
or regenerate it unless the user explicitly asks.

For short status output, ` M .coverage` means modified but unstaged. `M  .coverage`
or `MM .coverage` means it is staged or partially staged and must be removed from
the index before committing a docs-only handoff.

## Lightweight Validation

Validation run for this experience handoff:

```powershell
Test-Path docs\agent-handoffs\cycle-115-experience.md
rg -n "[ \t]$" docs\agent-handoffs\cycle-115-experience.md
rg -n "docs/knowledge/ai-presenter-maintenance.md|acceptance-runs.md|narration.skillPaths|presenter/skills|src/ai_presenter/presenter/skills|Codex skill|.coverage" docs\agent-handoffs\cycle-115-experience.md
git diff --check -- docs\agent-handoffs\cycle-115-experience.md
git status --short --untracked-files=all
```

Expected result: the file exists, trailing-whitespace search is empty, the
content-check search finds the intended boundary phrases, `git diff --check`
reports no whitespace errors, and `.coverage` remains unstaged.

## Next-Cycle Notes

- Future implementation cycles should read
  `docs/knowledge/ai-presenter-maintenance.md` before choosing package, runtime,
  docs, runbook, or skill-candidate work.
- If the playbook starts getting repeated verbatim across several handoffs, split
  the repeated section into a narrower repo knowledge doc before promoting it to
  a real Codex skill.
- If a future cycle is authorized to edit active presenter skills, include both
  skill copies, profile loading expectations, and the presenter-skill packaging
  test in the plan from the start.
- If a future cycle records live RingCentral evidence, write it to the canonical
  RingCentral evidence docs with exact date and environment instead of burying it
  in an implementation handoff.
