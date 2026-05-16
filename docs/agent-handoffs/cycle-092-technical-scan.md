# Cycle 092 Technical Scan: control-map-reactions JA

Scope for the next implementation slice: add Japanese narration only to `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-reactions`.

This scan intentionally created only this handoff file. Do not modify YAML, code, tests, source index, profiles, or other docs in this scan.

## Current Baseline

Verified with:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Current Japanese localization report:

```text
Localization report: 42/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
- meeting-control-map-demo: 13/22 narration localized
  missing: control-map-reactions, control-map-raise-hand, control-map-more, control-map-recording, control-map-notes, control-map-background, control-map-settings, control-map-leave, control-map-summary
questionAliases.ja present on 3/27 entrypoints (9 aliases)
```

The targeted slice should add only `localizedText.ja` under `meeting-control-map-demo` -> `control-map-reactions`.

## Entrypoint And Demo Step

Entrypoint `ringcentral.video.toolbar.react`:

```yaml
- id: ringcentral.video.toolbar.react
  title: Reactions
  area: Meeting toolbar
  purpose: Send meeting reactions without interrupting speech.
  openSteps:
  - action: clickWindowControl
    target: React
    match:
      controlType: button
      cleanup: escape
  presenterNotes:
  - Reactions are lightweight feedback signals.
  - This is a good fallback when the presenter wants to acknowledge without opening a panel.
  - Observed reactions include heart, thumbs up, celebration, clap, smile, and Be right back.
  - Close the reaction strip with Escape if no reaction should be sent.
```

Demo step `control-map-reactions`:

```yaml
- id: control-map-reactions
  title: Reactions
  action:
    entrypointId: ringcentral.video.toolbar.react
    operation: open
  narration:
    text: For lightweight interaction, Reactions gives quick feedback such as approval, celebration, applause,
      or be-right-back without interrupting the speaker.
    localizedText:
      zh: Reactions 适合轻量互动。比如点赞、庆祝、鼓掌，或者提示马上回来；它能表达反馈，又不会打断正在说话的人。
    placement: during
    actionOffsetMs: 350
```

Important nuance: this is an `open` step. Opening the reaction strip is acceptable for orientation, but selecting any reaction sends a visible in-meeting signal. The Japanese narration must keep the tour at route/explanation level and must not imply that a heart, thumbs up, celebration, clap, smile, or Be right back reaction is sent automatically.

## Expected Coverage Numbers After This Round

Expected deltas after adding exactly one Japanese narration:

- Overall Japanese demo steps: `42/51` -> `43/51`
- `meeting-control-map-demo`: `13/22` -> `14/22`
- First missing step: `control-map-reactions` -> `control-map-raise-hand`
- Q&A coverage: stay `12/12` questions and `12/12` answers
- `questionAliases.ja`: stay `3/27` entrypoints and `9` aliases
- `--require-complete` for Japanese: still fails because later control-map steps remain untranslated

## Focused Tests To Update/Add

`tests/unit/test_material_packages.py`

- In `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`, update:
  - `report.demo_localized_steps` from `42` to `43`
  - `meeting-control-map-demo.localized_steps` from `13` to `14`
  - first missing from `control-map-reactions` to `control-map-raise-hand`
- Add `test_meeting_control_map_has_japanese_reactions_narration` immediately after `test_meeting_control_map_has_japanese_share_narration`.
- Update existing adjacent assertions that currently treat Reactions as missing:
  - `test_meeting_control_map_has_japanese_camera_menu_narration`
  - `test_meeting_control_map_has_japanese_share_narration`
- Keep Q&A assertions unchanged: `12/12` questions, `12/12` answers.
- Keep alias assertions unchanged: `3/27` entrypoints, `9` aliases.

`tests/unit/test_cli.py`

- In both Japanese localization-report tests, update:
  - `Localization report: 42/51 demo steps` -> `Localization report: 43/51 demo steps`
  - `- meeting-control-map-demo: 13/22 narration localized` -> `- meeting-control-map-demo: 14/22 narration localized`
  - `missing: control-map-reactions` -> `missing: control-map-raise-hand`
- Keep `missing: explain-leave` absent.
- Keep Q&A and alias output assertions unchanged.
- `test_localization_report_require_complete_fails_for_japanese_demo_gap` should still expect exit code `1` and `Localization coverage incomplete for ja.`

`tests/unit/test_diagnostics.py`

- In `test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`, update `42/51 demo steps` -> `43/51 demo steps`.
- Keep status `FAIL`, detail `required ja localization incomplete`, and Q&A details unchanged.

Expected red before YAML implementation:

- Updated count assertions fail because current state is `42/51` overall and `13/22` for `meeting-control-map-demo`.
- New focused JA narration test fails because `step.narration.localized_text["ja"]` is missing for `control-map-reactions`.

Expected green after YAML implementation:

- Overall JA demo coverage: `43/51`
- `meeting-control-map-demo`: `14/22`
- First missing JA step in that flow: `control-map-raise-hand`
- Q&A and alias coverage unchanged

## Route/action Assertions

Recommended focused assertions for the new Reactions test:

```python
def test_meeting_control_map_has_japanese_reactions_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-control-map-demo")
    step = next(step for step in flow.steps if step.id == "control-map-reactions")

    assert step.action.entrypoint_id == "ringcentral.video.toolbar.react"
    assert step.action.operation == "open"
    assert step.narration.placement == "during"
    assert step.narration.action_offset_ms == 350

    report = build_localization_status(package, language="ja")
    reactions_entrypoint = package.entrypoint_by_id("ringcentral.video.toolbar.react")
    assert "ja" not in reactions_entrypoint.question_aliases
    assert report.entrypoints_with_aliases == 3
    assert report.alias_total == 9
    assert report.flow_by_id["meeting-control-map-demo"].missing_step_ids[0] == (
        "control-map-raise-hand"
    )

    assert len(reactions_entrypoint.open_steps) == 1
    open_step = reactions_entrypoint.open_steps[0]
    assert open_step.action == "clickWindowControl"
    assert open_step.target == "React"
    assert open_step.match["controlType"] == "button"
    assert open_step.match["cleanup"] == "escape"

    assert "lightweight feedback signals" in reactions_entrypoint.presenter_notes[0]
    assert "Observed reactions include" in reactions_entrypoint.presenter_notes[2]
    assert "heart" in reactions_entrypoint.presenter_notes[2]
    assert "thumbs up" in reactions_entrypoint.presenter_notes[2]
    assert "celebration" in reactions_entrypoint.presenter_notes[2]
    assert "clap" in reactions_entrypoint.presenter_notes[2]
    assert "smile" in reactions_entrypoint.presenter_notes[2]
    assert "Be right back" in reactions_entrypoint.presenter_notes[2]
    assert "Close the reaction strip with Escape" in reactions_entrypoint.presenter_notes[3]

    share_step = next(step for step in flow.steps if step.id == "control-map-share")
    assert "ja" in share_step.narration.localized_text
    raise_hand_step = next(step for step in flow.steps if step.id == "control-map-raise-hand")
    assert raise_hand_step.action.entrypoint_id == "ringcentral.video.toolbar.raise-hand"
    assert "ja" not in raise_hand_step.narration.localized_text
```

Text assertions should confirm the Japanese copy:

- includes `Reactions` or `React`
- includes lightweight feedback concepts such as `軽いフィードバック` or `軽量`
- includes examples such as `承認`, `祝福`, `拍手`, and `Be right back`
- includes the visible meeting signal boundary, such as `会議中に表示されるシグナル`
- includes explicit user-intent gating, such as `ユーザー` and `明示的`
- includes a no-send boundary, such as `送信しません`
- includes cleanup/closure when only explaining, such as `閉じます`
- does not imply the presenter chooses or sends a reaction

Useful negative assertions:

```python
assert "送信します" not in ja_text
assert "送ります" not in ja_text
assert "選択します" not in ja_text
assert "選びます" not in ja_text
assert "クリックします" not in ja_text
assert "押します" not in ja_text
assert "リアクションを送ります" not in ja_text
assert "自動" not in ja_text
assert "必ず" not in ja_text
```

Adjacent route guardrails:

- `control-map-share` must remain the previous localized step and keep its existing route/action assertions.
- `control-map-raise-hand` should become the first missing Japanese step after this slice.
- Do not add or change Japanese aliases for `ringcentral.video.toolbar.react`.
- Do not localize `control-map-raise-hand` or any later `meeting-control-map-demo` step in this slice.

## Safe Japanese Text Constraints

Recommended `localizedText.ja`:

```yaml
        ja: Reactions は、発話を遮らずに承認、祝福、拍手、Be right back などの軽いフィードバックを確認できるリアクション欄を開きます。リアクションは会議中に表示されるシグナルなので、ここでは選択肢の場所と役割だけを説明し、ユーザーが明示的に求めるまで送信しません。説明だけの場合は何も選ばずに閉じます。
```

Constraints:

- Keep it explanatory and route-level.
- Mention the reaction strip and representative quick-feedback options.
- State that reactions are visible meeting signals, not private notes.
- State that the presenter will not send or choose a reaction without explicit user request.
- Mention cleanup/closure after explanation, consistent with `cleanup: escape`.
- Do not claim to acknowledge, approve, celebrate, clap, smile, or mark Be right back on the user's behalf.
- Do not add aliases or Q&A entries in this slice.

Suggested concise variant if the implementation wants shorter narration:

```yaml
        ja: Reactions は、承認、祝福、拍手、Be right back などの軽いフィードバックを発話を遮らずに示すための欄を開きます。リアクションは会議中に表示されるシグナルなので、ユーザーが明示的に求めるまで送信しません。説明だけの場合は何も選ばずに閉じます。
```

## Source Index Update

`docs/knowledge/ringcentral-video/source-index.md` currently says Japanese coverage includes:

```text
... overview/meeting-information/network-quality/view-layout/report-issue/add-coworkers/participants/chat/microphone/audio-menu/camera/camera-menu/share steps of `meeting-control-map-demo` ...
```

After implementation, update that phrase to include reactions:

```text
... overview/meeting-information/network-quality/view-layout/report-issue/add-coworkers/participants/chat/microphone/audio-menu/camera/camera-menu/share/reactions steps of `meeting-control-map-demo` ...
```

Do not imply full `meeting-control-map-demo` Japanese coverage until all 22 steps are localized.

## Verification Commands

Focused red/green pytest command:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_camera_menu_narration tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_share_narration tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_reactions_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Localization report:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Expected excerpt after implementation:

```text
Localization report: 43/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
- meeting-control-map-demo: 14/22 narration localized
  missing: control-map-raise-hand
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

- one `localizedText.ja` block under `meeting-control-map-demo` -> `control-map-reactions`
- directly related test expectation updates and one focused test
- source-index coverage wording from `share` through `reactions`

## Out Of Scope

- Do not localize `control-map-raise-hand` or later steps.
- Do not add Japanese `questionAliases` for Reactions.
- Do not add or edit Q&A.
- Do not change entrypoint routes, cleanup, presenter notes, or demo step action metadata.
- Do not send or imply sending any reaction in narration-only control tours.
