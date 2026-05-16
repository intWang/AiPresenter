# Cycle 047 Implementation

## Slice

RingCentral Video meeting-info question safety.

## Root Cause

The package already marks meeting IDs, meeting links, dial-in details, host identity, and encryption details as sensitive. However, question-triggered operation permission depended on generic risky-word heuristics. `ringcentral.video.top.meeting-info` happened to be non-operable because its purpose contains `end-to-end`, which matches the risky word `end`; that was accidental, not a clear privacy policy.

Separately, English questions such as `where is the meeting ID` did not reliably match the meeting-info entrypoint because `meeting` is a stopword and `ID` is shorter than the meaningful-token threshold.

## Changes

- Added package-owned English aliases to `ringcentral.video.top.meeting-info`:
  - `meeting information`
  - `meeting details`
  - `meeting ID`
  - `meeting link`
- Added `_QUESTION_EXPLAIN_ONLY_ENTRYPOINT_IDS` in `runtime.questions`.
- Marked `ringcentral.video.top.meeting-info` explain-only for question-triggered `can_operate`.
- Updated doctor/diagnostics expectations from 49 to 53 package-owned aliases.

## TDD Evidence

Initial focused red run:

- `where is the meeting ID` returned no entrypoint.
- With `_RISKY_ENTRYPOINT_WORDS` monkeypatched to an empty set, `meeting information` returned `can_operate=True`.

Post-fix focused run:

- `test_meeting_info_privacy_questions_are_answer_only`
- `test_meeting_info_privacy_gate_does_not_depend_on_risky_words`

Result: `6 passed`.

## Focused Verification

- `tests/unit/test_questions.py tests/unit/test_material_packages.py tests/unit/test_diagnostics.py tests/unit/test_cli.py::test_doctor_loads_profile_package_and_flow`: `97 passed`.
- `ruff check --no-cache src\ai_presenter\runtime\questions.py tests\unit\test_questions.py tests\unit\test_cli.py tests\unit\test_diagnostics.py`: passed.
- `mypy --no-incremental src\ai_presenter\runtime\questions.py tests\unit\test_questions.py tests\unit\test_cli.py tests\unit\test_diagnostics.py`: passed.
- Probe confirmed:
  - `where is the meeting ID` -> `ringcentral.video.top.meeting-info`, `can_operate=False`
  - `where is the meeting link` -> `ringcentral.video.top.meeting-info`, `can_operate=False`
  - `network quality` remains operable
  - `participants` remains operable
  - `recording` remains non-operable safety Q&A

