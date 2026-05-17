# Cycle 160 Experience: System-Audio Sharing Prompts

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## What This Cycle Learned

- System-audio sharing is not a separate ordinary audio-device request. In the
  RingCentral Video UI it is adjacent to screen sharing, and prompts about
  sharing computer/system audio inherit the same privacy and confirmation risks
  as sharing a screen.
- The existing screen-sharing safety Q&A can absorb narrow adjacent subfeature
  prompts when the subfeature is part of the share flow. This kept Cycle 160
  small: exact system-audio prompts could reuse the answer-only sharing safety
  guidance instead of introducing a second overlapping Q&A item.
- The highest-risk misroute was semantic, not mechanical. `Share system audio`
  and `Include system audio` contain audio words, but they should not route to
  the microphone/speaker audio menu or imply AiPresenter can toggle meeting
  audio settings.
- Count hygiene matters even when the implementation looks like "just aliases."
  New Q&A items, localized prompt sets, authored-prompt diagnostics, and tests
  can count different things. Confirm which inventory changed before updating
  expectations.
- This cycle remains package, routing, and unit-test evidence only. It does not
  prove live RingCentral Video picker behavior, system-audio checkbox state,
  what participants hear, or whether local sound is actually included in a
  share.

## Reusing Screen-Sharing Safety Q&A

- Adjacent share-flow prompts can belong under the screen-sharing safety Q&A
  when the safe answer is the same: AiPresenter can explain the control, but it
  should not start sharing, select a source, toggle system audio, or claim a
  live state without explicit confirmation and visible verification.
- Reuse is preferable here because separate Q&A items for screen sharing and
  system-audio sharing could compete for the same prompts and drift in wording.
  A single safety answer keeps the boundary consistent.
- Keep the absorbed prompts exact and narrow. Good examples from this cycle:
  `Share system audio`, `Turn on share system audio`, `Include system audio`,
  `Share computer audio`, and `Can you share system audio?`.
- Do not generalize from these prompts to broad aliases such as `audio`,
  `system audio`, `computer audio`, `sound`, `share`, `turn on`, or `include`.
  Those tokens are too likely to steal ordinary audio-device, meeting-control,
  or future share-picker intents.
- The related entrypoint can remain `ringcentral.video.toolbar.share` while the
  response stays answer-only and non-operable. That preserves useful control
  context without pretending the assistant can perform the action.

## Audio-Menu Misroute Guardrails

- Guard explicitly against routing system-audio sharing prompts to
  `ringcentral.video.toolbar.audio-menu`. The audio-menu surface is for
  microphone, speaker, leave-computer-audio, and phone-audio location guidance;
  it is not the share picker.
- Tests should assert the positive route and the negative route. It is not
  enough to prove `can_operate is False`; the answer must be the sharing safety
  answer and the entrypoint must not be the audio menu.
- Watch for semantically plausible but unsafe matcher behavior. Words like
  `audio`, `computer audio`, and `turn on` can look close to audio-device tasks,
  while the user intent is actually about what gets broadcast with a share.
- Safe responses should avoid claiming that system audio was enabled, disabled,
  included, stopped, muted, audible, safe, or verified. The package can provide
  guidance; it cannot prove the live checkbox or participant audio experience.
- Do not solve misroutes by weakening ordinary audio-device discovery. Users
  still need stable location answers for microphone, speaker, phone audio, and
  leaving computer audio.

## Count Synchronization

- First identify whether a change adds a new Q&A item or only new exact English
  prompts under an existing item. Cycle 160's intended shape was the latter, so
  localized Q&A item totals stayed unchanged.
- Keep package inventory, diagnostics, CLI/doctor expectations, and unit-test
  fixtures synchronized with the actual counted unit. Do not update counts by
  intuition after adding prompt strings.
- Rerun the focused diagnostic or status command before changing expected
  counts. If the command says item totals are unchanged, avoid count churn.
- Localized question/answer counts should not change just because English exact
  aliases were added to an existing Q&A item, unless localized aliases or a new
  localized Q&A item were also introduced.
- Mention count decisions in handoffs. Future agents should know whether
  "counts unchanged" was intentional evidence or simply omitted work.

## Verification Lessons

- The focused route probe should cover all system-audio prompts together and
  inspect four properties: entrypoint, operability, interrupt creation, and
  answer text.
- The expected route for this cycle is:
  - `entrypoint_id == "ringcentral.video.toolbar.share"`
  - `can_operate is False`
  - no question interrupt step
  - screen-sharing safety answer text
- Include at least one assertion that audio-menu entrypoint-style wording is not
  returned. A non-operable audio-menu response would still be the wrong lesson
  for this prompt family.
- Use `--no-cov` for focused partial pytest runs when the repo-wide coverage
  gate would otherwise make a passing targeted selection exit nonzero.
- Do not claim live RingCentral Video validation from package/unit evidence.
  Keep acceptance language precise: routing is covered, live sharing behavior is
  not.

## Candidate Next-Cycle Gaps

- Add higher-layer presenter/session coverage for screen-sharing and
  system-audio sharing prompts, proving answer-only package routes cannot become
  queued demo steps or live interrupt actions.
- Review stop/disable variants for system audio, such as `Stop sharing system
  audio` or `Turn off share system audio`, with the same answer-only safety
  boundary. These may deserve exact prompts only after checking they do not
  collide with ordinary mute/audio-device tasks.
- Audit localized system-audio sharing phrasing for high-confidence exact
  prompts. Treat translation as intent mapping, not word substitution, because
  several locales may use the same audio words for microphone, speaker, and
  share-picker audio.
- Keep location lookup preservation on the list. Users should still be able to
  ask where the Share control or audio menu is without every `audio` or `share`
  word becoming a safety Q&A answer.
- If a future operable sharing workflow is planned, split it into a separate
  consented product slice with source selection, picker visibility, system-audio
  checkbox state, final confirmation, cancellation, cleanup wording, and live
  acceptance evidence.

## Safe Wording To Preserve

- "System-audio sharing prompts route to screen-sharing safety guidance because
  including computer audio is part of the share flow, not ordinary audio-device
  selection."
- "AiPresenter can explain where sharing controls are, but should not toggle
  system audio or start sharing without explicit confirmation and visible source
  verification."
- "These prompts are answer-only, non-operable, and should not create a question
  interrupt step."
- "Counts remain unchanged when only exact English prompts are added to an
  existing Q&A item and no new localized Q&A item is introduced."
- Avoid saying AiPresenter enabled system audio, changed a checkbox, opened the
  share picker, selected a source, started a share, verified participant audio,
  or inspected local audio content.
