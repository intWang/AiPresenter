# Cycle 184 Demand Analysis: Privacy-Safe Answer Source Telemetry

Date: 2026-05-17

## User Need

Operators need to know why a live question produced a text answer or a safe demo without exposing the user's raw question or AiPresenter's answer text in logs.

Cycle 183 added `answer_source` to the runtime/controller data model. Cycle 184 makes that source visible in successful runtime telemetry so test review and future UI/diagnostics work can distinguish matched Q&A guidance, matched entrypoints, presenter settings questions, and no-match fallbacks.

## Product Boundary

- Log only route metadata and safe tokens.
- Do not log the raw user question.
- Do not log the generated answer text.
- Do not change routing, controller summaries, package YAML, voice behavior, or RingCentral operation safety.

## Acceptance Criteria

- Successful `question_answered` logs include `answer_source=<qa|entrypoint|presenter_meta|no_match>`.
- Existing timing, package, language, tone, entrypoint, and `can_operate` metadata stays intact.
- Error logs stay minimal and do not invent an answer source.
- Tests cover all four answer source values.
- Tests prove raw prompts and answer text do not enter the log message.
- The repo maintenance playbook documents answer-source semantics and privacy boundaries.

## Non-Goals

- Do not add UI display for answer source in this cycle.
- Do not add exact-field-count requirements to structured log consumers.
- Do not add new RingCentral aliases or Q&A content.
