# Cycle 086 Technical Scan: control-map-chat JA

Date: 2026-05-16

## Target YAML Snapshot

Target file: `packages/ringcentral-video.yaml`

Current target step:

```yaml
- id: control-map-chat
  title: Chat
  action:
    entrypointId: ringcentral.video.toolbar.chat
    operation: open
  narration:
    text: Chat is the written side channel. Use it for links, follow-ups, and private messages, while keeping
      chat content private unless you explicitly ask me to read it.
    localizedText:
      zh: Chat 是会议里的文字侧边通道。适合发链接、补充信息或私聊；聊天内容默认保持隐私，除非你明确让我读。
    placement: during
    actionOffsetMs: 350
```

Current gap: `control-map-chat` has Chinese localized narration but no `localizedText.ja`.

Action semantics to preserve:

- `entrypointId`: `ringcentral.video.toolbar.chat`
- `operation`: `open`
- `placement`: `during`
- `actionOffsetMs`: `350`

This slice should add only `localizedText.ja` under `meeting-control-map-demo` -> `control-map-chat`.

Baseline verified with `.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja`: JA is `36/51` overall, `meeting-control-map-demo` is `7/22`, and the first missing step is `control-map-chat`.

## Entrypoint Route

Entrypoint: `ringcentral.video.toolbar.chat`

```yaml
- id: ringcentral.video.toolbar.chat
  title: Chat panel
  area: Meeting toolbar
  purpose: Open in-meeting chat.
  questionAliases:
    ja:
    - チャット
    - チャットパネル
    - メッセージ
    zh:
    - 聊天
    - 聊天室
    - 消息
    - 聊天在哪里
  openSteps:
  - action: clickWindowControl
    target: Chat
    match:
      controlType: button
      cleanup: toggle
  presenterNotes:
  - Chat is a collaboration side panel for meeting messages.
  - Do not read private chat text aloud unless the user explicitly asks.
  - Observed panel has Within everyone and Privately tabs plus a message box.
  - Toggle the Chat button or close the side panel before continuing.
```

Route details:

- Area: `Meeting toolbar`
- Purpose: `Open in-meeting chat.`
- Route action: `clickWindowControl`
- Target: `Chat`
- Match: `controlType: button`
- Cleanup: `toggle`
- Existing Japanese aliases are exactly `["チャット", "チャットパネル", "メッセージ"]`; this slice should not add aliases.

Presenter-note semantics to preserve:

- Chat is a collaboration side panel for meeting messages.
- Do not read private chat text aloud unless the user explicitly asks.
- Observed panel has `Within everyone` and `Privately` tabs plus a message box.
- Toggle the Chat button or close the side panel before continuing.

## Test Updates

Expected coverage deltas after adding only this one JA narration:

- Overall JA demo narration: `36/51` -> `37/51`
- `meeting-control-map-demo`: `7/22` -> `8/22`
- First missing step: `control-map-chat` -> `control-map-microphone`
- Required JA localization: still incomplete/failing
- Q&A JA coverage: still `12/12` questions and `12/12` answers
- JA aliases: still `3/27` entrypoints and `9` aliases

Recommended focused test updates:

- `tests/unit/test_material_packages.py`
  - In `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`, update localized steps from `36` to `37`, `meeting-control-map-demo` from `7` to `8`, and first missing from `control-map-chat` to `control-map-microphone`.
  - Add `test_meeting_control_map_has_japanese_chat_narration` near the adjacent control-map JA narration tests.
  - Assert `step.action.entrypoint_id == "ringcentral.video.toolbar.chat"`, `step.action.operation == "open"`, `step.narration.placement == "during"`, and `step.narration.action_offset_ms == 350`.
  - Assert the route has one open step using `clickWindowControl`, target `Chat`, `controlType == "button"`, and `cleanup == "toggle"`.
  - Assert JA aliases remain exactly `["チャット", "チャットパネル", "メッセージ"]`.
  - Assert presenter notes mention collaboration side panel, private chat text not read unless explicitly asked, `Within everyone`, `Privately`, message box, and toggle/close cleanup.
  - Assert JA text exists, has CJK, and includes `Chat`, `文字`, `サイド`, `リンク`, `フォローアップ`, `個別`, `メッセージ`, `プライベート`, `ユーザー`, `明示的`, `求め`, `読み上げません`, `Within everyone`, and `Privately`.
  - Assert JA text does not imply reading or sending content, such as `読み上げます`, `読みます`, `送信します`, `入力します`, `返信します`, `開示します`, `共有します`, `全員に送ります`, `必ず`, or `自動`.
- `tests/unit/test_cli.py`
  - In both Japanese localization-report tests, update `Localization report: 36/51 demo steps` -> `Localization report: 37/51 demo steps`.
  - Update `- meeting-control-map-demo: 7/22 narration localized` -> `- meeting-control-map-demo: 8/22 narration localized`.
  - Update `missing: control-map-chat` -> `missing: control-map-microphone`.
  - Keep `missing: explain-leave` absent, Q&A at `12/12`, and alias coverage at `questionAliases.ja present on 3/27 entrypoints (9 aliases)`.
- `tests/unit/test_diagnostics.py`
  - In `test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`, update `36/51 demo steps` -> `37/51 demo steps`.
  - Keep status `FAIL`, detail `required ja localization incomplete`, and Q&A details unchanged.

Expected red state before YAML implementation:

- Updated count assertions fail because current state is `36/51` overall and `7/22` for `meeting-control-map-demo`.
- Updated first-missing assertion fails because current first missing step is `control-map-chat`.
- New focused JA narration test fails because `step.narration.localized_text["ja"]` is missing for `control-map-chat`.

Expected green state after this slice:

- Overall JA demo narration: `37/51`
- `meeting-control-map-demo`: `8/22`
- First missing JA step in that flow: `control-map-microphone`
- Required JA localization: still incomplete/failing
- Q&A JA coverage: still `12/12` questions and `12/12` answers
- JA aliases: still `3/27` entrypoints and `9` aliases

## Suggested Japanese Text

Recommended `localizedText.ja`:

```yaml
        ja: Chat は会議内の文字ベースのサイドチャネルです。リンク、フォローアップ、個別メッセージのやり取りに使う場所で、Within everyone と Privately のタブ、メッセージ入力欄を確認できます。ただし、チャット内容はプライベートな情報として扱い、ユーザーが明示的に求めるまで読み上げません。説明後は、続行前に Chat パネルを閉じます。
```

Why this wording:

- Preserves the source meaning: Chat is the written side channel for links, follow-ups, and private messages.
- Reflects presenter notes: `Within everyone`, `Privately`, message box, and toggle/close cleanup.
- Keeps chat content private unless the user explicitly asks for it to be read.
- Avoids claiming the presenter sends, types, replies to, shares, exposes, or automatically reads messages.

Acceptable shorter variant:

```yaml
        ja: Chat は会議内の文字サイドチャネルです。リンク、フォローアップ、個別メッセージに使う場所で、Within everyone と Privately のタブやメッセージ入力欄があります。内容はプライベートな情報として扱い、ユーザーが明示的に求めるまで読み上げません。説明後はパネルを閉じます。
```

Avoid wording such as:

- `チャット内容を読み上げます`
- `メッセージを読みます`
- `メッセージを送信します`
- `返信します`
- `入力します`
- `全員に送ります`
- `内容を共有します`
- `内容を開示します`
- `自動で読み上げます`
- `必ず読み上げます`

## Verification Commands

Focused test command after implementation:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_chat_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Optional focused CLI check:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Expected CLI lines after implementation:

```text
Localization report: 37/51 demo steps
- meeting-control-map-demo: 8/22 narration localized
  missing: control-map-microphone
- localized questions: 12/12
- localized answers: 12/12
questionAliases.ja present on 3/27 entrypoints (9 aliases)
```

Japanese `--require-complete` should still exit nonzero and print `Localization coverage incomplete for ja.`

## Do-not-change Guardrails

- This scan writes only `docs/agent-handoffs/cycle-086-technical-scan.md`; do not edit YAML, code, tests, source index, profiles, or other docs in this scan.
- Implementation should edit only the targeted JA narration and directly related test expectations.
- Do not change `control-map-chat` action semantics: keep `entrypointId`, `operation`, `placement`, and `actionOffsetMs` exactly as they are.
- Do not change `ringcentral.video.toolbar.chat` route semantics: keep `clickWindowControl`, target `Chat`, `controlType: button`, and `cleanup: toggle`.
- Do not add or change Japanese aliases; current JA alias coverage should remain `3/27` entrypoints and `9` aliases.
- Do not localize `control-map-microphone` or any later `meeting-control-map-demo` step in this slice.
- Do not broaden into Q&A, Chinese/English narration, presenter notes, locator strategy, diagnostics behavior, CLI formatting, profiles, source-index updates, or acceptance evidence.
- Do not imply the presenter reads private/public chat content, sends messages, replies, types, shares links, opens private messages, exposes message contents, or summarizes chat unless the user explicitly asks and visible content has been verified.
- Do not leave the Chat panel open before continuing; the route cleanup expectation is toggle/side-panel close.
- Do not revert or overwrite concurrent edits from other agents.
