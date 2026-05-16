# Cycle 099 Technical Scan: Control Map Leave JA

Scope for the next implementation slice: add Japanese narration only to `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-leave`.

This scan intentionally writes only this handoff file. Do not modify YAML, code, tests, source-index docs, profiles, fixtures, coverage files, or git history during this scan. Other agents may be working in parallel; preserve unrelated local edits and do not revert their files.

## Baseline Confirmed

Command run during scan:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Current package output:

- Overall Japanese demo narration: `49/51`
- `meeting-control-map-demo`: `20/22`
- First missing Japanese step: `control-map-leave`
- Remaining missing control-map steps: `control-map-leave`, `control-map-summary`
- Japanese Q&A remains complete: `12/12` localized questions and `12/12` localized answers
- `questionAliases.ja` remains `3/27` entrypoints and `9` aliases

Working-tree note: `.coverage` was already modified before this scan. Leave it alone unless a later implementation assignment explicitly owns coverage artifacts.

## Target Package Change

Current target step:

```yaml
  - id: control-map-leave
    title: Leave meeting
    action:
      entrypointId: ringcentral.video.toolbar.leave
      operation: explain
    narration:
      text: Leave is the exit path. It can end your presence in the meeting, so I describe it but do not click it
        without explicit confirmation.
      localizedText:
        zh: Leave 是离开会议的入口。它会结束你在当前会议里的状态，所以我只说明作用，不会在没有确认时替你点击。
      placement: before
```

Add only `localizedText.ja` under this step. Preserve the English text, Chinese text, step order, `entrypointId`, `operation: explain`, and `placement: before`. Do not add `actionOffsetMs`; this is an explain-only step with no executable route.

Suggested Japanese text:

```yaml
        ja: Leave は現在の会議から退出するための出口です。自分の会議参加状態を終了させる破壊的なコントロールで、ホストの場合は全員に影響する終了系の選択肢につながることもあります。このコントロールマップでは場所と意味を説明するだけで、ユーザーが明確に求め、退出または終了の影響を確認するまで Leave はクリックしません。会議を離れたり終了したりせず、必要な場合も実行前に口頭で確認します。
```

## Expected Coverage After Implementation

After adding only `localizedText.ja` to `control-map-leave`:

- Overall Japanese demo narration: `49/51` -> `50/51`
- `meeting-control-map-demo`: `20/22` -> `21/22`
- First missing Japanese step: `control-map-leave` -> `control-map-summary`
- Remaining missing control-map steps should be `control-map-summary`
- Japanese Q&A should remain `12/12` questions and `12/12` answers
- `questionAliases.ja` should remain `3/27` entrypoints and `9` aliases
- `--require-complete` for Japanese should still fail because `control-map-summary` remains untranslated

## Focused Tests To Update/Add

`tests/unit/test_material_packages.py`:

- Update `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`:
  - `report.demo_localized_steps`: `49` -> `50`
  - `meeting-control-map-demo.localized_steps`: `20` -> `21`
  - first missing step: `control-map-leave` -> `control-map-summary`
  - keep total demo steps `51`, control-map total `22`, Q&A counts, alias counts, and `required_localization_complete is False`
- Add `test_meeting_control_map_has_japanese_leave_narration` near the existing control-map Japanese narration tests, after the settings test.
- Update adjacent focused tests that assert the first missing control-map step, especially camera-menu/share/reactions/raise-hand/more/recording/notes/background/settings tests, so they expect `control-map-summary`.
- In the settings focused test, change the leave adjacency assertion from `"ja" not in leave_step.narration.localized_text` to `"ja" in leave_step.narration.localized_text`.
- Keep the existing `meeting-controls-tour` `explain-leave` Japanese test unchanged; this slice targets only `meeting-control-map-demo`.

`tests/unit/test_cli.py`:

- Update both Japanese localization-report tests:
  - `Localization report: 49/51 demo steps` -> `Localization report: 50/51 demo steps`
  - `- meeting-control-map-demo: 20/22 narration localized` -> `- meeting-control-map-demo: 21/22 narration localized`
  - `missing: control-map-leave` -> `missing: control-map-summary`
  - keep `missing: explain-leave` negative assertion unchanged
  - keep Q&A counts and `questionAliases.ja present on 3/27 entrypoints (9 aliases)` unchanged
- Keep `test_localization_report_require_complete_fails_for_japanese_demo_gap` exit code `1`.

`tests/unit/test_diagnostics.py`:

- Update `test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`:
  - `49/51 demo steps` -> `50/51 demo steps`
  - keep status `FAIL`, detail `required ja localization incomplete`, and Q&A detail assertions unchanged

`tests/unit/test_package_demo.py`:

- No new executor behavior should be needed. Existing coverage already verifies that `operation="explain"` on `ringcentral.video.toolbar.leave` produces no driver actions.
- Add or update package-demo coverage only if route behavior changes, which this slice should avoid.

## Route And Action Assertions For Leave

The focused control-map leave test should lock the explain-only route and destructive-action boundary:

```python
assert step.action.entrypoint_id == "ringcentral.video.toolbar.leave"
assert step.action.operation == "explain"
assert step.narration.placement == "before"
leave_entrypoint = package.entrypoint_by_id("ringcentral.video.toolbar.leave")
assert leave_entrypoint.open_steps == []
assert "ja" not in leave_entrypoint.question_aliases
assert report.entrypoints_with_aliases == 3
assert report.alias_total == 9
assert report.flow_by_id["meeting-control-map-demo"].missing_step_ids[0] == (
    "control-map-summary"
)
```

Also assert:

- `leave_entrypoint.title == "Leave meeting"`
- `leave_entrypoint.area == "Meeting toolbar"`
- `leave_entrypoint.purpose == "Leave or end the meeting."`
- presenter notes include destructive-tour treatment, the risk that clicking Leave can immediately show a left-meeting state, explicit user request before ending, and verbal confirmation before leave/end actions
- previous step `control-map-settings` remains localized and uses `ringcentral.video.more.settings`
- next step `control-map-summary` remains without Japanese narration and becomes the first missing step

Suggested positive Japanese text assertions:

- contains `Leave`, `会議`, `退出`, `出口`, `破壊的`, `コントロール`, `ホスト`, `全員`, `説明するだけ`, `ユーザー`, `明確`, `確認`
- contains a phrase that means AiPresenter does not click Leave, leave the meeting, or end the meeting during the tour
- contains a phrase that requires verbal confirmation before any future leave/end action

Suggested negative assertions:

- does not contain `クリックします`, `押します`, `選択します`, `退出します`, `終了します`, `会議を終了`, `Leave を押します`, `Leave をクリック`, `自動`

## Safe Implementation Constraints

Keep this as a narrow localization slice:

- Do not add Japanese `questionAliases` for Leave.
- Do not change `operationEntrypoints`, `openSteps`, presenter notes, Q&A, controller safety, acceptance drafts, profiles, runtime logic, or validation target metadata.
- Do not localize `control-map-summary`.
- Do not change English or Chinese narration.
- Do not turn Leave into an executable route or add a locator.
- Do not click Leave in tests, demos, acceptance, or implementation verification.
- Do not imply AiPresenter leaves, ends, closes, or disconnects the meeting automatically.
- Do not imply host/end-meeting behavior is always present; phrase it as possible when host or role state allows it.
- Keep the narration explain-only and require explicit user request plus confirmation before any future leave/end action.
- Preserve `operation: explain` and `placement: before`; no `during` placement and no `actionOffsetMs` are needed for this step.

## Source Index Update If Needed

Current `docs/knowledge/ringcentral-video/source-index.md` says Japanese coverage is complete through the `.../more/recording/notes/background/settings` steps of `meeting-control-map-demo`.

If the implementation assignment includes source-index maintenance, update only that localization coverage sentence so it advances from `.../recording/notes/background/settings` to `.../recording/notes/background/settings/leave`. Keep `control-map-summary` and other entrypoint aliases marked as future work. Do not imply full `meeting-control-map-demo` Japanese coverage until all 22 steps are localized.

## Verification Commands

Focused pytest after implementation:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_settings_narration tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_leave_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Expected localization report after implementation:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Expected key lines:

```text
- meeting-control-map-demo: 21/22 narration localized
  missing: control-map-summary
Localization report: 50/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
questionAliases.ja present on 3/27 entrypoints (9 aliases)
```

Japanese required-complete should still fail:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
```

Expected: exit code `1`, with `Localization coverage incomplete for ja.`

Diff hygiene:

```powershell
git diff -- packages/ringcentral-video.yaml tests/unit/test_material_packages.py tests/unit/test_cli.py tests/unit/test_diagnostics.py docs/knowledge/ringcentral-video/source-index.md
git diff --check -- packages/ringcentral-video.yaml tests/unit/test_material_packages.py tests/unit/test_cli.py tests/unit/test_diagnostics.py docs/knowledge/ringcentral-video/source-index.md
```

Implementation diff should be limited to one `localizedText.ja` block for `control-map-leave`, directly necessary test expectation updates, the focused leave narration test, and the source-index coverage sentence if included by the implementation assignment.
