# Cycle 157 Technical Scan

## Recommendation

Treat the six leave/end meeting prompts as exact Q&A prompts, not entrypoint aliases:

- `Leave meeting`
- `End meeting`
- `Hang up`
- `End call`
- `Close meeting`
- `Can you leave the meeting?`

These are destructive or potentially destructive meeting-exit requests. The safest route is the existing Q&A item `How should AiPresenter handle leaving or ending the meeting safely?`, related to `ringcentral.video.toolbar.leave`, with `can_operate is False` and no interrupt step. Do not add English `questionAliases` to the leave entrypoint for these prompts; aliases would be operation-entrypoint lookups and can fall back to the thinner `Leave meeting: Leave or end the meeting.` answer instead of the explicit safety guidance.

## Current Routing

Runtime question flow in `src/ai_presenter/runtime/questions.py` is already correct for this use case:

- `answer_question()` normalizes the prompt with `normalize_question_prompt()`.
- `_match_qa()` checks `package.qa_questions_by_normalized` before entrypoint alias matching or scored entrypoint matching.
- Exact Q&A matches return the Q&A answer and the first related entrypoint id.
- `_can_operate()` then returns `False` for `ringcentral.video.toolbar.leave` because the entrypoint has no `openSteps` and is also covered by risky wording.
- `create_question_interrupt_step()` returns `None` for non-operable responses.

Current package data in `packages/ringcentral-video.yaml` already contains the leave/end safety Q&A item near the end of the `qa:` list. Its English localized questions include all six target prompts, and its answer starts with `Leaving or ending a meeting is destructive...`.

The leave entrypoint itself remains explain-only:

- id: `ringcentral.video.toolbar.leave`
- title: `Leave meeting`
- purpose: `Leave or end the meeting.`
- `openSteps: []`
- package-owned aliases exist for `es` and `zh`, but not `en`

## Current Counts

Observed from loading `packages/ringcentral-video.yaml` locally:

- Operation entrypoints: `27`
- Package-owned question aliases: `157`
- Q&A items: `13`
- Q&A question candidates/prompts: `102`

The current count drift is caused by adding the leave/end safety Q&A item and localized prompts after the previous recording cycle had tests expecting `92` Q&A prompts. The leave/end item contributes 10 prompt candidates: primary question, six English exact prompts, and one each for Spanish, Japanese, and Chinese.

## Test Evidence

Passing focused routing check:

```powershell
.\.venv\Scripts\pytest.exe tests\unit\test_questions.py::test_ringcentral_english_leave_end_questions_stay_qa_first -q --no-cov
```

Observed result:

```text
6 passed
```

Passing controller safety check:

```powershell
.\.venv\Scripts\pytest.exe tests\unit\test_controller.py::test_presenter_controller_answers_risky_question_without_demo tests\unit\test_controller_session.py::test_session_does_not_create_interrupt_for_risky_answer -q --no-cov
```

Observed result:

```text
2 passed
```

Currently failing count checks:

```powershell
.\.venv\Scripts\pytest.exe tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow -q --no-cov
```

Observed result:

```text
3 failed
```

Failures are stale expected counts only:

- `tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package` expects `92 Q&A question prompts...`; actual is `102 Q&A question prompts...`.
- `tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package` expects `92 Q&A question prompts...`; actual is `102 Q&A question prompts...`.
- `tests/unit/test_cli.py::test_doctor_loads_profile_package_and_flow` expects the old `92` substrings in doctor output; actual output contains the new `102` details.

## Files To Update

No source or package behavior appears necessary in the current tree. The smallest follow-up is test-count maintenance only:

- `tests/unit/test_diagnostics.py`
  - Change the two expected Q&A prompt count details from `92` to `102`.
- `tests/unit/test_cli.py`
  - Change the two expected doctor-output Q&A prompt count substrings from `92` to `102`.

Do not update these in this scan handoff; this cycle is documentation-only.

## Focused Verification Commands

Use `--no-cov` so the existing dirty `.coverage` file is not touched:

```powershell
.\.venv\Scripts\pytest.exe tests\unit\test_questions.py::test_ringcentral_english_leave_end_questions_stay_qa_first -q --no-cov
.\.venv\Scripts\pytest.exe tests\unit\test_controller.py::test_presenter_controller_answers_risky_question_without_demo tests\unit\test_controller_session.py::test_session_does_not_create_interrupt_for_risky_answer -q --no-cov
.\.venv\Scripts\pytest.exe tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow -q --no-cov
.\.venv\Scripts\pytest.exe tests\unit\test_questions.py tests\unit\test_controller.py tests\unit\test_controller_session.py tests\unit\test_diagnostics.py tests\unit\test_cli.py -q --no-cov
git diff --check -- packages\ringcentral-video.yaml tests\unit\test_questions.py tests\unit\test_diagnostics.py tests\unit\test_cli.py
```

## No-Go Scope

- Do not stage, commit, reset, or touch `.coverage`.
- Do not add English leave/end `questionAliases` to `ringcentral.video.toolbar.leave`.
- Do not add `openSteps` to the leave entrypoint.
- Do not make leave/end meeting questions operable from Q&A.
- Do not add UI automation for confirming Leave, End meeting, Hang up, or End call in this slice.
