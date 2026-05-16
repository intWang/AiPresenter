# Cycle 077 Technical Scan: meeting-controls-tour / explain-settings JA narration

Date: 2026-05-16

## Target YAML Snapshot

Target file: `packages/ringcentral-video.yaml`

Target flow and step:

```yaml
  - id: explain-settings
    title: Settings
    action:
      entrypointId: ringcentral.video.more.settings
      operation: open
    narration:
      text: 'Settings is the complete configuration area: audio, video, background, translation, join preferences,
        and general meeting preferences.'
      localizedText:
        zh: Settings 是完整配置区域，包含音频、视频、背景、翻译、入会偏好和通用会议偏好。
      placement: during
      actionOffsetMs: 400
```

Current JA gap:

```text
- meeting-controls-tour: 20/22 narration localized
  missing: explain-settings, explain-leave
Localization report: 27/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
```

This slice should add only `localizedText.ja` for `meeting-controls-tour` -> `explain-settings`.

## Entrypoint Route

The step uses `entrypointId: ringcentral.video.more.settings` with `operation: open`.

Current entrypoint:

```yaml
- id: ringcentral.video.more.settings
  title: Settings
  area: More menu
  purpose: Open the Settings dialog.
  openSteps:
  - action: clickWindowControl
    target: More
    match:
      occurrence: '3'
      controlType: button
  - action: clickWindowControl
    target: Settings
    match:
      cleanup: settings
  presenterNotes:
  - Observed Settings dialog opens to the current or last selected section.
  - Use this as the general route for audio, video, background, translation, join preferences, and general settings.
  - Close the Settings dialog using its top-right X before continuing.
```

Current route semantics:

- First open step targets `More`, with `action: clickWindowControl`, `occurrence: '3'`, and `controlType: button`.
- Second open step targets `Settings`, with `action: clickWindowControl` and `cleanup: settings`.
- The route opens the Settings dialog, but the dialog may open to the current or last selected section.
- Cleanup expectation is the Settings dialog close path.
- Step narration placement remains `during` with `actionOffsetMs: 400`.

## Test Updates

Recommended red-first edits for the implementation agent:

- `tests/unit/test_material_packages.py`
  - Update `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`:
    - `report.demo_localized_steps`: `27` -> `28`
    - `report.flow_by_id["meeting-controls-tour"].localized_steps`: `20` -> `21`
  - Add `test_meeting_controls_tour_has_japanese_settings_narration` near the existing background settings test.
  - Red state before YAML change: the count assertions fail with current `27/51` and `20/22`; the new focused test fails because `step.narration.localized_text["ja"]` is missing for `explain-settings`.
- `tests/unit/test_cli.py`
  - In `test_localization_report_outputs_japanese_demo_and_qa_coverage`:
    - `Localization report: 27/51 demo steps` -> `28/51`
    - `- meeting-controls-tour: 20/22 narration localized` -> `21/22`
    - `missing: explain-settings` -> `missing: explain-leave`
  - In `test_localization_report_require_complete_fails_for_japanese_demo_gap`, make the same count and first-missing updates.
  - Red state before YAML change: stdout still reports `27/51`, `20/22`, and first missing `explain-settings`.
- `tests/unit/test_diagnostics.py`
  - In `test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`:
    - diagnostic detail `27/51 demo steps` -> `28/51 demo steps`
  - Red state before YAML change: diagnostic detail still contains `27/51 demo steps`.

Expected green state after adding only this JA narration:

- Japanese demo narration: `27/51` -> `28/51`
- `meeting-controls-tour.localized_steps`: `20/22` -> `21/22`
- First missing `meeting-controls-tour` step: `explain-settings` -> `explain-leave`
- Remaining missing controls-tour step: `explain-leave`
- Japanese Q&A remains `12/12` questions and `12/12` answers.
- Japanese aliases remain `3/27` entrypoints and `9` aliases.
- Japanese `--require-complete` remains intentionally incomplete and should still exit `1`.
- `meeting-control-map-demo` remains `0/22`; do not localize control-map narration in this slice.

Focused material-package assertions should cover:

- `step.action.entrypoint_id == "ringcentral.video.more.settings"`
- `step.action.operation == "open"`
- `step.narration.placement == "during"`
- `step.narration.action_offset_ms == 400`
- `package.entrypoint_by_id("ringcentral.video.more.settings")` route targets `More`, then `Settings`
- first open step match has `occurrence == "3"` and `controlType == "button"`
- second open step match has `cleanup == "settings"`
- Japanese text exists and `has_cjk(ja_text)` is true
- Japanese text includes UI labels/terms such as `Settings`, `Audio`, `Video`, `Background`, `Translation`, `Join preferences`, and `General`
- Japanese text includes safety wording such as `場所`, `一覧`, `説明するだけ`, `ユーザー`, `明確に求める`, `変更しません`, and `閉じます`
- Japanese text does not include overreaching execution wording such as `音声を変更します`, `ビデオを変更します`, `背景を変更します`, `翻訳を有効にします`, `入会設定を変更します`, `General を変更します`, `選択します`, `切り替えます`, `適用します`, `クリック`, or `押します`

## Suggested Japanese Text

Recommended YAML addition:

```yaml
        ja: Settings は Audio、Video、Background、Translation、Join preferences、General などの会議設定セクションをまとめて確認できるダイアログです。ツアーでは各セクションの場所と役割を説明するだけで、ユーザーが明確に求めるまで音声、ビデオ、背景、翻訳、入会設定、General の設定は変更しません。説明後は Settings ダイアログを閉じます。
```

Rationale:

- Keeps required UI names in English where the product exposes them: `Settings`, `Audio`, `Video`, `Background`, `Translation`, `Join preferences`, and `General`.
- Mirrors the source meaning: Settings is the complete configuration area.
- Avoids saying AiPresenter will change audio, video, background, translation, join preferences, or general meeting preferences.
- Avoids claiming a specific tab because the entrypoint notes say Settings may open to the current or last selected section.
- Preserves the existing `open` route and `cleanup: settings` expectation.

## Verification Commands

Focused red/green test command:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_controls_tour_has_japanese_settings_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Coverage/report spot-check:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python -c "from pathlib import Path; from ai_presenter.packages.loader import load_material_package; from ai_presenter.packages.localization_status import build_localization_status, render_localization_status_lines; p=load_material_package(Path('packages/ringcentral-video.yaml')); r=build_localization_status(p, language='ja'); print('\n'.join(render_localization_status_lines(r)))"
```

Expected report excerpt after implementation:

```text
- meeting-controls-tour: 21/22 narration localized
  missing: explain-leave
Localization report: 28/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
```

`--require-complete` should still fail for JA because `explain-leave` and `meeting-control-map-demo` remain uncovered.

## Do-not-change Guardrails

- Do not edit code, runtime routing, YAML locators, tests, profiles, or generated artifacts in this technical-scan task.
- During implementation, edit only `localizedText.ja` for `meeting-controls-tour` -> `explain-settings`.
- Preserve `entrypointId: ringcentral.video.more.settings`, `operation: open`, `placement: during`, and `actionOffsetMs: 400`.
- Preserve the entrypoint route: `More` occurrence `3` button, then `Settings`, with `cleanup: settings`.
- Do not add or change `questionAliases.ja`, Q&A items, `meeting-control-map-demo`, diagnostics logic, CLI formatting, or flow order.
- Do not introduce wording that claims to modify audio, video, background, translation, join preferences, General, or any current meeting state.
- Do not claim Settings always opens to a specific tab; the entrypoint notes say it opens to the current or last selected section.
- Do not localize `explain-leave` or any control-map step in this slice.
