# Cycle 184 Technical Scan: Question Logging Source Field

Date: 2026-05-17

## Current Source Shape

`src/ai_presenter/runtime/questions.py` calls `log_timed_event(...)` in `answer_question()` for both successful and failed calls. `log_timed_event()` already accepts arbitrary keyword fields, skips `None`, and formats safe key-value metadata.

`QuestionResponse.answer_source` is already available from Cycle 183 with these values:

- `qa`
- `entrypoint`
- `presenter_meta`
- `no_match`

## Recommended Change

Add `answer_source=response.answer_source` to the success-only `question_answered` log.

No change is needed in `runtime/logging.py` because the logging helper already supports extra fields.

## Test Targets

- `tests/unit/test_questions.py::test_answer_question_logs_timing_without_question_text`
- `tests/unit/test_questions.py::test_answer_question_logs_failure_without_question_or_exception_text`
- `tests/unit/test_questions.py::test_answer_question_logs_answer_source`
- `tests/unit/test_runtime_logging.py`

## Compatibility Notes

The added key is low risk for tolerant key-value log readers. Any exact-message or fixed-field-count consumer would need a matching update.
