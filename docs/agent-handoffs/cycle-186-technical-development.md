# Cycle 186 Technical Development: Privacy-Safe Controller Outcomes

Date: 2026-05-17

## Files Changed

- `src/ai_presenter/runtime/controller.py`
  - Reorders `describe_question_result()` so `answer_source` text-only outcomes outrank non-operable entrypoint fallback.
  - Adds `describe_question_error(...)`.
  - Uses generic question-error wording in the UI exception path.
- `tests/unit/test_controller.py`
  - Covers Q&A guidance with an answer-only entrypoint.
  - Covers presenter-meta, no-match, and true non-operable entrypoint outcomes.
  - Covers exception-message redaction.
- `tests/unit/test_controller_view_model.py`
  - Covers privacy-safe question outcome pass-through in operator summary rows.
- `docs/knowledge/ai-presenter-maintenance.md`
  - Records the operator status/summary privacy boundary.

## Behavior Added

Q&A guidance tied to answer-only entrypoints now reports:

```text
Answered only: matched text guidance; no demo was started
```

Question-submit exceptions now report:

```text
Question error: question could not be answered safely.
```

The raw exception text is not copied into `last_question_outcome`.

## Red/Green

Initial RED after adding parity tests:

```text
7 failed, 8 passed
```

Failures showed `qa` answers with answer-only entrypoints still rendering as non-operable entrypoint outcomes.

GREEN after reordering `describe_question_result()`:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_controller.py::test_describe_question_result_distinguishes_queued_started_and_risky tests\unit\test_controller.py::test_describe_question_error_hides_exception_text tests\unit\test_controller.py::test_presenter_controller_keeps_sensitive_mixed_meta_question_text_only_when_idle tests\unit\test_controller.py::test_presenter_controller_keeps_sensitive_mixed_meta_question_text_only_while_running tests\unit\test_controller_view_model.py::test_operator_summary_uses_privacy_safe_question_outcome
```

Result: `15 passed`.

Additional focused sentinel:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_controller.py::test_presenter_controller_answers_risky_question_without_demo tests\unit\test_controller.py::test_presenter_controller_answers_no_match_without_demo tests\unit\test_controller.py::test_describe_question_result_distinguishes_queued_started_and_risky tests\unit\test_controller_view_model.py::test_operator_summary_uses_privacy_safe_question_outcome
```

Result: `4 passed`.
