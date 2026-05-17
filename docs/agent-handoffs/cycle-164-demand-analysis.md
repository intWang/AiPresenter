# Cycle 164 Demand Analysis: Meeting Information Private Values

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Latest inspected commit: `7627354`

## Context

Cycle 163 shipped Chat and Participants privacy prompt hardening. The remaining
adjacent RingCentral Video demand is Meeting information private values:
host details, dial-in numbers, dial-in details, and broad requests to read or
copy meeting details aloud.

`ringcentral.video.top.meeting-info` is already marked `questionPolicy:
answerOnly`. Its purpose and narration say the popover can include meeting
title, host, meeting ID, copy link, dial-in information, encryption, and
end-to-end encryption options. The package also has an existing Q&A item,
`How should AiPresenter handle meeting IDs and links safely?`, whose answer
already says exact IDs, links, dial-in details, and host information should not
be copied, read aloud, or exposed unless the user explicitly asks and visible
content is verified.

This demand-analysis agent inspected `packages/ringcentral-video.yaml`,
`tests/unit/test_questions.py`, and Cycle 163 handoffs only. I did not edit
code or tests, did not stage or commit, did not touch `.coverage`, and did not
run the full suite. The working tree was already dirty in `.coverage`,
`packages/ringcentral-video.yaml`, and `tests/unit/test_questions.py`; the
package/test dirty diff appears to add eight meeting-info private-value prompt
strings. Leave those changes to their owning implementation/test agents.

## User Demand

When a user asks about private Meeting information values, AiPresenter should
answer with privacy guidance instead of reading, inventing, copying, dialing,
pasting, or exposing the actual values. The assistant may explain where the
Meeting information surface is and what category of details it contains, but
it must stay answer-only until a later flow has explicit user intent, visible
content verification, and any required consent or permission boundary.

The demand is not to make Meeting information operable. It is to ensure common
host and dial-in value prompts resolve through the existing privacy Q&A instead
of thin `Meeting information:` entrypoint fallback text or any interrupt step.

## Exact Prompt Variants Worth Supporting

Support these as exact authored Q&A prompts, not broad aliases:

- `Read the dial-in number`
- `What is the dial-in number?`
- `Can you read the dial-in number?`
- `Copy the dial-in details`
- `Read dial-in details aloud`
- `Who is the host?`
- `Can you read the host name?`
- `Read meeting details aloud`

Avoid generic aliases such as `host`, `phone`, `number`, `copy`, `read`,
`dial`, or `details`; those are too broad and could steal unrelated meeting
control questions.

## Expected Answer-Only Behavior

For every supported prompt:

- Return the meeting-info privacy Q&A answer, not the thin
  `Meeting information:` fallback label.
- Prefer `entrypoint_id == ringcentral.video.top.meeting-info` so the answer
  remains tied to the relevant surface without opening it.
- Keep `can_operate is False`.
- Ensure `create_question_interrupt_step(package, response) is None`.
- Do not open the popover, copy to clipboard, dial phone audio, paste invite
  details, or queue any UI step from the question response.
- Do not read, invent, mask, summarize, validate, or expose an actual host
  name, account name, company name, dial-in number, phone access code, meeting
  ID, meeting link, invite text, or copied value.
- Do not claim the host, dial-in detail, encryption state, meeting policy, or
  visible value has been verified.

Location-style prompts can remain answer-only entrypoint answers when they are
asking where the surface is, such as `meeting information`, `where is the
meeting ID`, or `where is the meeting link`, provided they never expose private
values and never create an interrupt step.

## Why This Is Valuable

Meeting information is a compact surface with several high-risk private values.
Host identity can reveal a person or organization, dial-in numbers and access
details can let outsiders join or bridge into a meeting, and copy/read-aloud
requests can accidentally leak meeting access metadata into the room or logs.

This is also a natural follow-up to the previous privacy cycles. AiPresenter
already treats recording, leaving, sharing, invites, chat text, participant
names, and host actions as sensitive. Meeting information should feel equally
predictable: helpful about the control location, cautious about private values,
and quiet about anything it has not explicitly verified.

## Acceptance Criteria

- The selected prompt variants are package-authored under the existing
  meeting-info privacy Q&A item, or an equivalent meeting-info privacy Q&A item
  with the same boundary.
- Each prompt returns privacy-focused answer text that includes the existing
  boundary for private meeting details.
- Each prompt has `entrypoint_id == ringcentral.video.top.meeting-info`.
- Each prompt has `can_operate is False`.
- `create_question_interrupt_step(package, response) is None` for each prompt.
- No response contains the thin fallback label `Meeting information:`.
- No response contains concrete private-looking values such as `https://`,
  `ringcentral.com`, an email address, a realistic phone number, a numeric
  meeting ID, or a success claim such as copied, pasted, dialed, read, or
  verified.
- Existing meeting-link, invite-link, recording, leave, reaction, screen-share,
  notes/transcript, Chat/Participants privacy, and location-style meeting-info
  tests continue to pass.
- If eight new authored Q&A prompts are added on top of the Cycle 163 committed
  baseline, prompt inventory expectations should move from `149 Q&A question
  prompts` to `157 Q&A question prompts`. If another agent has already added a
  different subset, update counts to the actual authored-prompt delta only.
- Final implementation diff should exclude `.coverage`, runtime matcher code,
  profiles, README, acceptance evidence, and unrelated tests.

## Next-Cycle Backlog

- Localized host and dial-in value variants, especially Japanese and Chinese
  read/copy host or dial-in requests, after the English exact-prompt slice is
  stable.
- Meeting passcode/password prompts, but only after confirming that the
  RingCentral Video Meeting information surface actually exposes those fields
  in the observed product state.
- Encryption status prompts such as `Can you tell me the encryption status?`;
  these need state-verification wording rather than private-value wording.
- Meeting lock/security status prompts, separate from host and dial-in details
  because they involve live meeting state and role permission.
- Participant-role prompts such as `Show participant roles`, which remain a
  Participants privacy hardening candidate from the Cycle 163 handoffs.
- Caption/live-transcript text prompts such as `Read caption text` and
  `Show live caption text`, which should stay answer-only unless the user asks
  explicitly and visible text is verified.
