# Cycle 091 Technical Scan: control-map-share JA

Scope for the next implementation slice: add Japanese narration only to `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-share`.

This scan intentionally created only this handoff file. Do not modify YAML, code, tests, source index, profiles, or other docs in this scan.

## Current Baseline

Verified with:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Current Japanese localization report:

```text
Localization report: 41/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
- meeting-control-map-demo: 12/22 narration localized
  missing: control-map-share, control-map-reactions, control-map-raise-hand, control-map-more, control-map-recording, control-map-notes, control-map-background, control-map-settings, control-map-leave, control-map-summary
questionAliases.ja present on 3/27 entrypoints (9 aliases)
```

The targeted slice should add only `localizedText.ja` under `meeting-control-map-demo` -> `control-map-share`.

## Entrypoint And Demo Step

Entrypoint `ringcentral.video.toolbar.share`:

```yaml
- id: ringcentral.video.toolbar.share
  title: Screen sharing
  area: Meeting toolbar
  purpose: Start sharing a screen, window, or selected content.
  questionAliases:
    zh:
    - 共享屏幕
    - 分享屏幕
    - 屏幕共享
    - 共享
  openSteps:
  - action: clickWindowControl
    target: Share
    match:
      controlType: button
      cleanup: escape
  presenterNotes:
  - Narration must not infer shared-screen content unless verified by an allowed source.
  - Use this entry point to explain presenter handoff and collaboration.
  - Observed share picker includes entire screen, application windows, Share system audio, and Share.
  - Do not click the final Share button during a control tour unless the user explicitly asks to start sharing.
```

Demo step `control-map-share`:

```yaml
- id: control-map-share
  title: Share
  action:
    entrypointId: ringcentral.video.toolbar.share
    operation: open
  narration:
    text: Share opens the picker for screen or application sharing. I can explain the choices, but I do not press
      the final Share button unless you confirm what should be shown.
    localizedText:
      zh: Share 会打开屏幕或窗口选择器。我可以帮你说明每个选项，但不会替你点最终共享，除非你确认要展示哪一个内容。
    placement: during
    actionOffsetMs: 400
```

Important nuance: this is an `open` step that can expose screen/window candidates and a final high-impact Share button. The narration can describe the picker and handoff boundary, but it must not read source names, infer visible content, or imply that sharing starts automatically.

## Expected Coverage Numbers After This Round

Expected deltas after adding exactly one Japanese narration:

- Overall Japanese demo steps: `41/51` -> `42/51`
- `meeting-control-map-demo`: `12/22` -> `13/22`
- First missing step: `control-map-share` -> `control-map-reactions`
- Q&A coverage: stay `12/12` questions and `12/12` answers
- `questionAliases.ja`: stay `3/27` entrypoints and `9` aliases
- `--require-complete` for Japanese: still fails because later control-map steps remain untranslated

## Focused Tests To Update/Add

`tests/unit/test_material_packages.py`

- In `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`, update:
  - `report.demo_localized_steps` from `41` to `42`
  - `meeting-control-map-demo.localized_steps` from `12` to `13`
  - first missing from `control-map-share` to `control-map-reactions`
- Add `test_meeting_control_map_has_japanese_share_narration` immediately after `test_meeting_control_map_has_japanese_camera_menu_narration`.
- Keep Q&A assertions unchanged: `12/12` questions, `12/12` answers.
- Keep alias assertions unchanged: `3/27` entrypoints, `9` aliases.

`tests/unit/test_cli.py`

- In both Japanese localization-report tests, update:
  - `Localization report: 41/51 demo steps` -> `Localization report: 42/51 demo steps`
  - `- meeting-control-map-demo: 12/22 narration localized` -> `- meeting-control-map-demo: 13/22 narration localized`
  - `missing: control-map-share` -> `missing: control-map-reactions`
- Keep `missing: explain-leave` absent.
- Keep Q&A and alias output assertions unchanged.
- `test_localization_report_require_complete_fails_for_japanese_demo_gap` should still expect exit code `1` and `Localization coverage incomplete for ja.`

`tests/unit/test_diagnostics.py`

- In `test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`, update `41/51 demo steps` -> `42/51 demo steps`.
- Keep status `FAIL`, detail `required ja localization incomplete`, and Q&A details unchanged.

Expected red before YAML implementation:

- Updated count assertions fail because current state is `41/51` overall and `12/22` for `meeting-control-map-demo`.
- New focused JA narration test fails because `step.narration.localized_text["ja"]` is missing for `control-map-share`.

Expected green after YAML implementation:

- Overall JA demo coverage: `42/51`
- `meeting-control-map-demo`: `13/22`
- First missing JA step in that flow: `control-map-reactions`
- Q&A and alias coverage unchanged

## Route/action Assertions

Recommended focused assertions for the new share test:

```python
def test_meeting_control_map_has_japanese_share_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-control-map-demo")
    step = next(step for step in flow.steps if step.id == "control-map-share")

    assert step.action.entrypoint_id == "ringcentral.video.toolbar.share"
    assert step.action.operation == "open"
    assert step.narration.placement == "during"
    assert step.narration.action_offset_ms == 400

    report = build_localization_status(package, language="ja")
    share_entrypoint = package.entrypoint_by_id("ringcentral.video.toolbar.share")
    assert "ja" not in share_entrypoint.question_aliases
    assert report.entrypoints_with_aliases == 3
    assert report.alias_total == 9
    assert report.flow_by_id["meeting-control-map-demo"].missing_step_ids[0] == (
        "control-map-reactions"
    )

    assert len(share_entrypoint.open_steps) == 1
    open_step = share_entrypoint.open_steps[0]
    assert open_step.action == "clickWindowControl"
    assert open_step.target == "Share"
    assert open_step.match["controlType"] == "button"
    assert open_step.match["cleanup"] == "escape"

    assert "must not infer shared-screen content" in share_entrypoint.presenter_notes[0]
    assert "entire screen" in share_entrypoint.presenter_notes[2]
    assert "application windows" in share_entrypoint.presenter_notes[2]
    assert "Share system audio" in share_entrypoint.presenter_notes[2]
    assert "Do not click the final Share button" in share_entrypoint.presenter_notes[3]

    camera_menu_step = next(
        step for step in flow.steps if step.id == "control-map-camera-menu"
    )
    assert "ja" in camera_menu_step.narration.localized_text
    reactions_step = next(step for step in flow.steps if step.id == "control-map-reactions")
    assert "ja" not in reactions_step.narration.localized_text
```

Text assertions should confirm the Japanese copy:

- includes `Share`
- includes screen/window sharing concepts such as `画面` and `ウィンドウ`
- includes final Share button / start-sharing boundary, such as `最終的な Share ボタン` or `共有を開始`
- includes explicit user confirmation, such as `ユーザー` and `明示的`
- includes a no-reading/no-inference privacy boundary for candidates or screen contents
- does not imply the presenter presses Share or starts sharing

Useful negative assertions:

```python
assert "押します" not in ja_text
assert "クリックします" not in ja_text
assert "共有を開始します" not in ja_text
assert "読み上げます" not in ja_text
assert "推測します" not in ja_text
assert "選択します" not in ja_text
assert "自動" not in ja_text
assert "必ず" not in ja_text
```

Adjacent route guardrails:

- `control-map-camera-menu` must remain the previous localized step and keep its existing route/action assertions.
- `control-map-reactions` should become the first missing Japanese step after this slice.
- Do not add or change Japanese aliases for `ringcentral.video.toolbar.share`.
- Do not localize `control-map-reactions` or any later `meeting-control-map-demo` step in this slice.

## Safe Japanese Text Constraints

Recommended `localizedText.ja`:

```yaml
        ja: Share は、画面全体やアプリケーションウィンドウを共有するための選択画面を開きます。システム音声の共有もここで確認できますが、候補名や画面内容は、ユーザーが明示的に求め、表示内容が確認されるまで読み上げません。ここでは選択肢の場所と役割を説明するだけで、ユーザーが共有する内容を明確に確認するまで、最終的な Share ボタンを押して共有を開始しません。説明後は選択画面を閉じます。
```

Constraints:

- Keep it explanatory and route-level.
- Mention the picker, screen/window choices, optional system audio, and final Share button boundary.
- State that candidates/screen contents are private until explicitly requested and verified.
- State that the presenter will not press the final Share button or start sharing without clear confirmation.
- Mention cleanup/closure after explanation, consistent with `cleanup: escape`.
- Do not claim to inspect, summarize, infer, select, or expose a screen/window.
- Do not add aliases or Q&A entries in this slice.

Suggested concise variant if the implementation wants shorter narration:

```yaml
        ja: Share は、画面全体やアプリケーションウィンドウを共有するための選択画面を開きます。ここでは選択肢の場所と役割だけを説明し、候補名や画面内容は明確な依頼と確認済みの表示状況なしに読み上げません。ユーザーが共有する内容を明確に確認するまで、最終的な Share ボタンを押して共有を開始しません。説明後は選択画面を閉じます。
```

## Source Index Update

`docs/knowledge/ringcentral-video/source-index.md` currently says Japanese coverage includes:

```text
... overview/meeting-information/network-quality/view-layout/report-issue/add-coworkers/participants/chat/microphone/audio-menu/camera/camera-menu steps of `meeting-control-map-demo` ...
```

After implementation, update that phrase to include share:

```text
... overview/meeting-information/network-quality/view-layout/report-issue/add-coworkers/participants/chat/microphone/audio-menu/camera/camera-menu/share steps of `meeting-control-map-demo` ...
```

Do not imply full `meeting-control-map-demo` Japanese coverage until all 22 steps are localized.

## Verification Commands

Focused red/green pytest command:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_share_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Localization report:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Expected excerpt after implementation:

```text
Localization report: 42/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
- meeting-control-map-demo: 13/22 narration localized
  missing: control-map-reactions
questionAliases.ja present on 3/27 entrypoints (9 aliases)
```

Required-complete still fails:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
```

Expected: nonzero exit and `Localization coverage incomplete for ja.`

Optional scope check after implementation:

```powershell
git diff -- packages/ringcentral-video.yaml tests/unit/test_material_packages.py tests/unit/test_cli.py tests/unit/test_diagnostics.py docs/knowledge/ringcentral-video/source-index.md
```

Expected implementation diff should be limited to:

- one `localizedText.ja` block under `meeting-control-map-demo` -> `control-map-share`
- directly related test expectation updates and one focused test
- source-index coverage wording from `camera-menu` through `share`

## Out Of Scope

- Do not localize `control-map-reactions` or later steps.
- Do not add Japanese `questionAliases` for Share.
- Do not add or edit Q&A.
- Do not change entrypoint routes, cleanup, presenter notes, or demo step action metadata.
- Do not click or imply clicking the final Share button in narration-only control tours.
