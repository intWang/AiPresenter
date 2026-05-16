# Cycle 081 Technical Scan: control-map-network JA

Date: 2026-05-16

## Target YAML Snapshot

Target file: `packages/ringcentral-video.yaml`

Current target step:

```yaml
- id: control-map-network
  title: Network quality
  action:
    entrypointId: ringcentral.video.top.network-quality
    operation: open
  narration:
    text: Next is meeting health. Network quality is where you check whether audio, video, or sharing problems
      are coming from packet loss, jitter, or latency.
    localizedText:
      zh: 接着看会议健康状态。网络质量用来判断声音、视频或共享卡顿，是不是来自丢包、抖动或者延迟。
    placement: during
    actionOffsetMs: 350
```

Current gap: `control-map-network` has Chinese localized narration but no `localizedText.ja`.

Action semantics to preserve:

- `entrypointId`: `ringcentral.video.top.network-quality`
- `operation`: `open`
- `placement`: `during`
- `actionOffsetMs`: `350`

Because this is an executable open step, the Japanese copy can say `Network quality` is being checked as a meeting-health entry point, but it should avoid claiming an exact diagnosis, repair, settings change, or precise metric readout.

## Entrypoint Route

Entrypoint: `ringcentral.video.top.network-quality`

```yaml
- id: ringcentral.video.top.network-quality
  title: Network quality
  area: Meeting top bar
  purpose: Show diagnostic network quality for sharing, video, and audio, including packet loss, jitter, and latency.
  questionAliases:
    zh:
    - 网络质量
    - 连接质量
    - 卡顿
  openSteps:
  - action: clickWindowRelative
    target: Network quality
    match:
      x: '68'
      y: '21'
      cleanup: escape
```

Route details:

- Area: `Meeting top bar`
- Route action: `clickWindowRelative`
- Target: `Network quality`
- Coordinate match: `x: '68'`, `y: '21'`
- Cleanup: `escape`
- Presenter notes say this is behind the signal-bars icon at the top left, useful for call health or troubleshooting audio/video quality, and should be closed with Escape before clicking another control.

Do not change the entrypoint route, open steps, cleanup, aliases, or presenter notes in this round.

## Test Updates

Recommended red-first updates:

- `tests/unit/test_material_packages.py`
  - In `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`, update overall JA demo coverage from `31` to `32`.
  - Update `meeting-control-map-demo` localized steps from `2` to `3`.
  - Update first missing step from `control-map-network` to `control-map-views`.
  - Add a focused guard test for `meeting-control-map-demo` -> `control-map-network`, parallel to the existing `control-map-meeting-info` JA test.
  - The focused test should assert:
    - `step.action.entrypoint_id == "ringcentral.video.top.network-quality"`
    - `step.action.operation == "open"`
    - `step.narration.placement == "during"`
    - `step.narration.action_offset_ms == 350`
    - entrypoint route uses `clickWindowRelative`, target `Network quality`, `x == "68"`, `y == "21"`, and `cleanup == "escape"`
    - JA text exists, contains CJK, and includes required UI/concept terms such as `Network quality`, `会議`, `健全性`, `音声`, `ビデオ`, `共有`, `パケットロス`, `ジッター`, `遅延`
    - JA text includes a guard against overdiagnosis, for example `原因を決めつけません` or `正確な原因を推測しません`
    - JA text excludes over-action or over-promise wording such as `修復します`, `直します`, `改善します`, `設定を変更します`, `切り替えます`, `正確な原因です`, `問題を解決します`, `必ず`, `保証します`

- `tests/unit/test_cli.py`
  - In `test_localization_report_outputs_japanese_demo_and_qa_coverage`, update:
    - `Localization report: 31/51 demo steps` -> `Localization report: 32/51 demo steps`
    - `- meeting-control-map-demo: 2/22 narration localized` -> `- meeting-control-map-demo: 3/22 narration localized`
    - `missing: control-map-network` -> `missing: control-map-views`
  - In `test_localization_report_require_complete_fails_for_japanese_demo_gap`, make the same updates.
  - Keep `missing: explain-leave` absent.
  - Keep Q&A coverage unchanged at `12/12` questions and `12/12` answers.
  - Keep JA aliases unchanged at `questionAliases.ja present on 3/27 entrypoints (9 aliases)`.

- `tests/unit/test_diagnostics.py`
  - In `test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`, update `31/51 demo steps` -> `32/51 demo steps`.
  - Keep status `FAIL`.
  - Keep detail `required ja localization incomplete`.
  - Keep Q&A detail unchanged: `12/12 Q&A questions` and `12/12 Q&A answers`.

Expected red point before YAML implementation:

- Updated localization count assertions fail because current state is still `31/51`.
- Updated `meeting-control-map-demo` assertion fails because current state is still `2/22`.
- Updated first missing assertion fails because current first missing is still `control-map-network`.
- New focused JA narration test fails because `step.narration.localized_text["ja"]` is missing for `control-map-network`.

Expected green state after this slice:

- Overall JA demo narration: `32/51`
- `meeting-control-map-demo`: `3/22`
- First missing JA step in that flow: `control-map-views`
- Required JA localization: still incomplete/failing
- Q&A JA coverage: still `12/12` questions and `12/12` answers
- JA aliases: still `3/27` entrypoints and `9` aliases

## Suggested Japanese Text

Recommended `localizedText.ja`:

```yaml
        ja: 次は会議の健全性です。Network quality では、音声、ビデオ、共有の不安定さがパケットロス、ジッター、遅延と関係しているかを確認できます。観測値がないまま原因を決めつけたり、修復を約束したりしません。
```

Why this wording:

- Keeps necessary UI/concept names: `Network quality`, `会議の健全性`, `音声`, `ビデオ`, `共有`, `パケットロス`, `ジッター`, `遅延`.
- Matches the English source: meeting health and whether audio/video/sharing problems relate to packet loss, jitter, or latency.
- Stays diagnostic-light: it says the panel can be used to check relationships, not that AiPresenter knows the exact cause.
- Explicitly avoids repair promises and avoids changing meeting or device settings.

Acceptable shorter variant:

```yaml
        ja: 次は Network quality です。会議の健全性を確認する入口で、音声、ビデオ、共有の問題がパケットロス、ジッター、遅延と関係しているかを見る場所です。観測値がないまま正確な原因を推測しません。
```

Avoid wording that says AiPresenter fixes the network, improves quality, changes settings, guarantees a result, or reads exact metric values by default.

## Verification Commands

Use the project virtual environment and keep `PYTHONPATH=src` if the package is not installed editable in the active shell:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests/unit/test_material_packages.py::test_meeting_control_map_has_japanese_network_narration tests/unit/test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests/unit/test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests/unit/test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Optional focused CLI check:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m ai_presenter.cli localization-report --package ringcentral-video --language ja
```

Expected CLI lines after implementation:

```text
Localization report: 32/51 demo steps
- meeting-control-map-demo: 3/22 narration localized
  missing: control-map-views
- localized questions: 12/12
- localized answers: 12/12
questionAliases.ja present on 3/27 entrypoints (9 aliases)
```

Japanese `--require-complete` should still exit nonzero and print `Localization coverage incomplete for ja.`

## Do-not-change Guardrails

- Do not change code, runtime behavior, selectors, locators, route coordinates, YAML flow order, operation names, or test infrastructure for this slice.
- Do not change `control-map-network` action semantics: keep `entrypointId`, `operation`, `placement`, and `actionOffsetMs` exactly as they are.
- Do not change `ringcentral.video.top.network-quality` route semantics: keep `clickWindowRelative`, `Network quality`, `x: '68'`, `y: '21'`, and `cleanup: escape`.
- Do not add Japanese aliases for this entrypoint in this round unless the main session explicitly scopes that in; current alias coverage should remain `3/27` and `9`.
- Do not localize `control-map-views` or any later `meeting-control-map-demo` step in this cycle.
- Do not alter Q&A, Chinese/English narration, presenter notes, profiles, diagnostics logic, CLI formatting, or acceptance targets beyond the expected JA coverage count/test expectation changes.
- Do not read or include exact live diagnostic values such as packet-loss percentages, jitter milliseconds, latency milliseconds, participant/network identifiers, host names, account data, meeting links, or Meeting IDs.
- Do not use wording that says AiPresenter fixes the network, repairs audio/video/sharing, guarantees quality, changes settings, switches devices, starts/stops media, reports an issue, or performs an escalation action.
- Do not revert or overwrite concurrent edits from other agents. Current unrelated dirty state observed during this scan: `.coverage`.
