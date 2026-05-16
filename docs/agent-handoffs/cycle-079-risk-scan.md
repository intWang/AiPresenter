# Cycle 079 Risk Scan: control-map-overview JA Narration

Date: 2026-05-16

## Risk Summary

Risk review for adding Japanese `localizedText.ja` to `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-overview`.

This handoff is documentation-only. The future implementation should add only the Japanese narration under the existing `control-map-overview` step and preserve:

- `entrypointId: ringcentral.video.overview`
- `operation: explain`
- `placement: before`
- the existing first-step position before `control-map-meeting-info`
- all existing action operations in later `meeting-control-map-demo` steps

`control-map-overview` is the orientation step for the structured control map demo. It should describe the meeting surface at a high level: top status and health, center live meeting canvas, and bottom controls for people, media, sharing, reactions, and exit. It is not an instruction to press those controls and must not imply that AiPresenter has already opened panels, enabled recording, started screen sharing, turned on captions/transcripts/notes, changed settings, or left the meeting.

The main risk is copying wording from the already localized `meeting-controls-tour` overview without preserving the semantic difference. `meeting-controls-tour` is a complete controls tour that synchronizes narration with safe UI actions. `meeting-control-map-demo` is a structured map with later steps that separately open, point to, toggle, or explain controls. The overview should set the mental model only; it should not preview later actions as completed actions.

Neighboring context matters. The next steps include `control-map-meeting-info` and `control-map-network`, which open potentially sensitive panels, then several people, media, interaction, More, recording, notes, settings, and leave steps. The Japanese overview should stay broad enough that those later safety boundaries remain meaningful and do not sound redundant or already satisfied.

## Behavior Boundaries

- Keep `control-map-overview` explain-only. Do not change the operation to `open`, `point`, `toggle`, `click`, or any state-changing action.
- Do not add cleanup, open steps, locator changes, delays, or control-specific route behavior for the overview.
- Do not say AiPresenter will operate the controls from the overview step. The step should orient the user before any later control-specific steps run.
- Do not state or imply that recording is on, sharing is active, captions/transcript/notes have started, background settings changed, settings opened, or Leave clicked.
- Do not imply microphone or camera state changed. The later microphone and camera steps only point/explain readiness and privacy controls.
- Do not imply participants were invited, chat was read, reactions were sent, or Raise hand remains active. Those are handled by later steps with their own safety wording.
- Do not collapse the overview into the `meeting-controls-tour` text. It can overlap in product vocabulary, but this step's meaning is "map orientation" rather than "tour synchronized with actions."
- Do not copy Chinese phrasing through mechanical translation if it weakens the safety posture. Japanese should naturally preserve the source meaning and avoid action-completion verbs such as "started", "enabled", "opened", or "set" for controls that are only named.
- Keep the bottom bar categories neutral: people, media, sharing, reactions/interactions, and exit. Exit should be named as a location/category, not as a command.
- Keep later steps' existing action semantics unchanged: meeting info/network/views/report/add coworkers/participants/chat/audio menu/camera menu/share/reactions/more/notes/background/settings may open, microphone/camera may point, Raise hand may toggle and lower again, recording and Leave remain explain-only.

## Privacy Notes

- The overview should not read or expose meeting identity, meeting ID, invite link, dial-in data, encryption values, host names, participant names, chat content, transcript content, device labels, or account/settings values.
- The top bar can be described as the area for status and health without naming visible private values. Detailed meeting information belongs to `control-map-meeting-info`, which already says private values are summarized without being read aloud.
- The bottom toolbar can be described by categories without suggesting that AiPresenter inspects actual microphone/camera state, chat messages, participants, recording state, screen-share target, or Settings values.
- Japanese wording should avoid asserting current live state unless the flow verifies it visually. For example, prefer "where you manage" or "area for" over "is currently sharing", "recording is active", or "captions are enabled."
- Test artifacts and review diffs should avoid screenshots or logs that include meeting IDs, invite links, participant names, chat/transcript content, device labels, custom backgrounds, account details, or settings values.

## Required Test Guards

- Localization coverage should advance only the expected Japanese narration count for `meeting-control-map-demo`: from `0/22` to `1/22`, with first remaining missing step moving from `control-map-overview` to `control-map-meeting-info`.
- Overall Japanese demo localization totals should advance by exactly one step from the cycle 078 baseline, with `meeting-controls-tour` remaining `22/22`.
- Assert the new Japanese text is attached to `meeting-control-map-demo` -> `control-map-overview`, not to `meeting-controls-tour` -> `meeting-overview`, Q&A, entrypoint presenter notes, aliases, or other control-map steps.
- Assert `control-map-overview.action.entrypointId` remains `ringcentral.video.overview`.
- Assert `control-map-overview.action.operation` remains `explain`.
- Assert `control-map-overview.narration.placement` remains `before`.
- Assert the Japanese copy preserves the three-region map: top status/health, center live meeting canvas, bottom people/media/sharing/reactions-or-interactions/exit controls.
- Assert the Japanese copy does not contain action-completion claims for recording, sharing, captions, transcript, notes, settings, microphone, camera, participants, chat, reactions, Raise hand, or Leave.
- Assert the Japanese copy does not promise AiPresenter will click or execute any control from the overview step.
- Assert the Japanese copy does not read or request private meeting values.
- Assert neighboring steps remain unchanged, especially `control-map-meeting-info`, `control-map-network`, `control-map-share`, `control-map-recording`, `control-map-notes`, `control-map-settings`, and `control-map-leave`.
- If tests inspect package structure, keep `control-map-overview` as the first step and `control-map-summary` as the final step.
- If implementation updates CLI localization diagnostics, `--require-complete` for Japanese should still fail after this slice because the remaining `meeting-control-map-demo` steps are still untranslated.

## Rollback/Commit Notes

Proceed as a narrow narration-only commit. The safe rollback is to remove only the `localizedText.ja` line/block added under `meeting-control-map-demo` -> `control-map-overview`.

Do not rollback or alter other agents' concurrent edits. Before committing, verify the diff contains only the intended Japanese narration and any directly necessary test expectation updates owned by the implementation task. This risk scan itself intentionally changes only `docs/agent-handoffs/cycle-079-risk-scan.md`.

Recommended commit scope for the implementation owner: "Add JA narration for RingCentral control map overview." Keep later control-map localization, control execution behavior, privacy-sensitive panel reading, recording/share/notes/settings/leave automation, locator updates, and CLI behavior changes for separate cycles unless explicitly assigned.
