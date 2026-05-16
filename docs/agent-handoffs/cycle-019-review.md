# Cycle 019 Review

Date: 2026-05-16
Role: review worker
Write scope: this file only

## Findings

### P2 - Persistent errors still trigger repeated session-stop marks and operator refreshes

References:

- `src/ai_presenter/runtime/controller.py:122`
- `src/ai_presenter/runtime/controller.py:127`
- `src/ai_presenter/runtime/controller.py:851`
- `src/ai_presenter/runtime/controller.py:855`
- `src/ai_presenter/runtime/controller.py:861`
- `tests/unit/test_controller.py:666`

`resolve_controller_status()` returns `mark_session_stopped=True` on every poll while
`controller.last_error` remains set. `plan_controller_status_application()` then treats that
side effect as a refresh reason even when the visible status and pause label are unchanged, so
`refresh_status()` calls `session.mark_stopped()` and `refresh_operator_view()` every 500 ms for
a persistent error.

`ControllerSession.mark_stopped()` is currently idempotent, so this is not a correctness failure
for the running flag. It does undercut the no-op refresh objective for the error state and misses
the technical-scan recommendation to avoid repeat stop marks for the same ended/error state. The
new test at `tests/unit/test_controller.py:666` asserts that a stop side effect refreshes once,
but there is no test for the next identical error poll after the session has already been marked
stopped.

## Scope Questions

1. `plan_controller_status_application()` skips unchanged visible status/pause updates and refreshes
   for visible transitions. Running, Paused, Ending, Ended, Error, and Switching to answer remain
   visible because `resolve_controller_status()` changes the returned status/pause label for those
   states and the helper refreshes on those changes.
2. `session.mark_stopped()` still happens for ended/error transitions. The repeat persistent-error
   mark/refresh issue is the finding above.
3. `_apply_button_state()` is compatible with Tk-like buttons at runtime: it reads `cget("state")`
   and calls `configure(state=...)` only when needed. The fake-button tests cover the meaningful
   skip/change behavior without requiring a Tk root.
4. The wiring preserves `root.after(500, refresh_status)`, keeps passive voice readiness on
   `voice_readiness_cache.get()`, keeps Start/Submit on fresh `refresh()` checks, and leaves direct
   `refresh_operator_view()` calls in selection, scan, start, question, and `question.trace_add`
   paths.
5. Tests are sufficient for the happy path and button helper slice, but incomplete for repeated
   `mark_session_stopped` behavior on persistent errors.

## Open Risks

- There is no unit test simulating two consecutive identical Ended/Error polls after
  `session.is_running` has become false.
- The helper's public result does not distinguish "stop side effect needed once" from "the incoming
  update says stop"; that makes the repeated-error behavior easy to preserve accidentally.
- Full-suite, ruff, and mypy results are from the implementation handoff; this review reran only
  focused controller/view-model tests.

## Verification

- Command:
  `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller.py tests\unit\test_controller_view_model.py`
  Result: `40 passed in 6.76s`
- Command:
  `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller.py::test_controller_status_application_skips_operator_refresh_when_unchanged tests\unit\test_controller.py::test_controller_status_application_refreshes_when_status_or_pause_changes tests\unit\test_controller.py::test_controller_status_application_refreshes_for_session_stop_side_effect tests\unit\test_controller.py::test_apply_button_state_skips_configure_when_state_matches tests\unit\test_controller.py::test_apply_button_state_configures_only_on_state_change`
  Result: `5 passed in 3.38s`

No live RingCentral actions were run.

## Result

Review result: changes are mostly aligned with the Cycle 019 no-op refresh plan, but not clean due
to the repeated persistent-error stop/refresh issue.
