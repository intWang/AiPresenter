# Cycle 094 Technical Scan: Control Map More JA

Scope for the next implementation slice: add Japanese narration only to `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-more`.

This scan intentionally created only this handoff file. Do not modify YAML, code, tests, source index, profiles, or other docs in this scan.

## Baseline Verified

Command run:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Current output confirms:

- Overall Japanese demo narration: `44/51`
- `meeting-control-map-demo`: `15/22`
- First missing Japanese step: `control-map-more`
- Remaining missing steps: `control-map-more`, `control-map-recording`, `control-map-notes`, `control-map-background`, `control-map-settings`, `control-map-leave`, `control-map-summary`
- Japanese Q&A remains complete: `12/12` localized questions and `12/12` localized answers
- `questionAliases.ja` remains `3/27` entrypoints and `9` aliases

## Entrypoint And Step Shape

`ringcentral.video.toolbar.more` currently defines:

```yaml
- id: ringcentral.video.toolbar.more
  title: More actions
  area: Meeting toolbar
  purpose: Open additional meeting actions.
  openSteps:
  - action: clickWindowControl
    target: More
    match:
      occurrence: '3'
      controlType: button
      cleanup: escape
```

Important presenter notes:

- It is the expansion point for less frequent meeting tools.
- In the current observed two-person meeting layout, `Notes` is a direct toolbar button, while `More` keeps `Start recording`, `Background`, and `Settings`.
- The menu should be closed with Escape before continuing.

Target demo step `meeting-control-map-demo` -> `control-map-more` currently has:

```yaml
  - id: control-map-more
    title: More actions
    action:
      entrypointId: ringcentral.video.toolbar.more
      operation: open
    narration:
      text: Finally, More is the advanced shelf. Since Notes is already on the toolbar here, More gathers riskier
        or less frequent tools such as recording, background, and settings.
      localizedText:
        zh: ...
      placement: during
      actionOffsetMs: 350
```

Add only `localizedText.ja` under this step. Preserve the English text, Chinese text, action, placement, offset, step order, entrypoint open step, and presenter notes.

## Expected Coverage Numbers After This Round

After adding only `localizedText.ja` to `control-map-more`:

- Overall Japanese demo narration: `44/51` -> `45/51`
- `meeting-control-map-demo`: `15/22` -> `16/22`
- First missing Japanese step: `control-map-more` -> `control-map-recording`
- Remaining missing steps should start with `control-map-recording`, followed by `control-map-notes`, `control-map-background`, `control-map-settings`, `control-map-leave`, and `control-map-summary`
- Japanese Q&A should remain `12/12` questions and `12/12` answers
- `questionAliases.ja` should remain `3/27` entrypoints and `9` aliases
- `--require-complete` for Japanese should still fail because later `meeting-control-map-demo` steps remain untranslated

## Focused Tests To Update/Add

`tests/unit/test_material_packages.py`:

- Update `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`:
  - `report.demo_localized_steps`: `44` -> `45`
  - `meeting-control-map-demo.localized_steps`: `15` -> `16`
  - first missing step: `control-map-more` -> `control-map-recording`
  - keep total demo steps `51`, control-map total `22`, Q&A counts, alias counts, and `required_localization_complete is False`
- Add `test_meeting_control_map_has_japanese_more_narration` near the existing `test_meeting_control_map_has_japanese_raise_hand_narration`.
- Update adjacent focused tests that currently assert `control-map-more` is the first missing step:
  - `test_meeting_control_map_has_japanese_reactions_narration`
  - `test_meeting_control_map_has_japanese_raise_hand_narration`
- In the Raise hand test, change the adjacent expectation from `"ja" not in more_step.narration.localized_text` to `"ja" in more_step.narration.localized_text`, and assert `control-map-recording` remains without Japanese narration.

`tests/unit/test_cli.py`:

- In both Japanese localization report tests, update:
  - `Localization report: 44/51 demo steps` -> `Localization report: 45/51 demo steps`
  - `- meeting-control-map-demo: 15/22 narration localized` -> `- meeting-control-map-demo: 16/22 narration localized`
  - `missing: control-map-more` -> `missing: control-map-recording`
- Keep `missing: explain-leave` absent.
- Keep localized Q&A counts and `questionAliases.ja present on 3/27 entrypoints (9 aliases)` unchanged.
- Keep `test_localization_report_require_complete_fails_for_japanese_demo_gap` exit code `1`.

`tests/unit/test_diagnostics.py`:

- In `test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`, update `44/51 demo steps` -> `45/51 demo steps`.
- Keep status `FAIL`, detail `required ja localization incomplete`, and Q&A detail assertions unchanged.

## Route/Action Assertions

The new focused test should lock the route and action boundary:

- `step.action.entrypoint_id == "ringcentral.video.toolbar.more"`
- `step.action.operation == "open"`
- `step.narration.placement == "during"`
- `step.narration.action_offset_ms == 350`
- `more_entrypoint.question_aliases` does not gain `ja`
- global Japanese alias coverage remains `3` entrypoints and `9` aliases
- `more_entrypoint.open_steps` has one executable step
- open step action remains `clickWindowControl`
- open step target remains `More`
- open step match keeps `occurrence == "3"`, `controlType == "button"`, and `cleanup == "escape"`
- presenter notes still mention the expansion point, the current layout where `Notes` is already on the toolbar, and closing with Escape
- previous step `control-map-raise-hand` remains localized and remains a `toggle` on `ringcentral.video.toolbar.raise-hand`
- next step `control-map-recording` remains unlocalized for Japanese and remains the first missing step

Recommended focused assertions:

```python
assert "ja" in more_step.narration.localized_text
assert "ja" not in recording_step.narration.localized_text
assert report.flow_by_id["meeting-control-map-demo"].missing_step_ids[0] == (
    "control-map-recording"
)
```

## Safe Japanese Text Constraints

The Japanese line should be natural, concise product-demo narration. It should explain `More` as the overflow or advanced hub without executing secondary actions.

Good semantic content:

- Mention `More`.
- Mention that `Notes` is already on the toolbar in this build.
- Mention `Start recording`, `Background`, and `Settings` as lower-frequency or more careful actions gathered under `More`.
- State that this step explains only the entry point or menu location.
- State that recording start, background/settings changes, and exit-related actions are not executed until the user clearly asks or confirms.
- Keep later detailed boundaries for `control-map-recording`, `control-map-notes`, `control-map-background`, `control-map-settings`, and `control-map-leave`.

Suggested Japanese text:

```yaml
        ja: 最後に More は、二次的な会議操作をまとめた拡張メニューです。このビルドでは Notes はすでにツールバー上にあり、More には Start recording、Background、Settings など、使用頻度が低い操作や慎重に扱う操作がまとまっています。ここでは入口だけを説明し、録画の開始、背景や設定の変更、退出につながる操作は、ユーザーが明確に求めるまで実行しません。
```

Safe positive assertions can include:

- `More`
- `拡張メニュー` or `入口`
- `Notes`
- `Start recording` or `録画`
- `Background`
- `Settings`
- `使用頻度`
- `慎重`
- `実行しません`

Negative assertions should reject execution or unsafe promise language, especially:

- `録画します`
- `録画を始めます`
- `録画を開始します`
- `Notes を開始します`
- `メモを取ります`
- `文字起こしします`
- `内容を読み上げます`
- `要約します`
- `Background を変更します`
- `Blur にします`
- `背景を選びます`
- `Settings を調整します`
- `設定を変更します`
- `翻訳をオンにします`
- `デバイスを切り替えます`
- `Leave をクリックします`
- `退出します`
- `会議を終了します`
- `安全なので`
- `すぐに`

Avoid adding the word `自動` unless the final text explicitly says an action is not automatic; a simpler `実行しません` boundary is cleaner.

## Source Index Update

The established implementation pattern updates `docs/knowledge/ringcentral-video/source-index.md` after each localization slice.

If the implementation task includes source-index maintenance, update only the localization coverage sentence so it advances from coverage through `raise-hand` to coverage through `more`, and records the remaining control-map narration as future work.

Expected wording change concept:

- Before: Japanese coverage includes `.../share/reactions/raise-hand` steps of `meeting-control-map-demo`.
- After: Japanese coverage includes `.../share/reactions/raise-hand/more` steps of `meeting-control-map-demo`.

Do not update the source index during this technical scan.

## Verification Commands

Focused red/green pytest command for the implementation round:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_raise_hand_narration tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_more_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Expected localization report after implementation:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Expected key lines:

```text
Localization report: 45/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
- meeting-control-map-demo: 16/22 narration localized
  missing: control-map-recording, control-map-notes, control-map-background, control-map-settings, control-map-leave, control-map-summary
questionAliases.ja present on 3/27 entrypoints (9 aliases)
```

Japanese required-complete should still fail:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
```

Expected: exit code `1`, with `Localization coverage incomplete for ja.`

Diff checks for the implementation round:

```powershell
git diff -- packages/ringcentral-video.yaml tests/unit/test_material_packages.py tests/unit/test_cli.py tests/unit/test_diagnostics.py docs/knowledge/ringcentral-video/source-index.md
git diff --check -- packages/ringcentral-video.yaml tests/unit/test_material_packages.py tests/unit/test_cli.py tests/unit/test_diagnostics.py docs/knowledge/ringcentral-video/source-index.md
```

Implementation diff should be limited to one `localizedText.ja` block for `control-map-more`, directly necessary test expectation updates, and the source-index coverage sentence if included by the implementation assignment.
