# Cycle 157 Demand Analysis: Leave and End Meeting Exact Prompts

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Decision

Recommendation: make the next smallest high-value RingCentral Video increment
an exact English leave/end meeting prompt slice.

Add focused answer-only coverage for these user prompts:

- `Leave meeting`
- `End meeting`
- `Hang up`
- `End call`
- `Close meeting`
- `Can you leave the meeting?`
- `Can you end the meeting?`

All seven prompts should route to closeout safety guidance associated with
`ringcentral.video.toolbar.leave`, stay non-operable, and create no question
interrupt step. This is the right next slice because Cycle 155 handled the
microphone button route-quality gap, Cycle 156 handled recording exact prompts,
and the remaining high-risk meeting-control family with obvious user demand is
meeting closeout.

## Current Evidence

`ringcentral.video.toolbar.leave` already has the right safety shape: it is
titled `Leave meeting`, its purpose is `Leave or end the meeting.`, it has
`openSteps: []`, and its presenter notes say to treat it as destructive and use
verbal confirmation before any leave or end action.

Read-only routing probes show the gap is prompt coverage and answer quality:

- `Leave meeting` routes to `ringcentral.video.toolbar.leave`, but returns only
  thin entrypoint text: `Leave meeting: Leave or end the meeting.`
- `Can you leave the meeting?` also routes to
  `ringcentral.video.toolbar.leave`, but returns the same thin text.
- `End meeting`, `End call`, and `Can you end the meeting?` currently route to
  `ringcentral.video.top.meeting-info`, which is the wrong surface for a
  destructive closeout request.
- `Hang up` and `Close meeting` currently return no match.

The current results are non-operable, which is good, but they either miss the
intent or fail to give the safety answer a user needs before a destructive
meeting action.

## Why It Matters

Leaving or ending a meeting is a high-risk live-meeting boundary. Users ask for
it with short telephony phrasing while presenting: leave, end, hang up, end
call, close meeting. AiPresenter should recognize these as meeting closeout
requests, but it must not click Leave, pick an end-for-everyone choice, or imply
the meeting was actually closed.

The user need is not automation yet. It is reliable, answer-only safety
guidance:

- Explain that Leave exits the current participant from the meeting.
- Explain that host flows may expose an end-meeting-for-everyone option.
- Say AiPresenter will not leave, end, hang up, or close the meeting without a
  separate explicit confirmation and a safe confirmation path.
- Keep live RingCentral state claims out of the answer unless a later workflow
  explicitly inspects a visible confirmation dialog.

## Recommended Scope

Keep this as a package/test-only Q&A increment.

- Add a closeout safety Q&A item, or exact English aliases on an existing
  closeout Q&A item if one appears before implementation.
- Cover exactly the seven prompts listed in this document.
- Associate the answer with `ringcentral.video.toolbar.leave`.
- Keep every response `can_operate is False`.
- Ensure `create_question_interrupt_step(package, response) is None` for every
  prompt.
- Preserve existing demo flow behavior and the `openSteps: []` safety boundary
  on `ringcentral.video.toolbar.leave`.
- Update diagnostics or count expectations only if the authored Q&A inventory
  intentionally changes.

No runtime matcher, provider, profile, README, runbook, acceptance-evidence, or
live RingCentral validation change should be necessary.

## Expected Behavior

For `Leave meeting` and `Can you leave the meeting?`:

- AiPresenter should answer with closeout safety guidance instead of thin
  entrypoint text.
- It should not click Leave.
- It should not claim the user has left the meeting.

For `End meeting` and `Can you end the meeting?`:

- AiPresenter should route to `ringcentral.video.toolbar.leave`, not Meeting
  information.
- It should explain that ending may affect everyone and requires explicit
  confirmation plus verification of the visible choice.
- It should not claim host permission or end-for-everyone authority has been
  verified.

For `Hang up`, `End call`, and `Close meeting`:

- AiPresenter should treat these as closeout phrasing for the current
  RingCentral Video meeting.
- It should give the same answer-only safety boundary.
- It should not perform a telephony hangup, close the app window, leave
  computer audio, or terminate the meeting process.

## What To Avoid

- Do not make Leave operable.
- Do not add open steps or click `Leave`.
- Do not click or confirm `Leave meeting`, `End meeting for everyone`, `End`,
  `Close`, `Hang up`, or any visible closeout dialog option.
- Do not close the RingCentral Video window or terminate a process.
- Do not confuse meeting closeout with `Leave computer audio` in the audio menu.
- Do not claim the user left, ended, closed, or hung up the meeting.
- Do not claim host role, moderator role, meeting ownership, participant impact,
  or visible confirmation-dialog state has been verified.
- Do not add broad aliases such as `leave`, `end`, `close`, `call`, `meeting`,
  `exit`, or `quit`.
- Do not combine this with recording, Notes, Transcript, captions, microphone,
  share, invite, participants, app-window closing, or acceptance work.
- Do not touch `.coverage` or unrelated dirty files.

## Implementation Handoff Prompt

```text
Cycle157 implementation task. You are not alone in the repo; do not revert
other workers' edits and do not touch `.coverage` or unrelated dirty files.

Repository: C:\Users\rcadmin\Documents\Repos\AiPresenter

Goal: implement the next smallest high-value RingCentral Video user-need gap:
exact English leave/end meeting prompts that return safe answer-only guidance
without performing or implying live meeting closeout actions.

Read first:
- docs/agent-handoffs/cycle-157-demand-analysis.md
- packages/ringcentral-video.yaml around
  `ringcentral.video.toolbar.leave`
- tests/unit/test_questions.py around existing leave/recording answer-only
  tests
- tests/unit/test_diagnostics.py and tests/unit/test_cli.py only if Q&A prompt
  or alias count assertions need updates

Scope:
- Package/test-only change.
- Cover exactly these English prompts: `Leave meeting`, `End meeting`,
  `Hang up`, `End call`, `Close meeting`, `Can you leave the meeting?`, and
  `Can you end the meeting?`.
- Prefer a closeout safety Q&A item, or exact English aliases on an existing
  closeout Q&A item if one exists by implementation time.
- Route all covered prompts to `ringcentral.video.toolbar.leave`.
- Keep responses non-operable and ensure no question interrupt step is created.
- Answer that Leave exits the current participant, host/end choices can affect
  everyone, and AiPresenter will not leave or end the meeting without separate
  explicit confirmation and a safe confirmation path.

Do not:
- Edit runtime matcher source, package models, session interrupt logic,
  providers, profiles, README, runbooks, existing handoff docs, or acceptance
  evidence.
- Make Leave operable or add `openSteps`.
- Click or queue Leave, End meeting, End for everyone, Close, Hang up, or any
  confirmation-dialog option.
- Close the app window or terminate RingCentral Video.
- Treat this as `Leave computer audio`.
- Claim host permission, meeting ownership, participant impact, visible dialog
  state, or live RingCentral state has been verified.
- Claim the meeting has been left, ended, closed, or hung up.
- Add broad aliases such as `leave`, `end`, `close`, `call`, `meeting`, `exit`,
  or `quit`.
- Combine this with recording, Notes, Transcript, captions, microphone, share,
  invite, participants, app-window closing, or acceptance work.
- Touch `.coverage`.

Acceptance:
- `Leave meeting`, `End meeting`, `Hang up`, `End call`, `Close meeting`,
  `Can you leave the meeting?`, and `Can you end the meeting?` all route to
  closeout safety guidance associated with `ringcentral.video.toolbar.leave`.
- Each response keeps `can_operate is False`.
- `create_question_interrupt_step(package, response) is None` for each prompt.
- `End meeting`, `End call`, and `Can you end the meeting?` no longer route to
  `ringcentral.video.top.meeting-info`.
- No response claims live meeting closeout happened or that host/end authority
  has been verified.
- Existing Leave demo flow and `openSteps: []` behavior are preserved.
- Diagnostics remain green, with count expectations updated only for the exact
  authored Q&A inventory change.
- Final diff excludes `.coverage`, runtime source, profiles, README,
  acceptance evidence, and unrelated tests.
```
