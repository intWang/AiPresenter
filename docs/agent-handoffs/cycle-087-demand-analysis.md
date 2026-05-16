# Cycle 087 Demand Analysis

## Verdict/Recommendation

Proceed with a narrow Japanese localization slice for `meeting-control-map-demo` -> `control-map-microphone` only.

This step should explain the microphone button as the media privacy and speaking-readiness checkpoint. The Japanese narration should help a presenter point to where mute/unmute readiness is checked before speaking, while making clear that the tour does not mute, unmute, toggle local audio, capture audio, change devices, infer who can hear whom, or read device names without an explicit user request and verified UI state.

Keep the implementation package-content-only for this step. Add `narration.localizedText.ja` to the existing `control-map-microphone` step, then update only directly related localization coverage expectations and handoff/source-index notes if assigned to the implementation cycle. Do not change runtime behavior, locators, action operation, aliases, Q&A, adaptive routing, or flow order.

## Current Gap

- Current Japanese demo narration coverage is `37/51`.
- `meeting-control-map-demo` Japanese coverage is `8/22`.
- The first missing Japanese narration step is `meeting-control-map-demo` -> `control-map-microphone`.
- Existing localization report expectations now point to:
  - `Localization report: 37/51 demo steps`
  - `- meeting-control-map-demo: 8/22 narration localized`
  - `missing: control-map-microphone`
- The existing step uses `entrypointId: ringcentral.video.toolbar.audio`, `operation: point`, and `placement: before`. Those presenter semantics should remain unchanged.
- The underlying entrypoint route is the microphone control, whose button label alternates between `Mute` and `Unmute`; this slice should not modify locator behavior or convert the control-map explanation into a state-changing demo.
- Japanese aliases already exist for the audio entrypoint: `マイク`, `ミュート`, and `音声`. This demand is for localized flow narration, not alias expansion.

## User Need

Japanese users need the control map to move naturally from Chat into media readiness and understand where to check speaking readiness before contributing to a live meeting.

The Japanese text must express these intentions:

- The microphone button is the primary privacy control for local speaking audio.
- Before speaking, the presenter checks the visible mute/unmute state as readiness information.
- The step explains where the state is checked; it does not perform mute or unmute.
- Mic state is local, privacy-sensitive UI state and should be described only from verified UI labels.
- The presenter must not record, sample, or claim to hear microphone audio.
- The presenter must not infer who can hear whom, whether audio is actually reaching participants, or whether sound quality is good from the button alone.
- Device names, input levels, microphone selection, speaker selection, phone audio, and computer-audio changes belong to the next `control-map-audio-menu` slice, not this microphone button slice.
- Product labels such as `Mute`, `Unmute`, and `Microphone` may remain in English when that best matches the RingCentral UI, but the Japanese narration should sound like natural live presenter guidance.

## Acceptance Criteria

- `control-map-microphone` has `narration.localizedText.ja` attached to the existing step in `packages/ringcentral-video.yaml`.
- The existing action block remains unchanged:
  - `entrypointId: ringcentral.video.toolbar.audio`
  - `operation: point`
  - `placement: before`
- The existing audio entrypoint aliases remain unchanged:
  - `マイク`
  - `ミュート`
  - `音声`
- Japanese demo narration coverage advances from `37/51` to `38/51`.
- `meeting-control-map-demo` advances from `8/22` to `9/22`.
- The first remaining missing Japanese step for `meeting-control-map-demo` becomes `control-map-audio-menu`.
- Japanese `--require-complete` still fails because later control-map steps remain untranslated.
- Q&A localization counts remain unchanged at `12/12` localized questions and `12/12` localized answers.
- `questionAliases.ja` coverage remains unchanged unless a separate task explicitly requests alias work.
- The localized narration identifies the microphone button as the place to check local mute/unmute readiness before speaking.
- The localized narration includes privacy boundaries around mic state, verified UI labels, audio capture, device names, and explicit user request.
- The localized narration must not say or imply:
  - AiPresenter clicks, mutes, unmutes, or toggles the microphone during this step;
  - the microphone is turned on or off by the narration;
  - audio is being recorded, sampled, monitored, or analyzed;
  - AiPresenter can tell who can hear whom from this control alone;
  - sound quality, input level, or device correctness is verified by the button alone;
  - microphone or speaker devices are selected, changed, or named;
  - the audio menu is opened in this slice;
  - RingCentral meeting media state is changed without explicit user intent and visible UI verification.

## Non-goals

- Do not localize `control-map-audio-menu` or any later `meeting-control-map-demo` step in this slice.
- Do not change `operation: point`, placement, locator references, open steps, cleanup behavior, adaptive meeting-state behavior, or demo sequencing.
- Do not add or modify Japanese aliases, Q&A, presenter notes, manual controls, profile settings, runtime behavior, diagnostics logic, CLI formatting, or source data beyond directly required count expectations and documentation notes.
- Do not broaden this slice into microphone/speaker device recovery, audio level indicators, leave-computer-audio, phone audio, audio settings, camera controls, sharing, reactions, More, recording, Notes, background, settings, security, host controls, or leave behavior.
- Do not perform live mute/unmute toggles, audio capture, audio recording, device selection, device-name reading, participant audibility claims, or audio troubleshooting actions as part of this localization demand slice.

## Suggested Next Slice

After `control-map-microphone` is localized and reviewed, continue `meeting-control-map-demo` Japanese coverage with `control-map-audio-menu` as the next isolated slice.

That next slice should explain the microphone arrow/audio menu as the recovery surface for microphone choice, speaker choice, computer audio, phone audio, and deeper audio settings, while preserving explicit-user-request boundaries before changing devices or reading device names.
