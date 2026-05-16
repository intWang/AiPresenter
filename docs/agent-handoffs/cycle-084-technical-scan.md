# Cycle 084 Technical Scan: control-map-add-coworkers JA

Date: 2026-05-16

## Target YAML Snapshot

Target file: `packages/ringcentral-video.yaml`

Current target step:

```yaml
- id: control-map-add-coworkers
  title: Add coworkers
  action:
    entrypointId: ringcentral.video.main.add-coworkers
    operation: open
  narration:
    text: Moving from status into people, Add coworkers opens the invite dialog from the empty room. This is the
      fastest way to bring someone in when you are the first person here.
    localizedText:
      zh: 从状态区切到成员区。空会议里的 Add coworkers 会打开邀请窗口；当你一个人在会里时，这是最快的拉人入口。
    placement: during
    actionOffsetMs: 350
```

Current gap: `control-map-add-coworkers` has Chinese localized narration but no `localizedText.ja`.

Action semantics to preserve:

- `entrypointId`: `ringcentral.video.main.add-coworkers`
- `operation`: `open`
- `placement`: `during`
- `actionOffsetMs`: `350`

This slice should add only `localizedText.ja` under `meeting-control-map-demo` -> `control-map-add-coworkers`.

## Entrypoint Route

Entrypoint: `ringcentral.video.main.add-coworkers`

```yaml
- id: ringcentral.video.main.add-coworkers
  title: Add coworkers
  area: Meeting canvas
  purpose: Open the Invite others dialog from the empty-meeting callout.
  openSteps:
  - action: clickWindowControl
    target: Add coworkers
    match:
      controlType: button
      cleanup: modal
```

Route details:

- Area: `Meeting canvas`
- Route action: `clickWindowControl`
- Target: `Add coworkers`
- Match: `controlType: button`
- Cleanup: `modal`
- Presenter notes say the dialog includes a name/email field, suggestions, Copy meeting link, Cancel, and Invite; it is similar to the toolbar Invite control; the empty-room callout should be skipped when participant tiles or a Participants badge count show other attendees; and the dialog blocks the toolbar until closed with X or Cancel.

Do not change the entrypoint route, open steps, cleanup, purpose, question aliases, or presenter notes.

## Test Updates

Recommended red-first updates:

- `tests/unit/test_material_packages.py`
  - In `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`, update JA demo coverage from `34` to `35`.
  - Update `meeting-control-map-demo` localized steps from `5` to `6`.
  - Update first missing step from `control-map-add-coworkers` to `control-map-participants`.
  - Add `test_meeting_control_map_has_japanese_add_coworkers_narration` after the existing `test_meeting_control_map_has_japanese_report_narration`.
  - Focused assertions should cover:
    - `step.action.entrypoint_id == "ringcentral.video.main.add-coworkers"`
    - `step.action.operation == "open"`
    - `step.narration.placement == "during"`
    - `step.narration.action_offset_ms == 350`
    - entrypoint route has one open step using `clickWindowControl`, target `Add coworkers`, `controlType == "button"`, and `cleanup == "modal"`
    - presenter notes mention the name/email field, suggestions, Copy meeting link, Cancel, Invite, similarity to toolbar Invite, empty-room/first-one-here condition, and X or Cancel cleanup
    - JA text exists, has CJK, and includes terms such as `Add coworkers`, `Invite`, `空の会議`, `招待`, `同僚`, `検索`, `会議リンク`, `候補`, `名前`, `メールアドレス`, `読み上げません`, `ユーザー`, `明示的`, `確認`, and `閉じます`
    - JA text excludes overreach such as `招待します`, `Invite を押します`, `送信します`, `追加します`, `入力します`, `検索します`, `コピーします`, `読み上げます`, `参加者がいる場合も`, and `必ず`

- `tests/unit/test_cli.py`
  - In both Japanese localization-report tests, update:
    - `Localization report: 34/51 demo steps` -> `Localization report: 35/51 demo steps`
    - `- meeting-control-map-demo: 5/22 narration localized` -> `- meeting-control-map-demo: 6/22 narration localized`
    - `missing: control-map-add-coworkers` -> `missing: control-map-participants`
  - Keep `missing: explain-leave` absent.
  - Keep Q&A coverage unchanged at `12/12` questions and `12/12` answers.
  - Keep JA aliases unchanged at `questionAliases.ja present on 3/27 entrypoints (9 aliases)`.

- `tests/unit/test_diagnostics.py`
  - In `test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`, update `34/51 demo steps` -> `35/51 demo steps`.
  - Keep status `FAIL`, detail `required ja localization incomplete`, and Q&A details unchanged.

Expected red state before YAML implementation:

- Updated count assertions fail because current state is `34/51` overall and `5/22` for `meeting-control-map-demo`.
- Updated first-missing assertion fails because current first missing step is `control-map-add-coworkers`.
- New focused JA narration test fails because `step.narration.localized_text["ja"]` is missing for `control-map-add-coworkers`.

Expected green state after this slice:

- Overall JA demo narration: `35/51`
- `meeting-control-map-demo`: `6/22`
- First missing JA step in that flow: `control-map-participants`
- Required JA localization: still incomplete/failing
- Q&A JA coverage: still `12/12` questions and `12/12` answers
- JA aliases: still `3/27` entrypoints and `9` aliases

## Suggested Japanese Text

Recommended `localizedText.ja`:

```yaml
        ja: ステータス領域からメンバー関連の領域に移ります。空の会議に表示される Add coworkers は Invite ダイアログを開き、最初に入室しているときに同僚を招待する入口です。名前やメールアドレスの検索、候補、会議リンク、Invite などを確認できますが、ユーザーが明示的に求め、表示内容が確認されるまで、名前、メールアドレス、候補、非公開の会議リンクは読み上げません。説明後はダイアログを閉じます。
```

Why this wording:

- Keeps the source progression from status into people controls.
- Names the UI labels `Add coworkers`, `Invite`, and the empty-meeting condition.
- Reflects the entrypoint notes: search/name-email field, suggestions, meeting link, Invite dialog, and modal cleanup.
- Avoids claiming the presenter actually invites, types, searches, copies, sends, or reads private invite data.
- Preserves the empty-room caveat; this callout is not a universal participants route.

Acceptable shorter variant:

```yaml
        ja: 空の会議に表示される Add coworkers は Invite ダイアログを開き、最初に入室しているときに同僚を招待する入口です。名前やメールアドレスの検索、候補、会議リンク、Invite を確認できますが、ユーザーが明示的に求め、内容が確認されるまで個人情報や非公開リンクは読み上げません。説明後は閉じます。
```

Avoid wording such as:

- `同僚を招待します`
- `Invite を押します`
- `招待を送信します`
- `名前を入力します`
- `メールアドレスを検索します`
- `会議リンクをコピーします`
- `候補を読み上げます`
- `参加者がいる場合も Add coworkers を使います`
- `必ずこの入口を使います`

## Verification Commands

Focused test command after implementation:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_add_coworkers_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Optional focused CLI check:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Expected CLI lines after implementation:

```text
Localization report: 35/51 demo steps
- meeting-control-map-demo: 6/22 narration localized
  missing: control-map-participants
- localized questions: 12/12
- localized answers: 12/12
questionAliases.ja present on 3/27 entrypoints (9 aliases)
```

Japanese `--require-complete` should still exit nonzero and print `Localization coverage incomplete for ja.`

## Do-not-change Guardrails

- Do not edit YAML, code, tests, source-index, profiles, or other docs in this scan. The implementation slice should edit only the targeted JA narration and directly related test expectations.
- Do not change `control-map-add-coworkers` action semantics: keep `entrypointId`, `operation`, `placement`, and `actionOffsetMs` exactly as they are.
- Do not change `ringcentral.video.main.add-coworkers` route semantics: keep `clickWindowControl`, target `Add coworkers`, `controlType: button`, and `cleanup: modal`.
- Do not add Japanese aliases for Add coworkers in this slice; current JA alias coverage should remain `3/27` entrypoints and `9` aliases.
- Do not localize `control-map-participants` or any later `meeting-control-map-demo` step in this slice.
- Do not broaden into Q&A, Chinese/English narration, presenter notes, locator strategy, adaptive empty-room logic, diagnostics behavior, CLI formatting, or acceptance evidence.
- Do not imply the presenter clicks Invite, sends invitations, types names or email addresses, searches coworkers, copies links, reads private invite links, reads names, reads email addresses, or treats suggestions as verified identities unless the user explicitly asks and the visible content has been verified.
- Do not remove the empty-room condition: this callout appears only when the user is the first one here, and should be skipped when participant tiles or a Participants badge count show other attendees are present.
- Do not revert or overwrite concurrent edits from other agents. This handoff intentionally writes only `docs/agent-handoffs/cycle-084-technical-scan.md`.
