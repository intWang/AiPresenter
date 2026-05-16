# Cycle 078 Technical Scan: meeting-controls-tour / explain-leave JA narration

Date: 2026-05-16

## Target YAML Snapshot

Target file: `packages/ringcentral-video.yaml`

Target flow and step:

```yaml
  - id: explain-leave
    title: Leave meeting
    action:
      entrypointId: ringcentral.video.toolbar.leave
      operation: explain
    narration:
      text: Leave exits the meeting. It is a destructive control, so the presenter explains it but does not click
        it without explicit confirmation.
      localizedText:
        zh: Leave 会离开会议，是破坏性控制；Presenter 只说明它的作用，不会在没有明确确认时点击。
      placement: before
```

Current JA gap after cycle 077:

```text
- meeting-controls-tour: 21/22 narration localized
  missing: explain-leave
Localization report: 28/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
```

This slice should add only `localizedText.ja` for `meeting-controls-tour` -> `explain-leave`.

## Entrypoint Route

The step uses `entrypointId: ringcentral.video.toolbar.leave` with `operation: explain`.

Current entrypoint:

```yaml
- id: ringcentral.video.toolbar.leave
  title: Leave meeting
  area: Meeting toolbar
  purpose: Leave or end the meeting.
  questionAliases:
    zh:
    - 离开会议
    - 退出会议
    - 结束会议
  openSteps: []
  presenterNotes:
  - Treat this as destructive during a tour.
  - In this test build, clicking Leave can immediately show the left-meeting state, so AiPresenter should explain
    this control without clicking it unless the user explicitly asks to end the meeting.
  - Use a verbal confirmation before performing any leave or end action.
```

Current route semantics:

- There are no locator/openSteps for this entrypoint: `openSteps: []`.
- There is no `target`, `match`, or `cleanup` setting because the route must not open or activate the control during the tour.
- The demo step operation is `explain`, not `open`.
- Narration placement remains `before`.
- The English source describes Leave as a destructive meeting-exit control and says the presenter explains it without clicking unless there is explicit confirmation.

## Test Updates

Recommended red-first edits for the implementation agent:

- `tests/unit/test_material_packages.py`
  - Update `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`:
    - `report.demo_localized_steps`: `28` -> `29`
    - `report.flow_by_id["meeting-controls-tour"].localized_steps`: `21` -> `22`
  - Add `test_meeting_controls_tour_has_japanese_leave_narration` after `test_meeting_controls_tour_has_japanese_settings_narration`.
  - Focused assertions should cover:
    - `step.action.entrypoint_id == "ringcentral.video.toolbar.leave"`
    - `step.action.operation == "explain"`
    - `step.narration.placement == "before"`
    - `package.entrypoint_by_id("ringcentral.video.toolbar.leave").open_steps == []`
    - Japanese text exists and `has_cjk(ja_text)` is true
    - Japanese text includes `Leave`, `会議`, `退出`, `破壊的`, `コントロール`, `説明するだけ`, `ユーザー`, `明確`, `確認`
    - Japanese text does not include overreaching execution wording such as `クリック`, `押します`, `選択します`, `退出します`, `終了します`, `会議を終了`, `Leave を押します`
  - Red state before YAML change: the count assertions fail with current `28/51` and `21/22`; the new focused test fails because `step.narration.localized_text["ja"]` is missing for `explain-leave`.

- `tests/unit/test_cli.py`
  - In `test_localization_report_outputs_japanese_demo_and_qa_coverage`:
    - `Localization report: 28/51 demo steps` -> `29/51`
    - `- meeting-controls-tour: 21/22 narration localized` -> `22/22`
    - remove the `missing: explain-leave` expectation
    - keep the `meeting-control-map-demo: 0/22` missing list expectation if a first remaining missing assertion is desired; the first remaining step should be `control-map-overview`
  - In `test_localization_report_require_complete_fails_for_japanese_demo_gap`, make the same count and missing-text updates.
  - Red state before YAML change: stdout still reports `28/51`, `21/22`, and `missing: explain-leave`.

- `tests/unit/test_diagnostics.py`
  - In `test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`:
    - diagnostic detail `28/51 demo steps` -> `29/51 demo steps`
    - keep status `FAIL`, because `meeting-control-map-demo` remains untranslated
  - Red state before YAML change: diagnostic detail still contains `28/51 demo steps`.

Expected green state after adding only this JA narration:

- Japanese demo narration: `28/51` -> `29/51`
- `meeting-controls-tour.localized_steps`: `21/22` -> `22/22`
- `meeting-controls-tour` has no missing narration steps.
- First remaining overall JA demo missing step moves to `meeting-control-map-demo` -> `control-map-overview`.
- Japanese Q&A remains `12/12` questions and `12/12` answers.
- Japanese aliases remain `3/27` entrypoints and `9` aliases.
- Japanese `--require-complete` remains intentionally incomplete and should still exit `1`.
- `meeting-control-map-demo` remains `0/22`; do not localize control-map narration in this slice.

## Suggested Japanese Text

Recommended YAML addition:

```yaml
        ja: Leave は現在の会議から退出するための破壊的なコントロールです。ツアーではこの場所と役割を説明するだけで、ユーザーが明確に確認するまで Leave を実行しません。
```

Rationale:

- Keeps the required product UI name in English: `Leave`.
- Uses Japanese safety language around a destructive control while avoiding instruction-like wording.
- Avoids `クリック`, `押します`, `選択します`, `退出します`, `終了します`, and `会議を終了` so the narration does not sound like AiPresenter is taking the action.
- Mirrors the source behavior: explain the control, require explicit confirmation before any leave/end action.

## Verification Commands

Focused red/green test command:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_controls_tour_has_japanese_leave_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Current report spot-check used for this scan:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Current excerpt:

```text
- meeting-controls-tour: 21/22 narration localized
  missing: explain-leave
Localization report: 28/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
```

Expected report excerpt after implementation:

```text
- meeting-controls-tour: 22/22 narration localized
- meeting-control-map-demo: 0/22 narration localized
  missing: control-map-overview, control-map-meeting-info, ...
Localization report: 29/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
```

`--require-complete` should still fail for JA because `meeting-control-map-demo` remains uncovered. During this scan, the command below failed as expected for localization and also reported the current profile voice limitation for Japanese:

```powershell
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --language ja --require-localization
```

Relevant localization line:

```text
[FAIL] localization: required ja localization incomplete: 28/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers
```

## Do-not-change Guardrails

- Do not edit code, runtime routing, YAML locators, profiles, generated artifacts, or unrelated tests in this technical-scan task.
- During implementation, edit only `localizedText.ja` for `meeting-controls-tour` -> `explain-leave`, plus the focused tests listed above.
- Preserve `entrypointId: ringcentral.video.toolbar.leave`, `operation: explain`, and `placement: before`.
- Preserve `openSteps: []`; do not add a locator, `target`, `match`, or `cleanup`.
- Do not add or change `questionAliases.ja`, Q&A items, `meeting-control-map-demo`, diagnostics logic, CLI formatting, or flow order.
- Do not add wording that says AiPresenter will click, press, choose, leave the meeting, end the meeting, or perform the destructive control.
- Do not localize `meeting-control-map-demo` or any other remaining JA gap in this slice.
