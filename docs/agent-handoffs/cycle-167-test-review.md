# Cycle 167 Test Review: Caption/Transcript Action Prompts

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Role: Cycle167 test-review subagent

## Findings

### P2 - Action-leak assertions miss save/download/start success wording

`tests/unit/test_questions.py:1126` currently blocks `copied`, `exported`,
and `turned on`, but the same parametrized test now covers `Save captions`,
`Download captions`, and `Download transcript text`. A future regression could
answer with `saved`, `downloaded`, or `started` wording and still pass the
caption/transcript action prompt test. Add casefolded negatives for `saved`,
`downloaded`, and `started` beside the existing action-leak checks.

This is a test-hardening finding, not an observed runtime behavior bug. A direct
probe of the current dirty tree returned `entrypoint_id=None`,
`can_operate=False`, no interrupt, and no `copied`/`exported`/`saved`/
`downloaded`/`started`/`turned on` leak words for all six new prompts.

## Review Notes

- The package diff adds exactly the six requested English Q&A prompts under the
  existing `Where are captions, live transcription, and translation controls?`
  item: `Copy captions`, `Can you copy the captions?`, `Export captions`,
  `Save captions`, `Download captions`, and `Download transcript text`.
- I saw no runtime matcher, entrypoint alias, `relatedEntrypointIds`, open-step,
  profile, or localization-count changes in the tracked implementation diff.
- `tests/unit/test_questions.py` covers all six prompts in the existing
  answer-only parametrization and asserts `entrypoint_id is None`,
  `can_operate is False`, and `create_question_interrupt_step(...) is None`.
- The same test asserts the intended privacy text: `Notes and Transcript`,
  `Settings`, `caption or transcript text`, `explicitly asks`, and `verified`.
- Wrong-route and fallback checks are present for `Microphone control:`,
  `Meeting information:`, `Notes and transcript:`, and
  `I could not find a matching control`.
- Diagnostics and doctor count expectations move together from `167` to `173`.
  Package-owned alias count remains `157`; substring-risk expectation remains
  `11`.
- The safe caption/live-transcript variants recommended in earlier scans
  (`Show caption text`, `Read live captions aloud`, `Read live caption text`,
  `Read the live caption text`, `Read the live transcript text`, and
  `Show transcript text`) should remain future backlog, not part of this six
  prompt action-content slice. The technical-development handoff records that
  distinction clearly.

## Focused Verification

Ran only focused checks with pytest coverage addopts disabled and cache provider
disabled:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_captions_and_translation_questions_are_answer_only tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

Result: `21 passed in 4.24s`.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_english_transcript_content_requests_stay_answer_only
```

Result: `2 passed in 0.56s`.

Also ran a direct route/leak probe for the six new prompts. Each returned
`entrypoint=None`, `can_operate=False`, `interrupt=False`, and `leaks=[]` for
`copied`, `exported`, `saved`, `downloaded`, `started`, `turned on`,
`the caption says`, and `here are the captions`.

`git diff --check -- packages/ringcentral-video.yaml tests/unit/test_cli.py tests/unit/test_diagnostics.py tests/unit/test_questions.py`
reported no whitespace errors; it only repeated the existing LF-to-CRLF working
copy warnings.

I did not run the full suite, stage, commit, edit code/tests, or intentionally
touch `.coverage`. `.coverage` was already modified when this review began and
remained present in `git status --short`.
