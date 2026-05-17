# Cycle 207 Technical Scan

Date: 2026-05-17
Cycle: 207
Role: Technical scan subagent

## Implementation Map

- `src/ai_presenter/runtime/voice.py`
  - Extend `PresenterTone`, `PRESENTER_TONE_CHOICES`, `_TONE_DESCRIPTIONS`,
    `_TONE_LABELS`, and `_TONE_ALIASES`.
  - Add English dynamic rendering prefix `Training note.`.
  - Add Chinese dynamic rendering prefix for `instructor`.
  - Leave Chinese SAPI rate at the default `0`.
- `src/ai_presenter/runtime/questions.py`
  - Treat high-confidence `instructor tone`, `training tone`, and
    `tutorial tone` requests as Presenter meta requests.
- Data-driven surfaces
  - CLI `voices`, CLI voice preflight, controller dropdown, and controller
    labels use shared voice catalog helpers, so they should follow the runtime
    catalog after tests are updated.

## Focused Tests

- `tests/unit/test_voice.py`
  - Tone normalization, aliases, descriptions, rendering, SAPI rate, and matrix
    documentation contract.
- `tests/unit/test_cli.py`
  - `voices` catalog and targeted alias resolution.
- `tests/unit/test_controller.py`
  - Controller voice label.
- `tests/unit/test_questions.py`
  - Presenter meta routing and sensitive RingCentral route parity.

## Documentation

- `docs/knowledge/presenter-tone-behavior-matrix.md`
  - Add the canonical row and style-only boundary.
- `docs/knowledge/ringcentral-video/runtime-safety-routing.md`
  - Note that Cycle 207 `instructor` is phrasing-only and part of route-parity
    coverage.

## Edge Cases

- Avoid broad aliases like `guide` or `walk me through`; those may overlap with
  real RingCentral question intents.
- Keep CLI catalog output ASCII-safe by using ASCII aliases only.
- Do not change package counts, provider compatibility, voice assets, or live
  acceptance state.
