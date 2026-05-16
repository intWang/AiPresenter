# Cycle 098 Technical Scan: Japanese Settings Narration

Scope for the next implementation slice: add Japanese narration only to `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-settings`.

This scan intentionally writes only this handoff file. Do not modify YAML, code, tests, source-index docs, profiles, fixtures, coverage files, or git history during this scan. Parallel work is visible in `.coverage`, `tests/unit/test_cli.py`, `tests/unit/test_diagnostics.py`, and `tests/unit/test_material_packages.py`; preserve those edits and do not revert unrelated files.

## Baseline Confirmed

Command run during scan:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Current package output:

- Overall Japanese demo narration: `48/51`
- `meeting-control-map-demo`: `19/22`
- First missing Japanese step: `control-map-settings`
- Remaining missing control-map steps: `control-map-settings`, `control-map-leave`, `control-map-summary`
- Japanese Q&A remains complete: `12/12` localized questions and `12/12` localized answers
- `questionAliases.ja` remains `3/27` entrypoints and `9` aliases

Parallel-test note: the dirty test files already appear prepared for this slice, with `49/51`, `20/22`, and `control-map-leave` expectations plus a focused `test_meeting_control_map_has_japanese_settings_narration`. Treat those as red-test prep from another agent unless you own the implementation turn; reconcile, but do not overwrite or duplicate them blindly.

## Target Package Change

Current target step:

```yaml
  - id: control-map-settings
    title: Settings
    action:
      entrypointId: ringcentral.video.more.settings
      operation: open
    narration:
      text: Settings is the full configuration center for audio, video, background, translation, join preferences,
        and general meeting behavior.
      localizedText:
        zh: Settings 是完整配置中心。音频、视频、背景、翻译、入会偏好，以及通用会议行为，都可以在这里集中调整。
      placement: during
      actionOffsetMs: 400
```

Add only `localizedText.ja` under this step. Preserve the English text, Chinese text, step order, `entrypointId`, `operation: open`, `placement: during`, and `actionOffsetMs: 400`.

Suggested Japanese text:

```yaml
        ja: Settings は、音声、ビデオ、背景、翻訳、入会設定、一般設定などをまとめて確認できる設定センターです。このコントロールマップでは表示して説明するだけです。ユーザーが明確に求め、表示された項目を確認できるまで、デバイスは切り替えません。音声、ビデオ、背景、入会設定、一般設定は変更しません。翻訳もオンにしません。説明後は Settings ダイアログを閉じます。
```

## Expected Coverage After Implementation

After adding only `localizedText.ja` to `control-map-settings`:

- Overall Japanese demo narration: `48/51` -> `49/51`
- `meeting-control-map-demo`: `19/22` -> `20/22`
- First missing Japanese step: `control-map-settings` -> `control-map-leave`
- Remaining missing control-map steps should be `control-map-leave` and `control-map-summary`
- Japanese Q&A should remain `12/12` questions and `12/12` answers
- `questionAliases.ja` should remain `3/27` entrypoints and `9` aliases
- `--require-complete` for Japanese should still fail because later `meeting-control-map-demo` steps remain untranslated

## Focused Tests

In `tests/unit/test_material_packages.py`, update or keep `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`:

- `report.demo_localized_steps`: `48` -> `49`
- `meeting-control-map-demo.localized_steps`: `19` -> `20`
- first missing step: `control-map-settings` -> `control-map-leave`
- keep total demo steps `51`, control-map total `22`, Q&A counts, alias counts, and `required_localization_complete is False`

Add or keep `test_meeting_control_map_has_japanese_settings_narration` near the existing control-map Japanese narration tests. It should assert:

- `step.action.entrypoint_id == "ringcentral.video.more.settings"`
- `step.action.operation == "open"`
- `step.narration.placement == "during"`
- `step.narration.action_offset_ms == 400`
- `ringcentral.video.more.settings` has no `questionAliases.ja`
- alias coverage remains `3` entrypoints and `9` aliases
- first missing step is now `control-map-leave`
- `control-map-background` has Japanese narration
- `control-map-leave` does not yet have Japanese narration

Update adjacent focused tests that assert the first missing control-map step, especially camera-menu/share/reactions/raise-hand/more/recording/notes/background tests, so they expect `control-map-leave`. In the background test, change the settings-step adjacency assertion from `"ja" not in settings_step.narration.localized_text` to `"ja" in settings_step.narration.localized_text`.

In `tests/unit/test_cli.py`, update both Japanese localization-report tests:

- `Localization report: 48/51 demo steps` -> `Localization report: 49/51 demo steps`
- `- meeting-control-map-demo: 19/22 narration localized` -> `- meeting-control-map-demo: 20/22 narration localized`
- `missing: control-map-settings` -> `missing: control-map-leave`
- keep `test_localization_report_require_complete_fails_for_japanese_demo_gap` exit code `1`
- keep Q&A counts and `missing: explain-leave` negative assertion unchanged

In `tests/unit/test_diagnostics.py`, update `test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`:

- `48/51 demo steps` -> `49/51 demo steps`
- keep status `FAIL`, detail `required ja localization incomplete`, and Q&A detail assertions unchanged

No new executor behavior should be needed. Existing runtime cleanup behavior for `cleanup: settings` closes the Settings dialog if available and presses Escape. Add `tests/unit/test_package_demo.py` coverage only if the route shape changes, which this slice should avoid.

## Route And Action Assertions

The settings route already exists in `packages/ringcentral-video.yaml`:

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

Focused assertions should lock:

- first open step: `action == "clickWindowControl"`, `target == "More"`, `match["occurrence"] == "3"`, `match["controlType"] == "button"`
- second open step: `action == "clickWindowControl"`, `target == "Settings"`, `match["cleanup"] == "settings"`
- presenter notes mention current or last selected section, audio, video, background, translation, join preferences, general settings, and closing the Settings dialog
- the narration does not claim Settings always opens to a specific tab

## Safe Implementation Constraints

Keep this as a narrow localization slice:

- Do not add Japanese `questionAliases` for Settings.
- Do not change operation entrypoints, `openSteps`, presenter notes, cleanup behavior, source routes, code, profiles, runtime logic, or acceptance evidence.
- Do not localize `control-map-leave` or `control-map-summary`.
- Do not add Q&A items or change localized Q&A.
- Do not imply AiPresenter changes audio devices, video settings, background settings, translation, join preferences, General settings, or meeting state.
- Do not say a specific Settings tab is guaranteed to open first; notes say Settings may open to the current or last selected section.
- Keep the narration explain-only, requiring explicit user request and visible-item confirmation before any future configuration change.
- Include dialog cleanup language so the tour returns to the meeting surface before `control-map-leave`.

Suggested text assertions for the Japanese narration:

- contains `Settings`, `設定センター`, `音声`, `ビデオ`, `背景`, `翻訳`, `入会設定`, `一般設定`
- contains `表示して説明`, `明確に求め`, `表示された項目`, `切り替えません`, `変更しません`, `オンにしません`, `閉じます`
- does not contain `デバイスを切り替えます`, `音声を変更します`, `ビデオを変更します`, `翻訳をオンにします`, `入会設定を変更します`, `一般設定を変更します`, `クリックします`, or `自動`

## Source Index

`docs/knowledge/ringcentral-video/source-index.md` currently says Japanese coverage reaches the `.../recording/notes/background` steps of `meeting-control-map-demo`.

If the implementation assignment includes source-index maintenance, update only that localization coverage sentence so it advances from `.../recording/notes/background` to `.../recording/notes/background/settings`. Keep `control-map-leave`, `control-map-summary`, and other entrypoint aliases marked as future work. Do not imply full `meeting-control-map-demo` Japanese coverage until all 22 steps are localized.

## Verification Commands

Focused pytest after implementation:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_background_narration tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_settings_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Expected localization report after implementation:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Expected key lines:

```text
- meeting-control-map-demo: 20/22 narration localized
  missing: control-map-leave, control-map-summary
Localization report: 49/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
questionAliases.ja present on 3/27 entrypoints (9 aliases)
```

Japanese required-complete should still fail:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
```

Expected: exit code `1`, with `Localization coverage incomplete for ja.`

Diff hygiene:

```powershell
git diff -- packages/ringcentral-video.yaml tests/unit/test_material_packages.py tests/unit/test_cli.py tests/unit/test_diagnostics.py docs/knowledge/ringcentral-video/source-index.md
git diff --check -- packages/ringcentral-video.yaml tests/unit/test_material_packages.py tests/unit/test_cli.py tests/unit/test_diagnostics.py docs/knowledge/ringcentral-video/source-index.md
```

Implementation diff should be limited to one `localizedText.ja` block for `control-map-settings`, directly necessary test expectation updates or existing parallel red-test prep, and the source-index coverage sentence if included by the implementation assignment.
