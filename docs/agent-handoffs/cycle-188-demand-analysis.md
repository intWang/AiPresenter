# Cycle 188 Demand Analysis: RingCentralVideo Private-Surface Examples

Date: 2026-05-17

## User Need

Future maintainers need concrete examples for sensitive RingCentralVideo prompts so package, routing, localization, and controller changes keep the same privacy boundary: explain the surface safely, but do not read private content or change meeting state by default.

## Chosen Slice

Docs-only private-surface examples for:

- Chat
- Meeting information
- Recording
- Notes and Transcript

## Acceptance Criteria

- Examples separate safe location/explanation prompts from private-content or state-changing prompts.
- Runtime expectations distinguish `entrypoint`, Q&A answer-only, and `questionPolicy: answerOnly` behavior without changing code.
- Wording says the examples are policy/routing guidance, not live RingCentral acceptance evidence.
- Evidence and validation docs state that docs-only examples do not upgrade route evidence states.
- No package YAML, tests, aliases, localization, locator confidence, or acceptance-run changes.

## Non-Goals

- Do not claim live acceptance.
- Do not add or change package Q&A.
- Do not add aliases for content-reading or state-changing requests.
- Do not change `can_operate`, `questionPolicy`, or controller behavior.
