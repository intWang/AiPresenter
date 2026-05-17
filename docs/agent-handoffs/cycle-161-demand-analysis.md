# Cycle 161 Demand Analysis: RingCentral Video Invite Link And Coworker Prompts

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Decision

Recommendation: make the next smallest high-value RingCentral Video increment
an exact English answer-only Q&A slice for invite, meeting-link, meeting-ID, and
coworker-invite prompts.

Add focused Q&A coverage so action-shaped invite/link prompts return privacy
guidance instead of thin entrypoint text. This is the right next slice because
recent cycles covered recording, leave/end, reactions, screen sharing, and
system-audio sharing. The next adjacent live-meeting privacy risk is invite
material: links, meeting IDs, searched coworkers, suggestions, and send-invite
actions can expose private access details or create an external meeting side
effect.

## Current Evidence

The package already has the right surfaces:

- `ringcentral.video.top.meeting-info` exposes meeting details, meeting ID,
  meeting link, copy link, dial-in info, and encryption status. It has
  `questionPolicy: answerOnly`.
- `ringcentral.video.main.add-coworkers` opens the empty-room Invite dialog. Its
  notes say the dialog includes a name/email field, suggestions,
  `Copy meeting link`, `Cancel`, and `Invite`.
- `ringcentral.video.toolbar.invite` opens the same Invite dialog from the
  toolbar. Its notes already say to avoid reading private invite links aloud
  unless explicitly requested.
- The existing Q&A item `How can I bring people into the meeting?` gives the
  right broad answer for invite workflow questions, but English exact prompts
  are sparse.

Read-only probes on the current package show the gap is answer quality, not
operability:

| Prompt | Current behavior |
| --- | --- |
| `Copy meeting link` | Routes to `ringcentral.video.top.meeting-info`; non-operable; returns thin Meeting information text. |
| `Can you copy the meeting link?` | Routes to `ringcentral.video.top.meeting-info`; non-operable; returns thin Meeting information text. |
| `Read the invite link` | Routes to `ringcentral.video.toolbar.invite`; non-operable; returns thin Invite participants text. |
| `Invite John` | Routes to `ringcentral.video.toolbar.invite`; non-operable; returns thin Invite participants text. |
| `Send the invite` | Routes to `ringcentral.video.toolbar.invite`; non-operable; returns thin Invite participants text. |
| `Who can I invite?` | Routes to `ringcentral.video.toolbar.invite`; non-operable; returns thin Invite participants text. |
| `Can you read the meeting ID?` | Routes to `ringcentral.video.top.meeting-info`; non-operable; returns thin Meeting information text. |

That is safer than clicking, but it does not tell the user the privacy boundary:
AiPresenter should not read private links or IDs, inspect coworker suggestions,
type names/emails, copy the link to clipboard, or send an invite unless a later
confirmed workflow verifies the visible context and the user explicitly approves
the exact action.

## Recommended Exact Prompts

Cover exactly these English prompts:

- `Copy meeting link`
- `Can you copy the meeting link?`
- `Read the invite link`
- `Can you read the meeting ID?`
- `Invite John`
- `Send the invite`
- `Who can I invite?`

These are intentionally narrow. They represent common user phrasing without
adding broad aliases such as `copy`, `read`, `invite`, `link`, `ID`, `send`, or
`coworker`.

## Expected Behavior

For `Copy meeting link` and `Can you copy the meeting link?`:

- Return meeting-link privacy guidance, not thin Meeting information text.
- Keep `entrypoint_id == ringcentral.video.top.meeting-info` unless the
  implementation deliberately chooses the existing invite Q&A and documents why.
- Keep `can_operate is False`.
- Ensure `create_question_interrupt_step(package, response) is None`.
- Do not open Meeting information or Invite as a question response.
- Do not click `Copy meeting link` or place anything on the clipboard.
- Do not claim the meeting link was copied, verified, safe, or sent.

For `Read the invite link` and `Can you read the meeting ID?`:

- Return privacy guidance that says invite links and meeting IDs are sensitive
  meeting access details.
- Keep responses non-operable and no-interrupt.
- Do not read, invent, summarize, partially mask, or paraphrase an actual link,
  meeting ID, dial-in number, host name, or invite text.
- Do not claim the value is visible or verified unless a later approved
  observation workflow has captured it.

For `Invite John` and `Send the invite`:

- Return invite-action safety guidance associated with
  `ringcentral.video.toolbar.invite`.
- Keep `can_operate is False`.
- Ensure no question interrupt step is created.
- Do not type a name or email, select a suggestion, inspect suggestions, click
  `Invite`, or send any meeting invitation.
- Do not claim John exists, is a coworker, has been selected, or has been
  invited.

For `Who can I invite?`:

- Return invite privacy guidance associated with
  `ringcentral.video.toolbar.invite`.
- Explain the workflow at a high level: use Invite/Add coworkers to search or
  copy meeting details, but do not read coworker suggestions, names, or emails by
  default.
- Do not infer invite eligibility, company directory membership, attendee
  permissions, role, or policy from package routing alone.

## What To Avoid

- Do not make invite, copy-link, read-link, read-ID, coworker search, or
  send-invite prompts operable.
- Do not add or change `openSteps`.
- Do not click Meeting information, Add coworkers, Invite, Copy meeting link,
  Cancel, Invite, search fields, coworker suggestions, names, emails, or dial-in
  controls from these question prompts.
- Do not read or invent actual meeting links, meeting IDs, dial-in numbers,
  host names, coworker names, email addresses, invite suggestions, invite text,
  clipboard contents, or recipient lists.
- Do not claim an invite was sent, a link was copied, a meeting ID was read, a
  person was found, or a directory result was verified.
- Do not add broad aliases such as `copy`, `read`, `send`, `invite`, `link`,
  `meeting`, `ID`, `coworker`, `people`, `John`, or `who`.
- Do not combine this with participant-list reading, chat, screen sharing,
  recording, notes, transcript, captions, microphone, camera, reactions, raise
  hand, leave/end, runtime matcher changes, clipboard integration, OCR,
  provider calls, or live RingCentral acceptance work.
- Do not update acceptance evidence or claim live RingCentral Video validation.
- Do not touch `.coverage` or unrelated dirty files.

## Implementation Handoff Prompt

```text
Cycle161 implementation task. You are not alone in the repo; do not revert
other workers' edits and do not touch `.coverage` or unrelated dirty files.

Repository: C:\Users\rcadmin\Documents\Repos\AiPresenter

Goal: implement the next smallest high-value RingCentral Video user-need gap:
exact English invite, meeting-link, meeting-ID, and coworker-invite prompts that
return privacy-focused answer-only guidance instead of thin entrypoint text,
without copying links, reading private values, searching coworkers, or sending
invites.

Read first:
- docs/agent-handoffs/cycle-161-demand-analysis.md
- packages/ringcentral-video.yaml around
  `ringcentral.video.top.meeting-info`,
  `ringcentral.video.main.add-coworkers`,
  `ringcentral.video.toolbar.invite`, and the Q&A item
  `How can I bring people into the meeting?`
- tests/unit/test_questions.py around existing invite, meeting-info, and
  privacy question tests
- tests/unit/test_diagnostics.py and tests/unit/test_cli.py only if Q&A prompt
  count assertions need updates

Scope:
- Package/test-only change.
- Cover exactly these English prompts:
  - `Copy meeting link`
  - `Can you copy the meeting link?`
  - `Read the invite link`
  - `Can you read the meeting ID?`
  - `Invite John`
  - `Send the invite`
  - `Who can I invite?`
- Prefer exact English Q&A aliases on focused answer-only package Q&A items.
- Keep link/ID value prompts associated with
  `ringcentral.video.top.meeting-info` unless the implementation intentionally
  chooses a single invite-safety Q&A route and updates tests accordingly.
- Keep coworker/search/send prompts associated with
  `ringcentral.video.toolbar.invite`.
- Keep every response non-operable.
- Ensure `create_question_interrupt_step(package, response) is None` for every
  covered prompt.
- Ensure answers mention the privacy boundary for meeting links, meeting IDs,
  coworker suggestions, names/emails, copying, and sending invites.
- Preserve location-style behavior for prompts such as `where is the meeting
  ID`, `where is the meeting link`, `invite people`, and `how do I bring people
  into the meeting`.
- Update diagnostics or doctor count expectations only for the exact authored
  Q&A prompt inventory change.

Do not:
- Edit runtime matcher source, package models, session interrupt logic,
  providers, profiles, README, runbooks, existing handoff docs, or acceptance
  evidence.
- Make invite, copy-link, read-link, read-ID, coworker search, or send-invite
  prompts operable.
- Add or change `openSteps`.
- Click or queue Meeting information, Add coworkers, Invite, Copy meeting link,
  Cancel, Invite, search fields, coworker suggestions, names, emails, or dial-in
  controls from these question prompts.
- Read or invent actual meeting links, meeting IDs, dial-in numbers, host names,
  coworker names, email addresses, invite suggestions, invite text, clipboard
  contents, or recipient lists.
- Type `John` or any other name/email into RingCentral.
- Claim an invite was sent, a link was copied, a meeting ID was read, a person
  was found, or a directory result was verified.
- Add broad aliases such as `copy`, `read`, `send`, `invite`, `link`,
  `meeting`, `ID`, `coworker`, `people`, `John`, or `who`.
- Combine this with participant-list reading, chat, screen sharing, recording,
  notes, transcript, captions, microphone, camera, reactions, raise hand,
  leave/end, runtime matcher changes, clipboard integration, OCR, provider
  calls, or live RingCentral acceptance work.
- Touch `.coverage`.

Acceptance:
- All seven exact prompts return privacy-focused answer-only guidance, not thin
  entrypoint text.
- `Copy meeting link`, `Can you copy the meeting link?`, and
  `Can you read the meeting ID?` remain non-operable and do not claim a link or
  ID was copied, read, visible, verified, safe, or sent.
- `Read the invite link`, `Invite John`, `Send the invite`, and
  `Who can I invite?` remain non-operable and do not claim any invite link,
  coworker, suggestion, email, recipient, or sent-invite state was verified.
- Coworker/search/send prompts route to invite safety guidance associated with
  `ringcentral.video.toolbar.invite`.
- Link/ID value prompts route to meeting-info privacy guidance associated with
  `ringcentral.video.top.meeting-info`, unless the implementation deliberately
  chooses one invite-safety Q&A route and the tests encode that choice.
- `create_question_interrupt_step(package, response) is None` for all seven
  prompts.
- Existing location-style invite and meeting-info questions are preserved.
- Diagnostics remain green, with count expectations updated only for the exact
  authored prompt inventory change.
- Final diff excludes `.coverage`, runtime source, profiles, README,
  acceptance evidence, and unrelated tests.
```
