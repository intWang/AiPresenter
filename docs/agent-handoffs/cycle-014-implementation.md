# Cycle 014 Demo Flow Lookup Implementation

## Scope

- Implemented `docs/superpowers/plans/2026-05-16-demo-flow-lookup.md`.
- Stayed within the user-approved paths.
- Created only this implementation handoff; `cycle-014-review.md` and `cycle-014-summary.md`
  were not created because this worker's scope allowed only `cycle-014-implementation.md`.

## Changes

- Added package-owned demo-flow lookup indexes on `MaterialPackage`.
- Added duplicate demo-flow ID validation and a read-only `demo_flows_by_id` view.
- Added `MaterialPackage.demo_flow_by_id()` with the unified unknown-flow message.
- Added `MaterialPackage.with_demo_flow()` to rebuild full runtime indexes for synthetic flows.
- Switched controller-generated question-answer flows away from raw `model_copy`.
- Delegated the runtime package-demo wrapper to package-owned lookup.
- Surfaced the unified missing-flow message in diagnostics and CLI/controller coverage.
- Added runtime flow preflight before desktop driver setup for launch and existing-window demos.
- Documented flow listing and missing-flow acceptance checks.

## TDD Evidence

- RED: `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_material_package_exposes_read_only_demo_flow_index tests\unit\test_material_packages.py::test_demo_flow_by_id_preserves_unknown_id_error tests\unit\test_material_packages.py::test_rejects_duplicate_demo_flow_ids`
  - Result: 3 failed. Missing `demo_flows_by_id`, missing `demo_flow_by_id()`, and duplicate flows were accepted.
- GREEN: same command
  - Result: 3 passed.
- RED: `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_with_demo_flow_rebuilds_runtime_indexes_for_appended_flow tests\unit\test_controller.py::test_presenter_controller_starts_safe_question_demo_with_indexed_flow_lookup`
  - Result: 2 failed. Missing `with_demo_flow()` and controller question flow was absent from the package lookup index.
- GREEN: same command
  - Result: 2 passed.
- RED: `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_package_demo.py::test_demo_flow_by_id_delegates_to_package_lookup tests\unit\test_cli.py::test_controller_reports_available_flows_when_flow_is_missing tests\unit\test_diagnostics.py::test_doctor_uses_unified_missing_flow_message`
  - Result: 2 failed and 1 passed. Wrapper still iterated raw `demo_flows`; diagnostics still used the older missing-flow message.
- GREEN: same command
  - Result: 3 passed.
- RED: `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_runtime_factory.py::test_run_material_demo_validates_flow_before_desktop_driver tests\unit\test_runtime_factory.py::test_existing_window_material_demo_validates_flow_before_desktop_driver`
  - Result: 2 failed. Both runtime paths touched desktop setup before missing-flow validation.
- GREEN: same command
  - Result: 2 passed.

## Verification

- Focused tests: `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_package_demo.py tests\unit\test_cli.py tests\unit\test_diagnostics.py tests\unit\test_controller.py tests\unit\test_runtime_factory.py`
  - Result: 114 passed.
- Ruff: `.\.venv\Scripts\ruff check --no-cache src\ai_presenter\packages\models.py src\ai_presenter\runtime\package_demo.py src\ai_presenter\runtime\diagnostics.py src\ai_presenter\runtime\controller.py src\ai_presenter\runtime\factory.py tests\unit\test_material_packages.py tests\unit\test_package_demo.py tests\unit\test_cli.py tests\unit\test_diagnostics.py tests\unit\test_controller.py tests\unit\test_runtime_factory.py`
  - Result: All checks passed.
- Mypy: `.\.venv\Scripts\mypy --no-incremental src\ai_presenter\packages\models.py src\ai_presenter\runtime\package_demo.py src\ai_presenter\runtime\diagnostics.py src\ai_presenter\runtime\controller.py src\ai_presenter\runtime\factory.py tests\unit\test_material_packages.py tests\unit\test_package_demo.py tests\unit\test_cli.py tests\unit\test_diagnostics.py tests\unit\test_controller.py tests\unit\test_runtime_factory.py`
  - Result: Success, no issues found in 11 source files.
- Full suite: `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests`
  - Result: 427 passed, 1 known pywinauto STA warning.
- Whitespace review: `git diff --check -- <owned files>`
  - Result: exit 0; Git emitted existing LF-to-CRLF normalization warnings for tracked files.

## Review Notes

- No callable code-review subagent was available in this session. Local diff review plus focused
  and full verification were used instead.
- The shared worktree had pre-existing dirty changes in owned and unowned files. This worker
  preserved them and edited only the scoped files requested for Cycle 014.
