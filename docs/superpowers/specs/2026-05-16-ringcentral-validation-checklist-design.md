# RingCentral Validation Checklist Design

Date: 2026-05-16

## Context

AiPresenter now has a broad RingCentral Video knowledge package:

- `packages/ringcentral-video.yaml` owns executable entrypoints, flows, explainers, Q&A, and manual controls.
- `docs/knowledge/ringcentral-video/evidence-index.md` maps entrypoints and flows to current evidence levels.
- `docs/knowledge/ringcentral-video/acceptance-runs.md` is the dated proof log for automated and manual runs.
- `docs/runbooks/ringcentral-manual-acceptance.md` is procedure, not proof.

The remaining problem is operational. A future agent or human tester still has to jump between several docs to answer what to validate next, what privacy boundary applies, how cleanup should be checked, and where the result should be recorded.

## Chosen Approach

Create a procedural validation checklist index and protect it with a lightweight docs coverage test.

This keeps runtime behavior unchanged while making live RingCentral acceptance safer and more repeatable. The checklist will not promote any route to accepted; it will explain how to collect the evidence needed for that promotion later.

## Alternatives Considered

1. Docs-only checklist with no tests.
   - Lowest risk and fastest to write.
   - Rejected as the final shape because it can drift from package entrypoints silently.

2. Checklist plus docs coverage tests.
   - Recommended.
   - Gives future agents a single operator-ready guide and a machine check that every package entrypoint stays represented.

3. Add evidence metadata directly to `packages/ringcentral-video.yaml`.
   - Attractive longer term, but the package models currently forbid extra fields.
   - Deferred until schema design can be done without mixing docs discipline with runtime model changes.

## Design

Add `docs/knowledge/ringcentral-video/validation-checklist-index.md` as the operator-facing entry point for manual/live validation.

The document will include:

- An update rule: append dated evidence to `acceptance-runs.md` first, then update locator/evidence/privacy docs.
- A priority checklist table for P0/P1/P2 route groups.
- One row or route-group row covering every operation entrypoint from `packages/ringcentral-video.yaml`.
- Cleanup expectations for modal, side panel, toggle, Escape, settings, and explain-only routes.
- Privacy boundaries for meeting IDs, invite links, participant names, chat text, shared content, notes/transcript, recording, account/settings data, and room/background imagery.
- A "Do Not Execute Yet" section for recording and leave/end controls.

Update cross-links:

- `evidence-index.md` should list the checklist index as a primary source and maintenance target.
- `source-index.md` should describe the checklist as procedure for turning evidence gaps into safe manual runs.
- `ringcentral-manual-acceptance.md` should point operators to the checklist before live route validation.

Add tests in `tests/unit/test_material_packages.py`:

- Confirm every RingCentral operation entrypoint appears in the validation checklist.
- Confirm every demo flow appears in the evidence index.
- Confirm the checklist is linked from the evidence index and source index.
- Confirm sensitive blocked routes remain called out in the checklist.
- Confirm the checklist points to `acceptance-runs.md` as the proof log.

## Acceptance Criteria

- `validation-checklist-index.md` exists and is actionable without reading handoff docs.
- All 27 package entrypoint IDs are represented in the checklist.
- All 4 package demo flow IDs remain represented in `evidence-index.md`.
- `Add coworkers` remains P0 for live click plus modal cleanup.
- Recording and Leave remain blocked or explain-only, with no runtime route expansion.
- The checklist clearly says automated tests, dry runs, and runbook checkboxes are not live acceptance evidence.
- Tests fail when the checklist file or a package entrypoint reference is missing.

## Non-Goals

- No live RingCentral clicks in this cycle.
- No schema changes in `src/ai_presenter/packages/models.py`.
- No package YAML route changes.
- No CLI or diagnostic output changes.
- No promotion from `Observed` or `Repo-tested` to `Accepted`.

## Verification

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
git diff --check -- docs\knowledge\ringcentral-video\validation-checklist-index.md docs\knowledge\ringcentral-video\evidence-index.md docs\knowledge\ringcentral-video\source-index.md docs\runbooks\ringcentral-manual-acceptance.md tests\unit\test_material_packages.py
```

Expected result: package tests pass, full tests pass with the existing pywinauto STA warning only, and diff check reports no whitespace errors.

## Risks

- Documentation duplication can drift. The checklist should stay procedural and link to evidence docs instead of copying every observation detail.
- Tests that parse prose too deeply become brittle. The tests should use stable IDs and required file references rather than line numbers.
- Operators may still mistake a checklist item for proof. The checklist must repeatedly point to `acceptance-runs.md` as the proof source.
- RingCentral UI routes vary by build, locale, DPI, window bounds, role, participant count, and layout. The checklist must require those facts in each manual evidence record.
