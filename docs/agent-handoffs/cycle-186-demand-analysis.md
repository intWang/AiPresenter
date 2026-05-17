# Cycle 186 Demand Analysis: Controller Answer-Source Parity

Date: 2026-05-17

## User Need

Operators need the controller status and summary surface to explain text-only question outcomes as intentional, privacy-safe results. After recent cycles added `answer_source` to question results and logs, the UI-facing summary should preserve the same distinction without copying raw question text, answer text, or exception details into status rows.

## Acceptance Criteria

- Q&A guidance, including Q&A tied to answer-only entrypoints, displays as matched text guidance.
- Pure presenter settings prompts display as presenter settings responses.
- No-match prompts display as no matching safe control.
- True non-operable entrypoint matches still identify the safe route token and do not start a demo.
- Queued and started safe demos keep their existing wording.
- Operator summary rows show only the safe outcome string, not the raw question or answer text.
- Question exceptions use a generic safe status message.
- No package YAML, alias, routing, voice, diagnostics, or localization changes.

## Non-Goals

- Do not redesign the Tk controller layout.
- Do not expose enum labels such as `answer_source=qa` in the UI.
- Do not change `questionPolicy`, `_can_operate(...)`, Q&A-first matching, or interrupt creation.
- Do not claim live RingCentral acceptance.
