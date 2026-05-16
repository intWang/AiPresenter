# Cycle 084 Implementation: control-map-add-coworkers JA

Date: 2026-05-16

## Scope

Added Japanese narration for `meeting-control-map-demo` step `control-map-add-coworkers`.

This cycle intentionally kept the slice narrow:

- no locator changes
- no route or cleanup changes
- no adaptive empty-room logic changes
- no Q&A changes
- no alias changes
- no neighboring control-map step localization

## TDD Evidence

Red command:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_add_coworkers_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Red result: `5 failed`.

Expected failures:

- JA demo coverage remained `34/51` instead of expected `35/51`.
- `meeting-control-map-demo` remained `5/22` instead of expected `6/22`.
- `control-map-add-coworkers` had no `localizedText.ja`.
- CLI and diagnostics still reported `34/51`.

Green command:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_add_coworkers_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Green result: `5 passed`.

## Behavior Preserved

The focused guard test preserves the Add coworkers route:

- `entrypointId: ringcentral.video.main.add-coworkers`
- `operation: open`
- `placement: during`
- `actionOffsetMs: 350`
- `clickWindowControl`
- target `Add coworkers`
- `controlType: button`
- `cleanup: modal`

It also verifies the presenter notes still describe the name/email field, suggestions, Copy meeting link, Cancel, Invite, empty-room applicability, and the requirement to close with dialog X or Cancel before touching other controls.

## Localization Result

Expected Japanese coverage after this slice:

- overall demo coverage: `35/51`
- `meeting-control-map-demo`: `6/22`
- first remaining missing control-map step: `control-map-participants`
- Q&A coverage unchanged: `12/12` questions and `12/12` answers
- alias coverage unchanged: `3/27` entrypoints and `9` aliases
- `--require-complete` for Japanese still fails because later control-map steps remain untranslated

## Copy Boundary

The Japanese text describes `Add coworkers` as the empty-room entry point for the Invite dialog. It explains that name/email search, suggestions, meeting links, and Invite controls may be present, but names, email addresses, suggestions, and private meeting links are not read until the user explicitly asks and visible content is confirmed.

The copy avoids saying AiPresenter sends invites, selects contacts, types into search, copies links, reads private links, changes membership, or proceeds with the blocking dialog left open.
