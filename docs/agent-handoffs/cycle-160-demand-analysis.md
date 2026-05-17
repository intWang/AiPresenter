# Cycle 160 Demand Analysis: RingCentral Video System Audio Sharing Prompts

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Decision

Recommendation: make the next smallest RingCentral Video knowledge-pack
increment an exact English answer-only Q&A slice for system-audio sharing
prompts.

Add exact English prompts to the existing screen-sharing safety Q&A item,
`How should AiPresenter handle screen sharing safely?`, so system-audio sharing
requests route to screen-sharing safety guidance instead of microphone/speaker
device guidance.

## Current Evidence

Cycle 159 added an answer-only screen-sharing safety Q&A for these exact English
prompts:

- `Share my screen`
- `Start sharing`
- `Stop sharing`
- `Read the shared screen`
- `Can you describe what's on screen?`
- `Show my screen`

The remaining demand gap is adjacent system-audio wording. The Share entrypoint
already notes that the observed RingCentral Video share picker includes `Share
system audio`, and this feature belongs to the sharing surface rather than the
ordinary audio-device menu.

During this scan, `tests/unit/test_questions.py` already contained an
uncommitted five-prompt expansion in the targeted screen-sharing Q&A test. Treat
that as concurrent work, not as completed package behavior, unless the
implementation cycle confirms the package YAML and diagnostics counts are
updated and tests pass.

## Recommended Exact Prompts

Add these exact English prompts under the existing screen-sharing safety Q&A:

- `Share system audio`
- `Turn on share system audio`
- `Include system audio`
- `Share computer audio`
- `Can you share system audio?`

These are narrow, user-realistic variants that avoid broad matching while
covering the most likely ways a user asks for computer/system audio to be
included in a screen share.

## Expected Behavior

For each prompt:

- Answer with the existing screen-sharing safety guidance.
- Return `entrypoint_id == ringcentral.video.toolbar.share`.
- Keep `can_operate is False`.
- Ensure `create_question_interrupt_step(package, response) is None`.
- Do not route to `ringcentral.video.toolbar.audio-menu`.
- Do not open the Share picker.
- Do not toggle `Share system audio`.
- Do not click the final `Share` button.
- Do not claim system audio is shared, enabled, included, stopped, disabled,
  muted, safe, verified, or currently audible to participants.

The answer should make clear that system audio sharing can expose private local
sound and remains explain-only until the user explicitly confirms what should be
shared and the visible context is verified.

## What To Avoid

- Do not make system-audio sharing operable from Q&A.
- Do not add or change `openSteps`.
- Do not change runtime matcher scoring or package schema.
- Do not add broad aliases such as `audio`, `system audio`, `computer audio`,
  `sound`, `share audio`, `share`, `screen`, `start`, `turn on`, or `include`.
- Do not weaken normal microphone, speaker, leave-computer-audio, or phone-audio
  location answers.
- Do not read screen/window picker entries, app names, window titles,
  thumbnails, document names, browser tabs, notification contents, media names,
  or local audio sources aloud.
- Do not combine this with general Share picker operation, screen/window
  selection, presentation sharing, shared-screen reading, recording, Notes,
  Transcript, captions, microphone, speaker, camera, leave/end, participants,
  reactions, raise hand, runtime matching, or live acceptance work.
- Do not update acceptance evidence or claim live RingCentral Video validation.
- Do not touch `.coverage` or unrelated dirty files.

## Implementation Handoff Prompt

```text
Cycle160 implementation task. You are not alone in the repo; do not revert other
workers' edits and do not touch `.coverage` or unrelated dirty files.

Repository: C:\Users\rcadmin\Documents\Repos\AiPresenter

Goal: implement the next smallest RingCentral Video user-need gap: exact English
system-audio sharing prompts that return safe screen-sharing answer-only
guidance instead of microphone/speaker audio-menu guidance.

Read first:
- docs/agent-handoffs/cycle-160-demand-analysis.md
- docs/agent-handoffs/cycle-159-demand-analysis.md
- packages/ringcentral-video.yaml around the Q&A item
  `How should AiPresenter handle screen sharing safely?`
- packages/ringcentral-video.yaml around `ringcentral.video.toolbar.share` and
  `ringcentral.video.toolbar.audio-menu`
- tests/unit/test_questions.py around
  `test_ringcentral_english_screen_sharing_questions_stay_qa_first`
- tests/unit/test_diagnostics.py and tests/unit/test_cli.py only if authored
  Q&A prompt counts need updates

Scope:
- Package/test-only change.
- Add exactly these English prompts to the existing screen-sharing safety Q&A:
  - `Share system audio`
  - `Turn on share system audio`
  - `Include system audio`
  - `Share computer audio`
  - `Can you share system audio?`
- Route all five prompts to the existing screen-sharing safety answer.
- Keep `entrypoint_id == ringcentral.video.toolbar.share`.
- Keep responses non-operable.
- Ensure no question interrupt step is created.
- Prove these prompts do not route to `ringcentral.video.toolbar.audio-menu`.
- Preserve ordinary audio-device location behavior for microphone, speaker,
  leave-computer-audio, and phone-audio prompts.
- Update diagnostics or doctor count expectations only for the exact authored
  prompt inventory change.

Do not:
- Edit runtime matcher source, package models, session interrupt logic,
  providers, profiles, README, runbooks, existing handoff docs, or acceptance
  evidence.
- Make system-audio sharing operable from these question prompts.
- Add or change `openSteps`.
- Click or queue `Share`, the final picker `Share` button, `Share system audio`,
  screen/window tiles, or audio menu controls.
- Claim system audio was shared, enabled, included, stopped, disabled, muted,
  safe, verified, or audible to participants.
- Add broad aliases such as `audio`, `system audio`, `computer audio`, `sound`,
  `share audio`, `share`, `screen`, `start`, `turn on`, or `include`.
- Combine this with general Share picker operation, screen/window selection,
  presentation sharing, shared-screen reading, recording, Notes, Transcript,
  captions, microphone, speaker, camera, leave/end, participants, reactions,
  raise hand, runtime matcher changes, or acceptance work.
- Touch `.coverage`.

Acceptance:
- All five exact prompts return the screen-sharing safety answer.
- Each response has `entrypoint_id == ringcentral.video.toolbar.share`.
- Each response keeps `can_operate is False`.
- `create_question_interrupt_step(package, response) is None` for each prompt.
- None of the prompts route to `ringcentral.video.toolbar.audio-menu`.
- No response claims system audio was shared, enabled, included, stopped,
  disabled, muted, safe, verified, or audible to participants.
- Existing audio-device location behavior is preserved.
- Diagnostics remain green, with count expectations updated only for the exact
  five-prompt Q&A inventory change.
- Final diff excludes `.coverage`, runtime source, profiles, README, acceptance
  evidence, and unrelated tests.
```
