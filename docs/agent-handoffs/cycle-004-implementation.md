# Cycle 004 Implementation Handoff

Date: 2026-05-16

## Change

Replaced `ringcentral.video.main.add-coworkers` with a UIA `Add coworkers` button route.

## Evidence Used

- Cycle 003 observed `Add coworkers` as a `ButtonControl` at `(1029, 493, 1329, 541)`.
- Existing executor support for `clickWindowControl` handles target, occurrence, control type, and cleanup.

## Tests

- RED: `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_add_coworkers_uses_observed_uia_button_route`
  - Result: failed while route was still `clickWindowRelative`.
  - Failure: `AssertionError: assert 'clickWindowRelative' == 'clickWindowControl'`.
- GREEN: `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py`
  - Result: `9 passed in 1.15s`.
- FULL: `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests`
  - Result: `363 passed, 1 warning in 13.90s`.
  - Warning: `pywinauto` STA COM threading warning.

## Remaining Risk

- Route has not been clicked in a live meeting during Cycle 004.
- Modal cleanup still needs live manual validation.
