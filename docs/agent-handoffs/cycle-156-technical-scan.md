# Cycle 156 Technical Scan

## Recommendation

Treat the five recording-related exact English prompts as Q&A prompts, not operation aliases:

- `Record this meeting`
- `Start recording`
- `Stop recording`
- `Are we recording?`
- `Recording status`

They are not safe toolbar-operation aliases because several are imperative start/stop requests and two ask for recording state. The correct behavior is to route them to the existing safety Q&A item, `How do I handle meeting recording safely?`, which is related to `ringcentral.video.more.recording`, stays non-operable, and does not create a question interrupt step.

The smallest implementation shape is package-data only:

- Add the five strings under `packages/ringcentral-video.yaml` -> Q&A item `How do I handle meeting recording safely?` -> `localizedQuestions.en`.
- Do not add English `questionAliases` to `ringcentral.video.more.recording`.
- Do not add `openSteps` or runtime operation handling for recording.
- Keep `ringcentral.video.more.recording` explain-only / non-operable.

## Current Tree Evidence

The current tree already contains the intended package/test slice:

- `packages/ringcentral-video.yaml` includes the five English `localizedQuestions.en` prompts on the existing recording safety Q&A.
- `tests/unit/test_questions.py::test_ringcentral_english_recording_action_questions_stay_qa_first` covers all five exact prompts.
- The focused routing test passes with local source:

```powershell
.\.venv\Scripts\pytest.exe tests\unit\test_questions.py::test_ringcentral_english_recording_action_questions_stay_qa_first -q --no-cov
```

Observed result:

```text
5 passed
```

Local source probe confirms each prompt returns:

- `entrypoint_id == "ringcentral.video.more.recording"`
- `can_operate is False`
- no interrupt step
- answer starts with `Recording changes the meeting state...`
- no entrypoint-label fallback such as `Start recording:`

## Expected Failures

The prompt additions increase Q&A prompt diagnostics from `87` to `92`. The alias count should not change because these are Q&A prompts, not operation aliases.

Currently failing focused checks:

```powershell
.\.venv\Scripts\pytest.exe tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow -q --no-cov
```

Observed failures:

- `test_diagnostics_reports_qa_questions_ok_for_ringcentral_package` expects `87 Q&A question prompts...`; actual is `92 Q&A question prompts...`.
- `test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package` expects `87 Q&A question prompts...`; actual is `92 Q&A question prompts...`.
- `test_doctor_loads_profile_package_and_flow` expects the old `87` count in CLI output; actual output now contains `92`.

## Smallest TDD Follow-Up

If this cycle is being completed from the current tree, do not add more production behavior. The smallest remaining TDD implementation is to update count assertions only:

- `tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package`
  - expected detail becomes `92 Q&A question prompts have no cross-item duplicates`
- `tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package`
  - expected detail becomes `92 Q&A question prompts have no unsafe package-owned alias overlaps`
- `tests/unit/test_cli.py::test_doctor_loads_profile_package_and_flow`
  - expected CLI substring becomes `92 Q&A question prompts have no cross-item duplicates`
  - expected CLI substring becomes `92 Q&A question prompts have no unsafe package-owned alias overlaps`

Counts to preserve:

- Q&A items: still `12`
- Package-owned question aliases: still `157`
- Operation entrypoints: still `27`
- Demo steps: still `51`

## Verification Commands

Use `--no-cov` so the existing `.coverage` dirty file is not touched:

```powershell
.\.venv\Scripts\pytest.exe tests\unit\test_questions.py::test_ringcentral_english_recording_action_questions_stay_qa_first -q --no-cov
.\.venv\Scripts\pytest.exe tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow -q --no-cov
.\.venv\Scripts\pytest.exe tests\unit\test_questions.py tests\unit\test_diagnostics.py tests\unit\test_cli.py -q --no-cov
git diff --check -- packages\ringcentral-video.yaml tests\unit\test_questions.py tests\unit\test_diagnostics.py tests\unit\test_cli.py
```

## No-Go Scope

- Do not stage, alter, or revert `.coverage`.
- Do not add recording operation aliases for these English prompts.
- Do not make recording operable from question answering.
- Do not add a confirmed-action workflow, recording state extraction, or UI automation for start/stop/status in this slice.
- Do not edit runtime matcher scoring; exact Q&A prompt matching is sufficient.
