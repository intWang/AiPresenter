# Cycle 184 Technical Development: Log Question Answer Source

Date: 2026-05-17

## Files Changed

- `src/ai_presenter/runtime/questions.py`
  - Adds `answer_source=response.answer_source` to successful `question_answered` logs.
- `tests/unit/test_questions.py`
  - Asserts Q&A logging includes `answer_source=qa`.
  - Adds parametrized coverage for `no_match`, `entrypoint`, and `presenter_meta`.
  - Uses `show network quality` as the entrypoint prompt so the full raw prompt can be proven absent from logs.
- `docs/knowledge/ai-presenter-maintenance.md`
  - Documents runtime observability hygiene, answer-source meanings, and privacy boundaries.

## Behavior Added

Successful question logs now include an answer-source routing token:

```text
answer_source=qa
answer_source=entrypoint
answer_source=presenter_meta
answer_source=no_match
```

Error logs still omit answer source and do not include raw question, answer, or exception text.

## Focused Verification

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py::test_answer_question_logs_timing_without_question_text tests\unit\test_questions.py::test_answer_question_logs_failure_without_question_or_exception_text tests\unit\test_questions.py::test_answer_question_logs_canonical_language_for_language_alias tests\unit\test_questions.py::test_answer_question_logs_answer_source tests\unit\test_controller.py::test_describe_question_result_distinguishes_queued_started_and_risky tests\unit\test_runtime_logging.py
```

Result: `12 passed`.

An earlier focused command used a stale controller test name and ran no tests. The root cause was command drift; the equivalent current controller test is `test_describe_question_result_distinguishes_queued_started_and_risky`.
