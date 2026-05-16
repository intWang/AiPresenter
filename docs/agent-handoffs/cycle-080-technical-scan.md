# Cycle 080 Technical Scan: control-map-meeting-info JA

Date: 2026-05-16

## Target YAML Snapshot

Target file: `packages/ringcentral-video.yaml`

Current target step:

```yaml
- id: control-map-meeting-info
  title: Meeting information
  action:
    entrypointId: ringcentral.video.top.meeting-info
    operation: open
  narration:
    text: Starting at the top, meeting information answers the identity question. It shows the meeting details, link, dial-in options, and encryption information, so I summarize it without reading private values aloud.
    localizedText:
      zh: 先看顶部的会议信息。这里能确认会议身份、链接、拨入方式和加密状态；涉及隐私的数值，我只说明位置，不直接读出来。
    placement: during
    actionOffsetMs: 350
```

Current gap: `control-map-meeting-info` has Chinese localized narration but no `localizedText.ja`.

Action semantics to preserve:

- `entrypointId`: `ringcentral.video.top.meeting-info`
- `operation`: `open`
- `placement`: `during`
- `actionOffsetMs`: `350`

Because this is an executable open step, the Japanese copy can say the meeting information popover is being viewed or opened in context, but it should avoid implying that AiPresenter copies, dials, shares, changes encryption, or reads exact private values.

## Entrypoint Route

Entrypoint: `ringcentral.video.top.meeting-info`

```yaml
- id: ringcentral.video.top.meeting-info
  title: Meeting information
  area: Meeting top bar
  purpose: Open meeting details including meeting title, host, meeting ID, copy link, dial-in info, encryption, and end-to-end encryption option.
  questionAliases:
    en:
    - meeting information
    - meeting details
    - meeting ID
    - meeting link
    zh:
    - 会议信息
    - 会议号
    - 会议链接
  openSteps:
  - action: clickWindowRelative
    target: Meeting information
    match:
      x: '31'
      y: '21'
      cleanup: escape
```

Route details:

- Area: `Meeting top bar`
- Route action: `clickWindowRelative`
- Target: `Meeting information`
- Coordinate match: `x: '31'`, `y: '21'`
- Cleanup: `escape`
- Presenter notes warn that the popover can expose private meeting identifiers and copy-link controls; summarize purpose unless the user asks for exact values.
- The route should close with Escape before moving to another toolbar control.

Do not change the entrypoint route, open steps, cleanup, aliases, or presenter notes in this round.

## Test Updates

Recommended red-first updates:

- `tests/unit/test_material_packages.py`
  - In `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`, update overall JA demo coverage from `30` to `31`.
  - Update `meeting-control-map-demo` localized steps from `1` to `2`.
  - Update first missing step from `control-map-meeting-info` to `control-map-network`.
  - Add a focused guard test for `meeting-control-map-demo` -> `control-map-meeting-info`, parallel to the existing `control-map-overview` JA test.
  - The focused test should assert:
    - `step.action.entrypoint_id == "ringcentral.video.top.meeting-info"`
    - `step.action.operation == "open"`
    - `step.narration.placement == "during"`
    - `step.narration.action_offset_ms == 350`
    - entrypoint route uses `clickWindowRelative`, target `Meeting information`, `x == "31"`, `y == "21"`, and `cleanup == "escape"`
    - JA text exists, contains CJK, and includes required UI/concept terms such as `Meeting information`, `会議情報`, `Meeting ID`, `リンク`, `ダイヤルイン`, `暗号化`, `非公開`, `読み上げません`
    - JA text excludes over-action wording such as `コピーします`, `リンクをコピー`, `ダイヤルします`, `共有します`, `送信します`, `切り替えます`, `変更します`, `招待します`, `開始します`

- `tests/unit/test_cli.py`
  - In `test_localization_report_outputs_japanese_demo_and_qa_coverage`, update:
    - `Localization report: 30/51 demo steps` -> `Localization report: 31/51 demo steps`
    - `- meeting-control-map-demo: 1/22 narration localized` -> `- meeting-control-map-demo: 2/22 narration localized`
    - `missing: control-map-meeting-info` -> `missing: control-map-network`
  - In `test_localization_report_require_complete_fails_for_japanese_demo_gap`, make the same updates.
  - Keep `missing: explain-leave` absent.
  - Keep Q&A coverage unchanged at `12/12` questions and `12/12` answers.
  - Keep JA aliases unchanged at `questionAliases.ja present on 3/27 entrypoints (9 aliases)`.

- `tests/unit/test_diagnostics.py`
  - In `test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`, update `30/51 demo steps` -> `31/51 demo steps`.
  - Keep status `FAIL`.
  - Keep detail `required ja localization incomplete`.
  - Keep Q&A detail unchanged: `12/12 Q&A questions` and `12/12 Q&A answers`.

Expected red point before YAML implementation:

- Updated localization count assertions fail because current state is still `30/51`.
- Updated `meeting-control-map-demo` assertion fails because current state is still `1/22`.
- Updated first missing assertion fails because current first missing is still `control-map-meeting-info`.
- New focused JA narration test fails because `step.narration.localized_text["ja"]` is missing for `control-map-meeting-info`.

Expected green state after this slice:

- Overall JA demo narration: `31/51`
- `meeting-control-map-demo`: `2/22`
- First missing JA step in that flow: `control-map-network`
- Required JA localization: still incomplete/failing
- Q&A JA coverage: still `12/12` questions and `12/12` answers
- JA aliases: still `3/27` entrypoints and `9` aliases

## Suggested Japanese Text

Recommended `localizedText.ja`:

```yaml
        ja: 上部の Meeting information では、会議情報として Meeting ID、リンク、ダイヤルイン情報、暗号化状態などを確認できます。これらには非公開の値が含まれるため、ここでは場所と役割だけを説明し、ユーザーが明示的に求めるまで具体的な値は読み上げません。
```

Why this wording:

- Keeps necessary UI/concept names: `Meeting information`, `会議情報`, `Meeting ID`, `リンク`, `ダイヤルイン情報`, `暗号化状態`.
- Matches the English source: meeting identity/details, link, dial-in options, encryption information, and private-value handling.
- Explicitly avoids reading private values unless the user clearly asks.
- Does not claim to copy the meeting link, dial in, share a link, invite anyone, send anything, toggle encryption, or change meeting state.

Possible stricter variant if the team wants to avoid even "confirm/check" sounding too active:

```yaml
        ja: 上部の Meeting information は、会議情報の入口です。Meeting ID、リンク、ダイヤルイン情報、暗号化状態などが表示される領域ですが、非公開の値を含むため、ここでは場所と役割だけを説明し、ユーザーが明示的に求めるまで具体的な値は読み上げません。
```

## Verification Commands

Use the project virtual environment and keep `PYTHONPATH=src` if the package is not installed editable in the active shell:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests/unit/test_material_packages.py::test_meeting_control_map_has_japanese_meeting_info_narration tests/unit/test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests/unit/test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests/unit/test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Optional focused CLI check:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m ai_presenter.cli localization-report --package ringcentral-video --language ja
```

Expected CLI lines after implementation:

```text
Localization report: 31/51 demo steps
- meeting-control-map-demo: 2/22 narration localized
  missing: control-map-network
- localized questions: 12/12
- localized answers: 12/12
questionAliases.ja present on 3/27 entrypoints (9 aliases)
```

Japanese `--require-complete` should still exit nonzero and print `Localization coverage incomplete for ja.`

## Do-not-change Guardrails

- Do not change code, runtime behavior, selectors, locators, route coordinates, YAML flow order, operation names, or test infrastructure for this slice.
- Do not change `control-map-meeting-info` action semantics: keep `entrypointId`, `operation`, `placement`, and `actionOffsetMs` exactly as they are.
- Do not change `ringcentral.video.top.meeting-info` route semantics: keep `clickWindowRelative`, `Meeting information`, `x: '31'`, `y: '21'`, and `cleanup: escape`.
- Do not add Japanese aliases for this entrypoint in this round unless the main session explicitly scopes that in; current alias coverage should remain `3/27` and `9`.
- Do not localize `control-map-network` or any later `meeting-control-map-demo` step in this cycle.
- Do not alter Q&A, Chinese/English narration, presenter notes, profiles, diagnostics logic, CLI formatting, or acceptance targets.
- Do not read or include private values such as actual Meeting ID, meeting links, dial-in numbers, host names, participant names, account data, or encryption settings.
- Do not use wording that says AiPresenter copies a link, dials a number, shares/invites, sends anything, toggles encryption, changes meeting state, starts recording, or performs a destructive action.
- Do not revert or overwrite concurrent edits from other agents. Current unrelated dirty state observed during this scan: `.coverage`.
