# Cycle 094 Implementation Handoff

## Scope

- Localized `meeting-control-map-demo` step `control-map-more` for Japanese.
- Preserved the existing `ringcentral.video.toolbar.more` route as an `open` operation with `placement: during` and `actionOffsetMs: 350`.
- Updated the RingCentral Video source index to record Japanese control-map coverage through `more`.

## Test-Driven Evidence

- Red test command:
  `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_raise_hand_narration tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_more_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`
- Red result: five expected failures while Japanese coverage remained `44/51`, `meeting-control-map-demo` remained `15/22`, and first missing remained `control-map-more`.
- Green result after implementation and adjacent assertion update: same focused command passed with `6 passed`.

## Behavioral Notes

- Japanese demo coverage now advances to `45/51`.
- `meeting-control-map-demo` advances to `16/22`.
- The first missing Japanese control-map step moves to `control-map-recording`.
- `questionAliases.ja` remains unchanged at `3/27` entrypoints and `9` aliases.
- The Japanese narration treats More as an overflow or expansion menu for lower-frequency and more careful actions.
- It names `Start recording`, `Background`, `Settings`, and the current layout note that `Notes` is already on the toolbar, but does not click secondary actions or imply recording/background/settings/exit changes.
- The menu cleanup boundary remains `cleanup: escape`.

## Next Candidate

- Continue with `control-map-recording`, with explicit recording-consent, meeting-state, host-permission, and no-start-recording boundaries.
