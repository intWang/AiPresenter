# Cycle 068 Technical Scan: meeting-controls-tour / explain-camera JA narration

Date: 2026-05-16

## Scope

Add Japanese `localizedText.ja` for:

- Package: `packages/ringcentral-video.yaml`
- Flow: `meeting-controls-tour`
- Step: `explain-camera`
- Entrypoint: `ringcentral.video.toolbar.video`
- Operation: `point`

No runtime, locator, alias, Q&A, diagnostics, or CLI implementation changes are needed.

## Current Source Step

```yaml
- id: explain-camera
  title: Camera
  action:
    entrypointId: ringcentral.video.toolbar.video
    operation: point
  narration:
    text: Start video turns on your local camera. Once the camera is on, the same control becomes Stop video.
    localizedText:
      zh: Start video 会打开本地摄像头；开启后，同一个按钮会变成 Stop video，用来关闭视频。
    placement: before
```

Relevant entrypoint:

- `ringcentral.video.toolbar.video`
- Purpose: toggle local camera on or off
- Locator target: `Start video`
- Alternate target: `Stop video`
- Presenter notes: button alternates between `Start video` and `Stop video`; caret next to it exposes camera and video settings
- Locator matrix confidence: medium repo confidence; current labels still need variant validation

## Recommended Japanese Text

```yaml
        ja: Start video はローカルカメラをオンにするためのボタンです。カメラがオンになると同じ場所が Stop video になり、映像をオフにする入口になります。ここでは状態を確認して説明するだけで、ユーザーの明確な指示なしにカメラをオンまたはオフにしません。
```

Rationale:

- Preserves product labels `Start video` and `Stop video`.
- Keeps the step focused on the main camera state control.
- Explains local camera visibility without adding camera-menu or settings concepts.
- Adds an explicit safety boundary for real meetings.
- Matches the current `operation: point`; it explains the control instead of clicking it.

## Test Updates

Expected count updates:

- `tests/unit/test_material_packages.py`
  - Japanese report `demo_localized_steps`: `18` -> `19`
  - `meeting-controls-tour.localized_steps`: `11` -> `12`
  - Add focused test for `explain-camera`
- `tests/unit/test_cli.py`
  - `Localization report: 18/51 demo steps` -> `19/51`
  - `- meeting-controls-tour: 11/22 narration localized` -> `12/22`
  - first missing `explain-camera` -> `explain-camera-menu`
- `tests/unit/test_diagnostics.py`
  - diagnostic detail `18/51 demo steps` -> `19/51 demo steps`

Focused test should assert:

- `step.action.operation == "point"`
- Japanese text exists and has CJK
- Includes `Start video`, `Stop video`, `ローカル`, `カメラ`, `オン`, `オフ`, `ユーザー`, `明確な指示`, and `しません`
- Does not include `背景` or `設定`

## Expected CLI Result

After implementation:

```text
- meeting-controls-tour: 12/22 narration localized
  missing: explain-camera-menu, explain-share, explain-reactions, explain-raise-hand, explain-more, explain-recording, explain-notes, explain-background-settings, explain-settings, explain-leave
Localization report: 19/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
```

Japanese `--require-complete` should still exit `1`.

## Verification

Run the focused red/green set before and after YAML implementation:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_controls_tour_has_japanese_camera_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Then run the normal full verification suite for the cycle.
