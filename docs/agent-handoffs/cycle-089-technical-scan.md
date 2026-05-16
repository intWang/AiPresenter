# Cycle 089 Technical Scan: control-map-camera JA

Date: 2026-05-16

## Target YAML Snapshot

Target file: `packages/ringcentral-video.yaml`

Current target step:

```yaml
- id: control-map-camera
  title: Camera
  action:
    entrypointId: ringcentral.video.toolbar.video
    operation: point
  narration:
    text: The camera button controls whether others can see you. Once video is on, the same area becomes the
      stop-video control.
    localizedText:
      zh: 摄像头按钮决定别人能不能看到你。开启以后，同一个位置会变成停止视频，所以它既是入口也是状态提示。
    placement: before
```

Current gap: `control-map-camera` has Chinese localized narration but no `localizedText.ja`.

Action semantics to preserve:

- `entrypointId`: `ringcentral.video.toolbar.video`
- `operation`: `point`
- `placement`: `before`
- `actionOffsetMs`: none

This slice should add only `localizedText.ja` under `meeting-control-map-demo` -> `control-map-camera`.

Baseline verified with `.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja`: JA is `39/51` overall, `meeting-control-map-demo` is `10/22`, and the first missing step is `control-map-camera`.

## Entrypoint Route

Entrypoint: `ringcentral.video.toolbar.video`

```yaml
- id: ringcentral.video.toolbar.video
  title: Camera control
  area: Meeting toolbar
  purpose: Toggle local camera on or off.
  questionAliases:
    zh:
    - 摄像头
    - 开视频
    - 关视频
  openSteps:
  - action: clickWindowControl
    target: Start video
    match:
      alternateTargets: Stop video
      controlType: button
  presenterNotes:
  - Button text alternates between Start video and Stop video.
  - The caret next to this button exposes camera and video settings.
```

Route details:

- Area: `Meeting toolbar`
- Purpose: toggle local camera on or off.
- Route action: `clickWindowControl`
- Target: `Start video`
- Match: `alternateTargets: Stop video`, `controlType: button`
- Cleanup: none on the entrypoint route.
- Existing Japanese aliases: none on this entrypoint. Do not add aliases in this slice.

Presenter-note semantics to preserve:

- Button text alternates between `Start video` and `Stop video`.
- The nearby caret exposes camera and video settings, but this step is not the caret/menu step.

Important nuance: the demo step is `operation: point`, so the presenter should explain the button and its state without clicking it. Device selection, background configuration, and more video settings belong to `control-map-camera-menu`, which should remain the next missing Japanese step after this slice.

## Test Updates

Expected coverage deltas after adding only this one JA narration:

- Overall JA demo narration: `39/51` -> `40/51`
- `meeting-control-map-demo`: `10/22` -> `11/22`
- First missing step: `control-map-camera` -> `control-map-camera-menu`
- Required JA localization: still incomplete/failing
- Q&A JA coverage: still `12/12` questions and `12/12` answers
- JA aliases: still `3/27` entrypoints and `9` aliases

Recommended focused test updates:

- `tests/unit/test_material_packages.py`
  - In `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`, update localized steps from `39` to `40`, `meeting-control-map-demo` from `10` to `11`, and first missing from `control-map-camera` to `control-map-camera-menu`.
  - Add `test_meeting_control_map_has_japanese_camera_narration` near the existing control-map microphone/audio-menu tests.
  - Assert `step.action.entrypoint_id == "ringcentral.video.toolbar.video"`, `step.action.operation == "point"`, `step.narration.placement == "before"`, and `step.narration.action_offset_ms is None`.
  - Assert the route has one open step using `clickWindowControl`, target `Start video`, `alternateTargets == "Stop video"`, `controlType == "button"`, and no `cleanup` key.
  - Assert the camera entrypoint has no `ja` question aliases and global Japanese alias coverage remains unchanged.
  - Assert presenter notes mention `Start video`, `Stop video`, alternation, the caret, camera, and video settings.
  - Assert JA text exists, has CJK, and includes `カメラ`, `Start video`, `Stop video`, `見える`, `状態`, `ユーザー`, and `明示的`.
  - Assert JA text does not include unsafe action claims such as `クリックします`, `押します`, `オンにします`, `オフにします`, `切り替えます`, `変更します`, `選択します`, `開きます`, `背景`, `設定`, `デバイス`, `自動`, or `必ず`.
- `tests/unit/test_cli.py`
  - In both Japanese localization-report tests, update `Localization report: 39/51 demo steps` -> `Localization report: 40/51 demo steps`.
  - Update `- meeting-control-map-demo: 10/22 narration localized` -> `- meeting-control-map-demo: 11/22 narration localized`.
  - Update `missing: control-map-camera` -> `missing: control-map-camera-menu`.
  - Keep `missing: explain-leave` absent, Q&A at `12/12`, and alias coverage at `questionAliases.ja present on 3/27 entrypoints (9 aliases)`.
- `tests/unit/test_diagnostics.py`
  - In `test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`, update `39/51 demo steps` -> `40/51 demo steps`.
  - Keep status `FAIL`, detail `required ja localization incomplete`, and Q&A details unchanged.

Expected red state before YAML implementation:

- Updated count assertions fail because current state is `39/51` overall and `10/22` for `meeting-control-map-demo`.
- Updated first-missing assertion fails because current first missing step is `control-map-camera`.
- New focused JA narration test fails because `step.narration.localized_text["ja"]` is missing for `control-map-camera`.

Expected green state after this slice:

- Overall JA demo narration: `40/51`
- `meeting-control-map-demo`: `11/22`
- First missing JA step in that flow: `control-map-camera-menu`
- Required JA localization: still incomplete/failing
- Q&A JA coverage: still `12/12` questions and `12/12` answers
- JA aliases: still `3/27` entrypoints and `9` aliases

## Suggested Japanese Text

Recommended `localizedText.ja`:

```yaml
        ja: カメラボタンは、自分の映像をほかの参加者に見せるかどうかを確認するための主要なコントロールです。ビデオがオンになると、同じ場所が Stop video になり、現在の状態を示します。ここでは場所と状態を説明するだけで、ユーザーが明示的に求めるまでカメラをオンまたはオフにはしません。
```

Why this wording:

- Preserves the source meaning: the camera button controls whether others can see the user.
- Reflects presenter notes: the visible label can be `Start video` or `Stop video`, and that label indicates current state.
- Fits `operation: point` and `placement: before` by explaining location and state without opening or clicking anything.
- Keeps camera menu concerns out of scope; camera device selection and more video settings remain for `control-map-camera-menu`.

Acceptable shorter variant:

```yaml
        ja: カメラボタンは、ほかの参加者に自分の映像を見せるかどうかを確認する場所です。ビデオがオンのときは同じ場所が Stop video になり、状態の目印になります。ユーザーが明示的に求めるまで、カメラのオン・オフは切り替えません。
```

Avoid wording such as:

- `カメラをオンにします`
- `カメラをオフにします`
- `Start video をクリックします`
- `Stop video を押します`
- `カメラを切り替えます`
- `カメラを選択します`
- `ビデオ設定を開きます`
- `背景を変更します`
- `デバイスを変更します`
- `自動で切り替えます`
- `必ずオンにします`

## Verification Commands

Focused test command after implementation:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_camera_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Optional focused CLI check:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Expected CLI lines after implementation:

```text
Localization report: 40/51 demo steps
- meeting-control-map-demo: 11/22 narration localized
  missing: control-map-camera-menu
- localized questions: 12/12
- localized answers: 12/12
questionAliases.ja present on 3/27 entrypoints (9 aliases)
```

Japanese `--require-complete` should still exit nonzero and print `Localization coverage incomplete for ja.`

## Do-not-change Guardrails

- This scan writes only `docs/agent-handoffs/cycle-089-technical-scan.md`; do not edit YAML, code, tests, source index, profiles, or other docs in this scan.
- Implementation should edit only the targeted JA narration and directly related test expectations.
- Do not change `control-map-camera` action semantics: keep `entrypointId`, `operation`, `placement`, and absent `actionOffsetMs` exactly as they are.
- Do not change `ringcentral.video.toolbar.video` route semantics: keep `clickWindowControl`, target `Start video`, `alternateTargets: Stop video`, `controlType: button`, and no cleanup.
- Do not add or change Japanese aliases; current JA alias coverage should remain `3/27` entrypoints and `9` aliases.
- Do not localize `control-map-camera-menu` or any later `meeting-control-map-demo` step in this slice.
- Do not broaden into Q&A, Chinese/English narration, presenter notes, locator strategy, diagnostics behavior, CLI formatting, profiles, source-index updates, or acceptance evidence.
- Do not imply the presenter clicks the camera button, starts video, stops video, changes camera device, opens video settings, changes background, or changes any live media state unless the user explicitly asks and visible state has been verified.
- Do not reuse the camera-menu wording here; this step is the main camera state button, not the caret menu.
- Do not revert or overwrite concurrent edits from other agents.
