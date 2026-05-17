# Cycle 163 Technical Development: Chat And Participant Privacy Prompts

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Scope

Technical-development handoff for the current dirty Cycle 163 implementation.
This agent only inspected the diff and wrote this document. Source files,
tests, `.coverage`, git staging, commits, resets, and checkouts were left
untouched.

## Changed Files Observed

Dirty tracked files from the main-session implementation:

- `.coverage` is modified in the working tree, but it is not part of this
  handoff and was not touched here.
- `packages/ringcentral-video.yaml`
- `tests/unit/test_questions.py`
- `tests/unit/test_diagnostics.py`
- `tests/unit/test_cli.py`

Untracked Cycle 163 context docs already present:

- `docs/agent-handoffs/cycle-163-demand-analysis.md`
- `docs/agent-handoffs/cycle-163-risk-scan.md`
- `docs/agent-handoffs/cycle-163-technical-scan.md`

This handoff adds:

- `docs/agent-handoffs/cycle-163-technical-development.md`

## Behavior Implemented

The implementation adds exact English Q&A prompts to existing RingCentral Video
privacy/safety Q&A items. These prompts now resolve through authored
answer-only Q&A instead of falling through to Chat or Participants entrypoint
matching.

`Can the presenter read meeting messages or participant names?` now includes:

- `Can you read chat messages?`
- `Read chat aloud`
- `Summarize the chat`
- `What did John say in chat?`
- `Who is in the meeting?`
- `List participants`
- `Read participant names`

`Where are host controls for participants?` now includes:

- `Mute all participants`
- `Remove a participant`
- `Lock the meeting`

Expected routing and safety behavior:

- Chat-content prompts return answer-only chat privacy guidance.
- Participant-identity prompts return answer-only participant-name guidance.
- Host-action prompts return answer-only host-control guidance.
- All 10 prompts keep `response.entrypoint_id is None`.
- The prompts explicitly avoid routing to
  `ringcentral.video.toolbar.chat` or
  `ringcentral.video.toolbar.participants`.
- All 10 prompts keep `response.can_operate is False`.
- `create_question_interrupt_step(package, response) is None` for all 10
  prompts, so no Chat or Participants panel interrupt is queued.

## Tests And Count Updates

`tests/unit/test_questions.py` adds three focused parametrized test groups:

- `test_ringcentral_chat_content_requests_stay_answer_only`
  - covers the four chat-content prompts above;
  - asserts no Chat route, no operation, no interrupt, and answer text
    containing `chat messages` and `verified`.
- `test_ringcentral_participant_identity_requests_stay_answer_only`
  - covers the three participant-identity prompts above;
  - asserts no Participants route, no operation, no interrupt, and answer text
    containing `participant names` and `verified`.
- `test_ringcentral_participant_host_action_requests_stay_answer_only`
  - covers the three host-action prompts above;
  - asserts no Participants route, no operation, no interrupt, and answer text
    containing `Do not mute others` and `lock the meeting`.

`tests/unit/test_diagnostics.py` and `tests/unit/test_cli.py` update the Q&A
prompt inventory expectations from `139` to `149` for:

- cross-item duplicate Q&A prompt checks;
- unsafe package-owned alias overlap checks;
- doctor output assertions for the RingCentral profile/package/flow.

The prompt count change is `139 -> 149` because 10 authored English prompt
strings were added under existing Q&A entries. Q&A item localization totals and
package-owned alias totals were not changed.

## TDD Evidence

Red phase evidence available from the diff: the test coverage was added for 10
exact prompts before the package prompt inventory was expanded. Against the
pre-change package state, those prompts were not authored Q&A candidates and
would not satisfy the new answer-only assertions for Q&A privacy guidance,
`entrypoint_id is None`, `can_operate is False`, and no interrupt step.

Green phase evidence reported by the main session:

- Targeted question tests passed: `10 passed`.
- Focused package/diagnostics/doctor set passed: `153 passed`.

This handoff agent did not rerun tests, to avoid modifying `.coverage`.

## Routing Notes

The runtime fix is data-driven, not matcher-driven. The relevant behavior is
that `_match_qa()` evaluates normalized package Q&A prompts before entrypoint
aliases and token fallback. By adding exact prompts under the existing privacy
Q&A entries, the new questions are captured by Q&A-first routing.

That prevents two risky fallbacks:

- chat-content requests being interpreted as a Chat panel lookup;
- participant identity or host-action requests being interpreted as an
  operable Participants panel route.

Because the matched Q&A entries do not point at those operable entrypoints, the
responses stay answer-only and `create_question_interrupt_step(...)` has
nothing to queue.

## Residual Candidates For Future Cycles

Host and dial-in private meeting information remains open from
`cycle-163-demand-analysis.md`. Suggested exact prompts:

- `Read the dial-in number`
- `Can you read the dial-in number?`
- `Can you copy the dial-in number?`
- `Who is the host?`
- `Can you read the host name?`

Recommended target: add these under the existing Q&A item
`How should AiPresenter handle meeting IDs and links safely?`. In the current
dirty tree, adding all five would move the Q&A prompt count from `149` to
`154`, assuming no other concurrent prompt edits.

Participant-role hardening remains open from
`cycle-163-technical-scan.md`. Current probe there found
`Show participant roles` routing unsafely to
`ringcentral.video.toolbar.participants` with `can_operate=True` and an
interrupt queued. Suggested target: add the exact prompt under
`Can the presenter read meeting messages or participant names?` and test that
it stays answer-only with no Participants route.

Caption-text variants remain open from `cycle-163-technical-scan.md`.
Suggested exact prompts:

- `Read caption text`
- `Show captions text`
- `Show live caption text`

Recommended target: add these under
`Where are captions, live transcription, and translation controls?`. The scan
observed thin fallback behavior for caption-text prompts, including
`Show live caption text` incorrectly routing to
`ringcentral.video.toolbar.audio`. If implemented together with
`Show participant roles`, the scan's expected dirty-tree count impact is
`149 -> 153`.

## Commit Notes For Main Agent

Keep the current implementation package/test-only. Do not change runtime
matcher code, add broad aliases, add new `openSteps`, make Chat or Participants
Q&A operable, or include `.coverage` in the intended diff. Before committing,
review `.coverage` separately because it is dirty but unrelated to the prompt
hardening described here.
