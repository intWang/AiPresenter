# Cycle 163 Demand Analysis: Meeting Info Host And Dial-In Value Prompts

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Latest inspected commit: `46103c6`

## Context

Recent RingCentral Video cycles made privacy-sensitive Q&A prompts explicit and
non-operable for recording, leave/end, reactions and raise hand, screen/system
audio sharing, invites, meeting links, meeting URLs, copy/paste wording, and
read-aloud link requests.

The next adjacent RingCentral Video demand gap is still in
`ringcentral.video.top.meeting-info`. The package purpose and narration already
say Meeting information may expose meeting title, host, meeting ID, copy link,
dial-in info, encryption, and end-to-end encryption options. The existing
meeting-info privacy Q&A already says exact IDs, links, dial-in details, and
host information should not be copied, read aloud, or exposed without explicit
user request and verified visible content.

Direct read-only probes showed the safety layer is mostly intact, but the user
experience is inconsistent:

| Prompt | Current observed behavior |
| --- | --- |
| `Read the dial-in number` | Routes to `ringcentral.video.top.meeting-info`, non-operable, no interrupt, but returns thin `Meeting information:` fallback text. |
| `Can you copy the dial-in number?` | Routes to meeting-info privacy Q&A, non-operable, no interrupt. |
| `Who is the host?` | Routes to `ringcentral.video.top.meeting-info`, non-operable, no interrupt, but returns thin `Meeting information:` fallback text. |
| `Can you read the host name?` | Routes to meeting-info privacy Q&A, non-operable, no interrupt. |
| `What is the meeting passcode?` | No match. |
| `Can you tell me the encryption status?` | Routes to `ringcentral.video.top.meeting-info`, non-operable, no interrupt, but returns thin `Meeting information:` fallback text. |

Initial status showed only `.coverage` dirty. Later scope checks showed
additional concurrent dirty paths, including package/test edits for chat,
participant identity, host-action Q&A prompts, and another Cycle163 handoff.
This demand-analysis agent edited only this file; leave all other dirty paths
to their owning agents.

## Candidate Demand Gaps

1. Host and dial-in private-value prompts.

Users may ask naturally for the host name or dial-in number after opening
meeting information. Some exact prompts already reach the privacy Q&A through
token overlap, while others return the thin entrypoint label. This is high
value because host identity and phone access details are private meeting access
metadata, and the package already has the right answer text.

2. Meeting passcode or password prompts.

Prompts such as `What is the meeting passcode?` currently no-match. This may be
worth a later exact Q&A slice, but the current package purpose does not name a
passcode/password field, so it needs product/source confirmation before adding
authored prompts.

3. Encryption and meeting-lock status prompts.

Prompts such as `Can you tell me the encryption status?` and `Is the meeting
locked?` need a status-specific answer that avoids claiming a live state. This
is valuable, but it should be separate from host/dial-in private values because
the expected answer is more about state verification than private-value
redaction.

## Recommended Target

Implement a narrow package/test-only Cycle163 slice for exact English host and
dial-in private-value prompts by adding explicit `localizedQuestions.en` entries
to the existing Q&A item:

`How should AiPresenter handle meeting IDs and links safely?`

Do not create a new runtime rule and do not add `openSteps`. The existing
answer already covers `dial-in details` and `host information`; the fix is to
make the most likely exact prompts authored and test-backed so they do not fall
back to `Meeting information:` labels.

## Exact User Prompts To Test

Add focused question tests for exactly these prompts:

- `Read the dial-in number`
- `Can you read the dial-in number?`
- `Can you copy the dial-in number?`
- `Who is the host?`
- `Can you read the host name?`

These should be exact Q&A prompts, not broad entrypoint aliases. Do not add
generic aliases such as `host`, `dial-in`, `dial in`, `number`, `phone`,
`copy`, `read`, or `who`.

## Expected Behavior

For every prompt above:

- Return the meeting-info privacy answer, not thin `Meeting information:`
  fallback text.
- Prefer `entrypoint_id == ringcentral.video.top.meeting-info`.
- Keep `can_operate is False`.
- Ensure `create_question_interrupt_step(package, response) is None`.
- Do not open Meeting information from a question response.
- Do not read, invent, mask, summarize, copy, dial, paste, validate, or expose
  an actual phone number, meeting ID, access code, host name, account name,
  company name, invite text, meeting link, or dial-in detail.
- Do not claim the host, dial-in number, phone access detail, role, policy, or
  visible state was verified.

Preserve existing location-style behavior for prompts such as
`meeting information`, `where is the meeting ID`, and `where is the meeting
link`. They may remain answer-only entrypoint lookups as long as they do not
fabricate private values or create an interrupt step.

## Acceptance Criteria

- All five exact prompts are package-authored Q&A prompts under the existing
  meeting-info privacy Q&A item.
- All five prompts return privacy-focused answer text containing the current
  meeting-info private-detail boundary.
- All five prompts have `entrypoint_id == ringcentral.video.top.meeting-info`.
- All five prompts keep `can_operate is False`.
- `create_question_interrupt_step(package, response) is None` for all five.
- No response starts with or contains the thin fallback label
  `Meeting information:`.
- No response contains concrete private-looking values such as `https://`,
  `ringcentral.com`, an email address, a realistic phone number, a numeric
  meeting ID, a copied/read/dialed success claim, or a verified-host claim.
- Existing meeting-link, invite-link, recording, leave, reaction, screen-share,
  notes/transcript, and location-style meeting-info tests continue to pass.
- Diagnostics and CLI expected Q&A prompt counts are updated only for the exact
  authored prompt inventory change. If all five prompts are newly authored, the
  current `139 Q&A question prompts` expectations should become `144`.
- Final diff excludes `.coverage`, runtime source, profiles, README,
  acceptance evidence, and unrelated tests.

## Handoff Notes For Technical, Dev, And Test Agents

- Read first:
  - `packages/ringcentral-video.yaml` around `ringcentral.video.top.meeting-info`
    and the Q&A item `How should AiPresenter handle meeting IDs and links
    safely?`
  - `tests/unit/test_questions.py` around
    `test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first`
  - `tests/unit/test_diagnostics.py` and `tests/unit/test_cli.py` only if prompt
    inventory counts need updates
  - `docs/agent-handoffs/cycle-162-experience.md` for the exact-prompt privacy
    lessons from the previous link-copy slice
- Suggested TDD shape:
  - First extend the focused meeting-info privacy question test with the five
    exact prompts and assert the privacy answer wins over thin fallback text.
  - Add negative assertions for no question interrupt and no concrete private
    values or success claims.
  - Then add only the exact prompts to the existing package Q&A item.
  - Update diagnostics/CLI counts from `139` to `144` only if the package adds
    all five prompts.
- Keep scope tight:
  - Do not edit runtime matcher code.
  - Do not make Meeting information operable from Q&A.
  - Do not add or change `openSteps`.
  - Do not expand this into passcodes, passwords, encryption status, meeting
    lock status, participant names, invite suggestions, phone-audio routing,
    clipboard behavior, live RingCentral acceptance, or localization.
- Focused verification is enough for the implementation agent. Do not run the
  full test suite for this slice; use the targeted question tests plus any
  prompt-count diagnostics/CLI tests touched by the change.
