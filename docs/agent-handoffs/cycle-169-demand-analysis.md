# Cycle 169 Demand Analysis: Meeting Encryption Status Q&A

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Latest inspected commit: `62929a1`
Role: Cycle169 demand-analysis subagent

## Scope

Inspected the RingCentral package, question/diagnostic/CLI tests, knowledge
docs, and recent Cycle167/Cycle168 handoffs. I did not edit code, tests,
package YAML, staging, commits, or `.coverage`, and I did not run the full
suite.

This handoff writes only
`docs/agent-handoffs/cycle-169-demand-analysis.md`.

Initial workspace status showed `.coverage` already dirty. During inspection,
concurrent dirty edits were present in:

- `packages/ringcentral-video.yaml`
- `tests/unit/test_questions.py`
- `tests/unit/test_diagnostics.py`
- `tests/unit/test_cli.py`
- `docs/agent-handoffs/cycle-169-risk-scan.md`

Those edits appear to add several full-screen Views aliases/tests and move
package-owned alias expectations from `157` to `161`. Treat them as other-agent
work. Do not revert or overwrite them.

The concurrent Cycle169 risk scan recommends the full-screen/views slice. This
demand pass still recommends the encryption-status Q&A slice because the
full-screen work already has active dirty package/test coverage and a dedicated
risk handoff, while encryption prompts remain an unfixed privacy-sensitive Q&A
gap.

## Recommendation

Implement one narrow package/test-only slice for Meeting information encryption
status and encryption-detail prompts.

Use the existing Q&A item:

`How should AiPresenter handle meeting IDs and links safely?`

Extend that Q&A item, rather than adding entrypoint aliases or runtime matcher
logic. The item already owns private Meeting information values and already
routes to `ringcentral.video.top.meeting-info`, whose entrypoint has
`questionPolicy: answerOnly`.

This is the best next target because encryption prompts are still unfixed and
privacy-sensitive. Current behavior is safe from an operation perspective, but
it gives thin fallback text or no-match text for normal security/status
questions. The full-screen/views work is already active in dirty package/tests
and should be finished or reviewed separately.

## Repo Evidence

- `packages/ringcentral-video.yaml` says `ringcentral.video.top.meeting-info`
  opens meeting title, host, meeting ID, copy link, dial-in info, encryption,
  and an end-to-end encryption option.
- The Meeting information Q&A currently covers meeting IDs, links, dial-in
  details, and host information, but does not name encryption details in the
  prompt list or answer copy.
- `docs/knowledge/ringcentral-video/privacy-matrix.md` classifies encryption
  details as sensitive Meeting information.
- `docs/knowledge/ringcentral-video/runtime-safety-routing.md` says Meeting
  information may include account or encryption details and that exact values
  require explicit user request plus verified visible context.
- Cycle168 demand/risk scans already recommended this encryption-status slice;
  Cycle168 implementation intentionally chose host/security prompts instead.

## Current Behavior

Read-only route probes against the current dirty tree:

| Prompt | Current route |
| --- | --- |
| `Can you tell me the encryption status?` | Thin `Meeting information:` fallback, `entrypoint=ringcentral.video.top.meeting-info`, non-operable, no interrupt. |
| `What is the encryption status?` | Thin `Meeting information:` fallback, non-operable, no interrupt. |
| `Show meeting encryption status` | Thin `Meeting information:` fallback, non-operable, no interrupt. |
| `Is this meeting encrypted?` | No-match fallback, `entrypoint=None`, non-operable, no interrupt. |
| `Is end-to-end encryption on?` | Thin `Meeting information:` fallback, non-operable, no interrupt. |
| `Are we using end-to-end encryption?` | Thin `Meeting information:` fallback, non-operable, no interrupt. |
| `Can you verify encryption?` | Thin `Meeting information:` fallback, non-operable, no interrupt. |
| `Can you verify end-to-end encryption?` | Wrong `Leave` safety answer, non-operable, no interrupt. |
| `Open encryption settings` | Wrong `Background settings` route, operable, creates an interrupt. |
| `Read the encryption details` | Meeting-info privacy Q&A, but answer does not name encryption. |
| `Copy the encryption details` | Meeting-info privacy Q&A, but answer does not name encryption. |

The full-screen dirty work currently routes `Show full screen`, `Switch to full
screen`, `Where is full screen?`, and `Full screen view` to Views, but `Go full
screen` and `Enter full screen mode` still route to Screen sharing in probes.
Keep that as a separate Views backlog item.

## Exact Prompts

Add these exact English Q&A prompts under
`How should AiPresenter handle meeting IDs and links safely?`:

- `Can you tell me the encryption status?`
- `What is the encryption status?`
- `Show meeting encryption status`
- `Is this meeting encrypted?`
- `Is end-to-end encryption on?`
- `Are we using end-to-end encryption?`
- `Can you verify encryption?`
- `Can you verify end-to-end encryption?`
- `Open encryption settings`

Do not add broad entrypoint aliases such as `encryption`, `encrypted`,
`status`, `secure`, `security`, `copy`, `read`, or `details`.

## Expected Behavior

For every accepted prompt:

- Return the Meeting information privacy Q&A, not thin `Meeting information:`
  fallback text and not no-match text.
- Keep `entrypoint_id == "ringcentral.video.top.meeting-info"`.
- Keep `can_operate is False`.
- Ensure `create_question_interrupt_step(package, response) is None`.
- Do not open Meeting information, copy to clipboard, read values aloud, or
  queue any UI step.
- Do not claim the meeting is encrypted, unencrypted, E2EE-enabled, verified,
  compliant, copied, or read aloud from static package data.
- Answer copy should name encryption and end-to-end encryption details as
  private or state-verification-sensitive Meeting information.
- Exact status or exact values require explicit user intent and verified visible
  context.

## Acceptance Criteria

- The nine prompts are authored under the existing Meeting information privacy
  Q&A item, not under entrypoint `questionAliases`.
- The base answer is updated to include encryption and end-to-end encryption
  details alongside meeting IDs, links, dial-in details, and host information.
- Localized answers for that Q&A are updated semantically so they do not omit
  the new encryption privacy boundary.
- `tests/unit/test_questions.py` covers the nine prompts, either by extending
  `test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first` or by
  adding a focused `test_ringcentral_english_encryption_status_questions_stay_qa_first`.
- Each new prompt returns `ringcentral.video.top.meeting-info`, remains
  non-operable, and creates no question interrupt.
- Responses do not contain `Meeting information:` or
  `I could not find a matching control`.
- Responses do not contain `Background settings:` or
  `Leaving or ending a meeting`.
- Responses do not expose or invent meeting IDs, links, dial-in details, host
  names, encryption values, account details, passwords, passcodes, or access
  codes.
- Existing invite, participants/host-security, captions/transcript, recording,
  leave/end, screen sharing, and full-screen/view-layout tests keep their
  current routes.
- No runtime matcher, open-step, profile, demo-flow, locator, or source-code
  change is needed.
- `.coverage` remains untouched and unstaged.

## Count Impact

Committed `62929a1` baseline:

- Q&A question prompts: `178 -> 187`
- Q&A alias-overlap prompt count: `178 -> 187`
- Package-owned aliases: stays `157`
- Q&A alias substring-risk count: expected to stay `11`, but verify.

Current dirty tree with other-agent full-screen alias work:

- Q&A question prompts: `178 -> 187`
- Q&A alias-overlap prompt count: `178 -> 187`
- Package-owned aliases: observed `161`, and should stay `161` for this
  encryption slice.
- Q&A alias substring-risk count: observed `11`, expected to stay `11`, but
  verify.

If the full-screen dirty work changes again before implementation, recompute the
alias count from diagnostics instead of hard-coding either `157` or `161`.

## Focused Verification Recommendation

Do not run the full suite for this narrow slice unless the coordinator asks.
Use coverage-disabled, cache-disabled focused checks:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first tests\unit\test_questions.py::test_ringcentral_participant_host_action_requests_stay_answer_only tests\unit\test_questions.py::test_ringcentral_captions_and_translation_questions_are_answer_only tests\unit\test_questions.py::test_ringcentral_english_screen_sharing_questions_stay_qa_first
```

If diagnostics or doctor count strings are touched:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

Before staging in the implementation pass:

```powershell
git diff --check -- packages\ringcentral-video.yaml tests\unit\test_questions.py tests\unit\test_diagnostics.py tests\unit\test_cli.py
git status --short
```

## Backlog

1. Finish or review the current full-screen/views dirty work separately. It
   covers several exact prompts, but probes still show `Go full screen` and
   `Enter full screen mode` routing to Screen sharing.
2. Exact-pin `Read the encryption details` and `Copy the encryption details`
   later if reviewers want prompt-level coverage beyond the answer-copy update;
   those prompts already reach the Meeting information privacy Q&A today.
3. Add localized encryption-status prompts only after English exact prompts and
   answer copy are stable.
4. Add a separate state-verification slice for `Is the meeting locked?`, `Is
   the waiting room on?`, and related live security-status prompts after product
   or adapter evidence exists.
5. Keep password, passcode, and access-code prompts blocked until product/source
   evidence confirms where RingCentral Video exposes those values.
6. Continue caption/transcript action variants as separate exact Q&A prompt
   slices; do not combine them with Meeting information encryption details.
