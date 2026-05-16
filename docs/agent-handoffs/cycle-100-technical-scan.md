# Cycle 100 Technical Scan: Control Map Summary JA

Scope for the next implementation slice: add Japanese narration only to `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-summary`.

This scan intentionally writes only this handoff file. Do not modify YAML, code, tests, source-index docs, profiles, fixtures, coverage files, or git history during this scan. Other agents may be working in parallel; preserve unrelated local edits and do not revert their files. `.coverage` was already dirty during this scan and should be ignored.

## Baseline Confirmed

Command run during scan:

```powershell
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja
```

Current package output:

- Overall Japanese demo narration: `50/51`
- `meeting-control-map-demo`: `21/22`
- Missing Japanese step: `control-map-summary`
- Japanese Q&A remains complete: `12/12` localized questions and `12/12` localized answers
- `questionAliases.ja` remains `3/27` entrypoints and `9` aliases

Expected key lines from the confirmed baseline:

```text
- meeting-control-map-demo: 21/22 narration localized
  missing: control-map-summary
Localization report: 50/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
```

## Target YAML Node

Target file: `packages/ringcentral-video.yaml`.

Target structure:

```yaml
- id: meeting-control-map-demo
  title: Meeting Control Map
  goal: >-
    Teach RingCentral Video meeting controls as a coherent map: status, people, media, interaction,
    advanced tools, and closeout.
  steps:
  ...
  - id: control-map-leave
    title: Leave meeting
    action:
      entrypointId: ringcentral.video.toolbar.leave
      operation: explain
    narration:
      localizedText:
        ja: ...
        zh: ...
      placement: before
  - id: control-map-summary
    title: Control map summary
    action:
      entrypointId: ringcentral.video.overview
      operation: explain
    narration:
      text: >-
        That is the control map: top bar for status and troubleshooting, people controls for collaboration,
        media controls for readiness, interaction controls for feedback, and More for deeper settings and riskier
        actions.
      localizedText:
        zh: 这就是会议控制地图：上方看状态和排障，成员区负责协作，音视频区负责准备，共享和互动区负责表达，More 里放更深层或更谨慎的操作。
      placement: before
explainers:
```

Expected package change:

- Add only `narration.localizedText.ja` to `meeting-control-map-demo` -> `control-map-summary`.
- Preserve `entrypointId: ringcentral.video.overview`, `operation: explain`, `placement: before`, English text, Chinese text, step order, and all surrounding structure.
- Do not add `actionOffsetMs`; this is an explain-only summary step.
- Do not add or change `questionAliases`, `operationEntrypoints`, routes, locators, cleanup, Q&A, presenter notes, or runtime logic.

Suggested Japanese text:

```yaml
        ja: これが会議コントロールマップです。上部バーは状態確認とトラブルシューティング、参加者まわりは共同作業、音声とビデオは準備状況、共有とリアクションは発信やフィードバック、More はより深い設定や慎重に扱う操作、Leave は退出の境界です。深い設定変更やリスクのある操作は、ユーザーが明確に依頼し、画面上の選択肢と影響を確認できるまで実行しません。
```

Intent of the wording:

- Summarize each control-map area: top/status, people/collaboration, media/readiness, sharing/reactions/feedback, More/deeper settings, Leave/closeout.
- Explicitly keep deeper or riskier actions gated on an explicit user request plus visible confirmation of choices and impact.
- Avoid implying AiPresenter clicks, changes settings, records, shares, leaves, ends, or otherwise executes risky actions automatically.

## Expected Coverage After Implementation

After adding only `localizedText.ja` to `control-map-summary`:

- Overall Japanese demo narration: `50/51` -> `51/51`
- `meeting-control-map-demo`: `21/22` -> `22/22`
- `meeting-control-map-demo.missing_step_ids`: `("control-map-summary",)` -> `()`
- `required_localization_complete`: `False` -> `True`
- Japanese Q&A remains `12/12` questions and `12/12` answers
- `questionAliases.ja` remains `3/27` entrypoints and `9` aliases
- Japanese `--require-complete` should pass with exit code `0`

## Tests To Update

`tests/unit/test_material_packages.py`:

- Update `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`:
  - `report.demo_localized_steps`: `50` -> `51`
  - `report.required_localization_complete`: `False` -> `True`
  - `meeting-control-map-demo.localized_steps`: `21` -> `22`
  - replace the `missing_step_ids[0] == "control-map-summary"` assertion with `missing_step_ids == ()`
  - keep total demo steps `51`, control-map total `22`, Q&A counts, entrypoint count, and alias count unchanged.
- Update focused control-map JA narration tests that currently assert `missing_step_ids[0] == "control-map-summary"` or `missing_step_ids == ("control-map-summary",)` so they assert no missing steps, or remove the repeated missing-step assertion from tests whose purpose is not coverage completeness.
- Update `test_meeting_control_map_has_japanese_leave_narration`:
  - change `assert "ja" not in summary_step.narration.localized_text` to `assert "ja" in summary_step.narration.localized_text`
  - change the missing-step assertion to `()`.
- Add `test_meeting_control_map_has_japanese_summary_narration` near the existing control-map Japanese narration tests, after the leave test.
- In the new summary test, assert `entrypointId == "ringcentral.video.overview"`, `operation == "explain"`, `placement == "before"`, `action_offset_ms == 0`, Japanese text is non-empty and CJK, the previous leave step remains localized, and alias counts remain `3/27` entrypoints with `9` aliases.
- Positive text assertions should cover `コントロールマップ`, `上部バー`, `状態確認`, `トラブルシューティング`, `参加者`, `共同作業`, `音声`, `ビデオ`, `共有`, `リアクション`, `More`, `深い設定`, `慎重`, `Leave`, `退出`, `明確に依頼`, `画面上の選択肢と影響`, and `実行しません`.
- Negative text assertions should reject phrasing such as `クリックします`, `押します`, `選択します`, `変更します`, `録画します`, `共有します`, `退出します`, `終了します`, `実行します`, `自動`, and any wording that makes risky actions sound automatic or already confirmed.

`tests/unit/test_cli.py`:

- Update `test_localization_report_outputs_japanese_demo_and_qa_coverage`:
  - `Localization report: 50/51 demo steps` -> `Localization report: 51/51 demo steps`
  - `- meeting-control-map-demo: 21/22 narration localized` -> `- meeting-control-map-demo: 22/22 narration localized`
  - remove or invert `missing: control-map-summary`; it should not appear after implementation.
  - keep Q&A counts and `questionAliases.ja present on 3/27 entrypoints (9 aliases)` unchanged.
- Rename/update `test_localization_report_require_complete_fails_for_japanese_demo_gap` so Japanese `--require-complete` now passes:
  - expected exit code `1` -> `0`
  - expected `50/51` -> `51/51`
  - expected `21/22` -> `22/22`
  - assert `Localization coverage incomplete for ja.` is not present.

`tests/unit/test_diagnostics.py`:

- Update `test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing` so Japanese required localization is now complete:
  - rename to a pass-oriented name such as `test_diagnostics_require_localization_passes_for_ringcentral_japanese`
  - `localization_check.status`: `FAIL` -> `OK`
  - detail: `required ja localization incomplete` -> `required ja localization complete`
  - `50/51 demo steps` -> `51/51 demo steps`
  - keep `12/12 Q&A questions` and `12/12 Q&A answers` unchanged.

Japanese require-complete/pass scan result:

- Existing CLI test that must flip from fail to pass: `tests/unit/test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap`.
- Existing diagnostics test with the same completeness transition: `tests/unit/test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`.
- No separate Japanese doctor `--require-localization` CLI pass test was found; current doctor localization pass tests cover Chinese/default Chinese only.

## Source Index Update

Current source-index sentence:

```text
Japanese coverage is complete for ... the overview/meeting-information/network-quality/view-layout/report-issue/add-coworkers/participants/chat/microphone/audio-menu/camera/camera-menu/share/reactions/raise-hand/more/recording/notes/background/settings/leave steps of `meeting-control-map-demo`; `questionAliases.ja` now covers the microphone, Participants, and Chat basics, while the remaining control-map narration and other entrypoint aliases remain future work.
```

After implementation, update only this localization coverage sentence in `docs/knowledge/ringcentral-video/source-index.md`.

Preferred wording:

```text
Japanese coverage is complete for the existing Q&A safety set, the four-step virtual background blur demo, the three-step meeting basics demo, all twenty-two steps of `meeting-controls-tour`, and all twenty-two steps of `meeting-control-map-demo`; `questionAliases.ja` still covers the microphone, Participants, and Chat basics, while other entrypoint aliases remain future work.
```

Acceptable explicit-list variant: advance the list from `.../settings/leave` to `.../settings/leave/summary`.

Do not mistype or broaden aliases:

- Keep `questionAliases.ja` at `3/27` entrypoints and `9` aliases.
- Do not add Japanese aliases for overview, More, Leave, Summary, or any other entrypoint in this slice.
- Do not leave wording that says “remaining control-map narration” after `control-map-summary` is localized.

## Verification Commands

Focused tests after implementation:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_leave_narration tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_summary_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_passes_for_japanese tests\unit\test_diagnostics.py::test_diagnostics_require_localization_passes_for_ringcentral_japanese
```

Full relevant unit test files:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_cli.py tests\unit\test_diagnostics.py
```

Expected localization report:

```powershell
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja
```

Expected key lines:

```text
- meeting-control-map-demo: 22/22 narration localized
Localization report: 51/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
questionAliases.ja present on 3/27 entrypoints (9 aliases)
```

Japanese required-complete should pass:

```powershell
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja --require-complete
```

Expected: exit code `0`, no `Localization coverage incomplete for ja.` line.

Diff hygiene:

```powershell
git diff -- packages/ringcentral-video.yaml tests/unit/test_material_packages.py tests/unit/test_cli.py tests/unit/test_diagnostics.py docs/knowledge/ringcentral-video/source-index.md
git diff --check -- packages/ringcentral-video.yaml tests/unit/test_material_packages.py tests/unit/test_cli.py tests/unit/test_diagnostics.py docs/knowledge/ringcentral-video/source-index.md
```

Implementation diff should be limited to one `localizedText.ja` block for `control-map-summary`, directly necessary test expectation updates or the focused summary narration test, and the source-index coverage sentence if included by the implementation assignment.
