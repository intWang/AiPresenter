# Cycle 021 Summary - RingCentral Validation Target Discovery

## Theme

Cycle 021 added an offline RingCentralVideo validation target discovery tool so reviewers can list the next validation targets, evidence gaps, cleanup notes, privacy boundaries, and safe acceptance-draft commands without opening RingCentral or reading multiple Markdown tables by hand.

## Agents

- Demand analysis: Kuhn (`019e2d95-c79c-7420-99cb-fdff23d46af5`) produced `docs/agent-handoffs/cycle-021-demand-analysis.md`.
- Technical scan: Ramanujan (`019e2d95-cf9d-70e1-a3f4-b8dd080b9891`) produced `docs/agent-handoffs/cycle-021-technical-scan.md`.
- Implementation: Heisenberg (`019e2d9b-65b3-7030-aa78-bf167ab53812`) added the module, CLI, tests, and `docs/agent-handoffs/cycle-021-implementation.md`.
- Review: Fermat (`019e2da2-4bee-7491-9017-a892b866d23d`) produced `docs/agent-handoffs/cycle-021-review.md`.
- Re-review: Sartre (`019e2da6-9be4-7880-95e6-3d5ed3e196ad`) produced `docs/agent-handoffs/cycle-021-rereview.md`.

## Design And Plan

- Design doc: `docs/superpowers/specs/2026-05-16-validation-target-discovery-design.md`.
- Implementation plan: `docs/superpowers/plans/2026-05-16-validation-target-discovery.md`.

The design kept discovery read-only and docs-derived. It does not promote evidence, write `acceptance-runs.md`, launch RingCentral, or import desktop automation for the discovery path.

## Changes

- Added `src/ai_presenter/acceptance/validation_targets.py`.
- Added `ai-presenter validation-targets`.
- The command joins:
  - `packages/ringcentral-video.yaml`;
  - `docs/knowledge/ringcentral-video/evidence-index.md`;
  - `docs/knowledge/ringcentral-video/validation-checklist-index.md`.
- Default output includes the note:
  `repo-derived planning list only; not live acceptance evidence.`
- Default output excludes `Do Not Execute Yet` rows.
- `--include-blocked` lists blocked/explain-only routes such as recording and leave/end.
- P0 output includes:
  - `p0-add-coworkers-modal`;
  - `p0-controller-queued-chat-question`.
- `--target p0-add-coworkers-modal` shows Add coworkers cleanup, privacy, evidence level, and draft command.
- Group targets omit `--entrypoint` in generated draft commands.
- CLI runtime entrypoints now lazy-import `run_desktop_profile`, `run_material_demo`, and `run_controller`, so importing `ai_presenter.cli` no longer loads `ai_presenter.desktop.windows`, `ai_presenter.runtime.factory`, or `ai_presenter.runtime.controller`.

## Review Fix

The first review found one P2 issue: although `validation-targets` itself was read-only, importing `ai_presenter.cli` still loaded runtime/desktop modules before Typer dispatch.

Main-session fix:

- Added a subprocess import-isolation test.
- Verified RED: `ai_presenter.cli` import loaded all three probed modules.
- Replaced top-level runtime imports with same-name lazy wrapper functions.
- Verified GREEN: import probe returned `False / False / False`.

Re-review accepted the fix and found no remaining issues.

## Verification

Implementation worker evidence:

- Pure RED: missing module import failed.
- Pure GREEN: `9 passed in 2.11s`.
- CLI RED: focused command test failed before command registration.
- CLI GREEN: `55 passed in 10.41s`.
- Ruff: `All checks passed!`.
- Mypy: `Success: no issues found in 79 source files`.
- Full pytest: `491 passed, 1 warning in 26.91s`.
- Manual smoke: P0 list, target detail, and include-blocked outputs worked.

Review evidence:

- Focused pytest: `55 passed in 10.18s`.
- Ruff: `All checks passed!`.
- Manual smoke passed, but review found the P2 import-isolation issue.

Main-session review-fix evidence:

- RED import-isolation test failed.
- GREEN import-isolation test: `1 passed in 1.84s`.
- Direct import probe: `desktop.windows False`, `runtime.factory False`, `runtime.controller False`.
- Focused Cycle 021 tests: `56 passed in 9.33s`.
- Focused ruff: `All checks passed!`.

Re-review evidence:

- Import probe: `False / False / False`.
- Focused pytest: `56 passed in 11.83s`.
- Ruff: `All checks passed!`.
- Accepted.

Final main-session verification:

- Full pytest: `492 passed, 1 warning in 36.87s`.
- Mypy: `Success: no issues found in 79 source files`.
- Diff check for Cycle 021 paths: clean, with existing CRLF warnings only.

## Notes

- No live RingCentralVideo interaction was performed.
- No desktop automation was performed.
- No evidence docs, package YAML, or `acceptance-runs.md` files were written by the tool.
- The Markdown parser is intentionally conservative and fails on missing headers, unknown package ids, and duplicate generated target ids.

## Next Candidates

- Add an explicit `Target ID` column to `validation-checklist-index.md` if generated ids become too label-dependent.
- Add JSON output for `validation-targets` once the text output stabilizes.
- Improve blocked-target output so draft commands are labeled more explicitly as draft-only planning aids.
- Continue RingCentral evidence hardening by using `validation-targets` to drive the next manual checklist improvements.
