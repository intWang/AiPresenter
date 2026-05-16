# Cycle 090 Technical Scan: control-map-camera-menu JA

Scope: this is a planning/scan handoff only. Do not modify package YAML, tests, source-index, code, or commits in this round.

## Baseline

Current Japanese localization report:

```text
Localization report: 40/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
- meeting-control-map-demo: 11/22 narration localized
  missing: control-map-camera-menu, control-map-share, control-map-reactions, control-map-raise-hand, control-map-more, control-map-recording, control-map-notes, control-map-background, control-map-settings, control-map-leave, control-map-summary
questionAliases.ja present on 3/27 entrypoints (9 aliases)
```

The targeted slice should add only `localizedText.ja` under `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-camera-menu`.

## YAML Facts

Entrypoint `ringcentral.video.toolbar.video-menu`:

```yaml
- id: ringcentral.video.toolbar.video-menu
  title: Camera menu
  area: Meeting toolbar
  purpose: Open camera device selection and the More video settings shortcut.
  questionAliases:
    zh:
    - ...
  openSteps:
  - action: clickWindowControl
    target: More
    match:
      occurrence: '2'
      controlType: button
      cleanup: escape
  presenterNotes:
  - Observed menu includes the selected camera and More video settings.
  - Use More video settings for background, quality, and camera configuration.
  - Close the menu with Escape when the tour is only explaining the entry point.
```

Demo step `control-map-camera-menu`:

```yaml
- id: control-map-camera-menu
  title: Camera menu
  action:
    entrypointId: ringcentral.video.toolbar.video-menu
    operation: open
  narration:
    text: The camera menu lets you choose the camera and jump to video settings. It is the practical route for
      device changes and appearance setup.
    localizedText:
      zh: ...
    placement: during
    actionOffsetMs: 350
```

Important nuance: unlike `control-map-camera`, this step opens a live menu. The Japanese narration may describe the menu contents and route to video settings, but must stay explain-only and must not imply automatic camera switching, opening deeper settings, changing background or appearance, reading selected device names aloud, or leaving the menu open.

## Expected Coverage Numbers After This Round

Expected deltas after adding exactly one Japanese narration:

- Overall JA demo narration: `40/51` -> `41/51`
- `meeting-control-map-demo`: `11/22` -> `12/22`
- First missing step: `control-map-camera-menu` -> `control-map-share`
- Q&A: stay `12/12` questions and `12/12` answers
- `questionAliases.ja`: stay `3/27` entrypoints and `9` aliases
- Required JA localization: still incomplete/failing

## Focused Tests To Update/Add

`tests/unit/test_material_packages.py`

- In `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`, update:
  - `report.demo_localized_steps` from `40` to `41`
  - `meeting-control-map-demo.localized_steps` from `11` to `12`
  - first missing from `control-map-camera-menu` to `control-map-share`
- Add `test_meeting_control_map_has_japanese_camera_menu_narration` immediately after `test_meeting_control_map_has_japanese_camera_narration`.
- Keep global alias assertions unchanged: `entrypoints_with_aliases == 3`, `alias_total == 9`.

`tests/unit/test_cli.py`

- In both Japanese localization-report tests, update:
  - `Localization report: 40/51 demo steps` -> `Localization report: 41/51 demo steps`
  - `- meeting-control-map-demo: 11/22 narration localized` -> `- meeting-control-map-demo: 12/22 narration localized`
  - `missing: control-map-camera-menu` -> `missing: control-map-share`
- Keep `missing: explain-leave` absent, Q&A at `12/12`, and alias coverage at `questionAliases.ja present on 3/27 entrypoints (9 aliases)`.
- `--require-complete` must still exit `1` and print `Localization coverage incomplete for ja.`

`tests/unit/test_diagnostics.py`

- In `test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`, update `40/51 demo steps` -> `41/51 demo steps`.
- Keep status `FAIL`, detail `required ja localization incomplete`, and Q&A details unchanged.

## Route/Action Assertions

The new focused test should assert the route and open behavior, not just coverage:

```python
assert step.action.entrypoint_id == "ringcentral.video.toolbar.video-menu"
assert step.action.operation == "open"
assert step.narration.placement == "during"
assert step.narration.action_offset_ms == 350
```

Entrypoint assertions:

```python
camera_menu_entrypoint = package.entrypoint_by_id(
    "ringcentral.video.toolbar.video-menu"
)
assert "ja" not in camera_menu_entrypoint.question_aliases
assert report.entrypoints_with_aliases == 3
assert report.alias_total == 9
assert len(camera_menu_entrypoint.open_steps) == 1
open_step = camera_menu_entrypoint.open_steps[0]
assert open_step.action == "clickWindowControl"
assert open_step.target == "More"
assert open_step.match["occurrence"] == "2"
assert open_step.match["controlType"] == "button"
assert open_step.match["cleanup"] == "escape"
assert "selected camera" in camera_menu_entrypoint.presenter_notes[0]
assert "More video settings" in camera_menu_entrypoint.presenter_notes[0]
assert "background, quality, and camera configuration" in camera_menu_entrypoint.presenter_notes[1]
assert "Close the menu with Escape" in camera_menu_entrypoint.presenter_notes[2]
```

Adjacent route guardrails:

- `control-map-camera` must remain `operation: point` on `ringcentral.video.toolbar.video`.
- `control-map-camera-menu` must remain the only newly localized step in this slice.
- `control-map-share` should become the first missing Japanese step after this slice.

## Safe Japanese Text Constraints

Recommended `localizedText.ja`:

```yaml
        ja: カメラ横のメニューでは、使用するカメラの候補と More video settings への入口を確認できます。カメラ、背景、画質などの見え方を調整したいときの経路ですが、ここでは場所と選択肢を説明するだけで、ユーザーが明示的に求めるまでカメラや背景、ビデオ設定は変更しません。説明後はメニューを閉じます。
```

Expected positive assertions:

- contains `カメラ`
- contains `More video settings`
- contains `背景`
- contains `画質`
- contains `見え方`
- contains `ユーザー`
- contains `明示的`
- contains `変更しません`
- contains `閉じます`

Suggested negative assertions:

- does not contain `切り替えます`
- does not contain `選択します`
- does not contain `開きます`
- does not contain `読み上げます`
- does not contain `確認します` if the test wants to avoid sounding like device inspection; if this is too strict, use the exact recommended copy and allow generic `確認できます`
- does not contain `自動`
- does not contain `必ず`

Rationale:

- It matches `operation: open`, `placement: during`, and `actionOffsetMs: 350`: the menu is visible while the narration runs.
- It names camera menu affordances without promising to select a camera, inspect device labels, change appearance, open settings, or apply background/quality changes.
- It explicitly closes the menu after explanation, matching entrypoint cleanup via Escape.

## Source Index Update

After implementation, update only the localization bullet in `docs/knowledge/ringcentral-video/source-index.md`.

Current phrasing lists localized `meeting-control-map-demo` steps through `.../audio-menu/camera steps...`.

Update that list to include `camera-menu`:

```text
... overview/meeting-information/network-quality/view-layout/report-issue/add-coworkers/participants/chat/microphone/audio-menu/camera/camera-menu steps of `meeting-control-map-demo` ...
```

Do not change source coverage claims, aliases, runtime notes, or future gap categories.

## Verification Commands

Focused pytest command after implementation:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_camera_menu_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Localization report:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Expected report fragments:

```text
Localization report: 41/51 demo steps
- meeting-control-map-demo: 12/22 narration localized
  missing: control-map-share
- localized questions: 12/12
- localized answers: 12/12
questionAliases.ja present on 3/27 entrypoints (9 aliases)
```

Required-complete check should still fail:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
```

Expected: nonzero exit and `Localization coverage incomplete for ja.`

## Non-Goals

- Do not localize `control-map-share` or any later `meeting-control-map-demo` step.
- Do not change Chinese or English narration.
- Do not add Japanese aliases.
- Do not change entrypoint open steps, locator details, cleanup, presenter notes, flow order, Q&A, runtime behavior, diagnostics logic, CLI formatting, or profiles.
- Do not commit as part of this scan.
