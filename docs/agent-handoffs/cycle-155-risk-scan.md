# Cycle 155 Risk Scan: Audio, Microphone, and Video Toolbar Aliases

Date: 2026-05-17
Cycle: 155
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Scope

Documentation-only risk scan for future work that adds or adjusts RingCentral
Video audio, microphone, camera, or video toolbar aliases.

This scan does not edit source, tests, README, packages, profiles, existing
docs, generated artifacts, or `.coverage`.

Relevant current boundary:

- Toolbar media aliases can route user phrasing toward
  `ringcentral.video.toolbar.audio`, `ringcentral.video.toolbar.audio-menu`,
  `ringcentral.video.toolbar.video`, or `ringcentral.video.toolbar.video-menu`.
- The microphone and camera toolbar buttons are stateful controls. Their labels
  can alternate between `Mute` and `Unmute`, or between `Start video` and
  `Stop video`.
- Location phrasing such as "Where is the microphone button?" should be treated
  as routing to a known control, not as proof that audio or video state changed.
- Device-menu phrasing should stay separate from toolbar-button phrasing. The
  audio menu is for microphone and speaker device choices; the video menu is for
  camera choice and video settings.
- Any future implementation must keep provider output, speech synthesis,
  virtual microphone routing, live RingCentral acceptance, and permission safety
  out of scope unless there is separate dated evidence for those exact claims.

## Risk Summary

The useful goal is narrow: make explicit toolbar-location questions resolve to
the intended media control without expanding media authority.

The main risk is wording drift. Audio, microphone, and video controls sound
operational even when the intended alias is only a question-routing hint. A
handoff, test name, assertion, or release note can accidentally imply that
AiPresenter muted, unmuted, started camera, stopped camera, detected current
media state, verified microphone readiness, or proved RingCentral accepted live
media input.

The highest-risk phrases are action-shaped prompts around `mute`, `unmute`,
`turn on mic`, `turn off mic`, `start video`, `stop video`, `fix my audio`,
`switch microphone`, `share system audio`, and `is my camera on`. These can be
valid user questions, but alias coverage should not turn them into claims that
media state, device selection, provider output, or meeting permissions were
changed or verified.

Treat every media toolbar alias as a behavior change until tests prove the
route, `can_operate` value, and interrupt-step eligibility are still intended.

## Safe Wording

Preferred wording:

- "Adds a curated package-owned alias for explicit microphone button location
  phrasing."
- "Routes the covered prompt to the microphone toolbar control while preserving
  `can_operate=False` and no question interrupt step."
- "Adds camera or video toolbar aliases only for explicit location wording, not
  for changing camera state."
- "Keeps toolbar-button aliases separate from audio-menu and video-menu device
  selection aliases."
- "The change expands deterministic package matching for authored prompts; it
  does not change live audio, microphone, camera, or video state."
- "The route identifies a known control surface; it does not click mute,
  unmute, start video, stop video, choose a microphone, choose a speaker, choose
  a camera, or change settings."
- "This is package-routing evidence, not live RingCentral Video acceptance."
- "Provider output, speech synthesis, virtual microphone behavior, operating
  system permissions, browser permissions, device readiness, and meeting
  permission safety remain out of scope."

Use narrow verbs such as `adds`, `routes`, `matches`, `preserves`, `keeps`,
`separates`, and `reports`. Avoid verbs such as `mutes`, `unmutes`, `starts`,
`stops`, `enables`, `disables`, `verifies`, `proves`, `validates`, `certifies`,
or `confirms` unless separate evidence proves that exact runtime behavior.

## No-Go Claims

Do not claim or imply:

- A toolbar alias changed audio, microphone, camera, or video state.
- A toolbar alias executed mute, unmute, start video, stop video, leave computer
  audio, use phone audio, camera selection, speaker selection, microphone
  selection, or video setting changes.
- A route to `ringcentral.video.toolbar.audio` proves the user is muted,
  unmuted, safe to speak, audible, or privacy-protected.
- A route to `ringcentral.video.toolbar.video` proves the camera is on, off,
  ready, blocked, visible to others, or safe for the meeting.
- A route to an audio or video menu proves devices are connected, selected,
  working, permitted, or ready.
- `can_operate=False` proves permission safety, privacy safety, consent
  handling, device safety, or live meeting safety.
- `can_operate=True`, if ever introduced, proves a media action is safe in a
  real meeting.
- Package routing proves live RingCentral UI locators, current labels, button
  availability, media permissions, or acceptance by the live app.
- Unit tests, doctor output, dry runs, or localization reports are live
  microphone, speaker, camera, virtual microphone, provider, or RingCentral
  acceptance evidence.
- Provider behavior, OpenAI behavior, SAPI behavior, Piper behavior, speech
  quality, virtual microphone readiness, audio device routing, or generated
  audio playback changed.
- Localized aliases prove broader runtime language capability, live meeting
  readiness, or device readiness.

Avoid wording such as `mic ready`, `audio ready`, `camera ready`,
`mute verified`, `unmute verified`, `video started`, `video stopped`,
`permission-safe`, `privacy-safe`, `provider validated`, `virtual mic ready`,
`RingCentral accepted`, `live-ready`, or `safe in live meetings`.

## Test-Risk Guidance

Safe test patterns:

- Add a failing test before changing package aliases when routing behavior is
  expected to change.
- For every new toolbar media alias, assert the selected `entrypoint_id`,
  `can_operate`, and `create_question_interrupt_step(...)` result.
- For location-only aliases, assert `can_operate is False` and no interrupt
  step unless there is an explicit product decision to allow operation.
- Include negative or neighboring prompts that should stay on the menu route,
  such as microphone/speaker selection for the audio menu and camera/settings
  selection for the video menu.
- Test exact route separation for toolbar button versus device menu phrasing,
  for example `microphone button` versus `microphone menu`.
- Keep answer or narration assertions focused on boundary phrases when needed:
  no broad snapshots and no assertions that imply live state changed.
- Re-run diagnostics that cover duplicate question aliases, duplicate Q&A
  prompts, unsafe Q&A/alias overlap, and substring risk when alias inventory
  changes.
- If a future change intentionally allows a media toolbar interrupt step,
  require a separate risk review that documents the product decision, exact
  prompt shape, visible-state preconditions, cleanup expectations, and live-test
  boundary.

No-go test patterns:

- Do not make tests pass by relaxing risky-word policy, `questionPolicy`,
  `can_operate`, or interrupt-step blocking for media controls.
- Do not assert that a route proves mute state, unmute state, camera state,
  device readiness, permissions, provider readiness, or live acceptance.
- Do not add live RingCentral automation, provider calls, speech synthesis,
  virtual microphone output, SAPI, Piper, OpenAI, or OS permission checks to
  prove alias routing.
- Do not use broad aliases such as `microphone`, `mic`, `audio`, `video`,
  `camera`, `mute`, `unmute`, `sound`, or `settings` unless tests prove they do
  not steal more specific toolbar-button, device-menu, Q&A, or answer-only
  routes.
- Do not update diagnostic counts without proving the authored alias or Q&A
  inventory actually changed.

Recommended focused verification for implementation cycles:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_diagnostics.py
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
git diff --check -- packages\ringcentral-video.yaml tests\unit\test_questions.py tests\unit\test_material_packages.py tests\unit\test_diagnostics.py
```

Do not run coverage-producing commands for an alias-only slice unless the user
explicitly asks. If `.coverage` is already dirty, leave it untouched.

## Go/No-Go

Go if the alias change:

- Adds narrow, explicit location wording for the intended toolbar or menu
  surface.
- Preserves the distinction between media toolbar buttons and media device
  menus.
- Preserves `can_operate=False` and no interrupt step for location-only media
  aliases.
- Includes route, `can_operate`, and interrupt-step assertions for every prompt
  whose behavior can change.
- Keeps diagnostics meaningful and reviews new duplicate, overlap, or substring
  reports.
- Describes the work as deterministic package-routing coverage, not media-state
  execution, readiness, permission safety, provider readiness, or live
  RingCentral acceptance.

No-go if the alias change:

- Turns a location question into mute, unmute, start-video, stop-video, device
  selection, or settings execution without a separate product decision and
  regression tests.
- Blurs toolbar-button phrasing with audio-menu or video-menu device-selection
  phrasing.
- Relies on broad media terms that can steal unrelated Q&A, menu, or answer-only
  routes.
- Claims audio state changed, microphone state changed, camera state changed,
  video state changed, provider readiness, speech readiness, virtual microphone
  readiness, permission safety, or live RingCentral acceptance.
- Touches unrelated source, tests, README, packages, profiles, existing docs,
  generated artifacts, or `.coverage` as part of the alias slice.

Recommended risk level is high. The implementation surface may be a small alias
edit, but the language sits next to stateful meeting controls where a routing
claim can easily be mistaken for live media execution or readiness.
