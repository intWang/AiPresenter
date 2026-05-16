# Cycle 069 Demand Analysis: JA Camera Menu Narration

Date: 2026-05-16

## Recommendation

Proceed with a narrow Japanese narration slice for `meeting-controls-tour` -> `explain-camera-menu`.

This is the next missing Japanese controls-tour step after Cycle 068. It should stay separate from screen share, reactions, recording, notes, background settings, and any live validation of the `More` occurrence route.

## Current Gap

- Japanese demo narration: `19/51`
- `meeting-controls-tour`: `12/22`
- First missing controls-tour step: `explain-camera-menu`
- Japanese Q&A remains complete at `12/12`
- Japanese aliases remain unchanged at `3/27` entrypoints and `9` aliases

## Product Need

Japanese presenters need to explain the camera arrow as the place for camera choice and the shortcut to deeper video settings. This helps with visual readiness and recovery while keeping the main camera on/off button from Cycle 068 distinct.

## Scope

Owned change:

- Add `localizedText.ja` under `meeting-controls-tour` -> `explain-camera-menu`.
- Update localization tests and source-index wording.

Strict non-goals:

- Do not localize `explain-share` or later steps.
- Do not add or change aliases, Q&A, runtime behavior, locators, open steps, cleanup, or state extraction.
- Do not claim AiPresenter will switch camera devices, open deeper settings, change background, or modify video preferences.
- Do not include real camera device names, room details, account labels, or settings values.

## Acceptance Criteria

- Japanese demo narration advances from `19/51` to `20/51`.
- `meeting-controls-tour` advances from `12/22` to `13/22`.
- First missing controls-tour step advances from `explain-camera-menu` to `explain-share`.
- `explain-camera-menu` keeps `operation: open`.
- Japanese text mentions camera selection, video settings, background, explicit-user-intent boundary, and menu cleanup.
- Q&A and alias counts remain unchanged.

## Next Candidate

After this, `explain-share` is the next missing controls-tour step and should receive its own screen-share privacy review.
