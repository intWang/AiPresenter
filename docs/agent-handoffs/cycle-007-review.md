# Cycle 007 Timing Telemetry Review

Date: 2026-05-16

Verdict: `approved_with_risks`

## Summary

The timing telemetry implementation is approved for this cycle. The helper formats durations consistently, omits `None` fields, and routes field values through the existing secret redaction helper. Question and package-action telemetry are metadata-only on the implemented paths, and both wrappers preserve raised exceptions.

The remaining risk is test coverage rather than observed behavior: the committed tests do not directly lock down the question error path or package failure-path UI-label privacy, although I verified both with read-only ad hoc probes during review.

## Findings

### P0

None.

### P1

None.

### P2

- `tests/unit/test_questions.py:431` covers successful `question_answered` logging and asserts the user question/answer text stay out of the log, but there is no committed regression test for the question failure path. The implementation at `src/ai_presenter/runtime/questions.py:156` logs only package, language, and tone before re-raising, and my ad hoc probe confirmed the exception is preserved and question/answer text are absent. Still, because failure-path privacy was explicitly in scope, this should be committed as a focused test in the next pass.
- `tests/unit/test_package_demo.py:452` covers `package_action_executed status=error`, but it does not assert that failed control target labels such as `Raise hand` / `Lower hand` are absent from the telemetry log. The implementation at `src/ai_presenter/runtime/package_demo.py:92` logs package, entrypoint, operation, and cleanup booleans only, and my ad hoc probe confirmed those labels stay out of the log while `PackageActionExecutionError` still propagates. This is a coverage gap, not a functional blocker.

### P3

- `src/ai_presenter/runtime/logging.py:16` redacts field values via `redact_value()` and does not redact the `event` or `status` parameters. That matches the design's "field values" wording and current call sites use constant event/status strings. If future callers make event/status dynamic, they should not pass sensitive values there.

## Scope Checks

- Timing helper behavior: `elapsed_ms()` rounds milliseconds to two decimals at `src/ai_presenter/runtime/logging.py:12`, and `log_timed_event()` renders `duration_ms` with two decimals at `src/ai_presenter/runtime/logging.py:24`.
- `None` omission: `log_timed_event()` skips `None` field values at `src/ai_presenter/runtime/logging.py:25`.
- Secret redaction: field values are passed through `redact_value()` at `src/ai_presenter/runtime/logging.py:28`.
- Question telemetry privacy: success logging at `src/ai_presenter/runtime/questions.py:168` includes package/language/tone/entrypoint/can_operate and does not include user question text or answer text. Error logging at `src/ai_presenter/runtime/questions.py:157` includes package/language/tone only and re-raises at `src/ai_presenter/runtime/questions.py:166`.
- Package action telemetry privacy: logging at `src/ai_presenter/runtime/package_demo.py:92` includes package/entrypoint/operation/cleanup state/status/duration only. It does not include open-step target text or control labels.
- Behavior preservation: I did not treat `can_operate=True` for the background entrypoint as a bug, per cycle instruction. The wrapper around `answer_question()` delegates existing behavior to `_answer_question()` and returns the same response after logging.

## Verification Run

- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_runtime_logging.py tests\unit\test_questions.py tests\unit\test_package_demo.py`
  - Result: `43 passed in 4.18s`
- `.\.venv\Scripts\ruff check --no-cache src\ai_presenter\runtime\logging.py src\ai_presenter\runtime\questions.py src\ai_presenter\runtime\package_demo.py tests\unit\test_runtime_logging.py tests\unit\test_questions.py tests\unit\test_package_demo.py`
  - Result: `All checks passed!`
- `.\.venv\Scripts\mypy --no-incremental src\ai_presenter\runtime\logging.py src\ai_presenter\runtime\questions.py src\ai_presenter\runtime\package_demo.py tests\unit\test_runtime_logging.py tests\unit\test_questions.py tests\unit\test_package_demo.py`
  - Result: `Success: no issues found in 6 source files`
- Read-only ad hoc probe: monkeypatched `runtime.questions._answer_question` to raise `RuntimeError("private answer text")`; verified the emitted `question_answered status=error` log contained package/language/tone and omitted both the user question and exception/private answer text while preserving the exception.
- Read-only ad hoc probe: forced `PackageActionExecutor.execute_action()` to fail on `Raise hand` / `Lower hand`; verified the emitted `package_action_executed status=error` log omitted both UI labels while preserving `PackageActionExecutionError`.

## Recommended Next Cycle

Add committed regression tests for the two ad hoc probes above: question error-path privacy/exception preservation and package action failure-path UI-label omission. After that, consider whether timing logs should move from single-line text to a structured logger/metrics sink, but that remains outside Cycle 007.
