# Cycle 075 Demand Analysis: JA Notes Narration

Date: 2026-05-16

## Recommendation

Proceed with a narrow Japanese narration slice for `meeting-controls-tour` -> `explain-notes`.

This is the next missing Japanese controls-tour step after Cycle 074. Keep it isolated from Background, Settings, Leave, live validation, locator confidence work, and any broad notes/transcript automation. The product requirement is to explain the Notes and Transcript panel while preserving user control: the panel may expose note or transcript content, and it may offer state-changing actions such as starting notes or recording, so AiPresenter must not start notes, enable recording, read transcript text, read note content, or summarize panel content unless the user explicitly asks and the visible meeting context supports it.

## Current Gap

- Japanese demo narration: `25/51`.
- `meeting-controls-tour`: `18/22`.
- First missing controls-tour step: `explain-notes`.
- Remaining missing controls-tour steps: `explain-notes`, `explain-background-settings`, `explain-settings`, and `explain-leave`.
- Japanese Q&A remains complete at `12/12` questions and `12/12` answers.
- Japanese aliases remain unchanged at `3/27` entrypoints and `9` aliases.
- Cycle 074 localized `explain-recording`, so the tour now explains the More-menu recording entry and moves the first missing step to Notes.
- The source `explain-notes` step currently has English narration and Chinese `localizedText.zh`, but no `localizedText.ja`.
- The existing step uses `entrypointId: ringcentral.video.more.notes`, `operation: open`, `placement: during`, and `actionOffsetMs: 400`.
- The `ringcentral.video.more.notes` entrypoint opens More, selects the Notes menu item exposed as `onconf.controls.NOTES`, and uses `cleanup: sidePanel`.
- Presenter notes say the current observed panel offers `Start notes` and `Also record this meeting`.
- Presenter notes also say starting notes or recording changes meeting state, so the default tour only explains the panel and closes it before continuing.
- Existing Japanese Q&A already treats Notes and Transcript as a discovery surface and says not to start notes, transcription, captions, translation, or read caption/transcript text unless the user explicitly asks and visible context is verified. The scripted Japanese tour still lacks that point-of-use boundary.

## Product And User Need

Japanese presenters need the controls tour to cover Notes and Transcript without treating the panel as a harmless static view. Unlike a simple menu item, this panel can sit on top of live meeting content, display or later display notes and transcripts, and expose controls that affect the meeting state. A localized tour that only says "Notes opens the panel" would be understandable, but it would miss the key user trust boundary: the assistant should help users find the panel without silently starting notes, enabling recording, or reading private meeting content.

The localized narration should therefore do four jobs:

- Identify Notes as the entry to the Notes and Transcript panel.
- Explain that the panel can contain or expose notes and transcript-related content.
- Explain that starting notes or recording from the panel changes meeting state and remains under user control.
- Make clear that AiPresenter does not start notes, enable recording, or read note/transcript content unless the user explicitly requests it and the visible context is appropriate.

## Recommended Scope

Owned future implementation scope:

- Add `localizedText.ja` under `packages/ringcentral-video.yaml` -> `meeting-controls-tour` -> `explain-notes` -> `narration`.
- Preserve the existing `entrypointId: ringcentral.video.more.notes`.
- Preserve `operation: open`; opening the panel is the scoped discovery action, not permission to click any controls inside it.
- Preserve `placement: during` and `actionOffsetMs: 400`.
- Preserve the existing More-to-Notes route and `cleanup: sidePanel` behavior on the entrypoint.
- Keep wording focused on Notes and Transcript only, not broader More-menu recording behavior or later settings/leave steps.
- Use source UI labels such as `Notes`, `Notes and Transcript`, `Start notes`, and `Also record this meeting` only where they help keep the safety boundary clear.
- State that Notes opens the Notes and Transcript panel.
- State that the panel may expose notes or transcript content.
- State that starting notes or recording from the panel can change meeting state.
- State that the tour explains or opens the panel only; it does not start notes or recording automatically.
- State that reading, summarizing, or otherwise using visible note/transcript content requires an explicit user request and appropriate visible context.
- Update only the focused Japanese localization expectations, any focused unit test for this step, and source-index wording needed to reflect the new coverage state in the implementation cycle.

This Cycle 075 handoff itself is documentation-only and should not modify YAML, tests, runtime code, git state, `.coverage`, or existing Cycle 074 artifacts.

## Strict Non-Goals

- Do not localize `explain-background-settings`, `explain-settings`, or `explain-leave` in the same slice.
- Do not change the completed `explain-recording` Japanese narration from Cycle 074.
- Do not change English or Chinese narration unless a separate review scopes that work.
- Do not add Japanese aliases, Q&A, manual controls, source routes, locators, cleanup behavior, runtime execution, state extraction, diagnostics behavior, CLI behavior, telemetry, or live acceptance evidence.
- Do not add an automatic workflow that starts notes, stops notes, enables recording, stops recording, starts transcription, starts captions, starts translation, or confirms any of those actions.
- Do not click `Start notes` or `Also record this meeting` during a normal tour.
- Do not read, quote, summarize, store, export, or infer meaning from note, transcript, caption, or chat content just because the panel is open.
- Do not imply AiPresenter can determine legal consent, organization policy, host permissions, or participant expectations without visible or user-provided context.
- Do not promise that transcripts, summaries, insights, recordings, or post-meeting artifacts will exist after the meeting.
- Do not broaden this into a general confirmed-action policy for every content-bearing or state-changing meeting control.
- Do not use screenshots, logs, or validation notes that include participant names, transcript lines, note content, meeting IDs, invite links, or other sensitive meeting details.

## Acceptance Criteria

- Japanese demo narration advances from `25/51` to `26/51`.
- `meeting-controls-tour` advances from `18/22` to `19/22`.
- First missing controls-tour step advances from `explain-notes` to `explain-background-settings`.
- `explain-notes` keeps `operation: open` on `ringcentral.video.more.notes`.
- `explain-notes` keeps `placement: during` and `actionOffsetMs: 400`.
- The Notes entrypoint keeps the existing More-menu route and `cleanup: sidePanel`.
- Japanese `localizedText.ja` exists, is authored Japanese text, and does not fall back to English or Chinese.
- Japanese text identifies Notes or Notes and Transcript as the panel entry.
- Japanese text says the panel may expose notes or transcript-related content.
- Japanese text says starting notes or recording from the panel can change meeting state.
- Japanese text says AiPresenter does not start notes or recording automatically during the tour.
- Japanese text requires an explicit user request before starting notes or enabling recording.
- Japanese text requires an explicit user request and appropriate visible context before reading, summarizing, or using note/transcript content.
- Japanese text stays focused on Notes and Transcript and does not pull in Background, Settings, Leave, or post-meeting artifact behavior.
- Japanese Q&A and alias counts remain unchanged.
- Japanese `--require-complete` remains incomplete because later controls-tour steps and `meeting-control-map-demo` narration are still missing.

## Next Candidate

After this, `explain-background-settings` should receive its own demand and risk review. It is lower risk than Notes because it is primarily a visual-preference settings surface, but it still deserves a separate slice for camera/background privacy, custom upload behavior, and the boundary between opening a settings page and applying a visible presentation change.
