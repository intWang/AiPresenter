# Cycle 187 Technical Scan: Controller Status Exception Text

Date: 2026-05-17

## Current Source Shape

Question-submit failures already use `describe_question_error(...)`.

Non-question paths still had direct exception text in user-visible status strings:

- `resolve_controller_status(...)` rendered `Error: {exception}`.
- App refresh rendered `App refresh error: {exception}`.
- Running-app scan rendered `Scan error: {exception}`.
- Start rendered `Start error: {exception}`.
- Voice asset checker exceptions became readiness detail text.

## Recommended Change

Add bounded public formatters:

- `describe_controller_error(exc)`
- `describe_controller_action_error(action, exc)`

Default to generic wording and allowlist only known public configuration errors such as `Unknown demo flow: ...`.

## Test Targets

- `tests/unit/test_controller.py`
- `tests/unit/test_controller_view_model.py`

## Risks

- Over-sanitizing all voice readiness messages would make expected provider compatibility failures less actionable. Keep validation messages intact and sanitize only checker exceptions.
- Do not touch RingCentral package files for this slice.
- Keep `.coverage` unstaged.
