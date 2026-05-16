# Cycle 064 Demand Analysis: meeting-controls-tour / explain-participants JA narration

Date: 2026-05-16

## Demand Judgment

Proceed with the next single-step Japanese localization slice: `meeting-controls-tour` -> `explain-participants`.

Cycle 063 advanced Japanese demo narration to `14/51` steps and `meeting-controls-tour: 7/22`, with the first missing Japanese step now `explain-participants`. This is the right next demand because it continues the tour in order and covers a high-value meeting surface: the Participants roster panel.

Keep this as a narrow roster-panel localization pass. Do not batch `explain-chat`, `explain-microphone`, audio menu, camera, share, reactions, notes, recording, leave, or any later tour steps. Each has a different privacy, state, cleanup, and side-effect profile.

## User Value

- Japanese presenters can continue the main meeting-controls tour past Invite without falling back to English.
- Users learn where to confirm attendance context and find people-related controls during a live meeting.
- The localized wording can reinforce roster privacy before the tour reaches more sensitive side panels like Chat.
- The slice reduces ambiguity between inviting people and viewing/managing people already in the room.

## Strict Scope

- Add only Japanese narration for `packages/ringcentral-video.yaml` -> `meeting-controls-tour` -> `explain-participants`.
- Preserve the existing action: `entrypointId: ringcentral.video.toolbar.participants`, `operation: open`.
- Preserve existing English and Chinese text, flow order, timing, locators, cleanup mode, Q&A, aliases, runtime behavior, and state extraction unless a separate owner explicitly expands scope.
- If implementation owns localization accounting, update only the expected JA coverage for this single step.
- If source-index maintenance is included, update the coverage note from the first seven `meeting-controls-tour` steps to the first eight through Participants.

## Non-Goals

- Do not localize `explain-chat`, `explain-microphone`, `explain-audio-menu`, `explain-camera`, `explain-share`, or any later step.
- Do not add or widen Japanese `questionAliases`.
- Do not change Participants open/close behavior, side-panel cleanup, UIA locators, adaptive demo logic, or operation permissions.
- Do not implement host-control actions, roster management, meeting lock, mute others, remove participant, role inspection, or security changes.
- Do not read participant names, roles, private tabs, chat messages, or attendee details by default.

## Privacy And State Boundaries

- Participants opens the roster panel and can expose attendee count, names, roles, search, invite, lock, mute, raise-hand, more controls, and a neighboring Chat tab.
- Default behavior should explain the panel purpose and, when verified, may summarize visible count at a high level.
- By default, do not identify people, read names or roles, infer attendance meaning, or describe host/moderator controls beyond their location.
- Do not click roster controls that change meeting state, including muting others, locking the meeting, removing people, changing security, raising hands for others, or opening private/person-specific actions.
- The panel should be closed or toggled before moving to Chat or later toolbar steps.
- Treat Participants separately from Chat: Participants is roster and people controls; Chat is message content and private/public conversation tabs.

## Acceptance Criteria

- `explain-participants` has `narration.localizedText.ja`.
- The Japanese text preserves the visible product label `Participants`.
- The text explains that Participants opens the roster or participant panel.
- The text states that the panel helps confirm who is in the room or find people controls only at a high level.
- The text includes a privacy boundary: names, roles, and participant details are not read unless the user explicitly asks and visible content is verified.
- The text does not claim AiPresenter will identify people, manage participants, mute others, lock the meeting, remove anyone, or change security settings.
- No Japanese text is added to Chat, Microphone, Share, Notes, Recording, Leave, or later steps in the same slice.
- Expected localization movement after implementation: JA demo narration `14/51` -> `15/51`; `meeting-controls-tour` `7/22` -> `8/22`; first missing `meeting-controls-tour` step should advance from `explain-participants` to `explain-chat`.
- Q&A localization should remain `12/12` questions and `12/12` answers; `questionAliases.ja` should remain `3/27 entrypoints (9 aliases)` unless a separate alias task is approved.

## Next-Step Recommendations

- Implementation should be narration-only and test-first: assert `explain-participants` is the first missing JA step, add the JA line, then update focused coverage expectations.
- Use wording that keeps `Participants` as the visible label and explicitly avoids reading names or roles by default.
- Run focused localization tests and the Japanese localization report after implementation.
- Prepare a separate demand/risk slice for `explain-chat`; do not combine it with Participants because Chat exposes message content and private conversation tabs.
- Keep Microphone and other media controls as later independent slices because they affect live meeting state.

## Sources Reviewed

- `packages/ringcentral-video.yaml`
- `docs/knowledge/ringcentral-video/source-index.md`
- `docs/knowledge/ringcentral-video/privacy-matrix.md`
- `docs/agent-handoffs/cycle-063-demand-analysis.md`
- `docs/agent-handoffs/cycle-063-risk-scan.md`
- `docs/agent-handoffs/cycle-063-summary.md`

## Changed Files

- `docs/agent-handoffs/cycle-064-demand-analysis.md`
