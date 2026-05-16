# Cycle 086 Demand Analysis

## Verdict/Recommendation

Proceed with a narrow Japanese localization slice for `meeting-control-map-demo` -> `control-map-chat` only.

This step should explain `Chat` as the meeting's written side channel: where it lives, what it is useful for, and the privacy boundary around message content. The Japanese narration should be safe product guidance, not a claim that AiPresenter reads messages, opens private tabs, sends text, copies links, exposes names, or inspects attachments.

The implementation should remain package-content-only for this step. Add `narration.localizedText.ja` to the existing `control-map-chat` step, and update only directly related localization coverage expectations and handoff/source-index notes if that is part of the implementation cycle. Do not change runtime behavior, locators, action operation, action timing, cleanup, aliases, Q&A, or flow order.

## Current Gap

- Current Japanese demo narration coverage is `36/51`.
- `meeting-control-map-demo` Japanese coverage is `7/22`.
- The first missing Japanese narration step is `meeting-control-map-demo` -> `control-map-chat`.
- Existing localization report tests expect:
  - `Localization report: 36/51 demo steps`
  - `- meeting-control-map-demo: 7/22 narration localized`
  - `missing: control-map-chat`
- The existing step uses `entrypointId: ringcentral.video.toolbar.chat`, `operation: open`, `placement: during`, and `actionOffsetMs: 350`. Those execution semantics should remain unchanged.
- `ringcentral.video.toolbar.chat` is a toolbar button route targeting `Chat`, with `controlType: button` and `cleanup: toggle`.
- Existing presenter notes say Chat is a collaboration side panel for meeting messages, private chat text should not be read aloud unless the user explicitly asks, the observed panel has `Within everyone` and `Privately` tabs plus a message box, and the panel should be toggled or closed before continuing.
- `docs/knowledge/ringcentral-video/source-index.md` currently says Japanese coverage includes the control-map overview, meeting-information, network-quality, view-layout, report-issue, add-coworkers, and participants steps; Chat remains future control-map narration work.

## User Need

Japanese users need to understand that `Chat` is the written meeting channel that complements spoken conversation. It is useful for links, follow-ups, and messages that should not interrupt the live audio flow.

The narration must also make the privacy contract obvious. Chat may contain public messages, private messages, meeting links, follow-up details, unread indicators, participant names, tabs, and attachments. AiPresenter can point out where Chat is and what it is for, but it should not read, summarize, expose, send, copy, or navigate through chat content unless the user explicitly asks and the visible content is appropriate to handle.

The desired presenter behavior is calm and bounded: open or identify the Chat panel as part of the control map, explain its purpose, preserve privacy by default, then close or toggle the side panel before the next control-map step.

## Acceptance Criteria

- `control-map-chat` has `narration.localizedText.ja` attached to the existing step in `packages/ringcentral-video.yaml`.
- The existing action block remains unchanged:
  - `entrypointId: ringcentral.video.toolbar.chat`
  - `operation: open`
  - `placement: during`
  - `actionOffsetMs: 350`
- The existing route remains unchanged:
  - toolbar target `Chat`
  - `controlType: button`
  - `cleanup: toggle`
- Japanese demo narration coverage advances from `36/51` to `37/51`.
- `meeting-control-map-demo` advances from `7/22` to `8/22`.
- The first remaining missing Japanese step for `meeting-control-map-demo` becomes `control-map-microphone`.
- Japanese `--require-complete` still fails because later control-map steps remain untranslated.
- Q&A counts remain unchanged at `12/12` localized questions and `12/12` localized answers.
- `questionAliases.ja` coverage remains unchanged at `3/27` entrypoints and `9` aliases unless a separate task explicitly requests alias work.
- The localized narration includes the key concepts of Chat as a written side channel, links/follow-ups/private messages as examples of use, and default privacy for chat content.
- The localized narration must not say or imply:
  - AiPresenter reads public or private messages by default;
  - AiPresenter opens the `Privately` tab or switches between public/private tabs to inspect content;
  - AiPresenter sends a message, drafts text, replies, reacts, copies links, downloads or opens attachments, or follows links;
  - unread indicators, participant names, message previews, timestamps, links, follow-ups, private tabs, or attachments are announced aloud;
  - private messages are available to everyone or safe to expose;
  - Chat content is summarized without explicit user request and visible-content verification;
  - the Chat side panel is left open in a way that interferes with the next control-map step.
- Focused localization tests and localization report expectations should be adjusted only to reflect the one-step coverage increase.

## Non-goals

- Do not localize `control-map-microphone` or any later `meeting-control-map-demo` step in this slice.
- Do not change `operation: open`, timing, placement, locator references, cleanup behavior, or demo sequencing.
- Do not add behavior that reads messages, sends chat text, copies meeting links, opens links, opens private conversations, switches chat tabs, downloads attachments, or exposes participant names.
- Do not add or modify Japanese aliases, Q&A, presenter notes, manual controls, profile settings, runtime behavior, diagnostics logic, or CLI formatting beyond directly required count expectations.
- Do not broaden this slice into Participants, microphone/audio controls, camera controls, sharing, reactions, recording, Notes, settings, or leaving the meeting.

## Suggested Next Slice

After `control-map-chat` is localized and reviewed, continue `meeting-control-map-demo` Japanese coverage with `control-map-microphone` as the next isolated slice.

That next slice should move from written collaboration to media readiness. It should explain the microphone button as the main speaking/privacy control while avoiding any claim that AiPresenter unmutes the user, changes the audio device, records audio, or infers who can hear whom without verified UI state.
