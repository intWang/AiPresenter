# Cycle 063 Implementation

## Scope

Added Japanese narration for the single `meeting-controls-tour` step `explain-invite`.

## Changes

- Added `localizedText.ja` for `explain-invite` in `packages/ringcentral-video.yaml`.
- Kept the step action, entrypoint, placement, offset, Chinese narration, aliases, Q&A, and runtime behavior unchanged.
- Updated Japanese demo coverage expectations from `13/51` to `14/51`.
- Updated `meeting-controls-tour` Japanese coverage from `6/22` to `7/22`.
- Updated the first missing Japanese step from `explain-invite` to `explain-participants`.
- Updated the RingCentral Video source index to record the first seven overview/top-bar/report/invite steps as localized.

## TDD Evidence

Red run before YAML changes:

`.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_controls_tour_has_japanese_invite_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`

Result: `5 failed`, with Japanese coverage still at `13/51` and no `localizedText.ja` on `explain-invite`.

Green run after YAML changes:

Same command: `5 passed`.

## Safety Notes

- The Japanese text identifies toolbar Invite as the active-meeting entrypoint, not the empty-room Add coworkers callout.
- It says Invite opens the same dialog as Add coworkers but keeps the state context as `進行中の会議`.
- It mentions meeting information and invite preparation without saying the presenter sends an invite.
- It explicitly avoids reading names, email addresses, suggestions, or private invite links unless the user explicitly asks and visible content is verified.
- It says the blocking dialog is closed after the explanation.
- It avoids the word `送信` to reduce accidental-invitation implication.

## Next Candidates

- `explain-participants` should get its own risk review because roster panels can expose participant names, roles, counts, and attendee controls.
- Chat, Share, Notes, Recording, and Leave should remain separate privacy/state slices.
