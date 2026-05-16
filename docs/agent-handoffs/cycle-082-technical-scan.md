# Cycle 082 Technical Scan: control-map-views JA

Date: 2026-05-16

## Target YAML Snapshot

Target file: `packages/ringcentral-video.yaml`

Current target step:

```yaml
- id: control-map-views
  title: View layout
  action:
    entrypointId: ringcentral.video.top.views
    operation: open
  narration:
    text: Views controls how the meeting is arranged on your screen. It changes layout, like gallery or full
      screen, without changing anyone's audio, video, or membership.
    localizedText:
      zh: 这里是视图布局。它只改变你看到会议的方式，比如宫格视图或全屏，不会影响别人的音频、视频，也不会改成员状态。
    placement: during
    actionOffsetMs: 350
```

Current gap: `control-map-views` has Chinese localized narration but no `localizedText.ja`.

Action semantics to preserve:

- `entrypointId`: `ringcentral.video.top.views`
- `operation`: `open`
- `placement`: `during`
- `actionOffsetMs`: `350`

Because this step opens a view-layout menu, the Japanese copy can name the menu and visible layout concepts, but should not instruct the user that AiPresenter is switching layouts, selecting a view, entering full screen, or changing any media, sharing, or membership state.

## Entrypoint Route

Entrypoint: `ringcentral.video.top.views`

```yaml
- id: ringcentral.video.top.views
  title: View layout menu
  area: Meeting top bar
  purpose: Switch the meeting layout, including Gallery view and Full screen.
  openSteps:
  - action: clickWindowRelative
    target: Views
    match:
      xFromRight: '237'
      y: '21'
      cleanup: escape
```

Route details:

- Area: `Meeting top bar`
- Route action: `clickWindowRelative`
- Target: `Views`
- Coordinate match: `xFromRight: '237'`, `y: '21'`
- Cleanup: `escape`
- Presenter notes say observed options include `Gallery` and `Full screen`, this changes presentation layout rather than meeting membership or media state, and the menu should be closed with Escape after explaining it.

Do not change the entrypoint route, open steps, cleanup, purpose, or presenter notes in this round.

## Test Updates

Recommended red-first updates:

- `tests/unit/test_material_packages.py`
  - In `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`, update overall JA demo coverage from `32` to `33`.
  - Update `meeting-control-map-demo` localized steps from `3` to `4`.
  - Update first missing step from `control-map-views` to `control-map-report`.
  - Add a focused guard test for `meeting-control-map-demo` -> `control-map-views`, parallel to the existing `control-map-meeting-info` and `control-map-network` JA tests.
  - The focused test should assert:
    - `step.action.entrypoint_id == "ringcentral.video.top.views"`
    - `step.action.operation == "open"`
    - `step.narration.placement == "during"`
    - `step.narration.action_offset_ms == 350`
    - entrypoint route uses `clickWindowRelative`, target `Views`, `xFromRight == "237"`, `y == "21"`, and `cleanup == "escape"`
    - JA text exists, contains CJK, and includes required UI/concept terms such as `Views`, `View layout`, `Gallery view`, `Full screen`, `会議`, `表示`, `音声`, `ビデオ`, `参加者`, `共有`
    - JA text frames the route as a menu/location/explanation, not as an instruction to change state
    - JA text excludes over-action wording such as `切り替えます`, `選択します`, `変更します`, `Gallery view を選択`, `Full screen にします`, `全画面にします`, `音声を変更`, `ビデオを変更`, `共有を開始`, `共有を変更`, `参加者を変更`

- `tests/unit/test_cli.py`
  - In `test_localization_report_outputs_japanese_demo_and_qa_coverage`, update:
    - `Localization report: 32/51 demo steps` -> `Localization report: 33/51 demo steps`
    - `- meeting-control-map-demo: 3/22 narration localized` -> `- meeting-control-map-demo: 4/22 narration localized`
    - `missing: control-map-views` -> `missing: control-map-report`
  - In `test_localization_report_require_complete_fails_for_japanese_demo_gap`, make the same updates.
  - Keep `missing: explain-leave` absent.
  - Keep Q&A coverage unchanged at `12/12` questions and `12/12` answers.
  - Keep JA aliases unchanged at `questionAliases.ja present on 3/27 entrypoints (9 aliases)`.

- `tests/unit/test_diagnostics.py`
  - In `test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`, update `32/51 demo steps` -> `33/51 demo steps`.
  - Keep status `FAIL`.
  - Keep detail `required ja localization incomplete`.
  - Keep Q&A detail unchanged: `12/12 Q&A questions` and `12/12 Q&A answers`.

Expected red point before YAML implementation:

- Updated localization count assertions fail because current state is still `32/51`.
- Updated `meeting-control-map-demo` assertion fails because current state is still `3/22`.
- Updated first missing assertion fails because current first missing is still `control-map-views`.
- New focused JA narration test fails because `step.narration.localized_text["ja"]` is missing for `control-map-views`.

Expected green state after this slice:

- Overall JA demo narration: `33/51`
- `meeting-control-map-demo`: `4/22`
- First missing JA step in that flow: `control-map-report`
- Required JA localization: still incomplete/failing
- Q&A JA coverage: still `12/12` questions and `12/12` answers
- JA aliases: still `3/27` entrypoints and `9` aliases

## Suggested Japanese Text

Recommended `localizedText.ja`:

```yaml
        ja: Views は、会議を画面上でどう表示するかを確認する View layout メニューです。Gallery view や Full screen などの見え方を説明できる場所ですが、ここでは音声、ビデオ、共有、参加者の状態には触れません。
```

Why this wording:

- Keeps necessary UI/concept names: `Views`, `View layout`, `Gallery view`, `Full screen`, `会議`, `表示`, `音声`, `ビデオ`, `共有`, `参加者`.
- Matches the source intent: the control concerns on-screen meeting arrangement, not audio/video/membership.
- Avoids saying AiPresenter will switch layouts, select Gallery, enter Full screen, or alter media/sharing/membership state.
- Uses `状態には触れません` to guard against overreach without claiming to perform or undo any state change.

Acceptable shorter variant:

```yaml
        ja: Views は View layout のメニューで、会議の表示方法を確認する入口です。Gallery view や Full screen などの項目を説明できますが、音声、ビデオ、共有、参加者の状態は扱いません。
```

Avoid wording such as:

- `レイアウトを切り替えます`
- `Gallery view を選択します`
- `Full screen にします`
- `音声を変更します`
- `ビデオを変更します`
- `共有を開始します`
- `共有を変更します`
- `参加者を変更します`

## Verification Commands

Use the project virtual environment and keep `PYTHONPATH=src` if the package is not installed editable in the active shell:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests/unit/test_material_packages.py::test_meeting_control_map_has_japanese_views_narration tests/unit/test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests/unit/test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests/unit/test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Optional focused CLI check:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m ai_presenter.cli localization-report --package ringcentral-video --language ja
```

Expected CLI lines after implementation:

```text
Localization report: 33/51 demo steps
- meeting-control-map-demo: 4/22 narration localized
  missing: control-map-report
- localized questions: 12/12
- localized answers: 12/12
questionAliases.ja present on 3/27 entrypoints (9 aliases)
```

Japanese `--require-complete` should still exit nonzero and print `Localization coverage incomplete for ja.`

## Do-not-change Guardrails

- Do not change code, runtime behavior, selectors, locators, route coordinates, YAML flow order, operation names, or test infrastructure for this scan.
- Do not change `control-map-views` action semantics: keep `entrypointId`, `operation`, `placement`, and `actionOffsetMs` exactly as they are.
- Do not change `ringcentral.video.top.views` route semantics: keep `clickWindowRelative`, `Views`, `xFromRight: '237'`, `y: '21'`, and `cleanup: escape`.
- Do not add Japanese aliases for this entrypoint in this round unless the main session explicitly scopes that in; current alias coverage should remain `3/27` and `9`.
- Do not localize `control-map-report` or any later `meeting-control-map-demo` step in this cycle.
- Do not alter Q&A, Chinese/English narration, presenter notes, profiles, diagnostics logic, CLI formatting, or acceptance targets beyond the expected JA coverage count/test expectation changes.
- Do not use wording that says AiPresenter switches layout, selects Gallery view, enters Full screen, changes audio/video, starts or changes sharing, changes membership, invites participants, or otherwise alters meeting state.
- Do not mention or read private meeting values, Meeting IDs, meeting links, account data, participant identifiers, media device names, or sharing content.
- Do not revert or overwrite concurrent edits from other agents. This handoff intentionally writes only `docs/agent-handoffs/cycle-082-technical-scan.md`.
