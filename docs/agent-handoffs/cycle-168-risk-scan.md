# Cycle 168 Risk/Test Scan: RingCentral Video Encryption Status Prompts

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Latest inspected commit: `20de0da`
Role: Cycle168 risk/test-scan subagent

## Scope

- Reviewed risk and test strategy for the Cycle168 Meeting information encryption-status prompt optimization.
- Aligned this scan with `docs/agent-handoffs/cycle-168-demand-analysis.md`, which appeared during this pass and recommends a narrow package/test-only encryption slice.
- Wrote only this handoff: `docs/agent-handoffs/cycle-168-risk-scan.md`.
- Did not edit source code, tests, package YAML, `.coverage`, staging, or commits.
- Did not run the full suite. Used read-only `git`, `rg`, and tiny no-bytecode route/count probes.
- Current dirty files observed and treated as other-agent work: `.coverage`, `packages/ringcentral-video.yaml`, `tests/unit/test_cli.py`, `tests/unit/test_diagnostics.py`, `tests/unit/test_questions.py`, and untracked `docs/agent-handoffs/cycle-168-demand-analysis.md` plus `docs/agent-handoffs/cycle-168-technical-scan.md`.

## Target Slice

Recommended implementation target from demand analysis:

- Extend the existing Q&A item `How should AiPresenter handle meeting IDs and links safely?`.
- Add exact English Meeting information encryption prompts there, not in entrypoint `questionAliases`.
- Update the base and localized answers so encryption and end-to-end encryption details are treated as private or state-verification-sensitive Meeting information.
- Keep the route tied to `ringcentral.video.top.meeting-info`, which already has `questionPolicy: answerOnly`.
- Do not add runtime matcher changes, open steps, aliases, or an operable route.

Recommended exact prompts:

- `Can you tell me the encryption status?`
- `What is the encryption status?`
- `Is this meeting encrypted?`
- `Is end-to-end encryption on?`
- `Are we using end-to-end encryption?`
- `Read the encryption details`
- `Copy the encryption details`

## Current Routing Evidence

Current dirty tree before the encryption slice:

| Prompt | Current observed route |
| --- | --- |
| `Can you tell me the encryption status?` | Thin `Meeting information:` fallback, `entrypoint=ringcentral.video.top.meeting-info`, non-operable, no interrupt. |
| `What is the encryption status?` | Thin `Meeting information:` fallback, non-operable, no interrupt. |
| `Is this meeting encrypted?` | No-match fallback, `entrypoint=None`, non-operable, no interrupt. |
| `Is end-to-end encryption on?` | Thin `Meeting information:` fallback, non-operable, no interrupt. |
| `Are we using end-to-end encryption?` | Thin `Meeting information:` fallback, non-operable, no interrupt. |
| `Read the encryption details` | Meeting-info privacy Q&A, but the current answer does not name encryption. |
| `Copy the encryption details` | Meeting-info privacy Q&A, but the current answer does not name encryption. |

Current behavior is safe from an operation perspective, but it is not a good answer for a security/status user. The optimization should turn thin fallback and no-match behavior into explicit Meeting information privacy guidance.

## Risk Matrix

| Risk | Likelihood | Impact | Recommended guard |
| --- | --- | --- | --- |
| Encryption status prompts keep thin fallback or no-match behavior | High without exact prompts | Medium | Add exact Q&A prompts and assert no `Meeting information:` fallback and no no-match text. |
| Answer copy claims a live encryption state from static package data | Medium | High | Do not say the meeting is encrypted, not encrypted, E2EE-enabled, verified, compliant, or safe unless visible context is explicitly verified. |
| Read/copy wording implies action completion | Medium | High | Assert no completed-action wording such as `I copied`, `copied the`, `I read`, `here are the`, or `the encryption status is`. |
| Exact prompts are added as `questionAliases` | Medium | High | Keep them under the existing Q&A item. Aliases can bypass privacy answer copy and alter alias diagnostics. |
| `relatedEntrypointIds` or policy changes make Meeting information operable | Low/Medium | High | Preserve `ringcentral.video.top.meeting-info` as `questionPolicy: answerOnly`; assert non-operable and no interrupt. |
| Broad encryption/security aliases steal other routes | Medium if aliases are added | High | Avoid `encryption`, `encrypted`, `status`, `secure`, `security`, `copy`, `read`, or `details` as aliases. |
| Encryption slice blurs with host/security settings | Medium in current dirty tree | Medium | Keep `Where are security settings?` and related host-control/security prompts separate from Meeting information encryption prompts. |
| Password/passcode prompts sneak into this slice | Low/Medium | High | Keep password, passcode, and access-code prompts blocked until product evidence proves the surface. |
| Diagnostics prompt counts go stale | High when prompts land | Medium | Update Q&A prompt totals based on the actual final dirty base, not assumption. |

## Recommended Assertions

For every accepted encryption prompt:

```python
assert response.entrypoint_id == "ringcentral.video.top.meeting-info"
assert response.can_operate is False
assert create_question_interrupt_step(package, response) is None
```

Pin the intended privacy answer and avoid thin fallback:

```python
assert "Meeting IDs and links are private meeting details" in response.answer_text
assert "encryption" in response.answer_text.casefold()
assert "Meeting information:" not in response.answer_text
assert "I could not find a matching control" not in response.answer_text
```

Preserve private-value and action-completion negatives:

```python
lowered = response.answer_text.casefold()
assert "https://" not in response.answer_text
assert "ringcentral.com" not in response.answer_text
assert "123456789" not in response.answer_text
assert "i copied" not in lowered
assert "copied the" not in lowered
assert "i read" not in lowered
assert "here are the" not in lowered
assert "the encryption status is" not in lowered
assert "this meeting is encrypted" not in lowered
assert "this meeting is not encrypted" not in lowered
assert "e2ee is on" not in lowered
assert "end-to-end encryption is on" not in lowered
```

Avoid simple negatives such as `assert "read aloud" not in response.answer_text` or `assert "copy" not in response.answer_text`: the privacy answer may legitimately say AiPresenter should not copy or read exact details aloud.

If localized answers are changed, add semantic checks at the package level for the updated languages rather than relying only on localization completeness counts. Completeness counts will stay green even if a localized answer omits the new encryption boundary.

## Positive And Negative Controls

Positive controls for the encryption slice:

- The seven recommended encryption prompts should all use Meeting information privacy guidance.
- Existing meeting-link and meeting-value prompts should continue to pass through the same privacy Q&A:
  - `Copy meeting link`
  - `Can you read the meeting ID?`
  - `Read the dial-in number`
  - `Copy the dial-in details`
  - `Who is the host?`
  - `Read meeting details aloud`

Negative controls that should not be captured by encryption prompt work:

- `meeting information`: should remain the existing answer-only Meeting information entrypoint lookup, not the privacy Q&A fallback if current tests expect the label.
- `Where are security settings?`, `Open meeting security settings`, and `Meeting security settings`: in the current dirty tree these are host-control/security prompts. They should not become encryption-status answers.
- `Participants`: should remain the Participants panel lookup.
- `Background settings`: should remain the Background settings lookup.
- `Can you share system audio?`: should remain screen-sharing safety guidance.
- `Where are captions?` and caption read/copy/export prompts: should remain captions/transcript privacy guidance.
- `Start recording` or recording status prompts: should remain recording safety guidance.
- Password, passcode, access-code, and waiting-room prompts should remain out of this slice.

## Diagnostics Count Guidance

Clean `20de0da` baseline from Cycle167:

- Q&A question prompts: `173`
- Package-owned aliases: `157`
- Q&A alias substring-risk prompts: `11`

Current dirty tree already includes another five-prompt host/security-settings diff:

- Q&A question prompts: `178`
- Package-owned aliases: `157`
- Q&A alias substring-risk prompts: `11`

Expected count movement:

- If only the seven encryption prompts are applied on clean `20de0da`, Q&A prompt totals should move `173 -> 180`.
- If the current five-prompt host/security-settings diff is the base and all seven encryption prompts are added, Q&A prompt totals should move `178 -> 185`.
- Adding exact English prompts to the existing Meeting information privacy Q&A should not change package-owned alias count.
- Adding exact English prompts to an existing Q&A item should not change Q&A item localization totals.
- Substring-risk count should remain `11` only after focused diagnostics confirms it. Do not preserve it by assumption because words such as `security` or `details` can interact with nearby aliases in future prompt edits.

Files whose count assertions must move together after the final prompt set is chosen:

- `tests/unit/test_diagnostics.py`: both RingCentral Q&A prompt detail strings.
- `tests/unit/test_cli.py::test_doctor_loads_profile_package_and_flow`: matching doctor output strings.

## Final Verification Checklist

- Confirm all accepted encryption prompts are under `How should AiPresenter handle meeting IDs and links safely?`.
- Confirm no encryption prompt was added to entrypoint `questionAliases`.
- Confirm no runtime matcher, open-step, profile, or question-policy change is part of this slice.
- Confirm the Meeting information entrypoint still has `questionPolicy: answerOnly`.
- Confirm all encryption prompts return `ringcentral.video.top.meeting-info`, remain non-operable, and create no interrupt.
- Confirm answer copy names encryption/end-to-end encryption as sensitive Meeting information without claiming the live status.
- Confirm the answer does not expose or invent meeting IDs, links, dial-in details, host names, encryption values, account details, passcodes, or passwords.
- Confirm host/security-settings, participants, background, invite, share, captions/transcript, recording, and leave/end controls keep their existing routes.
- Confirm diagnostics/doctor counts match the actual final prompt inventory: `180` if only the seven encryption prompts land on clean Cycle167, or `185` if the current five host/security prompts are also included.
- Run focused verification only, with coverage disabled and cache disabled:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first tests\unit\test_questions.py::test_ringcentral_participant_host_action_requests_stay_answer_only tests\unit\test_questions.py::test_ringcentral_english_invite_privacy_questions_stay_qa_first tests\unit\test_questions.py::test_ringcentral_captions_and_translation_questions_are_answer_only
```

- If diagnostics or doctor strings changed, run focused count checks only:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

- Run `git diff --check` before staging in the implementation pass.
- Run `git status --short` and keep `.coverage` unstaged.
- Do not run the full suite for this narrow prompt optimization unless the coordinator explicitly asks for it.
