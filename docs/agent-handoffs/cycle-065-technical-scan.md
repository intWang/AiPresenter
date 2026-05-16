# Cycle 065 Technical Scan: meeting-controls-tour / explain-chat JA narration

## Scope

Scan only for the next implementation pass. The proposed implementation should add Japanese `localizedText.ja` narration to one step:

- Package: `packages/ringcentral-video.yaml`
- Flow: `meeting-controls-tour`
- Step: `explain-chat`
- Entrypoint: `ringcentral.video.toolbar.chat`
- Operation: `open`

Do not change runtime behavior, open steps, action offsets, aliases, Q&A, flow order, diagnostics logic, CLI logic, or unrelated docs as part of this narration slice unless the implementation owner explicitly expands scope.

## Local Context Read

- `packages/ringcentral-video.yaml`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_diagnostics.py`
- Recent handoffs:
  - `docs/agent-handoffs/cycle-064-technical-scan.md`
  - `docs/agent-handoffs/cycle-064-implementation.md`
  - `docs/agent-handoffs/cycle-064-review.md`
  - `docs/agent-handoffs/cycle-064-summary.md`

Current verified baseline from:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

- `Localization report: 15/51 demo steps`
- `meeting-controls-tour: 8/22 narration localized`
- first missing `meeting-controls-tour` step: `explain-chat`
- Q&A remains complete: `12/12` localized questions and `12/12` localized answers
- Japanese aliases remain partial: `questionAliases.ja present on 3/27 entrypoints (9 aliases)`

Important current-tree note: the focused Cycle 065 tests already appear to be advanced to the expected post-implementation state. The package YAML has not yet been advanced for `explain-chat`, so the implementation owner should expect the advanced tests to fail until the YAML gets the Japanese narration. I confirmed this with the focused pytest command in the verification section: `5 failed`.

## Source Step

Current English narration:

```yaml
text: Chat opens the message panel. It supports messages to everyone and private conversations, but I do not
  read chat content unless you ask.
```

Current Chinese narration:

```yaml
zh: Chat 会打开消息面板，支持发给所有人的消息和私聊。聊天内容默认保持隐私，除非用户明确要求读取。
```

Relevant entrypoint notes for `ringcentral.video.toolbar.chat`:

- Chat is a collaboration side panel for meeting messages.
- Do not read private chat text aloud unless the user explicitly asks.
- Observed panel has Within everyone and Privately tabs plus a message box.
- Toggle the Chat button or close the side panel before continuing.

Relevant prior slices:

- Cycle 062 localized `explain-add-coworkers`, with privacy language for names, email addresses, suggestions, and private invite links.
- Cycle 063 localized `explain-invite`, preserving invite/link privacy.
- Cycle 064 localized `explain-participants`, preserving roster privacy and making `explain-chat` the next missing step.
- `meeting-basics-demo` already has Japanese `show-chat` narration with a useful baseline: Chat is a text collaboration channel, and chat content is private by default until the user explicitly asks.

## Recommended Japanese Wording

Recommended insertion under `narration.localizedText`:

```yaml
        ja: Chat はメッセージパネルを開きます。全員宛てのメッセージと非公開の会話に対応していますが、ユーザーが明示的に求めるまでチャット内容は読み上げません。説明したら、このサイドパネルを閉じます。ユーザーの明確な指示なしにメッセージを送信しません。
```

Rationale:

- Preserves visible UI label `Chat`.
- Includes `メッセージ`, `全員`, and `非公開`, matching the current advanced test expectations.
- Keeps the key safety rule: do not read chat content unless the user explicitly asks.
- Mentions closing the side panel before continuing, matching the entrypoint cleanup behavior.
- Adds an explicit no-send default. Opening Chat can expose a message box; this wording avoids implying AiPresenter can send chat messages during a tour.
- Avoids adding names, participant roles, or invite-link language that belongs to the surrounding Participants/Invite slices.

## Expected Count Changes

After adding only this `localizedText.ja` entry:

- Overall Japanese demo narration: `15/51` -> `16/51`
- `meeting-controls-tour`: `8/22` -> `9/22`
- First missing `meeting-controls-tour` step should advance from `explain-chat` to `explain-microphone`
- Q&A counts should remain `12/12` questions and `12/12` answers
- Japanese alias counts should remain `questionAliases.ja present on 3/27 entrypoints (9 aliases)`
- `--require-complete` for Japanese should still fail because the package remains partially localized.

## Tests To Update/Add

The current test files already contain the expected Cycle 065 assertions. If the implementation owner is working from this tree, no test edits should be needed; the YAML narration should turn the existing red tests green.

Existing expected test coverage to preserve:

- `tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`
  - expects `report.demo_localized_steps == 16`
  - expects `report.flow_by_id["meeting-controls-tour"].localized_steps == 9`
  - keeps `report.demo_total_steps == 51`
  - keeps `meeting-controls-tour` total at `22`
  - keeps Q&A and alias expectations unchanged

- `tests/unit/test_material_packages.py::test_meeting_controls_tour_has_japanese_chat_narration`
  - asserts Japanese text exists and contains CJK
  - asserts `Chat`
  - asserts `メッセージ`
  - asserts `全員`
  - asserts `非公開`
  - asserts `読み上げません`
  - asserts `閉じます`
  - asserts `送信しません`

- `tests/unit/test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage`
  - expects `Localization report: 16/51 demo steps`
  - expects `- meeting-controls-tour: 9/22 narration localized`
  - expects `missing: explain-microphone`
  - keeps Q&A and alias lines unchanged

- `tests/unit/test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap`
  - expects exit code `1`
  - expects `Localization report: 16/51 demo steps`
  - expects `- meeting-controls-tour: 9/22 narration localized`
  - expects `missing: explain-microphone`
  - keeps `Localization coverage incomplete for ja.`

- `tests/unit/test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`
  - expects diagnostic detail to include `16/51 demo steps`
  - keeps `required ja localization incomplete`
  - keeps `12/12 Q&A questions` and `12/12 Q&A answers`

If applying this scan to a branch that does not already have the chat-focused test, add it with the assertions listed above. Do not add Japanese `questionAliases` for new entrypoints in this pass; `ringcentral.video.toolbar.chat` already has Japanese aliases, and expected alias counts above assume no alias change.

## Expected CLI Output Changes

For:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Expected relevant output after implementation:

```text
Language: ja
- meeting-controls-tour: 9/22 narration localized
  missing: explain-microphone, explain-audio-menu, explain-camera, explain-camera-menu, explain-share, explain-reactions, explain-raise-hand, explain-more, explain-recording, explain-notes, explain-background-settings, explain-settings, explain-leave
- localized questions: 12/12
- localized answers: 12/12
questionAliases.ja present on 3/27 entrypoints (9 aliases)
Localization report: 16/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
```

For:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
```

Expected result after implementation:

- Exit code: `1`
- Includes `Localization report: 16/51 demo steps`
- Includes `- meeting-controls-tour: 9/22 narration localized`
- Includes `missing: explain-microphone`
- Includes `Localization coverage incomplete for ja.`

## Verification Commands

Run targeted tests with the project venv:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_controls_tour_has_japanese_chat_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Expected pre-implementation result in this current tree:

- `5 failed`
- failures are the advanced `16/51`, `9/22`, and `localized_text["ja"]` expectations for `explain-chat`

Optional broader package-localization sweep:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py -k "japanese or localization_status or chat"
```

CLI smoke checks:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
```

Optional doctor localization preflight:

```powershell
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --language ja --require-localization
```

Expected doctor result remains nonzero because Japanese localization is still incomplete, but the localization detail should move to `16/51 demo steps`.

## Notes For Implementer

- Keep the YAML insertion under `localizedText.ja`, not `localizedText.jp`.
- Preserve existing `zh`, `placement: during`, and `actionOffsetMs: 350`.
- Keep product/UI labels in English where they match visible UI: `Chat`.
- This step opens a side panel, not a modal. Keep the narration about closing the panel, but do not change cleanup or operation behavior in a narration-only pass.
- The Chat panel may show public meeting messages, private conversations, and a message composer. Default narration should describe the panel and privacy posture, not read message text or send messages.
- Do not imply AiPresenter will read chat content, infer private messages, switch private tabs, or send a message unless the user explicitly asks and visible context is verified.
