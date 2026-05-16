# Cycle 089 Risk Scan: RingCentral Video Control Map Camera JA

## Risk Summary

Risk review for adding Japanese `localizedText.ja` to `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-camera`.

This should be a narrow narration-only slice. The future implementation should add only Japanese narration under the existing `control-map-camera` step and preserve:

- the English and Chinese narration text
- `action.entrypointId: ringcentral.video.toolbar.video`
- `action.operation: point`
- `narration.placement: before`
- the step position after `control-map-audio-menu` and before `control-map-camera-menu`

Camera is a high-risk privacy control because the underlying entrypoint is a real local-video toggle. `ringcentral.video.toolbar.video` targets `Start video` with alternate target `Stop video`; clicking it can start camera capture and reveal the user's face, room, background, nearby people, screens, or physical environment. Safe Japanese copy may explain that this button controls whether others can see the user and that the label changes with state, but it must stay point/explain only. Do not imply AiPresenter starts, stops, verifies, previews, records, snapshots, analyzes, or changes camera output unless the user explicitly asks and the visible UI state is verified.

Adjacent context matters. The previous Audio menu step must be cleaned up before camera orientation so the toolbar state is visible. The next Camera menu step is the separate route for camera device choice and video settings; this slice should not open that menu, name camera devices, switch devices, open settings, change background effects, enable blur, or adjust appearance.

## Behavior Boundaries

- Keep this as a point-and-explain step. Do not change `operation: point` to `open`, `toggle`, or any action that executes the `Start video` / `Stop video` button.
- Do not click the camera button during the control-map tour. Starting or stopping local video is a live meeting-state and privacy change.
- Do not infer current camera state from generic text fragments, icon appearance, toolbar position, prior narration, or the existence of the camera control. Treat state as verified only when the UI clearly exposes `Start video` or `Stop video` for the self camera control.
- Do not claim the user's camera is on, off, safe, visible, hidden, blocked, or ready unless visible UI evidence supports that exact claim.
- Do not capture, inspect, summarize, snapshot, screenshot, record, or analyze the local video feed as part of this localization slice.
- Do not mention snapshots or recording as camera-button behavior. Recording is a separate `ringcentral.video.more.recording` entrypoint with consent implications, and screenshots/snapshots are not part of this step.
- Do not read or log camera device names here. Device selection belongs to `control-map-camera-menu` and should remain generic unless explicitly requested.
- Do not open camera settings, More video settings, Background, Blur, virtual backgrounds, video backgrounds, uploads, mirror controls, quality controls, or gallery settings from this step.
- Do not leave the Audio menu, Chat, Participants, Invite, Settings, Report issue, or any other panel open before this step; overlays can obscure toolbar evidence and create false confidence about state.

## Privacy Notes

- The camera button is a direct visual privacy boundary. Starting video can expose face, home or office background, bystanders, whiteboards, screens, documents, or other sensitive room details.
- Camera device names can reveal hardware, workplace setup, virtual camera software, capture cards, or personal devices. Avoid narrating or collecting exact names by default.
- Background effects protect room privacy but can also reveal custom images or persistent appearance preferences. Do not change blur, virtual background, mirror, upload, or video-background settings in this camera-button slice.
- Do not conflate camera visibility with recording. A camera-on state is not consent to record, snapshot, transcribe, summarize, or store visual content.
- Manual validation should prefer sanitized UIA labels and package metadata. Avoid screenshots or logs that include the local preview, participant tiles, device names, meeting identifiers, chat content, or background imagery unless explicitly needed and redacted.

## Required Test Guards

- Localization coverage should advance exactly one Japanese demo step: overall demo coverage from `39/51` to `40/51`, and `meeting-control-map-demo` from `10/22` to `11/22`.
- The first remaining missing `meeting-control-map-demo` Japanese step should move from `control-map-camera` to `control-map-camera-menu`.
- Japanese Q&A counts should remain `12/12` questions and `12/12` answers; `questionAliases.ja` should remain `3/27` entrypoints and `9` aliases unless a separate task explicitly assigns alias work.
- Assert the Japanese text is attached to `meeting-control-map-demo` -> `control-map-camera`, not to `meeting-controls-tour` -> `explain-camera`, Q&A, aliases, presenter notes, Audio menu, Camera menu, Background, Recording, or later control-map steps.
- Assert `control-map-camera.action.entrypoint_id` remains `ringcentral.video.toolbar.video`, `operation` remains `point`, and `narration.placement` remains `before`.
- Assert the camera entrypoint still has one open step targeting `Start video` with `alternateTargets: Stop video` and `controlType: button`; tests should document that this route is a real toggle and must not be executed by the control-map camera step.
- Preserve adapter guards that camera state is extracted from precise self labels and not from split labels such as `Start` / `video` or helper/settings phrases such as `Start video settings` and `Stop video help`.
- Assert adjacent steps remain unchanged: `control-map-audio-menu` stays an `open` step on `ringcentral.video.toolbar.audio-menu` with Escape cleanup, and `control-map-camera-menu` stays an `open` step on `ringcentral.video.toolbar.video-menu` with `actionOffsetMs: 350`.
- Assert the Japanese copy describes camera visibility and the start/stop label relationship without saying AiPresenter will click, start video, stop video, verify the feed, preview the camera, capture snapshots, record, identify people, read device names, change devices, change backgrounds, or open settings.
- If live validation is used, fail review if local video state changes, the camera menu opens during this step, a camera device is selected, camera settings or background effects are changed, a preview/screenshot/snapshot/recording is captured, device names or local video content enter evidence, or an overlay remains open from the previous audio-menu step.
- Japanese `--require-complete` should still fail after this slice because later `meeting-control-map-demo` steps remain untranslated.

## Rollback/Commit Notes

Proceed as a narrow narration-only implementation commit. The safe rollback is to remove only the `localizedText.ja` line/block added under `meeting-control-map-demo` -> `control-map-camera` and revert only directly related test/source-index expectation updates from the same implementation.

Do not rollback or alter other agents' concurrent edits. Before committing, verify the diff contains no YAML changes outside the assigned step except directly necessary coverage expectations or handoff/source-index notes owned by that implementation task.

Recommended commit scope for the implementation owner: "Add JA narration for RingCentral control map Camera." Keep start/stop video behavior, camera-menu behavior, device selection, background effects, recording/snapshot behavior, Q&A edits, aliases, locator changes, settings flows, and broader control-map localization for separate cycles unless explicitly assigned.
