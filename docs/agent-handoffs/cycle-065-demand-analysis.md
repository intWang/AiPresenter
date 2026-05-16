# Cycle 065 Demand Analysis: meeting-controls-tour / explain-chat JA narration

Date: 2026-05-16

## Demand Judgment

Proceed with the next single-step Japanese localization slice: `meeting-controls-tour` -> `explain-chat`.

Cycle 064 advanced Japanese demo narration to `15/51` steps and `meeting-controls-tour: 8/22`, with the first missing step now `explain-chat`. This is the right next slice because it continues the tour in order and covers a high-value collaboration surface before the tour moves into media controls.

Keep this as a narrow Chat message-panel localization pass. Do not batch `explain-microphone`, `explain-audio-menu`, camera, share, reactions, notes, recording, leave, or any later tour steps. Chat has message-content privacy risk; Microphone and Audio have live media-state risk. They deserve separate demand, risk, and implementation reviews.

## User Value

- Japanese presenters can continue the main meeting-controls tour from Participants into Chat without falling back to English.
- Users learn that Chat is the written side channel for messages to everyone and private conversations.
- The localized wording can reinforce that chat contents remain private by default.
- The slice cleanly separates roster privacy from message-content privacy before the tour enters microphone and audio controls.

## Strict Scope

- Add only Japanese narration for `packages/ringcentral-video.yaml` -> `meeting-controls-tour` -> `explain-chat`.
- Preserve the existing action: `entrypointId: ringcentral.video.toolbar.chat`, `operation: open`.
- Preserve existing English and Chinese text, flow order, timing, locators, cleanup behavior, Q&A, aliases, runtime behavior, and state extraction unless a separate owner explicitly expands scope.
- If implementation owns localization accounting, update only the expected JA coverage for this single step.
- If source-index maintenance is included, update the coverage note from the first eight `meeting-controls-tour` steps to the first nine through Chat.

## Non-Goals

- Do not localize `explain-microphone`, `explain-audio-menu`, `explain-camera`, `explain-share`, or any later step.
- Do not add or widen Japanese `questionAliases`.
- Do not change Chat open/close behavior, side-panel cleanup, UIA locators, adaptive demo logic, operation permissions, or Q&A routing.
- Do not read, summarize, classify, translate, or infer any visible chat message content by default.
- Do not send messages, open private conversations, switch recipients, mention unread/private message details, or promise message history access.

## Privacy And State Boundaries

- Chat opens a side message panel that can expose public messages, private conversations, sender names, timestamps, links, files, mentions, and unread indicators.
- Default behavior should explain the panel purpose and its public/private conversation shape only.
- Chat contents are private by default. Read or summarize visible chat text only when the user explicitly asks and the content is verified from an approved observation source.
- Do not infer meaning from unread counts, private tabs, sender identity, message timing, or link previews.
- Do not send or draft messages during this slice.
- Participants and Chat share side-panel territory, but they are separate privacy classes: Participants covers roster/count/control context; Chat covers message content. The preceding Participants panel should be closed or safely switched before Chat narration plays.

## Acceptance Criteria

- `explain-chat` has `narration.localizedText.ja`.
- The Japanese text preserves the visible product label `Chat`.
- The text explains that Chat opens the message panel.
- The text mentions both messages to everyone and private conversations at a high level.
- The text states that chat content is not read unless the user explicitly asks; ideally it also requires visible/verified content.
- The text does not claim AiPresenter will read, summarize, translate, search, send, or manage chat messages by default.
- No Japanese text is added to Microphone, Audio menu, Camera, Share, Notes, Recording, Leave, or later steps in the same slice.
- Expected localization movement after implementation: JA demo narration `15/51` -> `16/51`; `meeting-controls-tour` `8/22` -> `9/22`; first missing `meeting-controls-tour` step should advance from `explain-chat` to `explain-microphone`.
- Q&A localization should remain `12/12` questions and `12/12` answers; `questionAliases.ja` should remain `3/27 entrypoints (9 aliases)` unless a separate alias task is approved.

## Next-Step Recommendations

- Implementation should be narration-only and test-first: assert `explain-chat` is the first missing JA step, add the JA line, then update focused coverage expectations.
- Use wording parallel to the existing Chinese boundary while adding the same explicit-user-request and verified-visible-content guard used elsewhere in Japanese privacy wording.
- Run focused localization tests and the Japanese localization report after implementation.
- Prepare separate slices for `explain-microphone` and `explain-audio-menu`; do not combine them with Chat because they touch live microphone state, device menus, and audio routing.

## Sources Reviewed

- `packages/ringcentral-video.yaml`
- `docs/knowledge/ringcentral-video/privacy-matrix.md`
- `docs/knowledge/ringcentral-video/source-index.md`
- `docs/knowledge/ringcentral-video/state-matrix.md`
- `docs/agent-handoffs/cycle-064-demand-analysis.md`
- `docs/agent-handoffs/cycle-064-summary.md`
- `docs/agent-handoffs/cycle-064-review.md`

## Changed Files

- `docs/agent-handoffs/cycle-065-demand-analysis.md`
