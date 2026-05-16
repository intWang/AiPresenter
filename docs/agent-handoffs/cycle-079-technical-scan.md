# Cycle 079 Technical Scan: control-map-overview JA

Date: 2026-05-16

## Target YAML Snapshot

Target file: `packages/ringcentral-video.yaml`

Target flow and step:

```yaml
- id: meeting-control-map-demo
  title: Meeting Control Map
  steps:
  - id: control-map-overview
    title: Orient the meeting surface
    action:
      entrypointId: ringcentral.video.overview
      operation: explain
    narration:
      text: Think of this meeting window as a control map. The top tells you status and health, the center is the live meeting canvas, and the bottom is where you manage people, media, sharing, reactions, and exit.
      localizedText:
        zh: 先把会议窗口看成一张控制地图。上方看状态和网络，中间是会议画面，下方负责成员、音视频、共享、互动和离开。
      placement: before
```

Current gap: this step has `zh` localized narration but no `localizedText.ja`.

## Entrypoint/Action Semantics

- Entrypoint: `ringcentral.video.overview`
- Operation: `explain`
- Narration placement: `before`
- `actionOffsetMs`: absent
- Step type: explain-only orientation step.

This is not an `open`, `toggle`, `select`, or other executable UI-changing step. It should be treated as a conceptual map overview of the RingCentral Video meeting surface. The implementation should preserve the existing action block exactly and add only Japanese narration under `narration.localizedText`.

Because the step is explain-only, the Japanese copy should not say that AiPresenter clicks, opens, enables, selects, toggles, sends, starts, records, shares, invites, raises hand, leaves, or changes meeting state. It should orient the user to regions and categories only.

## Test Updates

Recommended red-first test edits:

- `tests/unit/test_material_packages.py`
  - In `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`, update `report.demo_localized_steps` from `29` to `30`.
  - Add or extend assertions for `report.flow_by_id["meeting-control-map-demo"]`: expected `localized_steps == 1`, `total_steps == 22`, and first missing should now be `control-map-meeting-info` if the report object exposes missing step IDs.
  - Add a focused Japanese narration guard for `meeting-control-map-demo` -> `control-map-overview`: assert `ja` exists, has CJK, keeps `entrypointId == "ringcentral.video.overview"`, `operation == "explain"`, `placement == "before"`, no `action_offset_ms`, includes key concepts such as `コントロールマップ`, `上部`, `状態`, `ネットワーク` or `健全性`, `中央`, `ライブ会議キャンバス` or `会議画面`, `下部`, `参加者` or `メンバー`, `メディア`, `共有`, `リアクション`, `退出`, and excludes over-action wording such as `クリック`, `押します`, `開きます`, `切り替えます`, `変更します`, `開始します`, `送信します`, `録画します`, `退出します`.

- `tests/unit/test_cli.py`
  - In `test_localization_report_outputs_japanese_demo_and_qa_coverage`, update:
    - `Localization report: 29/51 demo steps` -> `Localization report: 30/51 demo steps`
    - `- meeting-control-map-demo: 0/22 narration localized` -> `- meeting-control-map-demo: 1/22 narration localized`
    - `missing: control-map-overview` -> `missing: control-map-meeting-info`
  - In `test_localization_report_require_complete_fails_for_japanese_demo_gap`, make the same updates.
  - Keep `missing: explain-leave` absent, Q&A `12/12`, and `questionAliases.ja present on 3/27 entrypoints (9 aliases)` unchanged.

- `tests/unit/test_diagnostics.py`
  - In `test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`, update `29/51 demo steps` -> `30/51 demo steps`.
  - Keep status `FAIL` and detail `required ja localization incomplete`; Japanese required localization must still fail because only 1 of 22 `meeting-control-map-demo` steps will be localized.
  - Keep Q&A detail unchanged: `12/12 Q&A questions` and `12/12 Q&A answers`.

Expected red point before YAML implementation: the updated tests should fail because current Japanese coverage is still `29/51`, `meeting-control-map-demo` is still `0/22`, and the first missing step is still `control-map-overview`.

Expected green state after this slice:

- Overall JA demo narration: `30/51`
- `meeting-control-map-demo`: `1/22`
- First missing JA step in that flow: `control-map-meeting-info`
- Required JA localization: still incomplete/failing
- Q&A JA coverage: still `12/12` questions and `12/12` answers
- JA aliases: still `3/27` entrypoints and `9` aliases

## Suggested Japanese Text

Recommended `localizedText.ja`:

```yaml
        ja: この会議ウィンドウを、まずコントロールマップとして捉えます。上部では会議の状態やネットワークなどの健全性を確認し、中央はライブ会議キャンバス、下部は参加者、メディア、共有、リアクション、退出に関するコントロールの領域です。
```

Why this wording:

- Keeps the key concept `コントロールマップ`.
- Preserves the source structure: top status/health, center live meeting canvas, bottom people/media/sharing/reactions/exit.
- Includes necessary UI/concept vocabulary: `会議ウィンドウ`, `上部`, `状態`, `ネットワーク`, `健全性`, `中央`, `ライブ会議キャンバス`, `下部`, `参加者`, `メディア`, `共有`, `リアクション`, `退出`, `コントロール`.
- Avoids unauthorized action language. It does not say to click, open, start, send, select, toggle, share, record, invite, raise hand, leave, or change any setting.

Alternative if the team prefers a more literal phrase for the center:

```yaml
        ja: この会議ウィンドウを、まずコントロールマップとして捉えます。上部では会議の状態やネットワークなどの健全性を確認し、中央はライブの会議画面、下部は参加者、メディア、共有、リアクション、退出に関するコントロールの領域です。
```

## Verification Commands

Use the project virtual environment and keep `PYTHONPATH=src` if the package is not installed editable in the active shell:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests/unit/test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests/unit/test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests/unit/test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Optional focused CLI check:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m ai_presenter.cli localization-report --package ringcentral-video --language ja
```

Expected CLI lines after implementation:

```text
Localization report: 30/51 demo steps
- meeting-control-map-demo: 1/22 narration localized
  missing: control-map-meeting-info
- localized questions: 12/12
- localized answers: 12/12
questionAliases.ja present on 3/27 entrypoints (9 aliases)
```

Japanese `--require-complete` should still exit nonzero and print `Localization coverage incomplete for ja.`

## Do-not-change Guardrails

- Do not change code, runtime behavior, selectors, locators, commands, YAML structure, flow order, action operations, or test infrastructure for this slice.
- Do not alter `entrypointId`, `operation`, `placement`, or add `actionOffsetMs` for `control-map-overview`.
- Do not localize `control-map-meeting-info` or any later `meeting-control-map-demo` step in this cycle.
- Do not change Q&A, aliases, presenter notes, manual controls, profiles, diagnostics logic, CLI formatting, or Chinese/English narration.
- Do not copy or overwrite concurrent edits from other agents. Current unrelated dirty state observed during this scan: `.coverage`.
- Do not use Japanese wording that implies clicking/opening panels or changing meeting state from the overview step.
- Do not mention private values such as Meeting ID, invite links, dial-in data, participant names, chat content, transcripts, device labels, or account/settings values in this overview narration.
