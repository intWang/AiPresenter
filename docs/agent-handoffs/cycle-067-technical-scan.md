# Cycle 067 Technical Scan: meeting-controls-tour / explain-audio-menu JA narration

## Scope

Scan only for the next implementation pass. The proposed implementation should add Japanese `localizedText.ja` narration to one step:

- Package: `packages/ringcentral-video.yaml`
- Flow: `meeting-controls-tour`
- Step: `explain-audio-menu`
- Entrypoint: `ringcentral.video.toolbar.audio-menu`
- Operation: `open`

Do not change runtime behavior, open steps, action offsets, aliases, Q&A, flow order, diagnostics logic, CLI logic, tests, YAML outside this one narration entry, git state, or unrelated docs as part of this scan.

## Local Context Read

- `packages/ringcentral-video.yaml`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_diagnostics.py`
- Recent handoffs:
  - `docs/agent-handoffs/cycle-066-technical-scan.md`
  - `docs/agent-handoffs/cycle-066-risk-scan.md`
  - `docs/agent-handoffs/cycle-066-implementation.md`
  - `docs/agent-handoffs/cycle-066-summary.md`
  - `docs/agent-handoffs/cycle-065-summary.md`

Current verified baseline from:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

- `Localization report: 17/51 demo steps`
- `meeting-controls-tour: 10/22 narration localized`
- first missing `meeting-controls-tour` step: `explain-audio-menu`
- Q&A remains complete: `12/12` localized questions and `12/12` localized answers
- Japanese aliases remain partial: `questionAliases.ja present on 3/27 entrypoints (9 aliases)`

Important current-tree note: the focused Cycle 067 tests already appear advanced to the expected post-implementation state. The package YAML has not yet been advanced for `explain-audio-menu`, so the implementation owner should expect the focused tests and current `localization-report` assertions to fail until the YAML gets the Japanese narration.

## Source Step

Current English narration:

```yaml
text: The microphone arrow opens audio devices. You can switch microphone and speaker, leave computer audio,
  use phone audio, or go to more audio settings.
```

Current Chinese narration:

```yaml
zh: 麦克风箭头会打开音频设备菜单，可以切换麦克风和扬声器、离开电脑音频、使用电话音频，或进入更多音频设置。
```

Relevant entrypoint details for `ringcentral.video.toolbar.audio-menu`:

- Title: `Microphone and speaker menu`
- Area: `Meeting toolbar`
- Purpose: `Open microphone and speaker device controls, audio level indicators, leave-computer-audio, phone-audio, and more audio settings.`
- Open step clicks `More` with `occurrence: '1'`, `controlType: button`, and `cleanup: escape`.
- Presenter notes say observed menu sections include `Microphone`, `Speaker`, `Leave computer audio`, `Use phone audio`, and `More audio settings`.
- Presenter notes frame this as the recovery path for the wrong microphone or speaker.
- Presenter notes warn that a system-default-audio-devices toast close coordinate can overlap Add coworkers on the clean main screen.

Relevant prior slice:

- Cycle 066 localized `explain-microphone` as the point-only Mute/privacy step.
- Cycle 066 intentionally left device choice, speaker choice, audio level indicators, leave computer audio, phone audio, and more audio settings for this `explain-audio-menu` slice.

## Recommended Japanese Wording

Recommended insertion under `narration.localizedText`:

```yaml
        ja: マイクの矢印を開くと、音声デバイスのメニューが表示されます。ここでマイクとスピーカーの選択、コンピューター音声からの退出、電話音声の利用、その他の音声設定に進めます。ユーザーの明確な指示なしにデバイスや音声接続は切り替えず、説明したらメニューを閉じます。
```

Rationale:

- Preserves the English meaning and current Chinese scope: microphone arrow, audio device menu, microphone/speaker switching, leave computer audio, use phone audio, and more audio settings.
- Names `マイク`, `スピーカー`, `デバイス`, `コンピューター音声`, `電話音声`, and `音声設定`, matching the existing focused assertions.
- Adds the safety boundary expected for a live meeting menu: opening/explaining is okay, but do not switch devices or audio connection without clear user instruction.
- Ends with menu cleanup language because the entrypoint has `cleanup: escape`.
- Keeps the main `Mute` privacy/toggle behavior out of this step; that belongs to `explain-microphone`.

## Expected Count Changes

After adding only this `localizedText.ja` entry:

- Overall Japanese demo narration: `17/51` -> `18/51`
- `meeting-controls-tour`: `10/22` -> `11/22`
- First missing `meeting-controls-tour` step should advance from `explain-audio-menu` to `explain-camera`
- Q&A counts should remain `12/12` questions and `12/12` answers
- Japanese alias counts should remain `questionAliases.ja present on 3/27 entrypoints (9 aliases)`
- `--require-complete` for Japanese should still fail because the package remains partially localized.

## Tests To Update/Add

The current test files already contain the expected Cycle 067 assertions. If the implementation owner is working from this tree, no test edits should be needed; the YAML narration should turn the existing advanced tests green.

Existing expected test coverage to preserve:

- `tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`
  - expects `report.demo_localized_steps == 18`
  - expects `report.flow_by_id["meeting-controls-tour"].localized_steps == 11`
  - keeps `report.demo_total_steps == 51`
  - keeps `meeting-controls-tour` total at `22`
  - keeps Q&A and alias expectations unchanged

- `tests/unit/test_material_packages.py::test_meeting_controls_tour_has_japanese_audio_menu_narration`
  - asserts `step.action.operation == "open"`
  - asserts Japanese text exists and contains CJK
  - asserts `マイク`
  - asserts `スピーカー`
  - asserts `デバイス`
  - asserts `コンピューター音声`
  - asserts `電話音声`
  - asserts `音声設定`
  - asserts `切り替えません`
  - asserts `閉じます`

- `tests/unit/test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage`
  - expects `Localization report: 18/51 demo steps`
  - expects `- meeting-controls-tour: 11/22 narration localized`
  - expects `missing: explain-camera`
  - keeps Q&A and alias lines unchanged

- `tests/unit/test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap`
  - expects exit code `1`
  - expects `Localization report: 18/51 demo steps`
  - expects `- meeting-controls-tour: 11/22 narration localized`
  - expects `missing: explain-camera`
  - keeps `Localization coverage incomplete for ja.`

- `tests/unit/test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`
  - expects diagnostic detail to include `18/51 demo steps`
  - keeps `required ja localization incomplete`
  - keeps `12/12 Q&A questions` and `12/12 Q&A answers`

If applying this scan to a branch that does not already have the audio-menu-focused test, add it with the assertions listed above. Do not add Japanese `questionAliases` in this pass; this is narration-only and expected alias counts assume no alias change.

## Expected CLI Output Changes

For:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Expected relevant output after implementation:

```text
Language: ja
- meeting-controls-tour: 11/22 narration localized
  missing: explain-camera, explain-camera-menu, explain-share, explain-reactions, explain-raise-hand, explain-more, explain-recording, explain-notes, explain-background-settings, explain-settings, explain-leave
- localized questions: 12/12
- localized answers: 12/12
questionAliases.ja present on 3/27 entrypoints (9 aliases)
Localization report: 18/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
```

For:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
```

Expected result after implementation:

- Exit code: `1`
- Includes `Localization report: 18/51 demo steps`
- Includes `- meeting-controls-tour: 11/22 narration localized`
- Includes `missing: explain-camera`
- Includes `Localization coverage incomplete for ja.`

## Verification Commands

Run targeted tests with the project venv:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_controls_tour_has_japanese_audio_menu_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Expected pre-implementation result in this current tree:

- failures for the advanced `18/51`, `11/22`, `missing: explain-camera`, and missing `localized_text["ja"]` expectations for `explain-audio-menu`

Optional broader package-localization sweep:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py -k "japanese or localization_status or audio_menu"
```

CLI smoke checks:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
```

Optional doctor localization preflight:

```powershell
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --language ja --require-localization
```

Expected doctor result remains nonzero because Japanese localization is still incomplete, but the localization detail should move to `18/51 demo steps`.

## Notes For Implementer

- Keep the YAML insertion under `localizedText.ja`, not `localizedText.jp`.
- Preserve existing English text, Chinese `localizedText.zh`, `placement: during`, and `actionOffsetMs: 350`.
- Preserve `entrypointId: ringcentral.video.toolbar.audio-menu` and `operation: open`.
- Do not change the `ringcentral.video.toolbar.audio-menu` open step, `More` occurrence, cleanup, or locator behavior.
- Do not switch microphone, speaker, computer audio, or phone audio as part of this narration-only pass.
- Do not bundle this with camera, share, reactions, notes, recording, leave, aliases, Q&A, route matching, diagnostics logic, or CLI output formatting.
- Keep `Mute`/main microphone privacy behavior in `explain-microphone`; this step is specifically the device and audio connection menu.

## Changed Files

- `docs/agent-handoffs/cycle-067-technical-scan.md`
