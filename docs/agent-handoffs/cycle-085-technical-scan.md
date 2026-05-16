# Cycle 085 Technical Scan: control-map-participants JA

Date: 2026-05-16

## Target YAML Snapshot

Target file: `packages/ringcentral-video.yaml`

Current target step:

```yaml
- id: control-map-participants
  title: Participants
  action:
    entrypointId: ringcentral.video.toolbar.participants
    operation: open
  narration:
    text: Participants is the meeting roster. It helps you confirm who is present and exposes people controls
      like invite, lock, mute, raise hand, and more options.
    localizedText:
      zh: Participants 是参会人列表。你可以确认谁在会议里，也能找到邀请、锁定会议、静音、举手和更多成员操作。
    placement: during
    actionOffsetMs: 350
```

Current gap: `control-map-participants` has Chinese localized narration but no `localizedText.ja`.

Action semantics to preserve:

- `entrypointId`: `ringcentral.video.toolbar.participants`
- `operation`: `open`
- `placement`: `during`
- `actionOffsetMs`: `350`

This slice should add only `localizedText.ja` under `meeting-control-map-demo` -> `control-map-participants`.

## Entrypoint Route

Entrypoint: `ringcentral.video.toolbar.participants`

```yaml
- id: ringcentral.video.toolbar.participants
  title: Participants panel
  area: Meeting toolbar
  purpose: Open participant list and meeting people controls.
  questionAliases:
    ja:
    - 参加者
    - 参加者一覧
    - 参加者パネル
    zh:
    - 参会者
    - 参会人列表
    - 谁在会议里
  openSteps:
  - action: clickWindowControl
    target: Participants
    match:
      controlType: button
      cleanup: toggle
```

Route details:

- Area: `Meeting toolbar`
- Purpose: `Open participant list and meeting people controls.`
- Route action: `clickWindowControl`
- Target: `Participants`
- Match: `controlType: button`
- Cleanup: `toggle`
- Existing Japanese aliases already cover `参加者`, `参加者一覧`, and `参加者パネル`; this slice should not add aliases.

Presenter notes:

- Use this to answer questions about attendee count and meeting control.
- Do not identify participants unless the UI text is verified and allowed.
- Observed panel has Participant and Chat tabs, search, invite, lock, mute, raise-hand, and more controls.
- Toggle the Participants button or close the side panel before opening Chat.

Do not change the entrypoint route, aliases, open steps, cleanup, purpose, or presenter notes.

## Test Updates

Recommended red-first updates:

- `tests/unit/test_material_packages.py`
  - In `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`, update JA demo coverage from `35` to `36`.
  - Update `meeting-control-map-demo` localized steps from `6` to `7`.
  - Update first missing step from `control-map-participants` to `control-map-chat`.
  - Add `test_meeting_control_map_has_japanese_participants_narration` after `test_meeting_control_map_has_japanese_add_coworkers_narration`.
  - Focused assertions should cover:
    - `step.action.entrypoint_id == "ringcentral.video.toolbar.participants"`
    - `step.action.operation == "open"`
    - `step.narration.placement == "during"`
    - `step.narration.action_offset_ms == 350`
    - entrypoint route has one open step using `clickWindowControl`, target `Participants`, `controlType == "button"`, and `cleanup == "toggle"`
    - presenter notes mention attendee count, meeting control, not identifying participants unless verified and allowed, Participant and Chat tabs, search, invite, lock, mute, raise-hand, more controls, and toggle-or-close cleanup before Chat
    - JA aliases remain exactly `["参加者", "参加者一覧", "参加者パネル"]`
    - JA text exists, has CJK, and includes `Participants`, `参加者`, `一覧`, `人数`, `Invite`, `ロック`, `ミュート`, `挙手`, `その他`, `ユーザー`, `明示的`, `求め`, `表示内容`, `確認`, `読み上げません`, and `閉じます`
    - JA text excludes overreach such as `名前を読み上げます`, `参加者を特定します`, `ミュートします`, `ロックします`, `Invite を押します`, `招待します`, `検索します`, `挙手させます`, `操作します`, `全員`, and `必ず`

- `tests/unit/test_cli.py`
  - In both Japanese localization-report tests, update:
    - `Localization report: 35/51 demo steps` -> `Localization report: 36/51 demo steps`
    - `- meeting-control-map-demo: 6/22 narration localized` -> `- meeting-control-map-demo: 7/22 narration localized`
    - `missing: control-map-participants` -> `missing: control-map-chat`
  - Keep `missing: explain-leave` absent.
  - Keep Q&A coverage unchanged at `12/12` questions and `12/12` answers.
  - Keep JA aliases unchanged at `questionAliases.ja present on 3/27 entrypoints (9 aliases)`.

- `tests/unit/test_diagnostics.py`
  - In `test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`, update `35/51 demo steps` -> `36/51 demo steps`.
  - Keep status `FAIL`, detail `required ja localization incomplete`, and Q&A details unchanged.

Expected red state before YAML implementation:

- Updated count assertions fail because current state is `35/51` overall and `6/22` for `meeting-control-map-demo`.
- Updated first-missing assertion fails because current first missing step is `control-map-participants`.
- New focused JA narration test fails because `step.narration.localized_text["ja"]` is missing for `control-map-participants`.

Expected green state after this slice:

- Overall JA demo narration: `36/51`
- `meeting-control-map-demo`: `7/22`
- First missing JA step in that flow: `control-map-chat`
- Required JA localization: still incomplete/failing
- Q&A JA coverage: still `12/12` questions and `12/12` answers
- JA aliases: still `3/27` entrypoints and `9` aliases

## Suggested Japanese Text

Recommended `localizedText.ja`:

```yaml
        ja: Participants は会議の参加者一覧パネルです。ここでは現在の人数を確認し、Invite、会議のロック、ミュート、挙手、その他の参加者操作に進める場所を把握できます。ただし、名前や役割などの参加者情報は、ユーザーが明示的に求め、表示内容が確認されるまで読み上げません。説明後は、Chat を開く前にこのパネルを閉じます。
```

Why this wording:

- Preserves the source meaning: `Participants` is the roster and exposes people controls.
- Names the expected panel capabilities from presenter notes: attendee count, invite, lock, mute, raise-hand, and more controls.
- Keeps the presenter explanation-only and privacy-safe for roster names, roles, and attendee details.
- Reflects route cleanup: this is a toggle side panel and should be closed before moving to Chat.
- Avoids claiming the presenter invites, locks, mutes, raises hands, searches, identifies attendees, or reads participant names.

Acceptable shorter variant:

```yaml
        ja: Participants は会議の参加者一覧です。人数を確認し、Invite、ロック、ミュート、挙手、その他の参加者操作に進める場所ですが、ユーザーが明示的に求め、表示内容が確認されるまで名前や役割は読み上げません。説明後はパネルを閉じます。
```

Avoid wording such as:

- `参加者の名前を読み上げます`
- `参加者を特定します`
- `参加者をミュートします`
- `会議をロックします`
- `Invite を押します`
- `同僚を招待します`
- `参加者を検索します`
- `手を挙げさせます`
- `参加者操作を実行します`
- `全員の状態を確認します`
- `必ず閉じます`

## Verification Commands

Focused test command after implementation:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_participants_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Optional focused CLI check:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Expected CLI lines after implementation:

```text
Localization report: 36/51 demo steps
- meeting-control-map-demo: 7/22 narration localized
  missing: control-map-chat
- localized questions: 12/12
- localized answers: 12/12
questionAliases.ja present on 3/27 entrypoints (9 aliases)
```

Japanese `--require-complete` should still exit nonzero and print `Localization coverage incomplete for ja.`

## Do-not-change Guardrails

- Do not edit YAML, code, tests, source-index, profiles, or other docs in this scan. This scan writes only `docs/agent-handoffs/cycle-085-technical-scan.md`.
- Implementation should edit only the targeted JA narration and directly related test expectations.
- Do not change `control-map-participants` action semantics: keep `entrypointId`, `operation`, `placement`, and `actionOffsetMs` exactly as they are.
- Do not change `ringcentral.video.toolbar.participants` route semantics: keep `clickWindowControl`, target `Participants`, `controlType: button`, and `cleanup: toggle`.
- Do not add or change Japanese aliases; current JA alias coverage should remain `3/27` entrypoints and `9` aliases.
- Do not localize `control-map-chat` or any later `meeting-control-map-demo` step in this slice.
- Do not broaden into Q&A, Chinese/English narration, presenter notes, locator strategy, diagnostics behavior, CLI formatting, or acceptance evidence.
- Do not imply the presenter clicks Invite, invites people, searches attendees, identifies participants, reads names or roles, locks the meeting, mutes anyone, raises hands for anyone, or performs participant-management actions unless the user explicitly asks and the visible content has been verified.
- Do not leave the Participants panel open before the next `control-map-chat` step; the route cleanup expectation is toggle/side-panel close before opening Chat.
- Do not revert or overwrite concurrent edits from other agents.
