# Cycle 004 Summary

Date: 2026-05-16

## Outcome

Cycle 004 converted the RingCentral Video `Add coworkers` entrypoint from a coordinate route to the UIA button route observed in Cycle 003. This reduces dependence on window geometry for the empty-room invite callout.

## Changed Files

- `packages/ringcentral-video.yaml`
- `tests/unit/test_material_packages.py`
- `docs/knowledge/ringcentral-video/locator-matrix.md`
- `docs/knowledge/ringcentral-video/acceptance-runs.md`
- `docs/superpowers/plans/2026-05-16-add-coworkers-uia-route.md`
- `docs/agent-handoffs/cycle-004-implementation.md`
- `docs/agent-handoffs/cycle-004-review.md`
- `docs/agent-handoffs/cycle-004-demand-analysis.md`

## Implementation

- Added `test_ringcentral_add_coworkers_uses_observed_uia_button_route`.
- Updated `ringcentral.video.main.add-coworkers` to:
  - `action: clickWindowControl`
  - `target: Add coworkers`
  - `controlType: button`
  - `cleanup: modal`
- Updated the RingCentral knowledge package to say Cycle 004 changed the package route but did not perform live click/manual modal validation.

## Review

The independent implementation review verdict was `approved_with_risks`.

Blocking issues: none.

Residual risk:

- Live click and modal cleanup validation have not been performed for this route.

## Verification

- RED evidence from implementer:
  - `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_add_coworkers_uses_observed_uia_button_route`
  - Result: failed while the route was still `clickWindowRelative`.
- Focused verification:
  - `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py`
  - Result: `9 passed in 1.46s`.
- Full verification:
  - `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests`
  - Result: `363 passed, 1 warning in 13.89s`.
  - Warning: `pywinauto` STA COM threading warning.

## Parallel Demand Analysis

Cycle 004 also produced `docs/agent-handoffs/cycle-004-demand-analysis.md`. Its top recommendation is `Controller Operator Cockpit And View-Model Split`, because Cycle 001 made live interruption reliable and the controller now needs clearer operator-facing state.

## Recommended Cycle 005

Implement the first slice of the Controller Operator Cockpit:

1. Add pure controller view-model helpers for source, target, flow, voice, scan freshness, current run state, and question outcome.
2. Use tests to define button enabled/disabled states and readable status labels.
3. Wire only low-risk pieces into the Tk controller after the pure helpers are covered.
4. Keep UI changes compact and operational rather than decorative.
