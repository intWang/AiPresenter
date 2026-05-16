# Cycle 010 Implementation: RingCentral Evidence Index

Date: 2026-05-16

## Objective

Make the RingCentral Video knowledge package easier to act on by connecting package entrypoints to evidence level, locator confidence, privacy policy, acceptance history, and next validation targets.

## Implementation

- Created `docs/knowledge/ringcentral-video/evidence-index.md`.
  - Defines evidence levels: `Accepted`, `Observed`, `Repo-tested`, `Backlog`, and `Blocked`.
  - Adds `Evidence Records` with stable local evidence IDs for Cycle 001, 002, 003, 004, and this index.
  - States the current overall evidence position: no executable route is fully live accepted yet.
  - Adds a ranked validation priority queue.
  - Adds an entrypoint evidence table covering all 27 current package entrypoints.
  - Adds flow coverage for all 4 current package flows.
  - Adds runbook mapping rows for smoke, audio, controller, and running-app checks.
  - Adds surface-level evidence notes for empty-room canvas, toolbar, More menus, top bar, settings/background, notes/transcript, recording, and leave.
  - Adds a risk queue for unresolved locator, cleanup, privacy, and confirmation gaps.
  - Adds acceptance-run requirements for future evidence.
  - Adds a maintenance checklist to reduce future doc drift.
- Updated `docs/knowledge/ringcentral-video/source-index.md`.
  - Added `evidence-index.md` as a repo-local evidence navigation source.
- Added planning docs:
  - `docs/superpowers/specs/2026-05-16-ringcentral-evidence-index-design.md`
  - `docs/superpowers/plans/2026-05-16-ringcentral-evidence-index.md`

## Source Inputs

- `docs/knowledge/ringcentral-video/source-index.md`
- `docs/knowledge/ringcentral-video/observation-log.md`
- `docs/knowledge/ringcentral-video/locator-matrix.md`
- `docs/knowledge/ringcentral-video/state-matrix.md`
- `docs/knowledge/ringcentral-video/privacy-matrix.md`
- `docs/knowledge/ringcentral-video/acceptance-runs.md`
- `docs/runbooks/ringcentral-manual-acceptance.md`
- `packages/ringcentral-video.yaml`
- `docs/agent-handoffs/cycle-010-demand-analysis.md`

## Verification

- Entrypoint coverage check:
  - Command enumerated package entrypoints and flows with `load_material_package()` and verified every ID appears in `evidence-index.md`.
  - Result: `entrypoints= 27 missing_entrypoints= []`, `flows= 4 missing_flows= []`.
- Required-heading/key-target check:
  - Command used a Python check for the exact headings `## Evidence Records`, `## Validation Priority Queue`, `## Entry Point Evidence Table`, `## Flow Coverage`, `## Runbook Mapping`, `## Surface Evidence Notes`, `## Risk Queue`, `## Acceptance Run Requirements For New Evidence`, and `## Maintenance Checklist`, plus key targets `ringcentral.video.main.add-coworkers` and `meeting-control-map-demo`.
  - Result: `missing_headings= []`, `missing_targets= []`.
- Placeholder scan:
  - `rg -n "TODO|TBD|PLACEHOLDER" docs\knowledge\ringcentral-video\evidence-index.md docs\knowledge\ringcentral-video\source-index.md`
  - Result: no matches.
- Link target smoke check:
  - `Test-Path` returned `True` for locator matrix, observation log, privacy matrix, acceptance runs, and manual acceptance runbook.
- Source-index check:
  - `Select-String -Path docs\knowledge\ringcentral-video\source-index.md -Pattern "evidence-index"`
  - Result: evidence index row present.
- Review follow-up:
  - Renamed the repository-local source table's third column from `Current Evidence` to `Repository Signal`.
  - Changed the runbook row role to `Manual acceptance checklist` and clarified that dated acceptance evidence belongs in `acceptance-runs.md`.
- Diff whitespace check:
  - `git diff --check -- docs\knowledge\ringcentral-video\evidence-index.md docs\knowledge\ringcentral-video\source-index.md docs\agent-handoffs\cycle-010-implementation.md`
  - Result: no whitespace errors.

## Notes

- This cycle did not run live RingCentral clicks, screenshots, or UIA captures.
- This cycle did not change package YAML routes.
- The evidence index intentionally keeps `Add coworkers` at `Observed`, not `Accepted`, because live click/modal cleanup validation has not been recorded.
- The index intentionally keeps Recording and Leave as `Blocked`/explain-only until a confirmation workflow and role/privacy policy exist.
