# Cycle 065 Risk Scan: `explain-chat` JA Narration

Date: 2026-05-16

## Scope

Assess risks for adding Japanese `localizedText.ja` narration to `packages/ringcentral-video.yaml` -> `meeting-controls-tour` -> `explain-chat`.

Only this handoff document was edited. The scan read targeted local context:

- `packages/ringcentral-video.yaml`
- `presenter/skills/ringcentral-safety.md`
- `docs/knowledge/ringcentral-video/privacy-matrix.md`
- `docs/knowledge/ringcentral-video/source-index.md`
- Cycle 064 handoffs for the Participants-to-Chat boundary
- focused localization and question-routing tests already present for this slice

## Risk List

1. **Chat message content exposure**
   - Chat can expose public and private messages.
   - The current English says Chat supports messages to everyone and private conversations, but content is not read unless the user asks.
   - Japanese narration must preserve that default privacy boundary and avoid summarizing, quoting, translating, or implying inspection of message bodies.

2. **Public vs private recipient ambiguity**
   - Entry point notes say the observed panel has `Within everyone` and `Privately` tabs plus a message box.
   - A vague translation could blur the difference between messages to everyone and one-to-one/private conversations.
   - The line should name the high-level distinction without opening or reading a private tab by default.

3. **Recipient and sender identity leakage**
   - Chat rows may expose sender names, recipient names, avatars, timestamps, read/unread cues, or private conversation labels.
   - Even when content is not read, naming who sent a message or who a private chat targets can leak meeting participation and conversation context.
   - Treat sender names, recipient names, and private conversation labels like participant names: only read when explicitly requested and verified.

4. **Unread/private tab sensitivity**
   - Unread badges, selected private tabs, and private conversation lists can reveal that private messages exist.
   - The narration may explain that the panel supports public and private chat, but should not report unread counts, private tab names, or the presence of a private thread by default.
   - Manual validation should avoid recording screenshots or logs that include private tab contents or badges.

5. **Message box side effects**
   - The Chat panel includes a message input box.
   - A localization slice must not add behavior that types, sends, drafts, copies, or submits text.
   - The Japanese line should not promise that AiPresenter can send messages unless a separate confirmed workflow exists.

6. **Panel cleanup/toggle risk**
   - `ringcentral.video.toolbar.chat` uses `cleanup: toggle`, and presenter notes say to toggle Chat or close the side panel before continuing.
   - If Chat remains open, the next `explain-microphone` step can look like the presenter is still observing private chat while discussing audio.
   - Cleanup must return to a stable meeting surface before moving to Microphone.

7. **Boundary with Participants**
   - Participants and Chat share a side-panel area and adjacent tabs, but they expose different privacy classes.
   - Participants covers roster names, roles, counts, and people controls; Chat covers public/private message content, senders, recipients, tabs, and message input.
   - The Japanese Chat line must not drift into roster explanation, attendee count, host controls, or participant management.

8. **Boundary with Microphone**
   - The next step is `explain-microphone`, a local audio privacy control.
   - Chat cleanup should happen before microphone narration so the demo does not conflate text-message privacy with audio mute state.
   - Do not introduce any mute/unmute behavior, audio state claims, or live meeting side effects in the Chat localization slice.

9. **Alias/Q&A routing risk**
   - Japanese aliases already exist for Chat, and there is a Japanese Q&A for whether the presenter can read chat content or participant names.
   - Tests already assert the Japanese chat privacy question stays answer-only with aliases, `entrypoint_id is None`, and `can_operate is False`.
   - Adding narration must not expand aliases or routing so privacy questions like "can you read chat content" open Chat automatically.

10. **Localized UI mismatch**
   - The package keeps product labels such as `Chat`, `Participants`, and `Mute` as visible control names.
   - Japanese narration does not prove the live RingCentral UI or accessibility names are localized.
   - Keep `Chat` in the Japanese line so spoken guidance maps to the modeled toolbar control and existing tests.

## Mitigations

- Keep implementation narration-only: add only `narration.localizedText.ja` under `meeting-controls-tour` -> `explain-chat`.
- Preserve the visible product label `Chat`.
- Mention the message panel at a high level and distinguish messages to everyone from private conversations.
- Include an explicit default privacy boundary: do not read chat content unless the user explicitly asks and the visible content is verified.
- Do not read or mention sender names, recipient names, unread counts, private thread names, message timestamps, or message bodies by default.
- Include cleanup language so the panel is closed or toggled after explanation.
- Do not type, draft, send, copy, translate, summarize, or quote chat messages in this slice.
- Do not change entrypoints, locators, `openSteps`, cleanup behavior, aliases, Q&A, runtime behavior, tests, or unrelated docs unless a separate owner explicitly owns that scope.
- Keep Participants and Microphone separate from Chat; no roster controls, attendee counts, host controls, or mute/unmute behavior should be added here.

## Must Verify

- YAML shape:
  - `localizedText.ja` is added under `meeting-controls-tour` -> `explain-chat` -> `narration`.
  - Existing English text, Chinese `localizedText.zh`, `placement: during`, and `actionOffsetMs: 350` remain unchanged unless a separate owner explicitly changes them.
  - No entrypoint, locator, `openSteps`, cleanup, aliases, Q&A, runtime, or unrelated flow changes are bundled into this narration slice.

- Text safety:
  - Includes `Chat`.
  - Mentions the message panel or message area.
  - Mentions messages to everyone/public recipients and private conversations/tabs at a high level.
  - Includes a default "do not read" privacy boundary.
  - Does not say AiPresenter will read, summarize, translate, quote, send, draft, copy, or submit chat messages by default.
  - Does not mention sender names, recipient names, unread counts, private thread labels, participant names, attendee counts, or microphone state as something AiPresenter will report by default.

- Panel and flow behavior:
  - Chat may be opened for the scripted tour, but the message box remains untouched.
  - The Chat panel is toggled closed or safely returned to the stable meeting surface before `explain-microphone`.
  - A lingering Chat panel while Microphone narration plays is a failure unless the UI is intentionally being closed and no message content is read aloud.

- Privacy routing:
  - Japanese Chat where-is aliases can still map to `ringcentral.video.toolbar.chat`.
  - Japanese privacy questions about reading chat content remain answer-only, with no entrypoint and `can_operate` false.
  - Japanese Q&A and alias counts should remain unchanged.

- Expected localization movement after implementation:
  - Overall Japanese demo narration should move from `15/51` to `16/51`.
  - `meeting-controls-tour` Japanese narration should move from `8/22` to `9/22`.
  - First missing `meeting-controls-tour` step should advance from `explain-chat` to `explain-microphone`.
  - `--require-complete` for Japanese should still fail because later demo narration remains incomplete.

- Current-tree test expectation note:
  - Focused tests already appear advanced for this slice: Japanese coverage assertions expect `16/51`, `meeting-controls-tour: 9/22`, and `missing: explain-microphone`.
  - A focused test for `explain-chat` expects the Japanese text to include `Chat`, message/public/private privacy terms, "do not read", "close", and "do not send" language.
  - A focused question-routing test expects the Japanese chat/participant privacy question to remain answer-only.

- Suggested focused checks after implementation:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_meeting_controls_tour_has_japanese_chat_narration tests\unit\test_questions.py::test_ringcentral_japanese_chat_privacy_question_stays_answer_only_with_aliases tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Manual validation, if any, should use a disposable meeting with no real chat content. Do not record private message bodies, sender names, recipient names, private tab labels, unread badges, participant names, invite links, or screenshots containing private meeting content.

## Recommendation

Proceed as a narrow narration-only slice if the Japanese line keeps `Chat` mapped to the visible toolbar control, explains public/private chat at the panel level, states that AiPresenter does not read content unless explicitly asked and verified, and closes or toggles the panel before Microphone. This is acceptable localization risk, but it should not be batched with aliases, Q&A routing, runtime behavior, message sending, Participants cleanup changes, Microphone behavior, or any live chat-content handling.

## Changed Files

- `docs/agent-handoffs/cycle-065-risk-scan.md`
