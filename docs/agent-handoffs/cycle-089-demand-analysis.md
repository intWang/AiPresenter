# Cycle 089 Demand Analysis: RingCentral Video Control Map Camera JA

## Verdict/Recommendation

Proceed with a narrow Japanese localization slice for `meeting-control-map-demo` -> `control-map-camera` only.

Frame the camera button as a local video visibility and privacy checkpoint. The Japanese narration should help the presenter orient the user to the visible camera state and the `Start video` / `Stop video` control area without implying AiPresenter starts video, stops video, captures frames, records, changes devices, applies background effects, or infers who can see whom beyond what the visible UI indicates.

Keep this as narration-only package content. The next implementer should add `narration.localizedText.ja` to the existing `control-map-camera` step and update only directly related localization expectations and documentation notes if assigned. Do not change runtime behavior, locators, action operation, aliases, Q&A, flow order, or adjacent camera-menu behavior.

## Current Gap

- Current Japanese demo narration coverage is `39/51`.
- `meeting-control-map-demo` Japanese coverage is `10/22`.
- The first missing Japanese narration step is `meeting-control-map-demo` -> `control-map-camera`.
- The existing step uses `entrypointId: ringcentral.video.toolbar.video`, `operation: point`, and `placement: before`.
- The underlying entrypoint targets the `Start video` button with alternate target `Stop video`; the package purpose says it toggles the local camera on or off.
- Presenter notes say the button text alternates between `Start video` and `Stop video`, and the caret next to it exposes camera and video settings.
- Camera menu/device/background coverage is separate in the next step, `control-map-camera-menu`, and should not be pulled into this slice.

## User Need

Japanese users need a calm explanation of how to check their local video privacy state before presenting or joining visually.

The Japanese text should express these intentions:

- The camera button is the visible place to check whether local video is currently off or on.
- `Start video` / `Stop video` labels are state cues and privacy cues, not a promise that AiPresenter will click them.
- The presenter may point to this control to orient the user before any video action.
- Any action that starts or stops local video requires an explicit user request plus visible UI verification.
- The narration should avoid claiming that AiPresenter knows exactly who can see the user, whether remote participants are watching, or whether video is being recorded.
- Camera names, selected devices, camera menu contents, background effects, and deeper video settings are private or separate surfaces and should stay out of this step unless explicitly requested in the later camera-menu slice.

## Acceptance Criteria

- `control-map-camera` has `narration.localizedText.ja` attached to the existing step in `packages/ringcentral-video.yaml`.
- The existing action semantics remain unchanged:
  - `entrypointId: ringcentral.video.toolbar.video`
  - `operation: point`
  - `placement: before`
- The existing camera entrypoint remains unchanged:
  - target `Start video`
  - alternate target `Stop video`
  - `controlType: button`
- Japanese demo narration coverage advances from `39/51` to `40/51`.
- `meeting-control-map-demo` advances from `10/22` to `11/22`.
- The first remaining missing Japanese step for `meeting-control-map-demo` becomes `control-map-camera-menu`.
- Japanese `--require-complete` still fails because later control-map steps remain untranslated.
- Q&A localization counts remain `12/12` localized questions and `12/12` localized answers.
- `questionAliases.ja` coverage remains unchanged unless a separate task explicitly requests alias work.
- The localized narration includes camera/video privacy language around local video state, visible UI verification, and explicit user request.
- The localized narration must not say or imply:
  - AiPresenter starts video, stops video, toggles the camera, captures frames, records, or changes camera devices;
  - AiPresenter reads camera names, opens the camera menu, changes background effects, or changes video settings;
  - the presenter can infer who is watching, who sees whom, participant attention, recording status, or remote visibility beyond the visible local control state;
  - video state is changed automatically or without explicit user intent and visible UI confirmation.

## Non-goals

- Do not localize `control-map-camera-menu` or any later `meeting-control-map-demo` step in this slice.
- Do not change `operation: point`, placement, locator references, open steps, adaptive meeting-state behavior, cleanup behavior, or demo sequencing.
- Do not add or modify Japanese aliases, Q&A, presenter notes, manual controls, profile settings, runtime behavior, diagnostics logic, CLI formatting, or source data beyond directly required count expectations and documentation notes.
- Do not broaden this slice into camera-device selection, camera names, background effects, More video settings, screenshot capture, video recording, participant visibility inference, sharing, reactions, More, Notes, settings, security, host controls, or leave behavior.
- Do not capture screenshots, logs, transcripts, or manual evidence that exposes participant names, meeting identifiers, camera names, device lists, video thumbnails, or background previews unless explicitly required and sanitized.

## Suggested Next Slice

After `control-map-camera` is localized and reviewed, continue `meeting-control-map-demo` Japanese coverage with `control-map-camera-menu` as the next isolated slice.

That next slice should explain the camera menu as the route for camera selection and video settings while preserving privacy boundaries around camera names, selected devices, background effects, and explicit user request before any device or appearance change.
