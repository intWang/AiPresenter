# Cycle 014 Summary: Demo Flow Lookup

Date: 2026-05-16

## Completed

Cycle 014 moved demo-flow lookup into the material package model, giving CLI, diagnostics,
controller, and runtime paths one indexed source of truth for flow IDs.

- Added read-only `MaterialPackage.demo_flows_by_id`.
- Added `MaterialPackage.demo_flow_by_id()` with a shared unknown-flow message that includes available flows.
- Rejected duplicate demo flow IDs during package validation.
- Added `MaterialPackage.with_demo_flow()` so controller-generated question-answer flows rebuild indexes safely.
- Delegated `runtime.package_demo.demo_flow_by_id()` to package-owned lookup.
- Updated diagnostics and CLI/controller coverage for unified missing-flow messages.
- Added flow preflight before desktop setup in demo, existing-window demo, and controller runtime entrypoints.
- Updated README and RingCentral manual acceptance runbook with flow listing and missing-flow dry-run checks.

## Evidence

- TDD red/green evidence is recorded in `docs/agent-handoffs/cycle-014-implementation.md`.
- Independent review and re-review are recorded in `docs/agent-handoffs/cycle-014-review.md`.
- Coordinator reran focused verification:
  - `116 passed` for package/demo/CLI/diagnostics/controller/runtime factory tests.
  - Ruff passed.
  - Mypy passed.
- Coordinator reran full verification:
  - `429 passed, 1 warning in 24.96s`.
  - Warning is the known pywinauto STA COM threading warning.

## Changed Paths

- `src/ai_presenter/packages/models.py`
- `src/ai_presenter/runtime/package_demo.py`
- `src/ai_presenter/runtime/diagnostics.py`
- `src/ai_presenter/runtime/controller.py`
- `src/ai_presenter/runtime/factory.py`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_package_demo.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_diagnostics.py`
- `tests/unit/test_controller.py`
- `tests/unit/test_runtime_factory.py`
- `README.md`
- `docs/runbooks/ringcentral-manual-acceptance.md`
- `docs/superpowers/specs/2026-05-16-demo-flow-lookup-design.md`
- `docs/superpowers/plans/2026-05-16-demo-flow-lookup.md`
- `docs/agent-handoffs/cycle-014-demand-analysis.md`
- `docs/agent-handoffs/cycle-014-technical-scan.md`
- `docs/agent-handoffs/cycle-014-implementation.md`
- `docs/agent-handoffs/cycle-014-review.md`

## Follow-Ups

- Add installed Windows SAPI voice availability checks to `voices` and `doctor`.
- Add Piper model availability checks for the Piper speaker profile.
- Continue RingCentral manual acceptance evidence, especially the observed Add coworkers UIA route.
