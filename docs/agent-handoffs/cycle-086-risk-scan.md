# Cycle 086 Risk Scan: RingCentral Video Control Map Chat JA

## Risk Summary

Risk review for adding Japanese `localizedText.ja` to `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-chat`.

This should be a narrow narration-only slice. The future implementation should add only Japanese narration under the existing `control-map-chat` step and preserve:

- the English and Chinese narration text
- `narration.placement: during`
- `narration.actionOffsetMs: 350`
- the step position after `control-map-participants` and before `control-map-microphone`
- the entrypoint route: `clickWindowControl`, target `Chat`, `controlType: button`, `cleanup: toggle`

Chat is privacy-sensitive because it can expose public messages, private conversations, participant names, links, attachments, unread indicators, and a text-entry/send surface. Safe Japanese copy may explain that Chat is the written side channel for links, follow-ups, and private messages, but it must not imply that AiPresenter reads message bodies, opens private tabs, copies content, downloads attachments, enters text, or sends messages unless the user explicitly asks and visible content is verified.

Adjacent context matters. The previous Participants step opens a side panel with Participant and Chat tabs and must be closed before Chat opens. The next Microphone step starts media readiness and audio privacy guidance. Chat narration must not bleed into roster identification, participant management, audio-state changes, microphone muting/unmuting, or any later device-control step.

## Behavior Boundaries

- Keep this as an open-and-explain step. Opening the Chat panel for orientation is acceptable only with toggle/side-panel cleanup.
- Do not read public or private message text by default.
- Do not open, select, summarize, or name private conversations unless the user explicitly asks and the displayed content has been verified.
- Do not read participant names, sender names, roles, account details, or avatars from Chat unless explicitly requested and verified.
- Do not click links, preview links, copy URLs, copy message text, download attachments, upload files, open attachment menus, or inspect message metadata during this localization slice.
- Do not type into the message box, paste clipboard content, use emoji/GIF/reaction/file controls, or press Send. Sending a chat message is a meeting-visible action and needs explicit user confirmation in a separate behavior path.
- Treat unread indicators and tab badges as status only. The narration can mention public/private chat areas, but should not promise exact unread counts or message contents unless verified and allowed.
- Preserve cleanup. Toggle Chat or close the side panel before continuing to Microphone and audio steps.
- Treat cleanup failure as blocking. If Chat remains open, later microphone/audio actions can be visually or focus-wise confused with the side panel, message box, private tabs, or Participants overlap.
- Keep Chat and Participants separate. The Chat copy should not describe attendee search, invite, lock, mute, raise-hand, or host controls beyond relying on the prior Participants cleanup.

## Privacy Notes

- Chat can expose message bodies, private tabs, direct-message recipients, sender names, participant names, links, attachments, timestamps, unread counts, meeting context, and text drafts.
- Public/everyone messages are still sensitive by default. Do not treat "everyone" as permission to read aloud.
- Private chat tabs are higher risk: avoid tab switching, recipient naming, and message reading unless the user explicitly requests it and the visible UI confirms the target.
- Manual validation should prefer sanitized UIA/window metadata. Avoid screenshots or logs that include message text, sender names, participant names, private recipient names, links, attachments, draft text, meeting identifiers, or account context.
- If evidence is needed for route confidence, record generic labels only, such as `Chat`, `Within everyone`, `Privately`, and `message box`, not message contents.

## Required Test Guards

- Localization coverage should advance only the expected Japanese narration count for `meeting-control-map-demo`: from `7/22` to `8/22`, with the first remaining missing step moving from `control-map-chat` to `control-map-microphone`.
- Overall Japanese demo localization totals should advance by exactly one step: from `36/51` to `37/51`, with `meeting-controls-tour` remaining `22/22`.
- Assert the new Japanese text is attached to `meeting-control-map-demo` -> `control-map-chat`, not to `meeting-controls-tour` -> `explain-chat`, Q&A, aliases, presenter notes, Participants, Microphone, or later control-map steps.
- Assert `control-map-chat.narration.placement` remains `during`.
- Assert `control-map-chat.narration.actionOffsetMs` remains `350`.
- Assert the entrypoint `ringcentral.video.toolbar.chat` still has `cleanup: toggle` and presenter notes covering collaboration side panel, no private chat reading unless explicitly requested, observed `Within everyone` and `Privately` tabs plus message box, and toggle/close cleanup before continuing.
- Assert the Japanese copy clearly describes Chat as a written side channel for links, follow-ups, and private messages while preserving privacy.
- Assert the Japanese copy includes or preserves explicit-user-request boundaries before reading chat content.
- Assert the Japanese copy does not imply opening private tabs, reading public/private messages, identifying senders or participants, clicking links, handling attachments, copying content, entering text, sending messages, or changing microphone/audio state.
- Assert neighboring steps remain unchanged, especially `control-map-participants`, `control-map-microphone`, and the existing `meeting-controls-tour` Chat explainer.
- Keep the Japanese chat privacy Q&A answer-only guard intact; it should not become an operational route just because Chat has localized demo narration.
- If live or screenshot-based validation is used, fail review when the Chat panel remains open before Microphone, when private tabs or message rows are inspected without explicit request, when text is entered or sent, or when evidence captures message content, participant names, links, attachments, drafts, or account/meeting identifiers.
- Japanese `--require-complete` should still fail after this slice because later `meeting-control-map-demo` steps remain untranslated.

## Rollback/Commit Notes

Proceed as a narrow narration-only commit. The safe rollback is to remove only the `localizedText.ja` line/block added under `meeting-control-map-demo` -> `control-map-chat`.

Do not rollback or alter other agents' concurrent edits. Before committing, verify the diff contains only the intended Japanese narration and any directly necessary test expectation updates owned by the implementation task. This risk scan itself intentionally changes only `docs/agent-handoffs/cycle-086-risk-scan.md`.

Recommended commit scope for the implementation owner: "Add JA narration for RingCentral control map Chat." Keep private-tab operation, message reading, link/attachment handling, copy behavior, text entry, message sending, Participants behavior, microphone/audio behavior, locator changes, Q&A edits, aliases, and broader control-map localization for separate cycles unless explicitly assigned.
