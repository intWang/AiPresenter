# Cycle 014 Review: Demo Flow Lookup

Date: 2026-05-16

## Review Result

Approved after one review-fix loop.

## Initial Findings

The independent reviewer found two controller-runtime gaps:

- `run_controller()` validated voice before desktop setup, but did not validate the initial `flow_id`
  before creating `WindowsDesktopDriver()`.
- `resolve_controller_status()` rendered `KeyError` with Python's quoted `str(KeyError(...))`
  representation, so a unified missing-flow message could appear as
  `Error: 'Unknown demo flow: ...'`.

## Fixes Applied

- Added `material_package.demo_flow_by_id(flow_id)` to `run_controller()` before desktop driver setup.
- Added `_exception_message()` so controller status messages use `KeyError.args[0]` without extra quotes.
- Added regression coverage:
  - `test_run_controller_validates_flow_before_desktop_driver`
  - `test_resolve_controller_status_uses_unquoted_key_error_message`

## Re-Review

The reviewer rechecked the fixes and reported no remaining findings.

Verdict: APPROVED.

## Review Verification

- New regression tests:
  - `2 passed`
- Reviewer spot check:
  - `3 passed`
- Focused Cycle 014 pytest:
  - `116 passed`
- Ruff on Cycle 014 source and test files:
  - passed
- Mypy on Cycle 014 source and test files:
  - passed, no issues in 11 source files
- Full suite:
  - `429 passed, 1 warning`
  - Warning is the known pywinauto STA COM threading warning.

## Residual Risk

`MaterialPackage.with_demo_flow()` is the safe path for appending synthetic flows because it rebuilds
the package through full Pydantic validation. Direct `model_copy(update={"demo_flows": ...})` can still
produce stale private indexes, so future code should avoid that pattern for runtime flow mutation.
