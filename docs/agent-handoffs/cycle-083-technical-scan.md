# Cycle 083 Technical Scan: control-map-report JA

Date: 2026-05-16

## Target YAML Snapshot

Target file: `packages/ringcentral-video.yaml`

Current target step:

```yaml
- id: control-map-report
  title: Report issue
  action:
    entrypointId: ringcentral.video.top.report-issue
    operation: open
  narration:
    text: Report issue is the escalation path when something is wrong with audio, video, sharing, joining,
      notes, or transcript. Because it opens a blocking dialog, I close it before continuing.
    localizedText:
      zh: 如果音频、视频、共享、入会、笔记或转录出问题，可以从这里上报。它会弹出前置窗口，所以讲完我会先把它关闭。
    placement: during
    actionOffsetMs: 400
```

Current gap: `control-map-report` has Chinese localized narration but no `localizedText.ja`.

Action semantics to preserve:

- `entrypointId`: `ringcentral.video.top.report-issue`
- `operation`: `open`
- `placement`: `during`
- `actionOffsetMs`: `400`

Because this step opens a blocking Report issue dialog, the Japanese copy can name the visible issue areas and dialog behavior, but should not imply AiPresenter files a report, picks an issue category, uploads logs, reads private diagnostic content, or promises a support/result outcome.

## Entrypoint Route

Entrypoint: `ringcentral.video.top.report-issue`

```yaml
- id: ringcentral.video.top.report-issue
  title: Report issue
  area: Meeting top bar
  purpose: Open the issue reporting dialog for Audio, Video, Screen sharing, Meeting join, Notes and transcript,
    or Other.
  openSteps:
  - action: clickWindowRelative
    target: Report
    match:
      xFromRight: '168'
      y: '21'
      cleanup: modal
```

Route details:

- Area: `Meeting top bar`
- Route action: `clickWindowRelative`
- Target: `Report`
- Coordinate match: `xFromRight: '168'`, `y: '21'`
- Cleanup: `modal`
- Presenter notes say this opens a foreground dialog that blocks every other meeting control, no issue category should be picked during a feature tour unless the user wants to file a report, and the dialog should be closed with its X because Escape did not reliably clear it during testing.

Do not change the entrypoint route, open steps, cleanup, purpose, or presenter notes in this round.

## Test Updates

Recommended red-first updates:

- `tests/unit/test_material_packages.py`
  - In `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`, update overall JA demo coverage from `33` to `34`.
  - Update `meeting-control-map-demo` localized steps from `4` to `5`.
  - Update first missing step from `control-map-report` to `control-map-add-coworkers`.
  - Add a focused guard test for `meeting-control-map-demo` -> `control-map-report`, parallel to the existing `control-map-network` and `control-map-views` JA tests.
  - The focused test should assert:
    - `step.action.entrypoint_id == "ringcentral.video.top.report-issue"`
    - `step.action.operation == "open"`
    - `step.narration.placement == "during"`
    - `step.narration.action_offset_ms == 400`
    - entrypoint route uses `clickWindowRelative`, target `Report`, `xFromRight == "168"`, `y == "21"`, and `cleanup == "modal"`
    - JA text exists, contains CJK, and includes required UI/concept terms such as `Report issue`, `Report`, `Audio`, `Video`, `Screen sharing`, `Meeting join`, `Notes`, `Transcript`, `Other`, `会議コントロール`, and `ダイアログ`
    - JA text frames this as a dialog location/role explanation, not as report submission or troubleshooting completion
    - JA text excludes overreach wording such as `送信`, `提出`, `報告します`, `カテゴリを選択`, `選択します`, `アップロード`, `ログ`, `サポート`, `解決します`, `修復します`, `改善します`, `保証します`, and `必ず`

- `tests/unit/test_cli.py`
  - In `test_localization_report_outputs_japanese_demo_and_qa_coverage`, update:
    - `Localization report: 33/51 demo steps` -> `Localization report: 34/51 demo steps`
    - `- meeting-control-map-demo: 4/22 narration localized` -> `- meeting-control-map-demo: 5/22 narration localized`
    - `missing: control-map-report` -> `missing: control-map-add-coworkers`
  - In `test_localization_report_require_complete_fails_for_japanese_demo_gap`, make the same updates.
  - Keep `missing: explain-leave` absent.
  - Keep Q&A coverage unchanged at `12/12` questions and `12/12` answers.
  - Keep JA aliases unchanged at `questionAliases.ja present on 3/27 entrypoints (9 aliases)`.

- `tests/unit/test_diagnostics.py`
  - In `test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`, update `33/51 demo steps` -> `34/51 demo steps`.
  - Keep status `FAIL`.
  - Keep detail `required ja localization incomplete`.
  - Keep Q&A detail unchanged: `12/12 Q&A questions` and `12/12 Q&A answers`.

Expected red point before YAML implementation:

- Updated localization count assertions fail because current state is still `33/51`.
- Updated `meeting-control-map-demo` assertion fails because current state is still `4/22`.
- Updated first missing assertion fails because current first missing is still `control-map-report`.
- New focused JA narration test fails because `step.narration.localized_text["ja"]` is missing for `control-map-report`.

Expected green state after this slice:

- Overall JA demo narration: `34/51`
- `meeting-control-map-demo`: `5/22`
- First missing JA step in that flow: `control-map-add-coworkers`
- Required JA localization: still incomplete/failing
- Q&A JA coverage: still `12/12` questions and `12/12` answers
- JA aliases: still `3/27` entrypoints and `9` aliases

## Suggested Japanese Text

Recommended `localizedText.ja`:

```yaml
        ja: Report issue は、Audio、Video、Screen sharing、Meeting join、Notes、Transcript、Other の問題を確認する Report ダイアログへの入口です。このダイアログは会議コントロールの前面に出るため、ここでは場所と役割だけを説明し、続行前に閉じます。原因は断定しません。
```

Why this wording:

- Keeps necessary UI/concept names: `Report issue`, `Report`, `Audio`, `Video`, `Screen sharing`, `Meeting join`, `Notes`, `Transcript`, `Other`, `会議コントロール`, `ダイアログ`.
- Matches the source intent: this is an escalation/troubleshooting route for audio, video, sharing, joining, notes, or transcript issues.
- Reflects the route behavior: the dialog is blocking/foreground and must be closed before continuing.
- Avoids saying AiPresenter submits a report, chooses a category, uploads logs, reads diagnostics, guarantees repair, or promises support follow-up.

Acceptable shorter variant:

```yaml
        ja: Report issue は、Audio、Video、Screen sharing、Meeting join、Notes、Transcript、Other の問題を確認する Report ダイアログです。会議コントロールを覆う前面ダイアログなので、説明後は閉じます。原因は決めつけません。
```

Avoid wording such as:

- `報告を送信します`
- `問題を報告します`
- `カテゴリを選択します`
- `ログをアップロードします`
- `サポートに送ります`
- `原因を特定します`
- `問題を解決します`
- `必ず改善します`

## Verification Commands

Use the project virtual environment and keep `PYTHONPATH=src` if the package is not installed editable in the active shell:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests/unit/test_material_packages.py::test_meeting_control_map_has_japanese_report_narration tests/unit/test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests/unit/test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests/unit/test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Optional focused CLI check:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m ai_presenter.cli localization-report --package ringcentral-video --language ja
```

Expected CLI lines after implementation:

```text
Localization report: 34/51 demo steps
- meeting-control-map-demo: 5/22 narration localized
  missing: control-map-add-coworkers
- localized questions: 12/12
- localized answers: 12/12
questionAliases.ja present on 3/27 entrypoints (9 aliases)
```

Japanese `--require-complete` should still exit nonzero and print `Localization coverage incomplete for ja.`

## Do-not-change Guardrails

- Do not change code, runtime behavior, selectors, locators, route coordinates, YAML flow order, operation names, or test infrastructure for this scan.
- Do not change `control-map-report` action semantics: keep `entrypointId`, `operation`, `placement`, and `actionOffsetMs` exactly as they are.
- Do not change `ringcentral.video.top.report-issue` route semantics: keep `clickWindowRelative`, `Report`, `xFromRight: '168'`, `y: '21'`, and `cleanup: modal`.
- Do not change the presenter note behavior that categories should not be picked during a feature tour unless the user wants to file a report, and that the dialog should be closed with X rather than relying on Escape.
- Do not add Japanese aliases for this entrypoint in this round unless the main session explicitly scopes that in; current alias coverage should remain `3/27` and `9` aliases.
- Do not localize `control-map-add-coworkers` or any later `meeting-control-map-demo` step in this cycle.
- Do not alter Q&A, Chinese/English narration, presenter notes, profiles, diagnostics logic, CLI formatting, or acceptance targets beyond the expected JA coverage count/test expectation changes.
- Do not use wording that says AiPresenter submits a report, selects an issue category, uploads logs, reads private diagnostics, promises support follow-up, fixes audio/video/sharing/joining/notes/transcript problems, or guarantees an outcome.
- Do not mention or read private meeting values, Meeting IDs, meeting links, account data, participant identifiers, media device names, logs, diagnostics payloads, transcript content, notes content, or sharing content.
- Do not revert or overwrite concurrent edits from other agents. This handoff intentionally writes only `docs/agent-handoffs/cycle-083-technical-scan.md`.
