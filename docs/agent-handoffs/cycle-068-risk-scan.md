# Cycle 068 Risk Scan: explain-camera JA Narration

Date: 2026-05-16

## Scope

Risk review for adding Japanese `localizedText.ja` to `meeting-controls-tour` -> `explain-camera`.

The owned implementation should be narration-only and should preserve `operation: point`.

## Key Risks

1. **Camera visibility and room privacy**
   - Turning video on can expose the presenter's face, room, background, whiteboards, people nearby, or sensitive objects.
   - Japanese narration must not imply AiPresenter will turn the camera on by default.

2. **Meeting-visible state change**
   - Camera on/off is visible to other participants and can change the social state of the meeting.
   - The tour can explain the control, but real operation needs explicit user intent.

3. **Boundary with camera menu**
   - The next step, `explain-camera-menu`, owns camera device selection and video settings.
   - This pass should not mention device names, camera choices, background effects, HD, appearance, or settings.

4. **State label ambiguity**
   - The main button alternates between `Start video` and `Stop video`.
   - Narration should avoid claiming the current camera state unless the state is observed.
   - The text can explain both labels generically.

5. **Localized label confidence**
   - Current package labels and tests are based on English UI labels.
   - This pass adds Japanese narration only; it should not change locator targeting or assert Japanese UI labels.

## Mitigations

- Keep `operation: point`, not `click` or `open`.
- Say the button is for camera on/off, but AiPresenter only checks/explains unless the user clearly asks for a state change.
- Keep `Start video` and `Stop video` as product labels.
- Do not mention background, settings, camera device selection, or the camera arrow.
- Do not add Q&A or aliases in this slice.
- Do not claim video is currently on/off.

## Must-Verify Checks

- `localizedText.ja` is added only to `explain-camera`.
- `entrypointId` remains `ringcentral.video.toolbar.video`.
- `operation` remains `point`.
- `placement: before` remains unchanged.
- No locator, cleanup, alias, Q&A, runtime, or state extraction changes are bundled.
- Japanese coverage advances to `19/51`.
- `meeting-controls-tour` advances to `12/22`.
- First missing step advances to `explain-camera-menu`.
- `.coverage` remains unstaged.

## Recommendation

Proceed as a narrow narration slice. Do not treat this as live camera-operation acceptance, and do not bundle camera menu or settings coverage into the same commit.
