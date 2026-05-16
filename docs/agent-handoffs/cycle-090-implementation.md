# Cycle 090 Implementation Handoff

## Scope

- Localized `meeting-control-map-demo` step `control-map-camera-menu` for Japanese.
- Preserved the existing `ringcentral.video.toolbar.video-menu` route as an `open` operation with `placement: during` and `actionOffsetMs: 350`.
- Updated the RingCentral Video source index to record Japanese control-map coverage through `camera-menu`.

## Test-Driven Evidence

- Red test command:
  `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_camera_menu_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`
- Red result: five expected failures while Japanese coverage remained `40/51`, `meeting-control-map-demo` remained `11/22`, and first missing remained `control-map-camera-menu`.
- Green result after implementation: same focused command passed with `5 passed`.

## Behavioral Notes

- Japanese demo coverage now advances to `41/51`.
- `meeting-control-map-demo` advances to `12/22`.
- The first missing Japanese control-map step moves to `control-map-share`.
- `questionAliases.ja` remains unchanged at `3/27` entrypoints and `9` aliases.
- The Japanese narration presents the camera menu as an orientation route for camera candidates and `More video settings`, while explicitly avoiding camera/background/video setting changes unless the user asks.
- The menu cleanup boundary remains `cleanup: escape`.

## Next Candidate

- Continue with `control-map-share`, keeping screen-share privacy, source selection, and accidental disclosure risks separate from camera-menu behavior.
