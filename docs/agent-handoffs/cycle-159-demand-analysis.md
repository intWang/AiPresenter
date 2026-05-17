# Cycle 159 Demand Analysis: Share System Audio Safety Prompts

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Decision

Recommendation: make the next smallest high-value RingCentral Video increment
an exact English answer-only Q&A slice for Share system audio prompts.

Add exact English Q&A aliases to the existing screen-sharing safety item,
`How should AiPresenter handle screen sharing safely?`, for:

- `Share system audio`
- `Turn on share system audio`

Both prompts should return the screen-sharing safety answer, stay non-operable,
and create no question interrupt step. This is the right next slice because the
headline screen-share action prompts are already covered, while these two
system-audio prompts currently route to the microphone/speaker menu and return
thin device-control text.

## Current Evidence

Cycle 158 completed exact English answer-only coverage for Reactions and Raise
hand prompts. The current package also already protects these screen-share
prompts under `How should AiPresenter handle screen sharing safely?`:

- `Share my screen`
- `Start sharing`
- `Stop sharing`
- `Read the shared screen`
- `Can you describe what's on screen?`
- `Show my screen`

Read-only routing probes show those six prompts now return the screen-sharing
safety answer with `entrypoint_id == ringcentral.video.toolbar.share`,
`can_operate is False`, and no interrupt step.

The remaining sharp gap is system audio wording:

| Prompt | Current behavior |
| --- | --- |
| `Share system audio` | Routes to `ringcentral.video.toolbar.audio-menu` and returns thin microphone/speaker menu text. |
| `Turn on share system audio` | Routes to `ringcentral.video.toolbar.audio-menu` and returns thin microphone/speaker menu text. |

This happens even though the Share entrypoint notes already say the observed
share picker includes `Share system audio`, and the existing screen-sharing
safety answer already covers the right boundary: sharing can expose private
content and changes what other people see.

## Why It Matters

Sharing system audio is part of the screen-share picker, not a normal
microphone/speaker device selection. It can broadcast local computer audio into
a live meeting, including private notification sounds, media playback, other
calls, recordings, or app audio. A thin audio-menu answer is misleading because
it frames the request as device configuration rather than a meeting-visible
sharing action.

The user need is not live operation in this cycle. The useful increment is
reliable answer-only safety guidance for exact system-audio sharing requests.

## Recommended Scope

Keep this as a package/test-only Q&A increment.

- Add exactly the two English prompts listed above to the existing Q&A item
  `How should AiPresenter handle screen sharing safely?`
- Route both prompts to the screen-sharing safety answer.
- Keep `entrypoint_id == ringcentral.video.toolbar.share`.
- Keep `can_operate is False`.
- Ensure `create_question_interrupt_step(package, response) is None`.
- Prove both prompts no longer route to
  `ringcentral.video.toolbar.audio-menu`.
- Preserve ordinary audio-device location behavior, such as microphone and
  speaker menu prompts, outside this exact slice.
- Update diagnostics or doctor count expectations only if the authored Q&A
  prompt inventory intentionally changes.

No runtime matcher, provider, profile, README, runbook, acceptance-evidence, or
live RingCentral validation change should be necessary.

## Exact User Prompts

System-audio sharing prompts:

- `Share system audio`
- `Turn on share system audio`

These should be tested as exact English prompts. Keep authored coverage narrow;
normalization can handle case or punctuation if it already does so, but this
slice should not add broad aliases.

## Expected Behavior

For both prompts:

- AiPresenter should answer with the existing screen-sharing safety guidance.
- It should identify the related surface as `ringcentral.video.toolbar.share`,
  not `ringcentral.video.toolbar.audio-menu`.
- It should not open the Share picker as a question response.
- It should not toggle `Share system audio`.
- It should not click the final `Share` button.
- It should not claim system audio is being shared, stopped, enabled, disabled,
  safe, muted, or verified.
- It should explain that sharing controls remain explain-only until the user
  explicitly confirms what should be shared or stopped.

## What To Avoid

- Do not make system-audio sharing operable from these question prompts.
- Do not add or change `openSteps`.
- Do not click `Share`, the final picker `Share` button, `Share system audio`,
  any screen/window tile, or any microphone/speaker menu item.
- Do not claim system audio is shared, unshared, enabled, disabled, muted, or
  verified.
- Do not read screen/window picker entries, app names, window titles,
  thumbnails, document names, browser tabs, notification contents, or local
  audio sources aloud.
- Do not add broad aliases such as `audio`, `system audio`, `share audio`,
  `computer audio`, `sound`, `screen`, `share`, `start`, or `turn on`.
- Do not combine this with general Share picker operation, screen/window
  selection, presentation sharing, shared-screen reading, recording, Notes,
  Transcript, captions, microphone, speaker, camera, leave/end, participants,
  reactions, raise hand, runtime matcher changes, or acceptance work.
- Do not touch `.coverage` or unrelated dirty files.

## Implementation Handoff Prompt

```text
Cycle159 implementation task. You are not alone in the repo; do not revert
other workers' edits and do not touch `.coverage` or unrelated dirty files.

Repository: C:\Users\rcadmin\Documents\Repos\AiPresenter

Goal: implement the next smallest high-value RingCentral Video user-need gap:
exact English Share system audio prompts that return safe screen-sharing
answer-only guidance instead of thin microphone/speaker menu text.

Read first:
- docs/agent-handoffs/cycle-159-demand-analysis.md
- packages/ringcentral-video.yaml around
  `ringcentral.video.toolbar.share`,
  `ringcentral.video.toolbar.audio-menu`, and the Q&A item
  `How should AiPresenter handle screen sharing safely?`
- tests/unit/test_questions.py around
  `test_ringcentral_english_screen_sharing_questions_stay_qa_first`,
  audio-menu location tests, and `test_share_screen_answer_is_not_operable`
- tests/unit/test_diagnostics.py and tests/unit/test_cli.py only if Q&A prompt
  count assertions need updates

Scope:
- Package/test-only change.
- Add exactly these English prompts to the existing screen-sharing safety Q&A:
  - `Share system audio`
  - `Turn on share system audio`
- Route both prompts to the existing screen-sharing safety answer.
- Keep `entrypoint_id == ringcentral.video.toolbar.share`.
- Keep responses non-operable and ensure no question interrupt step is created.
- Prove both prompts no longer route to `ringcentral.video.toolbar.audio-menu`.
- Preserve existing microphone/speaker menu location behavior for ordinary
  audio-device prompts.
- Update Q&A prompt count expectations only for the exact authored inventory
  change.

Do not:
- Edit runtime matcher source, package models, session interrupt logic,
  providers, profiles, README, runbooks, existing handoff docs, or acceptance
  evidence.
- Make Share system audio operable from these question prompts.
- Add or change `openSteps`.
- Click or queue `Share`, the final picker `Share` button, `Share system audio`,
  screen/window tiles, or audio menu controls.
- Claim system audio was shared, stopped, enabled, disabled, muted, safe, or
  verified.
- Add broad aliases such as `audio`, `system audio`, `share audio`,
  `computer audio`, `sound`, `screen`, `share`, `start`, or `turn on`.
- Combine this with general Share picker operation, screen/window selection,
  presentation sharing, shared-screen reading, recording, Notes, Transcript,
  captions, microphone, speaker, camera, leave/end, participants, reactions,
  raise hand, runtime matcher changes, or acceptance work.
- Touch `.coverage`.

Acceptance:
- `Share system audio` and `Turn on share system audio` both return the
  screen-sharing safety answer.
- Each response has `entrypoint_id == ringcentral.video.toolbar.share`.
- Each response keeps `can_operate is False`.
- `create_question_interrupt_step(package, response) is None` for both prompts.
- Neither prompt routes to `ringcentral.video.toolbar.audio-menu`.
- No response claims system audio was shared, stopped, enabled, disabled, muted,
  safe, or verified.
- Existing audio-device location behavior is preserved.
- Diagnostics remain green, with count expectations updated only for the exact
  two-prompt Q&A inventory change.
- Final diff excludes `.coverage`, runtime source, profiles, README,
  acceptance evidence, and unrelated tests.
```
