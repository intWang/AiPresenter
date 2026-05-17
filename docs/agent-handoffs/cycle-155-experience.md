# Cycle 155 Experience: Microphone Button Alias

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## What This Cycle Learned

- The microphone button alias was the right Cycle 155 slice because Cycle 154
  had already handled the sharper Notes, Transcript, and captions safety
  problem. The remaining issue was a small route-quality mismatch:
  `Where is the microphone button?` used to prefer
  `ringcentral.video.toolbar.audio-menu`, even though "button" points to the
  toolbar mute/unmute control.
- The fix belongs in the package, not runtime scoring. A package-owned
  `microphone button` alias under `ringcentral.video.toolbar.audio` lets exact
  user wording beat token scoring while preserving the existing matcher order.
- The safety boundary did not need to move. The toolbar microphone control is
  still a risky mute/unmute surface, so the answer remains non-operable and no
  question interrupt step should be created.
- The narrow alias is safer than broad media wording. Terms like `microphone`,
  `mic`, `mute`, `audio`, or `audio button` can steal device-menu, state,
  answer-only, or future safety phrasing. The exact `microphone button` phrase
  captures the visual-location intent without widening the route.

## TDD Red And Green

- Red target:
  `tests/unit/test_questions.py::test_ringcentral_microphone_button_location_routes_to_audio_without_interrupt`
  should fail before the package edit because the entrypoint is
  `ringcentral.video.toolbar.audio-menu` instead of
  `ringcentral.video.toolbar.audio`.
- The useful red assertion is the entrypoint mismatch. `can_operate is False`
  and `create_question_interrupt_step(package, response) is None` already
  describe the safety behavior that must stay green.
- Green implementation:
  add exactly one English package-owned alias, `microphone button`, to
  `ringcentral.video.toolbar.audio`.
- Green behavior:
  `Where is the microphone button?` routes to
  `ringcentral.video.toolbar.audio`, stays non-operable, and creates no
  interrupt step. No runtime source change is needed because package aliases
  are checked before token scoring.
- Run focused pytest checks with `--no-cov` when verifying this slice so the
  repository-level coverage defaults do not rewrite `.coverage`.

## Diagnostic Count Learning

- Adding one entrypoint alias changes the RingCentral package-owned alias count
  from 156 to 157. That count is durable inventory, so diagnostics expectations
  should move when the authored alias inventory really changes.
- Q&A prompt counts should not change for this slice. Cycle 154 moved the Q&A
  prompt count from 84 to 87 by adding exact answer-only prompts; Cycle 155
  adds no Q&A items.
- Treat count changes as evidence to explain, not a chore to silence. If the
  new count differs, prove whether it came from an intentional alias or prompt
  addition before updating assertions.
- Duplicate, overlap, and substring-risk diagnostics stay meaningful after a
  count bump. Do not relax them just because the expected total increased.

## Safe Wording

- Say "Adds one exact package-owned alias for the explicit microphone button
  location question."
- Say "Routes the covered prompt to the toolbar microphone control while
  preserving non-operable answer behavior and no question interrupt step."
- Say "This is package-routing evidence only; it does not change live audio,
  microphone state, device selection, provider readiness, or RingCentral Video
  acceptance."
- Say "The package-owned alias count increases from 156 to 157 because one
  authored entrypoint alias was added."
- Avoid claiming that AiPresenter can mute, unmute, verify microphone state,
  switch devices, route virtual microphone output, or prove live audio was
  accepted.
- Avoid broad phrasing such as "audio controls are fixed" or "microphone
  questions now work"; the slice covers the exact button-location wording.

## Next-Cycle Ideas

- Record answer-only exact prompts deserve their own policy pass. Good
  candidates to evaluate are `Record this meeting`, `Start recording`,
  `Stop recording`, `Are we recording?`, and `Recording status`.
- Keep the first recording slice exact and answer-only unless a product decision
  says a non-operable entrypoint route is preferable for status or location
  questions.
- Separate recording action, status, and location wording. Those prompts should
  not imply consent, host permission, live recording state, transcript access,
  or artifact-reading capability.
- Consider a later `share system audio` scan, but do not combine it with
  microphone button or recording work. It overlaps with audio-device language
  and may need product evidence about the RingCentral sharing surface.
- Keep using narrow red/green tests plus diagnostics for every alias or Q&A
  increment. The fastest safe cycle is still one exact prompt family, one
  package inventory change, and one clear count explanation.
