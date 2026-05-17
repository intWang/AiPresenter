# Cycle 163 Test Review: Chat And Participant Privacy Prompts

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Reviewer scope: current dirty diff in `packages/ringcentral-video.yaml`,
`tests/unit/test_questions.py`, `tests/unit/test_diagnostics.py`, and
`tests/unit/test_cli.py`, plus existing `docs/agent-handoffs/cycle-163-*`
handoffs.

## Findings

1. [P1] The reviewed diff is internally a `149 Q&A question prompts` change,
   but the main-session verification note says the focused package,
   diagnostics, and doctor set passed at `153`.

   Current package/test changes add ten exact English Q&A prompts over the
   committed `139` baseline: seven chat/participant identity prompts under
   `Can the presenter read meeting messages or participant names?` and three
   host-control action prompts under `Where are host controls for
   participants?`. The diagnostics and doctor expectations are updated to
   `149`, not `153`, in `tests/unit/test_diagnostics.py:657`,
   `tests/unit/test_diagnostics.py:674`, `tests/unit/test_cli.py:1512`, and
   `tests/unit/test_cli.py:1514`.

   The `153` count appears in `cycle-163-technical-scan.md` as a recommended
   follow-up after adding four more prompts: `Show participant roles`,
   `Read caption text`, `Show captions text`, and `Show live caption text`.
   Those prompts are not present in the reviewed package or question tests.
   Resolve this before final handoff: either this slice is the current `149`
   change, or the final Cycle163 diff is missing the role/caption additions and
   the diagnostics expectations are stale for the stated `153` verification.

2. [P3] The new question tests cover the core safety behavior, but they do not
   explicitly assert absence of thin fallback labels.

   The current assertions make fallback unlikely because they require
   `entrypoint_id is None`, `can_operate is False`, no interrupt, and answer
   fragments from the authored privacy text. Still, the tests would be stronger
   with direct negative checks such as `Participants panel:` not in host or
   identity responses and `Chat:` or another chat entrypoint label not in chat
   responses. This is a test-hardening gap, not an observed failure in the
   current diff.

## Coverage Check

- Answer-only behavior is asserted for all ten new prompts:
  `response.entrypoint_id is None`, `response.can_operate is False`, and
  `create_question_interrupt_step(package, response) is None` appear in each
  new test group at `tests/unit/test_questions.py:989-994`,
  `tests/unit/test_questions.py:1016-1021`, and
  `tests/unit/test_questions.py:1043-1048`.
- No interrupt is directly asserted for chat content, participant identity, and
  host action prompts through `create_question_interrupt_step(...) is None`.
- Expected privacy text is asserted:
  chat prompts require `chat messages` and `verified`; participant identity
  prompts require `participant names` and `verified`; host action prompts
  require `Do not mute others` and `lock the meeting`.
- No chat or participant entrypoint operation is asserted:
  chat prompts require `entrypoint_id is None` and not
  `ringcentral.video.toolbar.chat`; participant identity and host action
  prompts require `entrypoint_id is None` and not
  `ringcentral.video.toolbar.participants`.
- Diagnostics count is asserted in both diagnostics and CLI doctor tests at
  `149 Q&A question prompts`, matching the current ten-prompt diff from the
  `139` baseline.

## Coordinator Resolution

- Cycle 163 intentionally ships the ten-prompt Chat/Participants slice and keeps
  the package prompt-count assertion at `149`.
- The `153 passed` note in the main session referred to focused pytest cases
  passing, not to the number of authored Q&A prompts.
- `Show participant roles` and caption-text variants remain future-cycle
  candidates from `cycle-163-technical-scan.md`.
- The test-hardening recommendation was accepted: the question tests now assert
  that authored privacy answers do not fall back to `Chat panel:`,
  `Participants panel:`, `Meeting information:`, or the generic no-match text.

## Remaining Risk And Test Gaps

- The known `Show participant roles` unsafe route from
  `cycle-163-technical-scan.md` is not covered by this diff. If that prompt is
  in scope for Cycle163, add it to the participant privacy Q&A and to the
  participant identity test before relying on the `153` verification story.
- The caption text prompts from `cycle-163-technical-scan.md` are also absent.
  They remain a separate gap unless Cycle163 is intentionally limited to chat,
  participant names, and host controls.
- The host-action test checks important authored text, but it does not assert
  `explicitly asks`, `visible context is verified`, or no private participant
  names/roles. The static answer currently contains the right boundary, so this
  is low risk.
- This review agent did not run the full suite, per instruction. I also did not
  stage or commit anything.
