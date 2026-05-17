# Cycle 165 Test Review: Participant Role Privacy Prompts

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Role: Cycle165 test-review subagent

## Findings

- Low: `tests/unit/test_questions.py:1039` through `tests/unit/test_questions.py:1041` assert the role/private-identity answer contains `participant names`, `roles`, and `verified`, but they do not pin the rest of the privacy boundary currently present in `packages/ringcentral-video.yaml:1784` through `packages/ringcentral-video.yaml:1786`: `private tabs` and `explicitly asks`. The current answer is correct, so this is not blocking. Adding those two positive assertions next time would better lock the "private identity metadata only after explicit request and verified content" boundary.
- Low: `docs/agent-handoffs/cycle-165-demand-analysis.md` describes the participant-role prompts as already authored and tested "in HEAD", while the current role prompt work is still an uncommitted working-tree diff. The risk-scan, technical-scan, experience, and technical-development handoffs correctly treat it as current/concurrent worktree context. This is only a handoff wording issue, but future coordination should avoid reading that line as committed baseline state.

## Coverage Checked

The current participant-role diff adds these exact English Q&A prompts under the existing chat/participants privacy Q&A:

- `Show participant roles`
- `Read participant roles`
- `List participant roles`
- `Who is host or moderator?`

`tests/unit/test_questions.py::test_ringcentral_participant_identity_requests_stay_answer_only` now covers all four prompts plus the existing participant-name prompts. It asserts:

- Answer-only routing: `response.entrypoint_id is None` and `response.can_operate is False`.
- Not the Participants entrypoint: `response.entrypoint_id != "ringcentral.video.toolbar.participants"`.
- No interrupt/demo step: `create_question_interrupt_step(package, response) is None`.
- Role/privacy answer content: `participant names`, `roles`, and `verified`.
- Not Participants panel fallback: `Participants panel:` is absent.
- Not generic no-match fallback: `I could not find a matching control` is absent.

Diagnostics count coverage is aligned with the four added Q&A prompts:

- `tests/unit/test_diagnostics.py:657` expects `161 Q&A question prompts have no cross-item duplicates`.
- `tests/unit/test_diagnostics.py:674` expects `161 Q&A question prompts have no unsafe package-owned alias overlaps`.
- `tests/unit/test_cli.py:1512` and `tests/unit/test_cli.py:1514` expect the same `161` doctor output strings.
- Package-owned alias count remains `157`, which matches the data-only Q&A prompt change.

## Additional Assertions

No additional negative assertions are required to accept the current participant-role slice. The important negatives requested for this review are present: no Participants panel fallback, no generic no-match, no Participants entrypoint, and no interrupt.

Optional hardening for a future pass:

- Add `assert "explicitly asks" in response.answer_text`.
- Add `assert "private tabs" in response.answer_text`.
- Consider targeted leak/action negatives for role prompts, such as absence of `The host is`, `The moderator is`, `Here are the participants`, `I verified the roles`, `copied`, `exported`, or roster-like fixture values if future tests introduce observed UI text.

## Caption Text

Caption text should remain the next cycle slice. The current diff is participant-role/private-identity only. The Cycle165 demand, risk, technical-scan, experience, and technical-development handoffs all point to exact caption-content prompts such as `Read caption text`, `Show captions text`, and `Show live caption text` as the next small privacy-hardening target. Those should go under the existing captions/live transcription Q&A, not entrypoint aliases, and should assert no Audio fallback, no no-match fallback, no interrupt, and no transcript/caption operation.

## Verification

Focused tests run with coverage disabled and cache provider disabled:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_participant_identity_requests_stay_answer_only tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

Result: `10 passed in 2.63s`.

`git diff --check -- packages/ringcentral-video.yaml tests/unit/test_questions.py tests/unit/test_diagnostics.py tests/unit/test_cli.py` reported no whitespace errors; PowerShell printed only existing CRLF conversion warnings.

I did not run the full suite, edit code/tests, stage, commit, or touch `.coverage`.
