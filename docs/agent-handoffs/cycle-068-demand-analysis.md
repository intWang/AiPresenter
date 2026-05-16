# Cycle 068 Demand Analysis: JA Camera Narration

Date: 2026-05-16

## Recommendation

Proceed with a narrow Japanese narration slice for `meeting-controls-tour` -> `explain-camera`.

This is the next visible gap after Cycle 067 and should stay separate from `explain-camera-menu`. The user value is clear: Japanese presenters can explain the main camera state control without drifting into camera device selection, background effects, or deeper video settings.

## Current Gap

After Cycle 067:

- Japanese demo narration: `18/51`
- `meeting-controls-tour`: `11/22`
- First missing controls-tour step: `explain-camera`
- Japanese Q&A remains complete at `12/12`
- Japanese aliases remain partial and unchanged

## Product Need

The camera button is a high-salience meeting control. It affects whether other participants can see the local room, person, background, and visual context. The Japanese tour needs to explain:

- `Start video` is the main local camera-on control.
- Once video is on, the same location becomes `Stop video`.
- This step is about identifying and explaining the state control, not changing the meeting state by default.

## Scope

Owned change:

- Add `localizedText.ja` under `packages/ringcentral-video.yaml` -> `meeting-controls-tour` -> `explain-camera` -> `narration`.
- Update localization count expectations and the source index.
- Add focused tests for the Japanese camera narration boundary.

Strict non-goals:

- Do not localize `explain-camera-menu`, `explain-share`, reactions, notes, recording, leave, or later steps.
- Do not add or change Japanese aliases.
- Do not change Q&A.
- Do not change locators, runtime behavior, open steps, cleanup, or state extraction.
- Do not describe camera device selection, background effects, HD/quality, gallery layout, or video settings.
- Do not imply AiPresenter will turn camera on or off without explicit user intent.

## Acceptance Criteria

- Japanese demo narration advances from `18/51` to `19/51`.
- `meeting-controls-tour` advances from `11/22` to `12/22`.
- First missing controls-tour step advances from `explain-camera` to `explain-camera-menu`.
- `explain-camera` keeps `operation: point`.
- The Japanese text mentions `Start video`, `Stop video`, local camera visibility, and the safety boundary.
- The Japanese text does not mention background, settings, camera menu, or device selection.
- Q&A and aliases remain unchanged.

## Next Candidate

After this slice, `explain-camera-menu` can be considered separately because it has different risks: device names, background/video settings, and low-confidence `More` occurrence behavior.
