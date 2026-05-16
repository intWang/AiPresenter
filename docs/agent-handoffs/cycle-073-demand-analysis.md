# Cycle 073 Demand Analysis: JA More Actions Narration

Date: 2026-05-16

## Recommendation

Proceed with a narrow Japanese narration slice for `meeting-controls-tour` -> `explain-more`.

This is the next missing Japanese controls-tour step after Cycle 072. Keep it isolated from downstream recording, notes, background, settings, leave/end behavior, live validation, locator confidence work, and any broad confirmed-action workflow. The product requirement is to explain More as the overflow hub for secondary meeting actions, while making the safety boundary explicit: opening More is navigation and discovery only; AiPresenter must not automatically choose, start, stop, configure, or trigger the actions exposed beyond that menu.

## Current Gap

- Japanese demo narration: `23/51`.
- `meeting-controls-tour`: `16/22`.
- First missing controls-tour step: `explain-more`.
- Remaining missing controls-tour steps: `explain-more`, `explain-recording`, `explain-notes`, `explain-background-settings`, `explain-settings`, and `explain-leave`.
- Japanese Q&A remains complete at `12/12` questions and `12/12` answers.
- Japanese aliases remain unchanged at `3/27` entrypoints and `9` aliases.
- The source `explain-more` step currently has English narration and Chinese `localizedText.zh`, but no `localizedText.ja`.
- The existing step uses `entrypointId: ringcentral.video.toolbar.more`, `operation: open`, `placement: during`, and `actionOffsetMs: 350`.
- The `ringcentral.video.toolbar.more` entrypoint opens the third `More` toolbar button and uses Escape cleanup.
- Existing presenter notes frame More as the expansion point for less frequent meeting tools. The observed layout notes mention Start recording, Background, and Settings under More, while Notes can vary by layout and is handled by its own downstream entrypoint.

## Product And User Need

Japanese presenters need the controls tour to continue from Raise hand into More without making the menu sound like a command that performs every advanced action inside it. More is valuable because it gathers secondary or less frequently used meeting tools behind one overflow control. That helps the user understand where to look when the primary toolbar does not show a specific action.

The localized narration should therefore do three jobs:

- Explain More as an overflow or expansion hub for secondary meeting actions.
- Make clear that opening More is a navigation step, not the same as starting recording, starting notes, changing background/settings, or leaving the meeting.
- Preserve user control by saying downstream actions remain separate, intentional choices and are not triggered automatically by AiPresenter.

## Recommended Scope

Owned future implementation scope:

- Add `localizedText.ja` under `packages/ringcentral-video.yaml` -> `meeting-controls-tour` -> `explain-more` -> `narration`.
- Preserve the existing `entrypointId`, `operation: open`, `placement: during`, and `actionOffsetMs: 350`.
- Keep the wording focused on the More menu itself as an overflow hub.
- Mention secondary meeting tools only as destinations or examples, not as actions being executed.
- Keep recording, notes, background, settings, and leave/end behavior as separate downstream steps with their own safety requirements.
- Include the no-automatic-action boundary: AiPresenter may open More to explain where tools live, but does not automatically start recording, start notes, change settings/background, or leave/end a meeting.
- Update only the focused Japanese localization expectations, any focused unit test for this step, and source-index wording needed to reflect the new coverage state in the implementation cycle.

This Cycle 073 handoff itself is documentation-only and should not modify YAML, tests, runtime code, git state, or existing Cycle 072 artifacts.

## Strict Non-Goals

- Do not localize `explain-recording`, `explain-notes`, `explain-background-settings`, `explain-settings`, or `explain-leave` in the same slice.
- Do not change neighboring `explain-raise-hand`, reactions, share, or any downstream More-menu step.
- Do not add or change Q&A, aliases, diagnostics behavior, CLI implementation, route matching, locators, runtime execution, state extraction, or live acceptance evidence.
- Do not add a workflow that automatically starts or stops recording, starts notes, changes background, changes settings, leaves, or ends a meeting.
- Do not imply that opening More confirms, previews, configures, or performs any downstream action.
- Do not claim that recording, notes, background, settings, or leave/end controls are safe to operate without explicit user direction and appropriate meeting context.
- Do not broaden this into a general confirmed-action policy, screenshots, live meeting validation, telemetry, or menu layout reconciliation.
- Do not change English or Chinese narration unless a separate review scopes that work.

## Acceptance Criteria

- Japanese demo narration advances from `23/51` to `24/51`.
- `meeting-controls-tour` advances from `16/22` to `17/22`.
- First missing controls-tour step advances from `explain-more` to `explain-recording`.
- `explain-more` keeps `operation: open` on `ringcentral.video.toolbar.more`.
- Japanese `localizedText.ja` exists, is authored Japanese text, and does not fall back to English or Chinese.
- Japanese text explains More as an overflow, expansion, or secondary-actions hub.
- Japanese text treats opening More as navigation/discovery only.
- Japanese text keeps downstream recording, notes, background, settings, and leave/end actions separate from the More-menu explanation.
- Japanese text says or clearly implies AiPresenter does not automatically trigger downstream state-changing or meeting-exit actions from More.
- Japanese Q&A and alias counts remain unchanged.
- Japanese `--require-complete` remains incomplete because later controls-tour steps are still missing.

## Next Candidate

After this, `explain-recording` should receive its own demand and risk review. Recording is the first remaining downstream More-related step and is higher risk than the More hub itself because starting or stopping recording changes meeting state and must remain explicitly user-confirmed.
