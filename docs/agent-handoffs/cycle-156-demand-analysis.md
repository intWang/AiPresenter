# Cycle 156 Demand Analysis: Recording Exact Prompts

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Decision

Recommendation: make the next smallest high-value RingCentral Video increment
an exact English recording prompt slice.

Add focused answer-only coverage for these user prompts:

- `Record this meeting`
- `Start recording`
- `Stop recording`
- `Are we recording?`
- `Recording status`

The implementation should route all five prompts to recording safety guidance
without starting, stopping, confirming, or reporting live recording state. This
is the right next slice because Cycle 155 intentionally deferred recording
after landing the smaller microphone button alias. The remaining gap is now
directly in the recording prompt family, and the highest-value fix is to make
short live-meeting English requests land on the existing recording safety
answer instead of thin entrypoint text or no match.

## Why It Matters

Recording is a high-intent live-meeting request. Users often ask in terse
phrases while presenting, and those phrases can be action-shaped rather than
policy-shaped. AiPresenter should recognize the need immediately, but it must
not imply that it can perform or verify the recording action.

The current materials already know the safe boundary:

- `ringcentral.video.more.recording` is observed under More as
  `Start recording`.
- Recording changes meeting state.
- Tours explain the entry without clicking it.
- The Q&A answer for `How do I handle meeting recording safely?` says recording
  is explain-only until explicit confirmation, role permission, and participant
  consent are clear.

The user-need gap is English exact phrasing. Prior scans recorded that
`record this meeting` had no match, while nearby prompts such as
`start recording`, `are we recording?`, and `recording status` could route to
`ringcentral.video.more.recording` but return thin control text. That is close,
but not good enough for a safety-sensitive request family.

## Recommended Scope

Keep this as a package/test-only Q&A increment.

- Add exact English Q&A aliases, or equivalent package-owned answer-only
  coverage if the current Q&A structure prefers a new canonical question, for
  the five prompts listed above.
- Reuse the existing recording safety answer unless implementation evidence
  shows a small wording update is necessary.
- Route all five prompts to `ringcentral.video.more.recording`.
- Keep every response non-operable.
- Ensure no question interrupt step is created.
- Preserve the existing location/control-map behavior for ordinary recording
  entrypoint questions.
- Update diagnostics or count expectations only if the authored Q&A prompt or
  alias inventory intentionally changes.

No runtime matcher, provider, session interrupt, profile, README, runbook, or
acceptance-evidence change should be necessary.

## Exact User Prompts

Action-shaped prompts:

- `Record this meeting`
- `Start recording`
- `Stop recording`

Status-shaped prompts:

- `Are we recording?`
- `Recording status`

These should be tested as exact English prompts, including capitalization and
punctuation where shown. If the implementation adds lowercase variants through
normalization, keep the authored surface narrow and avoid adding broad aliases.

## Expected Behavior

For `Record this meeting`:

- AiPresenter should recognize this as a recording request.
- It should answer with recording safety guidance.
- It should not start recording.
- It should not ask a follow-up that sounds like it is about to execute a live
  recording action unless a separate confirmed-action workflow exists.

For `Start recording`:

- AiPresenter should not click or queue the `Start recording` entrypoint.
- It should explain that recording changes meeting state and requires explicit
  confirmation, role permission, and participant consent or meeting agreement.
- It should keep `can_operate` false and create no interrupt step.

For `Stop recording`:

- AiPresenter should not claim it can stop an active recording.
- It should treat stop recording as the same safety-sensitive recording family.
- It should avoid implying that a recording is currently running.

For `Are we recording?`:

- AiPresenter should not assert live recording state.
- It should explain that it cannot verify recording status unless the visible
  RingCentral UI clearly shows it and the user has asked it to inspect that
  visible state.
- It should still point to the recording safety boundary rather than returning
  generic no-match text.

For `Recording status`:

- AiPresenter should not invent status.
- It should explain the status-verification boundary and avoid reading private
  meeting artifacts, transcripts, participants, or post-meeting recordings.
- It should remain answer-only and non-operable.

## What To Avoid

- Do not make recording operable.
- Do not add or enable open steps for `ringcentral.video.more.recording`.
- Do not click `Start recording`, `Stop recording`, Notes, Transcript, or
  `Also record this meeting`.
- Do not claim recording has started, stopped, is active, is inactive, or is
  available.
- Do not imply host permission, admin policy, organization consent, participant
  consent, or meeting agreement has been verified.
- Do not read, summarize, locate, or promise access to recording files,
  transcripts, summaries, insights, chat, participants, or shared-screen
  content.
- Do not add broad aliases such as `record`, `recording`, `meeting recording`,
  `recorded`, `status`, `meeting status`, or `transcript`.
- Do not combine this with Notes, Transcript, captions, post-meeting artifacts,
  chat, participants, invite/share, system audio, microphone, or background
  routing work.
- Do not update acceptance evidence or claim live RingCentral Video validation.
- Do not touch `.coverage`.

## Implementation Handoff Prompt

```text
Cycle156 implementation task. You are not alone in the repo; do not revert
other workers' edits and do not touch `.coverage`.

Repository: C:\Users\rcadmin\Documents\Repos\AiPresenter

Goal: implement the next smallest high-value RingCentral Video user-need gap:
exact English recording prompts that return safe answer-only guidance without
performing or implying live recording actions.

Read first:
- docs/agent-handoffs/cycle-156-demand-analysis.md
- docs/agent-handoffs/cycle-155-experience.md
- packages/ringcentral-video.yaml around
  `ringcentral.video.more.recording` and the Q&A item
  `How do I handle meeting recording safely?`
- tests/unit/test_questions.py around existing recording tests
- tests/unit/test_diagnostics.py and tests/unit/test_cli.py only if prompt or
  alias count assertions need updates

Scope:
- Package/test-only change.
- Cover exactly these English prompts:
  `Record this meeting`, `Start recording`, `Stop recording`,
  `Are we recording?`, and `Recording status`.
- Prefer adding exact Q&A aliases to the existing recording safety Q&A item,
  unless the package model requires an equally narrow canonical Q&A addition.
- Route all covered prompts to `ringcentral.video.more.recording`.
- Keep responses non-operable and ensure no question interrupt step is created.
- Preserve the safety answer: recording changes meeting state and requires
  explicit confirmation, role permission, and participant consent or meeting
  agreement before any real action.

Do not:
- Edit runtime matcher source, package models, session interrupt logic,
  providers, profiles, README, runbooks, existing handoff docs, or acceptance
  evidence.
- Make recording operable or add `openSteps`.
- Click or queue `Start recording`, `Stop recording`, Notes, Transcript, or
  `Also record this meeting`.
- Claim the meeting is or is not being recorded.
- Claim consent, role permission, host permission, admin policy, or live
  RingCentral state has been verified.
- Add broad aliases such as `record`, `recording`, `meeting recording`,
  `recorded`, `status`, `meeting status`, or `transcript`.
- Combine this with Notes, Transcript, captions, post-meeting recordings,
  participants, chat, invite/share, microphone, system-audio, background, or
  acceptance work.
- Touch `.coverage`.

Acceptance:
- `Record this meeting`, `Start recording`, `Stop recording`,
  `Are we recording?`, and `Recording status` all route to safe recording
  guidance associated with `ringcentral.video.more.recording`.
- Each response keeps `can_operate is False`.
- `create_question_interrupt_step(package, response) is None` for each prompt.
- No response claims live recording state or performs a live RingCentral action.
- Existing recording entrypoint/location behavior is preserved.
- Diagnostics remain green, with count expectations updated only for the exact
  authored inventory change.
- Final diff excludes `.coverage`, source runtime files, profiles, README,
  acceptance evidence, and unrelated tests.
```
