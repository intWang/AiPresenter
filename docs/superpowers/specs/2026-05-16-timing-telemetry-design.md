# Timing Telemetry Design

Date: 2026-05-16

## Context

Cycle 004 demand analysis identified performance as a real but unmeasured concern. AiPresenter currently logs runtime progress, but it does not consistently record durations for question matching or package action execution. Before optimizing, we need low-risk timing evidence.

## Design

Add a small redaction-safe logging helper in `src/ai_presenter/runtime/logging.py`:

- `elapsed_ms(start, end)` returns milliseconds.
- `log_timed_event(logger, event, *, duration_ms, status, **fields)` writes a structured single-line log message.
- Field values pass through existing `redact_value()`.
- `None` fields are omitted.

Instrument two narrow paths:

- `runtime.questions.answer_question`
  - Event: `question_answered`
  - Fields: package app id, voice language, voice tone, matched entrypoint id, `can_operate`, status.
  - Explicitly do not log user question text or answer text.
- `runtime.package_demo.PackageActionExecutor.execute_action`
  - Event: `package_action_executed`
  - Fields: package app id, entrypoint id, operation, cleanup/deferred state if easy, status.
  - Do not log UI text contents beyond existing package ids and entrypoint ids.

## Safety And Privacy

Telemetry must be metadata-only. Do not log meeting names, chat content, participant names, invite links, user question text, generated answer text, or API keys. The helper should redact known secret-looking values even when future callers pass them by mistake.

## Tests

Add tests for:

- Duration calculation.
- Secret redaction in timed event fields.
- Question timing log contains duration and entrypoint but not question text.
- Package action timing log contains duration, entrypoint, and operation.
- Package action failure logs `status=error` before raising.

## Out Of Scope

- Async controller scanning.
- Aggregated metrics export.
- OpenTelemetry or third-party dependencies.
- Timing every runtime path in one cycle.
- Any performance optimization based on these logs.
