# Cycle 058 Implementation

## Scope

Added package-owned Japanese `questionAliases.ja` for the three RingCentral Video meeting-basics entrypoints:

- `ringcentral.video.toolbar.audio`
- `ringcentral.video.toolbar.participants`
- `ringcentral.video.toolbar.chat`

## Changes

- Added three Japanese aliases per entrypoint in `packages/ringcentral-video.yaml`.
- Updated Japanese localization status/report expectations from `0/27 entrypoints (0 aliases)` to `3/27 entrypoints (9 aliases)`.
- Added a material package assertion that only these three entrypoints own Japanese aliases in this round.
- Added runtime question tests with the legacy dynamic alias table disabled, proving the package-owned Japanese aliases route natural location questions to the intended entrypoints.
- Added two Q&A priority regressions:
  - Chat/participant privacy questions remain answer-only and do not route to the Chat entrypoint.
  - Audio/video troubleshooting remains the localized Q&A answer for Network quality and is not stolen by the new `音声` alias.
- Updated the RingCentral Video source index to record this partial Japanese alias coverage without claiming full Japanese localization.

## TDD Evidence

Red run before YAML alias changes:

`.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_ringcentral_package_owns_japanese_aliases_for_meeting_basics_routes tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_questions.py::test_ringcentral_japanese_meeting_basics_questions_match_package_aliases_without_legacy_table tests\unit\test_questions.py::test_ringcentral_japanese_chat_privacy_question_stays_answer_only_with_aliases`

Result: `4 failed, 1 passed`, confirming `questionAliases.ja` still reported `0/27`, the expected aliases were absent, and Japanese location questions returned no match.

Green run after YAML alias changes and the extra audio Q&A regression:

`.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_ringcentral_package_owns_japanese_aliases_for_meeting_basics_routes tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_questions.py::test_ringcentral_japanese_meeting_basics_questions_match_package_aliases_without_legacy_table tests\unit\test_questions.py::test_ringcentral_japanese_chat_privacy_question_stays_answer_only_with_aliases tests\unit\test_questions.py::test_ringcentral_japanese_audio_troubleshooting_question_stays_qa_with_aliases`

Result: `6 passed`.

## Notes For Next Cycle

- The next Japanese alias slice should avoid broad content-reading phrases and prefer location-only controls.
- Candidates for a future low-risk alias cycle: `network-quality`, `meeting-info`, and `notes`, each with privacy-specific Q&A regression tests.
- `meeting-controls-tour` and `meeting-control-map-demo` Japanese narration remain at `0/22` each.
