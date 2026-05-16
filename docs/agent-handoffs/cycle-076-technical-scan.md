# Cycle 076 Technical Scan: meeting-controls-tour / explain-background-settings JA narration

Date: 2026-05-16

## Target YAML Snapshot

Target file: `packages/ringcentral-video.yaml`

Target flow and step:

```yaml
  - id: explain-background-settings
    title: Background settings
    action:
      entrypointId: ringcentral.video.more.background
      operation: open
    narration:
      text: Background opens the settings page for visual presentation. You can turn effects off, blur the room,
        choose a built-in background, use a video background, or upload your own.
      localizedText:
        zh: Background 会打开视觉呈现设置，可以关闭效果、模糊房间、选择内置背景、使用视频背景或上传自己的背景。
      placement: during
      actionOffsetMs: 400
```

Current JA gap:

```text
- meeting-controls-tour: 19/22 narration localized
  missing: explain-background-settings, explain-settings, explain-leave
Localization report: 26/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
```

This slice should add only `localizedText.ja` for `meeting-controls-tour` -> `explain-background-settings`.

## Entrypoint Route

The step uses `entrypointId: ringcentral.video.more.background` with `operation: open`.

Current entrypoint:

```yaml
- id: ringcentral.video.more.background
  title: Background
  area: More menu
  purpose: Open the Settings dialog directly on the Background tab.
  openSteps:
  - action: clickWindowControl
    target: More
    match:
      occurrence: '3'
      controlType: button
  - action: clickWindowControl
    target: Background
    match:
      cleanup: settings
  presenterNotes:
  - Observed Settings dialog tabs include Audio, Video, Background, Translation, Join preferences, and General.
  - Background includes Off, Blur, built-in static backgrounds, video backgrounds, upload, and Mirror my video.
  - Close the Settings dialog using its top-right X before continuing.
```

Current route semantics:

- First open step targets `More`, with `action: clickWindowControl`, `occurrence: '3'`, and `controlType: button`.
- Second open step targets `Background`, with `action: clickWindowControl` and `cleanup: settings`.
- The route opens the Settings dialog directly on the Background tab.
- Cleanup expectation is the Settings dialog close path, not side panel cleanup.
- Step narration placement remains `during` with `actionOffsetMs: 400`.

## Test Updates

Recommended red-first edits for the implementation agent:

- `tests/unit/test_material_packages.py`
  - Update `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`:
    - `report.demo_localized_steps`: `26` -> `27`
    - `report.flow_by_id["meeting-controls-tour"].localized_steps`: `19` -> `20`
  - Add `test_meeting_controls_tour_has_japanese_background_settings_narration` near the existing `explain-notes` test.
  - Red state before YAML change: the count assertions fail with current `26/51` and `19/22`; the new focused test fails because `step.narration.localized_text["ja"]` is missing.
- `tests/unit/test_cli.py`
  - In `test_localization_report_outputs_japanese_demo_and_qa_coverage`:
    - `Localization report: 26/51 demo steps` -> `27/51`
    - `- meeting-controls-tour: 19/22 narration localized` -> `20/22`
    - `missing: explain-background-settings` -> `missing: explain-settings`
  - In `test_localization_report_require_complete_fails_for_japanese_demo_gap`, make the same count and first-missing updates.
  - Red state before YAML change: stdout still reports `26/51`, `19/22`, and first missing `explain-background-settings`.
- `tests/unit/test_diagnostics.py`
  - In `test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`:
    - diagnostic detail `26/51 demo steps` -> `27/51 demo steps`
  - Red state before YAML change: diagnostic detail still contains `26/51 demo steps`.

Expected green state after adding only this JA narration:

- Japanese demo narration: `26/51` -> `27/51`
- `meeting-controls-tour.localized_steps`: `19/22` -> `20/22`
- First missing `meeting-controls-tour` step: `explain-background-settings` -> `explain-settings`
- Remaining missing controls-tour steps: `explain-settings`, `explain-leave`
- Japanese Q&A remains `12/12` questions and `12/12` answers.
- Japanese aliases remain `3/27` entrypoints and `9` aliases.
- Japanese `--require-complete` remains intentionally incomplete and should still exit `1`.
- `meeting-control-map-demo` remains `0/22`; do not localize control-map narration in this slice.

Focused material-package assertions should cover:

- `step.action.entrypoint_id == "ringcentral.video.more.background"`
- `step.action.operation == "open"`
- `step.narration.placement == "during"`
- `step.narration.action_offset_ms == 400`
- `package.entrypoint_by_id("ringcentral.video.more.background")` route targets `More`, then `Background`
- first open step match has `occurrence == "3"` and `controlType == "button"`
- second open step match has `cleanup == "settings"`
- Japanese text exists and `has_cjk(ja_text)` is true
- Japanese text includes UI labels/terms such as `Background`, `Settings`, `Off`, `Blur`, `Mirror my video`, and `Upload`
- Japanese text includes safety wording such as `ユーザー`, `明確に求める`, `説明するだけ`, `閉じます`, and wording that keeps the current video/background state unchanged
- Japanese text does not include overreaching execution wording such as `変更します`, `選択します`, `アップロードします`, `クリック`, `押します`, `Background を変更します`, `背景を変更します`, `背景をアップロードします`, or `Upload を押します`

## Suggested Japanese Text

Recommended YAML addition:

```yaml
        ja: Background は Settings ダイアログの Background タブにある表示設定の場所です。ここには Off、Blur、組み込み背景、動画背景、Upload、Mirror my video などの項目があります。ツアーでは場所と選択肢を説明するだけで、ユーザーが明確に求めるまで背景効果の変更、背景の選択、Upload の操作は行いません。説明後は Settings ダイアログを閉じます。
```

Rationale:

- Keeps required UI names in English where the product exposes them: `Background`, `Settings`, `Off`, `Blur`, `Upload`, and `Mirror my video`.
- Mirrors the source meaning: the route opens visual presentation settings and lists available background/effect choices.
- Avoids saying AiPresenter will change the background, upload a background, select a built-in option, or click a button.
- Preserves the existing `open` route and `cleanup: settings` expectation.

## Verification Commands

Focused red/green test command:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_controls_tour_has_japanese_background_settings_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Coverage/report spot-check:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python -c "from pathlib import Path; from ai_presenter.packages.loader import load_material_package; from ai_presenter.packages.localization_status import build_localization_status, render_localization_status_lines; p=load_material_package(Path('packages/ringcentral-video.yaml')); r=build_localization_status(p, language='ja'); print('\n'.join(render_localization_status_lines(r)))"
```

Expected report excerpt after implementation:

```text
- meeting-controls-tour: 20/22 narration localized
  missing: explain-settings, explain-leave
Localization report: 27/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
```

`--require-complete` should still fail for JA because `explain-settings`, `explain-leave`, and `meeting-control-map-demo` remain uncovered.

## Do-not-change Guardrails

- Do not edit code, runtime routing, YAML locators, tests, profiles, or generated artifacts in this technical-scan task.
- During implementation, edit only `localizedText.ja` for `meeting-controls-tour` -> `explain-background-settings`.
- Preserve `entrypointId: ringcentral.video.more.background`, `operation: open`, `placement: during`, and `actionOffsetMs: 400`.
- Preserve the entrypoint route: `More` occurrence `3` button, then `Background`, with `cleanup: settings`.
- Do not add or change `questionAliases.ja`, Q&A items, `meeting-control-map-demo`, diagnostics logic, CLI formatting, or flow order.
- Do not introduce wording that claims to change the current background, select a background, upload a background, click `Upload`, press buttons, or alter the current video/background state without explicit user request.
- Do not localize `explain-settings`, `explain-leave`, or any control-map step in this slice.
