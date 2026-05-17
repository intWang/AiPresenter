# Cycle 179 Demand Analysis: Non-Chat Mixed-Meta Orchestration

Date: 2026-05-17

## User Need

Users mix presenter-style instructions with RingCentralVideo requests beyond Chat:

- `Please be brief and show network quality`
- `Please be brief and open notes and transcript`

Cycle 178 covered Chat as the safe operable path and Meeting Info as answer-only. Cycle 179 should pin one non-Chat operable surface and one Notes/Transcript answer-only surface through session/controller orchestration.

## Acceptance Criteria

For `Please be brief and show network quality`:

- Routes to `ringcentral.video.top.network-quality`.
- `can_operate is True`.
- Answer does not start with `Presenter settings:`.
- `ControllerSession.create_interrupt_step(...)` returns an interrupt.
- Idle controller starts `question-answer-demo`.
- Running controller queues the interrupt, does not stop the active demo, and does not start `question-answer-demo`.

For `Please be brief and open notes and transcript`:

- Routes to `ringcentral.video.more.notes`.
- `can_operate is False` because Notes/Transcript remains answer-only.
- Answer includes the notes safety boundary, such as starting notes can change meeting state.
- No session interrupt is created.
- Idle and running controller results stay `text_only`.
- No queued interrupt, no stop request, and no runner call.

## Edge Cases

- Chat content prompts such as `Please be brief and show chat messages` must remain answer-only.
- Meeting Info privacy prompts such as `Please be brief and read meeting information aloud` must remain answer-only.
- Notes action/content prompts like `Please be brief and start meeting notes`, `summarize the transcript`, and `download transcript text` should not become operable.
- Avoid broad participant aliases in this slice; `show participants` needs a separate privacy-adjacent pass.

## Files And Tests To Touch

- `tests/unit/test_questions.py`
  - Add or verify mixed-meta rows for Network Quality and Notes/Transcript in the routing matrix.

- `tests/unit/test_controller_session.py`
  - Add or verify session interrupt/no-interrupt coverage for both prompts.

- `tests/unit/test_controller.py`
  - Add or verify idle and running controller sentinels for started, queued, and text-only outcomes.

Only touch source if tests expose a gap:

- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/runtime/session.py`
- `src/ai_presenter/runtime/controller.py`
- `packages/ringcentral-video.yaml`

Preserve Q&A-first routing, Chat content privacy guard precedence, and `questionPolicy: answerOnly` behavior.
