# Cycle 016 Review: Controller Voice Readiness

Date: 2026-05-16

## Review Result

Approved after one review-fix loop.

## Initial Finding

The independent reviewer found one P1 issue:

- `refresh_status()` runs every 500 ms and calls `refresh_operator_view()`.
- `refresh_operator_view()` was calling the local voice asset checker on every tick.
- With real SAPI/Piper checks this could repeatedly enumerate COM voices or inspect local Piper
  assets on the Tk UI thread.

## Fix Applied

- Added `_ControllerVoiceReadinessCache`, keyed by normalized `(language, tone)`.
- `refresh_operator_view()` now uses the cache for ordinary UI refreshes.
- Start and Submit still force a fresh readiness check through `refresh()` before triggering work.
- Added `test_controller_voice_readiness_cache_reuses_selected_voice_until_it_changes`.

## Re-Review

The reviewer confirmed the P1 is closed and reported no remaining findings.

Verdict: APPROVED.

## Verification

- New cache regression test:
  - `1 passed`
- Focused controller/view-model pytest:
  - `35 passed`
- Scoped ruff:
  - passed
- Scoped mypy:
  - passed, no issues in 4 source files
- Full suite:
  - `449 passed, 1 warning in 22.85s`
  - Warning is the known pywinauto STA COM threading warning.

## Residual Risk

No real Tk event-loop acceptance test was added. The Start and Submit readiness guards are covered
by helper-level tests and code review; full GUI callback automation remains a future hardening item.
