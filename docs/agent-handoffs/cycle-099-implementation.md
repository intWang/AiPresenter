# Cycle 099 Implementation Handoff

## Scope

Cycle 099 localizes only `meeting-control-map-demo` -> `control-map-leave` for Japanese.

Implemented files:

- `packages/ringcentral-video.yaml`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_diagnostics.py`
- `docs/knowledge/ringcentral-video/source-index.md`

## Behavior Added

`control-map-leave` now has `narration.localizedText.ja`.

The Japanese narration keeps `Leave` as an explain-only destructive meeting lifecycle control:

- explains that `Leave` is the exit path from the current meeting
- states that executing it ends the user's meeting participation state
- notes that host-context end options may affect everyone
- says the control-map step explains only the location and role
- says AiPresenter does not click `Leave` or confirm leaving/ending until the user explicitly asks and the visible option plus impact are orally confirmed

Preserved boundaries:

- `action.entrypointId` remains `ringcentral.video.toolbar.leave`
- `action.operation` remains `explain`
- `narration.placement` remains `before`
- no `actionOffsetMs` was added
- `ringcentral.video.toolbar.leave.openSteps` remains empty
- no Japanese `questionAliases` were added
- `control-map-summary` remains untranslated for the next cycle

## Tests

TDD red command before implementation:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_settings_narration tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_leave_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Expected red result:

- 6 failed
- coverage still `49/51`
- `meeting-control-map-demo` still `20/22`
- first missing step still `control-map-leave`

Focused green command after implementation:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_settings_narration tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_leave_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Focused green result:

- 6 passed

## Expected Report State

After this implementation:

```text
Localization report: 50/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
- meeting-control-map-demo: 21/22 narration localized
  missing: control-map-summary
questionAliases.ja present on 3/27 entrypoints (9 aliases)
```

Japanese `--require-complete` should still fail with exit code `1` because `control-map-summary` is intentionally left untranslated.

## Review Notes

Review should focus on:

- whether the Japanese wording avoids implying AiPresenter will leave or end the meeting
- whether host/end-meeting impact is conditional rather than assumed
- whether the package change is limited to one new `localizedText.ja` block
- whether test expectation updates advance exactly one step
- whether `.coverage` remains unstaged
