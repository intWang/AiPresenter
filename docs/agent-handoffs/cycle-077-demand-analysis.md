# Cycle 077 Demand Analysis: JA Settings Narration

Date: 2026-05-16

## Verdict/Recommendation

Proceed with a narrow Japanese narration slice for `meeting-controls-tour` -> `explain-settings`.

This should be a package-content localization pass only. The step opens the general `Settings` dialog from the More menu and should explain that Settings is the complete configuration area for RingCentral Video meeting preferences. The Japanese narration must describe the entry point and scope, then preserve user control over every configuration change.

## Current Gap

- Current Japanese demo narration coverage should remain `27/51` before this slice.
- Current `meeting-controls-tour` Japanese narration coverage should remain `20/22` before this slice.
- The next missing controls-tour step is `explain-settings`.
- Remaining missing controls-tour steps are `explain-settings` and `explain-leave`.
- Japanese Q&A remains complete at `12/12` questions and `12/12` answers.
- Japanese aliases remain unchanged at `3/27` entrypoints and `9` aliases.
- `docs/knowledge/ringcentral-video/source-index.md` currently says Japanese coverage includes the first twenty controls-tour steps through `background-settings`.
- `tests/unit/test_cli.py` currently expects `Localization report: 27/51 demo steps`, `- meeting-controls-tour: 20/22 narration localized`, and `missing: explain-settings` for Japanese.
- `tests/unit/test_material_packages.py` currently expects Japanese report totals of `27/51` and controls-tour `20/22`.
- The source step has English and Chinese narration but no Japanese narration:
  - Step: `meeting-controls-tour` -> `explain-settings`.
  - Entrypoint: `ringcentral.video.more.settings`.
  - Operation: `open`.
  - Placement: `during`.
  - `actionOffsetMs`: `400`.
  - English intent: `Settings is the complete configuration area: audio, video, background, translation, join preferences, and general meeting preferences.`
- The related entrypoint `ringcentral.video.more.settings` opens More -> Settings and has `cleanup: settings`.
- Entrypoint notes say the Settings dialog may open to the current or last selected section, and should be used as the general route for audio, video, background, translation, join preferences, and general settings.
- This step is broader than `explain-background-settings`; it should not read like a Background-only continuation or a blur/background action.

## User Need

Japanese users need the controls tour to explain where the general Settings dialog lives and what kinds of meeting preferences it covers. Because Settings can affect devices, camera behavior, background appearance, translation-related preferences, join behavior, and broader meeting behavior, the narration should help users understand the configuration hub without implying that AiPresenter will make durable preference changes on their behalf.

The Japanese narration must express these intentions:

- `Settings` is opened from the More menu.
- `Settings` is the complete configuration area, not a single-feature panel.
- Its scope includes audio, video, background, translation, join preferences, and general meeting preferences.
- The step is a tour/navigation action that explains the location and range of configuration categories.
- AiPresenter must not change microphone or speaker devices, camera/video settings, background effects, translation preferences, join preferences, or general meeting settings unless the user clearly asks for that specific change.
- Since Settings may open to the current or last selected section, the narration should avoid claiming that a specific tab is always selected by default.
- After explaining the surface, the tour should close the Settings dialog before continuing.

## Acceptance Criteria

- Add `localizedText.ja` only under `packages/ringcentral-video.yaml` -> `meeting-controls-tour` -> `explain-settings` -> `narration`.
- Preserve `entrypointId: ringcentral.video.more.settings`.
- Preserve `operation: open`; do not convert it to a selecting, toggling, or applying action.
- Preserve `placement: during` and `actionOffsetMs: 400`.
- Preserve the existing More -> Settings route and `cleanup: settings` behavior.
- Japanese demo narration should advance from `27/51` to `28/51`.
- `meeting-controls-tour` Japanese narration should advance from `20/22` to `21/22`.
- First missing controls-tour step should advance from `explain-settings` to `explain-leave`.
- Remaining missing controls-tour step should become only `explain-leave`.
- Japanese Q&A and alias counts should remain unchanged.
- Japanese `--require-complete` should still fail because later Japanese demo narration gaps remain.
- Japanese text should be authored Japanese text, not copied English or Chinese.
- Japanese text should include the UI label `Settings` and enough category labels or Japanese terms to cover audio, video, background, translation, join preferences, and general meeting preferences.
- Japanese text should include safety wording that the tour explains the location/scope only and does not change settings unless the user clearly requests it.
- Japanese text should mention closing the Settings dialog after explanation.
- Focused tests may assert the unchanged entrypoint/action/placement/offset, Japanese CJK presence, required labels/intent terms, and forbidden phrases that imply applying, selecting, toggling, switching, saving, or automatically changing settings.
- `source-index.md` may be updated in the implementation cycle to say controls-tour Japanese coverage now reaches the first twenty-one steps through Settings.

## Non-goals

- Do not localize `explain-leave` in this slice.
- Do not change the already localized `explain-background-settings`, `explain-notes`, `explain-recording`, `explain-more`, or any earlier controls-tour Japanese narration.
- Do not modify English or Chinese narration unless a separate review scopes it.
- Do not alter operation entrypoints, open-step routes, cleanup behavior, locators, runtime behavior, diagnostics behavior, CLI behavior, or telemetry.
- Do not add Japanese aliases or new Q&A.
- Do not select or change audio devices, speaker devices, microphone behavior, camera devices, video settings, background settings, translation settings, join preferences, or general meeting preferences.
- Do not imply that AiPresenter can decide the correct device, camera, background, translation language, join behavior, or meeting preference without a user request and verified visible context.
- Do not claim a specific Settings tab is guaranteed to open first, because current notes say Settings may open to the current or last selected section.
- Do not merge this with `explain-background-settings`; that step covers the Background tab, while this step covers the full Settings configuration surface.
- Do not expose or read private device names, personal backgrounds, translation/caption content, meeting details, or preference values unless the user explicitly asks and visible context is verified.

## Suggested Next Slice

After this step is localized and reviewed, localize `meeting-controls-tour` -> `explain-leave` as the final Japanese narration slice for the controls tour. Keep it separate because Leave is a destructive meeting-exit control and needs confirmation-focused wording rather than configuration-safety wording.
