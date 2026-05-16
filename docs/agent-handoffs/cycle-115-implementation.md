# Cycle 115 Implementation: Repo-Local Maintenance Playbook

Date: 2026-05-16
Scope: docs-only implementation notes for the Cycle 115 experience-crystallization slice.

## Decision

Cycle 115 implemented a repo-local AiPresenter maintenance playbook instead of a runtime presenter skill, packaged skill, or Codex home skill.

The implemented durable artifact is:

- `docs/knowledge/ai-presenter-maintenance.md`

The discoverability link is:

- `README.md`, under `Maintainer Knowledge`

This follows the technical scan's recommendation to keep repo-wide maintenance guidance under `docs/knowledge/` while still satisfying the demand scan's request for a practical playbook that helps future agents choose the next optimization artifact.

## What Changed

The new playbook covers:

- the difference between active presenter skills, soul/memory, material packages, durable knowledge, runbooks, handoffs, specs/plans, and Codex home skills;
- an artifact chooser for demand analysis, technical scans, risk scans, code changes, package YAML, presenter prompt context, RingCentral evidence docs, runbooks, repo knowledge, and skill candidates;
- RingCentral Video safety maintenance rules that link back to canonical runtime-safety, privacy, and acceptance docs;
- localization wedge rules for partial language support, diagnostics counts, report-only language status, and provider/voice compatibility;
- docs navigation rules for canonical RingCentral knowledge and repo-wide maintenance guidance;
- runtime performance hygiene rules around behavior parity, structural tests, cache invalidation, and stable public contracts;
- verification and staging reminders, including the explicit `.coverage` exclusion;
- a repo-local skill candidate register with graduation criteria instead of active skill installation.

## Files Intentionally Not Changed

This cycle did not edit:

- `presenter/skills/`
- `src/ai_presenter/presenter/skills/`
- `profiles/`
- `packages/`
- `src/`
- `tests/`
- `C:\Users\rcadmin\.codex\`
- `.coverage`

## Focused Checks Already Run

```powershell
Test-Path docs\knowledge\ai-presenter-maintenance.md
rg -n "docs/knowledge/ringcentral-video/runtime-safety-routing.md|presenter/skills|src/ai_presenter/presenter/skills|narration.skillPaths|.coverage|Codex home" docs\knowledge\ai-presenter-maintenance.md
rg -n "[ \t]$" docs\knowledge\ai-presenter-maintenance.md README.md
git diff --check -- docs\knowledge\ai-presenter-maintenance.md README.md
```

Notes:

- The initial `Test-Path` returned `False`, proving the durable playbook was absent before the implementation edit.
- The trailing-whitespace `rg` returned no matches.
- The first `git diff --check` covered README because the new playbook was still untracked; run staged diff checks before commit to validate all staged files.
- Git emitted the existing CRLF warning for README; no whitespace error was reported.

## Review Guidance

Review should focus on whether the playbook:

- stays project-scoped and does not create global agent behavior;
- keeps RingCentral acceptance and privacy evidence precise;
- avoids duplicating detailed package facts from the RingCentral knowledge bundle;
- gives future agents an operational chooser rather than a generic contribution guide;
- leaves `.coverage` unstaged.
