# Cycle 076 Demand Analysis: JA Background Settings Narration

Date: 2026-05-16

## Verdict/Recommendation

Proceed with a narrow Japanese narration slice for `meeting-controls-tour` -> `explain-background-settings`.

This should be a package-content localization pass only. The step is a Background settings entry point from the More menu, not the virtual-background blur demo and not a command to apply any visual effect. The Japanese copy should explain where the Background settings panel is and what kinds of choices it contains, while preserving user control over any visible appearance change.

## Current Gap

- Current Japanese demo narration coverage is expected to remain `26/51`.
- Current `meeting-controls-tour` Japanese narration coverage is expected to remain `19/22`.
- The next missing controls-tour step is `explain-background-settings`.
- Remaining missing controls-tour steps are `explain-background-settings`, `explain-settings`, and `explain-leave`.
- Japanese Q&A remains complete at `12/12` questions and `12/12` answers.
- Japanese aliases remain unchanged at `3/27` entrypoints and `9` aliases.
- `docs/knowledge/ringcentral-video/source-index.md` currently says Japanese coverage includes the first nineteen controls-tour steps through Notes.
- `tests/unit/test_cli.py` currently expects `Localization report: 26/51 demo steps`, `- meeting-controls-tour: 19/22 narration localized`, and `missing: explain-background-settings` for Japanese.
- `tests/unit/test_material_packages.py` currently expects Japanese report totals of `26/51` and controls-tour `19/22`.
- The source step has English and Chinese narration but no Japanese narration:
  - Step: `meeting-controls-tour` -> `explain-background-settings`.
  - Entrypoint: `ringcentral.video.more.background`.
  - Operation: `open`.
  - Placement: `during`.
  - `actionOffsetMs`: `400`.
  - English intent: Background opens visual presentation settings; the user can turn effects off, blur the room, choose a built-in background, use a video background, or upload their own.
- Related but distinct entrypoints:
  - `ringcentral.video.more.background` opens the Settings dialog directly on the Background tab.
  - `ringcentral.video.settings.background.blur` is the actual Blur selection action and should be used only when the user wants the presenter to change the local background effect.
- Existing `vbg-blur-demo` already has Japanese text for opening the Background panel, selecting Blur, and verifying blur. This slice should not restate that demo as if this controls-tour step applies Blur.

## User Need

Japanese users need the long controls tour to explain how to find Background settings from More without accidentally implying that AiPresenter will change their camera appearance. Background controls affect presentation quality and privacy, but they also change the visible local video tile and may involve personal or branded images. The tour should make the surface understandable while keeping the decision to disable effects, blur the room, choose a built-in image or video, or upload an asset with the user.

The Japanese narration must express these intentions:

- `Background` opens the Background settings area from the More menu.
- The area is for visual presentation and privacy-related camera background choices.
- The available options can include turning effects off, Blur, built-in backgrounds, video backgrounds, and custom uploads.
- Opening the panel is only a tour/navigation action.
- AiPresenter should not choose a background, apply Blur, upload an image, switch to a video background, or otherwise change the visible appearance unless the user explicitly confirms that action.
- If the panel or menu is open and more explanation is needed, the assistant may describe the options, then wait for user confirmation before operating any option.

## Acceptance Criteria

- Add `localizedText.ja` only under `packages/ringcentral-video.yaml` -> `meeting-controls-tour` -> `explain-background-settings` -> `narration`.
- Preserve `entrypointId: ringcentral.video.more.background`.
- Preserve `operation: open`; do not convert it to `select` or point it at the Blur entrypoint.
- Preserve `placement: during` and `actionOffsetMs: 400`.
- Japanese demo narration should advance from `26/51` to `27/51`.
- `meeting-controls-tour` Japanese narration should advance from `19/22` to `20/22`.
- First missing controls-tour step should advance from `explain-background-settings` to `explain-settings`.
- Remaining missing controls-tour steps should become `explain-settings` and `explain-leave`.
- Japanese Q&A and alias counts should remain unchanged.
- Japanese `--require-complete` should still fail because later Japanese demo narration gaps remain.
- Japanese text should be authored Japanese text, not copied English or Chinese.
- Japanese text should include enough UI labels to keep the route clear, especially `Background`, and may keep option labels such as `Blur` where useful.
- Japanese text should identify this as the Background settings area for visual presentation/privacy, not as the blur demo.
- Japanese text should mention the range of available choices without promising to make a choice.
- Japanese text should explicitly avoid automatic background changes and require user confirmation before applying an effect, selecting a background, uploading an image, or changing appearance.
- Focused tests may assert the unchanged entrypoint/action/placement/offset, Japanese CJK presence, required labels/intent terms, and forbidden phrases that imply selecting Blur, uploading, clicking, pressing, or changing the background automatically.
- `source-index.md` may be updated in the implementation cycle to say controls-tour Japanese coverage now reaches the first twenty steps through Background settings.

## Non-goals

- Do not localize `explain-settings` or `explain-leave` in this slice.
- Do not change the already localized `explain-notes`, `explain-recording`, `explain-more`, or camera-menu Japanese narration.
- Do not modify English or Chinese narration unless a separate review scopes it.
- Do not alter operation entrypoints, open-step routes, cleanup behavior, locators, runtime behavior, diagnostics behavior, CLI behavior, or telemetry.
- Do not add Japanese aliases or new Q&A.
- Do not select `Blur`, turn effects off, choose a built-in image, choose a video background, upload a custom image, toggle Mirror my video, or otherwise change the user's visible appearance.
- Do not merge this with `vbg-blur-demo`; that flow demonstrates selecting Blur, while this step only explains the Background settings entry point in the broader controls tour.
- Do not claim AiPresenter can judge whether a background is appropriate, branded, private, or compliant without user direction or visible context.
- Do not use live screenshots, logs, or examples that expose a user's room, face, uploaded image, company branding, or meeting details.

## Suggested Next Slice

After this step is localized and reviewed, localize `meeting-controls-tour` -> `explain-settings` as its own Japanese narration slice. Keep it separate from Background settings because the general Settings surface covers audio, video, background, translation, join preferences, and meeting behavior, and it needs broader configuration-safety wording than this Background-specific entry point.
