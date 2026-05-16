# AiPresenter Maintenance Playbook

Date: 2026-05-16
Scope: repo-local maintenance guidance for AiPresenter agents and reviewers.

## Purpose

Use this playbook before choosing the next AiPresenter optimization artifact. It turns repeated cycle lessons into a small decision guide so future work can stay scoped, testable, and reviewable.

This is not a runtime presenter skill, package fact source, live RingCentral acceptance log, or Codex home skill. It does not change profile prompts, provider behavior, package YAML, or global agent behavior.

## Skill Layer Map

AiPresenter now has several "skill-like" layers. Keep them separate.

| Layer | Location | Use it for | Change risk |
| --- | --- | --- | --- |
| Runtime presenter skills | `presenter/skills/*.md` and mirrored `src/ai_presenter/presenter/skills/*.md` | Prompt context loaded by profiles through `narration.skillPaths`. | Active behavior change. Requires package-copy parity and presenter-context tests. |
| Presenter soul and memory | `presenter/soul.md`, `presenter/memory.md` | Durable identity, voice, and user coaching used by narration providers. | Active behavior change. Keep wording precise and profile-compatible. |
| Material packages | `packages/*.yaml` | App-specific surfaces, entrypoints, demo flows, Q&A, aliases, localization, and safety metadata. | Product behavior and diagnostics change. Requires package, localization, doctor, and route-order checks. |
| Durable knowledge | `docs/knowledge/` | Maintainer knowledge, RingCentral evidence indexes, privacy matrices, locator notes, and repo-wide guidance. | Documentation change unless referenced by tests or package docs. Avoid acceptance claims without dated evidence. |
| Runbooks | `docs/runbooks/` | Human procedures and manual acceptance checklists. | Documentation change. Checklist completion is not evidence until recorded in the evidence log. |
| Cycle handoffs | `docs/agent-handoffs/` | Demand analysis, technical scans, risk scans, implementation notes, test review, and lessons for one cycle. | Local coordination artifact. Do not treat as evergreen truth without checking current source or docs. |
| Specs and plans | `docs/superpowers/specs/`, `docs/superpowers/plans/` | Designed implementation work and task breakdowns. | Planning artifact. Do not use as proof that code or docs already changed. |
| Codex home skills | `C:\Users\rcadmin\.codex\...` | Cross-repo agent behavior installed outside this project. | Global behavior change. Do not edit for normal AiPresenter cycles. Draft candidates in repo docs first. |

## Artifact Chooser

Choose the smallest artifact that makes the next cycle safer or more useful.

| Need | Prefer | Use when | Minimum verification |
| --- | --- | --- | --- |
| Product demand or prioritization | Demand handoff | The next high-value slice is unclear or competing requests need ranking. | Diff check and scoped status. |
| Implementation feasibility | Technical scan | You need file boundaries, public contracts, or likely test locations before editing. | Diff check and no staged generated files. |
| Safety/privacy boundaries | Risk scan | A slice might touch RingCentral live behavior, user data, global tools, or broad docs. | Diff check plus explicit no-go list. |
| Actual product behavior | Production code and tests | The change affects runtime, CLI, controller, provider prompts, package loading, or diagnostics. | Focused failing test first, then full verification before commit. |
| Package facts or demo content | Package YAML | The change adds entrypoints, Q&A, aliases, localization, flows, or safety metadata. | Package unit tests, doctor, localization reports, and route-order checks. |
| Runtime presenter behavior | Presenter skill, soul, or memory | The provider should receive new active guidance during demos. | Profile loading tests, packaged skill parity, prompt-context assertions. |
| RingCentral evidence knowledge | `docs/knowledge/ringcentral-video/` | You are recording locator, state, privacy, acceptance, or source navigation evidence. | Navigation/index checks and evidence language review. |
| Human procedure | Runbook | A user or tester needs repeatable manual steps. | Markdown diff check; record acceptance separately when executed. |
| Reusable maintenance guidance | Repo knowledge doc | Lessons apply across cycles but should not alter runtime behavior. | Path/content checks, diff check, staged-file review. |
| Potential future agent behavior | Skill candidate section | The guidance may later become a Codex skill, but it is not ready or approved. | Candidate is repo-local text only with graduation criteria. |

## RingCentral Video Maintenance Rules

- Keep safety routing precise: Q&A-first, answer-only, blocked, observed, repo-tested, and accepted are different states.
- Link to `docs/knowledge/ringcentral-video/runtime-safety-routing.md` for route policy instead of copying it into broad maintenance docs.
- Link to `docs/knowledge/ringcentral-video/privacy-matrix.md` for private surfaces and allowed summaries.
- Treat runbook checkboxes as procedure, not acceptance evidence. Dated runs belong in `docs/knowledge/ringcentral-video/acceptance-runs.md`.
- Do not claim live RingCentral acceptance unless the artifact names the date, environment, source path, command or manual route, and result.
- Preserve cleanup expectations for panels, modals, share pickers, settings, reactions, raised hand, recording, and leave/end paths.

## Localization Wedge Rules

- Add languages in small wedges unless the package has complete demo, Q&A, alias, voice, and provider coverage.
- Separate package localization from runtime language support. A partial report-only language is not automatically a demo-ready presenter language.
- Update diagnostic counts deliberately when aliases, Q&A prompts, or localized answers change.
- Use `localization-report --require-complete` only for languages expected to be complete.
- Avoid wording that implies live RingCentral acceptance, voice availability, or provider compatibility from package text alone.

## Docs Navigation Rules

- Canonical RingCentral Video knowledge belongs under `docs/knowledge/ringcentral-video/`.
- Register new RingCentral knowledge files in source and evidence navigation when they become canonical.
- Keep repo-wide AiPresenter maintenance guidance outside the RingCentral Video subdirectory unless it is package-specific.
- Handoffs can explain why a decision was made, but durable docs should link to current source, tests, runbooks, or evidence indexes.

## Runtime Performance Hygiene

- Preserve behavior first. For matching, routing, localization, and prompt assembly, assert ordering and fallback behavior before optimizing.
- Prefer structural tests over wall-clock thresholds. Timing notes can support a performance story, but they should not be the only guard.
- Cache derived indexes by stable content signatures when mutable inputs can be edited in place.
- Keep public schemas, package YAML, and diagnostics stable unless the performance slice explicitly requires them.
- Document any intentional cache invalidation rule in the implementation handoff.

## Verification And Staging Checklist

Before committing a cycle, choose checks that match the blast radius, then run the standard final gate.

- Docs-only guide: run path/content `rg` checks, `git diff --check`, and `git status --short`.
- Package change: add package unit tests, doctor, localization reports for complete languages, and any relevant negative partial-language report.
- Runtime change: add focused tests for behavior parity, then run pytest, ruff, mypy, doctor, localization reports, and `git diff --check`.
- Active presenter skill change: update both `presenter/skills/` and `src/ai_presenter/presenter/skills/`, then run presenter-context and packaging tests.
- Always inspect staged files with `git diff --cached --name-status`.
- Always prove `.coverage` is not staged before commit.

## Skill Candidate Register

These candidates are intentionally repo-local notes. Do not install or activate them without a later design cycle.

| Candidate | Trigger | Graduation criteria |
| --- | --- | --- |
| AiPresenter maintenance steward | Future cycles repeatedly need the artifact chooser and staging checklist. | At least several cycles use this playbook successfully; a separate spec defines install location, test fixtures, rollback, and repo boundary rules. |
| RingCentral evidence reviewer | RingCentral docs and package changes keep needing evidence-level review. | Current source-index, evidence-index, privacy, locator, state, and runtime safety docs are stable and have a fixture-based review test. |
| Localization wedge planner | More partial languages are added beyond Chinese, Japanese, and Spanish seeds. | Language lifecycle, report semantics, voice/provider compatibility, and diagnostics counts are captured in source-backed tests. |
| Presenter prompt skill editor | Runtime presenter skills change often enough to need a dedicated authoring workflow. | Packaged-copy parity, profile prompt assertions, and example provider prompts are part of the normal test suite. |

The default path is to improve this playbook first. Promote a candidate only when the guidance has proven reusable, the repository can verify it, and the user explicitly wants active skill behavior.
