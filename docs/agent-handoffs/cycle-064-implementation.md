# Cycle 064 Implementation

## Scope

Added Japanese narration for the single `meeting-controls-tour` step `explain-participants`.

## Changes

- Added `localizedText.ja` for `explain-participants` in `packages/ringcentral-video.yaml`.
- Kept the step action, entrypoint, placement, offset, Chinese narration, aliases, Q&A, and runtime behavior unchanged.
- Updated Japanese demo coverage expectations from `14/51` to `15/51`.
- Updated `meeting-controls-tour` Japanese coverage from `7/22` to `8/22`.
- Updated the first missing Japanese step from `explain-participants` to `explain-chat`.
- Updated the RingCentral Video source index to record the first eight overview/top-bar/report/invite/participants steps as localized.

## TDD Evidence

Red run before YAML changes:

`.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_controls_tour_has_japanese_participants_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`

Result: `5 failed`, with Japanese coverage still at `14/51` and no `localizedText.ja` on `explain-participants`.

Green run after YAML changes:

Same command: first run was `1 failed, 4 passed` because the cleanup wording used `閉じ` instead of the explicit `閉じます`; after tightening the narration, the same command returned `5 passed`.

## Safety Notes

- The Japanese text identifies Participants as the roster panel.
- It mentions visible attendee count and people-control areas without reading identities.
- It explicitly avoids reading participant names or roles unless the user explicitly asks and visible content is verified.
- It says the side panel is closed after explanation.
- It says other participants are not muted without clear user instruction.
- It does not change Participants aliases, Q&A, side-panel cleanup, locators, or host-control behavior.

## Next Candidates

- `explain-chat` should get its own risk review because it can expose public/private messages and tabs.
- Microphone and camera controls should remain separate live-state slices.
