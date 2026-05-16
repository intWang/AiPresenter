# Cycle 074 Demand Analysis: JA Recording Narration

Date: 2026-05-16

## Recommendation

Proceed with a narrow Japanese narration slice for `meeting-controls-tour` -> `explain-recording`.

This is the next missing Japanese controls-tour step after Cycle 073. Keep it isolated from Notes, Background, Settings, Leave, live validation, locator confidence work, and any broad confirmed-action workflow. The product requirement is to explain where recording lives while preserving a hard safety boundary: recording changes meeting state and can affect every participant, so AiPresenter should stay explain-only in the tour and must not start or stop recording without explicit user confirmation, an allowed role, and clear participant-consent context.

## Current Gap

- Japanese demo narration: `24/51`.
- `meeting-controls-tour`: `17/22`.
- First missing controls-tour step: `explain-recording`.
- Remaining missing controls-tour steps: `explain-recording`, `explain-notes`, `explain-background-settings`, `explain-settings`, and `explain-leave`.
- Japanese Q&A remains complete at `12/12` questions and `12/12` answers.
- Japanese aliases remain unchanged at `3/27` entrypoints and `9` aliases.
- Cycle 073 localized `explain-more`, so the tour now reaches the More menu and explicitly says recording start is not performed unless the user clearly asks.
- The source `explain-recording` step currently has English narration and Chinese `localizedText.zh`, but no `localizedText.ja`.
- The existing step uses `entrypointId: ringcentral.video.more.recording`, `operation: explain`, and `placement: before`.
- The `ringcentral.video.more.recording` entrypoint is observed under More as `Start recording`, has no `openSteps`, and presenter notes already require treating it as state-changing during a tour.
- Existing Japanese recording Q&A already says recording changes meeting state, affects everyone, and should stay entrypoint-only unless the user explicitly confirms, the current role is allowed, and participant consent is clear. The scripted Japanese tour still lacks this point-of-use narration.

## Product And User Need

Japanese presenters need the controls tour to move from the More hub into the recording entry without implying that recording is a passive demo action. Recording is materially different from opening an informational panel or changing a local view: it can create meeting artifacts, notify or affect participants, and may be governed by host role, organization policy, legal consent rules, or meeting-specific expectations.

The localized narration should therefore do four jobs:

- Identify `Start recording` as the recording entry available from More.
- Explain that starting or stopping recording changes meeting state and may affect everyone in the meeting.
- Make clear that AiPresenter only explains the entry during the tour and does not start or stop recording automatically.
- Require explicit user confirmation plus role/permission and participant-consent awareness before any real recording action.

## Recommended Scope

Owned future implementation scope:

- Add `localizedText.ja` under `packages/ringcentral-video.yaml` -> `meeting-controls-tour` -> `explain-recording` -> `narration`.
- Preserve the existing `entrypointId: ringcentral.video.more.recording`.
- Preserve `operation: explain`; do not convert this step into `open`, `click`, `toggle`, or any operation that could trigger recording.
- Preserve `placement: before`.
- Keep wording focused on recording only, not the broader More menu.
- Use source UI labels such as `Start recording` where helpful, while writing the surrounding narration in authored Japanese.
- State that recording changes meeting state and can affect all participants.
- State that in the tour AiPresenter only explains the entry and does not start or stop recording automatically.
- Include the confirmation boundary: starting or stopping recording requires the user to explicitly confirm the intent.
- Include role/permission awareness: recording should proceed only when the current role and meeting policy allow it.
- Include participant-consent awareness: recording should proceed only when consent or meeting-context permission is clear.
- Update only the focused Japanese localization expectations, any focused unit test for this step, and source-index wording needed to reflect the new coverage state in the implementation cycle.

This Cycle 074 handoff itself is documentation-only and should not modify YAML, tests, runtime code, git state, or existing Cycle 073 artifacts.

## Strict Non-Goals

- Do not localize `explain-notes`, `explain-background-settings`, `explain-settings`, or `explain-leave` in the same slice.
- Do not change the completed `explain-more` Japanese narration from Cycle 073.
- Do not change English or Chinese narration unless a separate review scopes that work.
- Do not add Japanese aliases, Q&A, manual controls, source routes, locators, cleanup behavior, runtime execution, state extraction, diagnostics behavior, CLI behavior, telemetry, or live acceptance evidence.
- Do not add an automatic workflow that starts, stops, pauses, resumes, confirms, validates, or monitors recording.
- Do not click `Start recording` during a normal tour, and do not imply the tour verifies recording availability by attempting the action.
- Do not claim recording is safe solely because the user asked about it; role/permission and participant consent still matter.
- Do not imply AiPresenter can determine legal consent, organization policy, or host permissions without visible or user-provided context.
- Do not broaden this into a general confirmed-action policy for every state-changing meeting control.
- Do not make promises about recording artifacts, transcripts, summaries, retention, storage location, or post-meeting availability; those belong to existing post-meeting Q&A or later scoped work.

## Acceptance Criteria

- Japanese demo narration advances from `24/51` to `25/51`.
- `meeting-controls-tour` advances from `17/22` to `18/22`.
- First missing controls-tour step advances from `explain-recording` to `explain-notes`.
- `explain-recording` keeps `operation: explain` on `ringcentral.video.more.recording`.
- Japanese `localizedText.ja` exists, is authored Japanese text, and does not fall back to English or Chinese.
- Japanese text identifies `Start recording` or the recording entry without implying it was clicked.
- Japanese text says recording changes meeting state and can affect participants.
- Japanese text says AiPresenter only explains the entry during the tour and does not automatically start or stop recording.
- Japanese text requires explicit user confirmation before starting or stopping recording.
- Japanese text includes role/permission awareness before recording can proceed.
- Japanese text includes participant-consent or meeting-consent awareness before recording can proceed.
- Japanese text stays focused on recording and does not pull in Notes, Background, Settings, Leave, or post-meeting artifact behavior.
- Japanese Q&A and alias counts remain unchanged.
- Japanese `--require-complete` remains incomplete because later controls-tour steps are still missing.

## Next Candidate

After this, `explain-notes` should receive its own demand and risk review. Notes is adjacent to recording because starting notes may involve transcript or recording-related meeting-state changes, but it needs separate treatment for panel contents, transcript privacy, and note-start confirmation.
