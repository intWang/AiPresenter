# Cycle 088 Demand Analysis

## Verdict/Recommendation

Proceed with a narrow Japanese localization slice for `meeting-control-map-demo` -> `control-map-audio-menu` only.

This step should present the audio menu as a safe recovery orientation surface: where a user can find microphone choice, speaker choice, audio level indicators, computer-audio exit, phone-audio entry, and deeper audio settings when sound is wrong. The Japanese narration should explain the menu's purpose and boundaries without selecting devices, leaving computer audio, joining phone audio, reading device names, interpreting levels, or opening deeper settings unless the user explicitly asks.

Keep the implementation package-content-only for this step. Add `narration.localizedText.ja` to the existing `control-map-audio-menu` step, then update only directly related localization coverage expectations and handoff/source-index notes if assigned to the implementation cycle. Do not change runtime behavior, locators, action operation, aliases, Q&A, adaptive routing, or flow order.

## Current Gap

- Current Japanese demo narration coverage is `38/51`.
- `meeting-control-map-demo` Japanese coverage is `9/22`.
- The first missing Japanese narration step is `meeting-control-map-demo` -> `control-map-audio-menu`.
- Existing localization report expectations now point to:
  - `Localization report: 38/51 demo steps`
  - `- meeting-control-map-demo: 9/22 narration localized`
  - `missing: control-map-audio-menu`
- The existing step uses `entrypointId: ringcentral.video.toolbar.audio-menu`, `operation: open`, `placement: during`, and `actionOffsetMs: 350`. Those presenter semantics should remain unchanged.
- The underlying entrypoint opens the first `More` button and cleans up with Escape. Presenter notes say the observed menu includes Microphone, Speaker, Leave computer audio, Use phone audio, and More audio settings.
- Presenter notes also warn that a system-default-audio-devices toast may appear and should be closed only when visible because its close coordinate overlaps Add coworkers on the clean main screen.

## User Need

Japanese users need the control map to explain where to recover from audio problems without making the recovery action happen for them.

The Japanese text must express these intentions:

- The audio menu is the place to orient around sound recovery when the wrong microphone, wrong speaker, or connection path may be involved.
- The menu can contain microphone and speaker choices, level indicators, computer-audio exit, phone-audio entry, and deeper audio settings.
- The presenter may open the menu to show where these options live, then close it after explanation.
- The narration is orientation, not a device switch, audio-route change, phone-audio join, or settings drill-down.
- Device names, visible audio levels, and system-default-device toasts can reveal private hardware, room, or account context and should not be read aloud, logged, or interpreted unless the user explicitly asks.
- The presenter should not claim the current microphone or speaker is correct, that audio levels are healthy, or that a participant can hear the user based only on the menu being visible.
- Product labels such as `Microphone`, `Speaker`, `Leave computer audio`, `Use phone audio`, and `More audio settings` may remain in English when that best matches the RingCentral UI, but the Japanese narration should sound like calm live guidance.

## Acceptance Criteria

- `control-map-audio-menu` has `narration.localizedText.ja` attached to the existing step in `packages/ringcentral-video.yaml`.
- The existing action and timing remain unchanged:
  - `entrypointId: ringcentral.video.toolbar.audio-menu`
  - `operation: open`
  - `placement: during`
  - `actionOffsetMs: 350`
- The existing audio-menu entrypoint remains unchanged:
  - `target: More`
  - `occurrence: '1'`
  - `controlType: button`
  - `cleanup: escape`
- Japanese demo narration coverage advances from `38/51` to `39/51`.
- `meeting-control-map-demo` advances from `9/22` to `10/22`.
- The first remaining missing Japanese step for `meeting-control-map-demo` becomes `control-map-camera`.
- Japanese `--require-complete` still fails because later control-map steps remain untranslated.
- Q&A localization counts remain unchanged at `12/12` localized questions and `12/12` localized answers.
- `questionAliases.ja` coverage remains unchanged unless a separate task explicitly requests alias work.
- The localized narration identifies the audio menu as the recovery surface for microphone/speaker selection, computer audio, phone audio, audio levels, and deeper audio settings.
- The localized narration includes privacy boundaries around device names, audio levels, system-default-device toast content, and explicit user request.
- The localized narration must not say or imply:
  - AiPresenter selects, changes, confirms, or recommends a microphone or speaker;
  - AiPresenter leaves computer audio or joins phone audio;
  - AiPresenter opens More audio settings or changes settings beyond this menu orientation;
  - device names, level values, toast content, meeting identifiers, or account details are read aloud by default;
  - audio levels prove sound quality, audibility, or correct routing;
  - RingCentral meeting audio state is changed without explicit user intent and visible UI verification.

## Non-goals

- Do not localize `control-map-camera` or any later `meeting-control-map-demo` step in this slice.
- Do not change `operation: open`, placement, offset, locator references, open steps, cleanup behavior, adaptive meeting-state behavior, or demo sequencing.
- Do not add or modify Japanese aliases, Q&A, presenter notes, manual controls, profile settings, runtime behavior, diagnostics logic, CLI formatting, or source data beyond directly required count expectations and documentation notes.
- Do not broaden this slice into actual microphone selection, speaker selection, audio tests, audio capture, phone-audio joining, computer-audio leaving, device-name reading, level interpretation, settings changes, camera controls, sharing, reactions, More, recording, Notes, background, settings, security, host controls, or leave behavior.
- Do not capture screenshots, logs, transcripts, or manual validation evidence that exposes participant names, meeting identifiers, device names, audio levels, toast text, or spoken content unless explicitly required and sanitized.

## Suggested Next Slice

After `control-map-audio-menu` is localized and reviewed, continue `meeting-control-map-demo` Japanese coverage with `control-map-camera` as the next isolated slice.

That next slice should explain the camera button as the visible video privacy and readiness control, while preserving explicit-user-request boundaries before starting or stopping video and keeping camera device selection separate for `control-map-camera-menu`.
