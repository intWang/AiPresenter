# Cycle 088 Risk Scan: RingCentral Video Control Map Audio Menu JA

## Risk Summary

Risk review for adding Japanese `localizedText.ja` to `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-audio-menu`.

This should be a narrow narration-only slice. The future implementation should add only Japanese narration under the existing `control-map-audio-menu` step and preserve:

- the English and Chinese narration text
- `action.entrypointId: ringcentral.video.toolbar.audio-menu`
- `action.operation: open`
- `narration.placement: during`
- `narration.actionOffsetMs: 350`
- the step position after `control-map-microphone` and before `control-map-camera`

Audio menu is higher risk than the previous microphone point step because it intentionally opens a live device menu. The menu exposes microphone and speaker choices, audio level indicators, `Leave computer audio`, `Use phone audio`, and `More audio settings`. Safe Japanese copy may describe the menu as a recovery surface for wrong sound or device setup, but it must stay explain-only: do not imply AiPresenter selects devices, reads device names, samples levels, changes audio routes, leaves computer audio, uses phone audio, or opens settings unless the user explicitly asks and the visible UI state is verified.

The underlying entrypoint targets the first toolbar `More` button with `cleanup: escape`. That first occurrence must remain distinct from the camera menu's second `More` and the overflow menu's third `More`. A system-default-audio-devices toast may appear; it should be closed only when visible because the toast close coordinate overlaps `Add coworkers` on a clean main screen.

## Behavior Boundaries

- Keep this as an open-and-explain step. Do not select any microphone, speaker, phone-audio, leave-computer-audio, or settings item during the control-map tour.
- Preserve `operation: open`, `placement: during`, and `actionOffsetMs: 350`; the narration is meant to run after the menu is visible, not as a pre-click privacy warning.
- Preserve the `ringcentral.video.toolbar.audio-menu` route: `clickWindowControl`, target `More`, `occurrence: '1'`, `controlType: button`, and `cleanup: escape`.
- Do not change `ringcentral.video.toolbar.audio`; the previous `control-map-microphone` step remains the mute/readiness privacy checkpoint and must not become a menu opener.
- Do not change the camera menu or overflow menu locators; `occurrence: '2'` remains camera settings and `occurrence: '3'` remains More actions.
- Do not infer that the selected microphone or speaker is correct, active, audible, quiet, loud, muted, or broken from menu presence alone.
- Do not claim that audio levels were measured, that sound quality was diagnosed, or that participants can hear the user.
- Do not leave the audio menu open before moving to `control-map-camera`; Escape cleanup should return the toolbar to a neutral state.
- Do not let the audio menu overlap with a Chat or Participants side panel, an Invite dialog, a Report dialog, Settings, or a camera menu. The preceding steps should already be cleaned up before this slice runs.

## Privacy Notes

- Device names can reveal hardware, workplace, user identity, room setup, or virtual audio software. The localized narration should mention device choice generically and should not read actual device labels by default.
- Audio level indicators can expose whether the local environment is producing sound. Do not sample, log, narrate, screenshot, or assert level activity unless the user explicitly requests troubleshooting and the evidence is minimized.
- `Leave computer audio` and `Use phone audio` are meeting audio-route changes. They can disconnect local computer audio or expose dial-in/phone context, so the tour should identify them as options without activating them.
- `More audio settings` can reveal deeper device preferences and permissions. Opening it belongs to a separate explicit settings task, not this localization slice.
- A system-default-device toast is transient UI evidence, not content to narrate. Handle it only as cleanup when visible; do not click its close area speculatively.

## Required Test Guards

- Localization coverage should advance exactly one step: overall Japanese demo coverage from `38/51` to `39/51`, and `meeting-control-map-demo` from `9/22` to `10/22`.
- The first remaining missing `meeting-control-map-demo` Japanese step should move from `control-map-audio-menu` to `control-map-camera`.
- Japanese Q&A counts should remain `12/12` questions and `12/12` answers; `questionAliases.ja` should remain `3/27` entrypoints and `9` aliases unless a separate task explicitly assigns alias work.
- Assert the Japanese text is attached to `meeting-control-map-demo` -> `control-map-audio-menu`, not to `meeting-controls-tour` -> `explain-audio-menu`, Q&A, aliases, presenter notes, microphone, camera, or later control-map steps.
- Assert `control-map-audio-menu.action.entrypoint_id` remains `ringcentral.video.toolbar.audio-menu`, `operation` remains `open`, `placement` remains `during`, and `action_offset_ms` remains `350`.
- Assert the audio-menu entrypoint still has one open step targeting `More` with `occurrence: '1'`, `controlType: button`, and `cleanup: escape`.
- Assert presenter notes still list `Microphone`, `Speaker`, `Leave computer audio`, `Use phone audio`, and `More audio settings`, and still preserve the system-default-device-toast warning.
- Assert adjacent media steps remain unchanged: `control-map-microphone` stays a `point` step on `ringcentral.video.toolbar.audio`; `control-map-camera` stays a `point` step on `ringcentral.video.toolbar.video`; `control-map-camera-menu` stays an `open` step on `ringcentral.video.toolbar.video-menu`.
- Assert the Japanese copy describes audio-menu recovery without saying AiPresenter will select, switch, change, test, monitor, measure, diagnose, read device names, leave computer audio, use phone audio, open settings, or keep the menu open.
- If live validation is used, fail review if a device is selected, audio route changes, computer audio is left, phone audio is opened, audio settings is opened, device names or audio levels are captured in evidence, the toast close coordinate is clicked when no toast is visible, or the audio menu remains open before the camera step.
- Japanese `--require-complete` should still fail after this slice because later `meeting-control-map-demo` steps remain untranslated.

## Rollback/Commit Notes

Proceed as a narrow narration-only implementation commit. The safe rollback is to remove only the `localizedText.ja` line/block added under `meeting-control-map-demo` -> `control-map-audio-menu` and revert only directly related test/source-index expectation updates from the same implementation.

Do not rollback or alter other agents' concurrent edits. Before committing, verify the diff contains no YAML changes outside the assigned step except directly necessary coverage expectations or handoff/source-index notes owned by that implementation task.

Recommended commit scope for the implementation owner: "Add JA narration for RingCentral control map Audio menu." Keep device selection behavior, audio-route changes, audio-level capture, toast automation changes, aliases, Q&A, locators, settings flows, camera steps, and broader control-map localization for separate cycles unless explicitly assigned.
