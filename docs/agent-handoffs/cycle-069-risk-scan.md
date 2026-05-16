# Cycle 069 Risk Scan: explain-camera-menu JA Narration

Date: 2026-05-16

## Scope

Risk review for adding Japanese `localizedText.ja` to `meeting-controls-tour` -> `explain-camera-menu`.

The owned implementation should remain narration-only and preserve `operation: open`.

## Key Risks

1. **Camera device names**
   - Camera menus may expose hardware, virtual camera, room-system, or driver names.
   - Narration and evidence should stay generic and never read exact device labels by default.

2. **Background and room privacy**
   - Background settings can reveal the presenter's room, custom background assets, or visual privacy preferences.
   - The narration may mention the background path, but must not claim AiPresenter will change it.

3. **Persistent video preferences**
   - More video settings may include durable camera, quality, appearance, or join-preference settings.
   - Do not imply settings are changed without explicit user instruction.

4. **Low-confidence `More` occurrence**
   - `ringcentral.video.toolbar.video-menu` uses the second visible `More` control.
   - It was observed only in one empty-room, en-US, 100% DPI state.
   - This localization pass must not upgrade live confidence.

5. **Boundary with main camera button**
   - Cycle 068 owns `Start video` / `Stop video` on/off explanation.
   - Camera-menu narration should not suggest toggling local camera state.

## Mitigations

- Keep `operation: open` and existing `actionOffsetMs`.
- Do not change locators, open steps, cleanup, aliases, Q&A, runtime routing, or state extraction.
- Frame camera selection, background, and video settings as menu capabilities only.
- Explicitly say AiPresenter does not switch cameras or change background/video settings without clear user instruction.
- Close the menu after explanation.
- Leave live acceptance of `More` occurrence behavior to a separate validation cycle.

## Must-Verify Checks

- `localizedText.ja` is added only to `explain-camera-menu`.
- `entrypointId` remains `ringcentral.video.toolbar.video-menu`.
- `operation` remains `open`.
- `placement: during` and `actionOffsetMs: 350` remain unchanged.
- Japanese coverage advances to `20/51`.
- `meeting-controls-tour` advances to `13/22`.
- First missing step advances to `explain-share`.
- Q&A and aliases remain unchanged.
- `.coverage` remains unstaged.

## Recommendation

Proceed as a narrow narration slice. Do not bundle screen-share localization, background settings implementation, camera device switching, or locator confidence updates into this commit.
