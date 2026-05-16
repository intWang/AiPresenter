# Cycle 076 Risk Scan: explain-background-settings JA Narration

Date: 2026-05-16

## Risk Summary

Risk review for adding Japanese `localizedText.ja` to `packages/ringcentral-video.yaml` -> `meeting-controls-tour` -> `explain-background-settings`.

This handoff is documentation-only. The future implementation should add only the Japanese narration under the existing step and preserve:

- `entrypointId: ringcentral.video.more.background`
- `operation: open`
- `placement: during`
- `actionOffsetMs: 400`
- the existing `ringcentral.video.more.background.openSteps` route through `More` occurrence `3` to `Background`
- `cleanup: settings` on the Background route

The current step opens the Settings dialog directly on the Background tab and explains visual presentation options: Off, Blur, built-in backgrounds, video backgrounds, and custom upload. That is lower risk than recording or notes, but it still touches camera appearance, room privacy, custom images, and persistent user preferences.

The main risk is scope creep from "explain the Background settings entrance" into "perform a background change." `vbg-blur-demo` already owns the explicit blur-selection path through `ringcentral.video.settings.background.blur`. This cycle should not select Blur, turn effects off, choose built-in media, open upload, upload a file, toggle Mirror my video, or verify the live tile after a visual change.

## Behavior Boundaries

- Keep `explain-background-settings` as a route-and-explain step. It may open Background settings and describe available choices.
- Do not change the user's camera appearance from this step. Selecting `Blur`, `Off`, a built-in image, a video background, a custom upload, or `Mirror my video` is outside this localization slice.
- Do not reuse the `vbg-blur-demo` action semantics. `vbg-blur-demo` has `select-blur` with `entrypointId: ringcentral.video.settings.background.blur`, `operation: select`, and a later live-video verification step. `explain-background-settings` has only `entrypointId: ringcentral.video.more.background`, `operation: open`.
- Keep wording neutral and capability-focused: Background settings let the user turn effects off, blur the room, choose built-in image/video backgrounds, or upload their own background.
- Include the safety boundary in Japanese: AiPresenter is explaining the location and options, and does not apply or upload a background unless the user clearly asks.
- Do not add aliases, Q&A entries, locators, cleanup behavior, runtime policies, state extraction, or tests as part of this risk-scan task.
- Do not change `ringcentral.video.settings.background`, `ringcentral.video.settings.background.blur`, `ringcentral.video.more.settings`, `vbg-blur-demo`, `meeting-control-map-demo`, or neighboring `meeting-controls-tour` steps in this slice.

## Privacy Notes

- Opening Background settings can expose the presenter's real room preview, current camera state, selected effect, and possibly recognizable custom background thumbnails.
- The custom upload tile is privacy-sensitive because it can reveal local files, personal images, company branding, or folder/file picker information if activated. The tour must not open upload or file picker UI.
- Built-in image and video backgrounds are still visible presentation changes. The narration can mention them as options, but should not imply automatic selection.
- Blur is privacy-protective, but selecting it still changes the user's local video appearance. That action remains reserved for `vbg-blur-demo` or an explicit user request.
- Settings tabs can expose adjacent device names and preferences if navigation drifts into Audio, Video, Translation, Join preferences, or General. The step should stay on Background and cleanly close Settings before continuing.
- Test evidence and handoff notes should avoid screenshots or logs that show room details, custom thumbnails, file names, account information, device names, or participants' private meeting context.

## Required Test Guards

- Localization coverage should advance only the expected Japanese narration count for `meeting-controls-tour`; the first missing controls-tour step should move from `explain-background-settings` to `explain-settings`.
- Assert the new Japanese text is attached to `meeting-controls-tour` -> `explain-background-settings`, not to `vbg-blur-demo`, `control-map-background`, Q&A, or entrypoint aliases.
- Assert the step still uses `entrypointId: ringcentral.video.more.background` and `operation: open`.
- Assert no Japanese wording says AiPresenter selects Blur, turns effects off, applies a built-in background, uses a video background, uploads a custom background, opens a file picker, toggles Mirror my video, verifies live video, or changes camera appearance by default.
- Assert `vbg-blur-demo` remains unchanged: four localized steps, `select-blur` still uses `ringcentral.video.settings.background.blur`, and the demo remains the only existing flow that intentionally performs blur selection.
- Assert cleanup expectations remain Settings-dialog cleanup only. Tests should not require or imply a new side-panel cleanup, live tile verification, or persistent preference restoration for this tour step.
- Keep existing Chinese text and English narration intact unless a separate implementation owner explicitly changes them.
- If CLI coverage tests are updated by the implementation owner, expected totals should reflect one additional Japanese-localized demo step and no broader package-content changes.

## Rollback/Commit Notes

Proceed as a narrow narration-only commit. The safe rollback is to remove only the `localizedText.ja` line/block added under `meeting-controls-tour` -> `explain-background-settings`.

Do not rollback or alter other agents' concurrent edits. Before committing, verify the diff contains only the intended Japanese narration and any directly necessary test expectation updates owned by the implementation task. This risk scan itself intentionally changes only `docs/agent-handoffs/cycle-076-risk-scan.md`.

Recommended commit scope for the implementation owner: "Add JA narration for RingCentral background settings tour step." Keep live route confidence, locator updates, upload behavior, `vbg-blur-demo` behavior, privacy-matrix updates, and broader Settings/Leave localization for separate cycles.
