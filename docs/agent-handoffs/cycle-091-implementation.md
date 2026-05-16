# Cycle 091 Implementation Handoff

## Scope

- Localized `meeting-control-map-demo` step `control-map-share` for Japanese.
- Preserved the existing `ringcentral.video.toolbar.share` route as an `open` operation with `placement: during` and `actionOffsetMs: 400`.
- Updated the RingCentral Video source index to record Japanese control-map coverage through `share`.

## Test-Driven Evidence

- Red test command:
  `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_share_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`
- Red result: five expected failures while Japanese coverage remained `41/51`, `meeting-control-map-demo` remained `12/22`, and first missing remained `control-map-share`.
- Green result after implementation: same focused command passed with `5 passed`.

## Behavioral Notes

- Japanese demo coverage now advances to `42/51`.
- `meeting-control-map-demo` advances to `13/22`.
- The first missing Japanese control-map step moves to `control-map-reactions`.
- `questionAliases.ja` remains unchanged at `3/27` entrypoints and `9` aliases.
- The Japanese narration presents Share as the picker for screen/application-window sharing and `Share system audio` as a distinct option.
- It explicitly avoids reading candidate names or screen content, selecting a source, pressing the final `Share` button, or starting sharing until the user confirms what should be shown.
- The picker cleanup boundary remains `cleanup: escape`.

## Next Candidate

- Continue with `control-map-reactions`, keeping emoji/reaction sending and meeting signal visibility as the next scoped risk surface.
