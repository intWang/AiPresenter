# Cycle 168 Demand Analysis: Meeting Encryption Status Prompts

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Latest inspected commit: `20de0dae35c7612e172c769d57520ca1e514d040`
Role: Cycle168 demand-analysis subagent

## Scope

Inspected `packages/ringcentral-video.yaml`, RingCentral question and adapter
tests, knowledge docs, and recent Cycle 163 through Cycle 167 handoffs. I did
not edit code, tests, package YAML, staging, commits, or `.coverage`, and I did
not run the full suite. I used read-only routing probes with bytecode disabled.

This handoff writes only `docs/agent-handoffs/cycle-168-demand-analysis.md`.
Initial workspace status showed `.coverage` already dirty; leave it untouched.
Final scope check also showed dirty `packages/ringcentral-video.yaml`,
`tests/unit/test_cli.py`, `tests/unit/test_diagnostics.py`, and
`tests/unit/test_questions.py` from concurrent worktree activity. I did not
edit, revert, or overwrite those files.

## Recommendation

Implement one narrow package/test-only slice for Meeting information encryption
status and encryption-detail prompts.

Recommended target Q&A item:

`How should AiPresenter handle meeting IDs and links safely?`

That item already owns private Meeting information values and already routes to
`ringcentral.video.top.meeting-info`. Extend its answer copy so encryption and
end-to-end encryption details are explicitly treated as verified-state/private
meeting details, then add exact English prompt variants there. Do not create
entrypoint aliases, runtime matcher logic, open steps, or an operable route.

## Repo Evidence

- `packages/ringcentral-video.yaml` says `ringcentral.video.top.meeting-info`
  opens meeting title, host, meeting ID, copy link, dial-in info, encryption,
  and an end-to-end encryption option.
- The same package narration says Meeting information includes encryption
  status/details and that private values should be summarized rather than read
  aloud by default.
- `docs/knowledge/ringcentral-video/privacy-matrix.md` classifies encryption
  details under Meeting information private values.
- `docs/knowledge/ringcentral-video/runtime-safety-routing.md` says Meeting
  information may include account or encryption details.
- `tests/integration/test_ringcentral_profile.py` covers waiting-room labels as
  adapter state, but there is no package Q&A for encryption status.
- `packages`, `docs/knowledge`, `src`, `profiles`, and tests contain no product
  evidence for meeting password/passcode/access-code fields. Treat those as
  blocked, not merely deferred.

## Current Behavior

Read-only spot probes against the current tree showed the gap:

| Prompt | Current observed route |
| --- | --- |
| `Can you tell me the encryption status?` | Thin `Meeting information:` fallback, `entrypoint=ringcentral.video.top.meeting-info`, non-operable, no interrupt. |
| `What is the encryption status?` | Thin `Meeting information:` fallback, non-operable, no interrupt. |
| `Is this meeting encrypted?` | No-match fallback, `entrypoint=None`, non-operable, no interrupt. |
| `Is end-to-end encryption on?` | Thin `Meeting information:` fallback, non-operable, no interrupt. |
| `Are we using end-to-end encryption?` | Thin `Meeting information:` fallback, non-operable, no interrupt. |
| `Read the encryption details` | Meeting-info privacy Q&A, but answer does not name encryption. |
| `Copy the encryption details` | Meeting-info privacy Q&A, but answer does not name encryption. |

Current behavior is not dangerous because it stays non-operable, but it is a
poor answer for a security/compliance user. Status questions should not fall to
generic location text or no-match, and read/copy requests should hear a clear
encryption-specific privacy boundary.

## Exact Prompt Variants

Add these exact English Q&A prompts:

- `Can you tell me the encryption status?`
- `What is the encryption status?`
- `Is this meeting encrypted?`
- `Is end-to-end encryption on?`
- `Are we using end-to-end encryption?`
- `Read the encryption details`
- `Copy the encryption details`

Avoid broad aliases such as `encryption`, `encrypted`, `status`, `secure`,
`security`, `copy`, `read`, or `details`. These can steal unrelated Meeting
information, security-settings, host-control, and troubleshooting prompts.

## Expected Behavior

For every accepted prompt:

- Return Meeting information privacy guidance, not thin `Meeting information:`
  fallback text and not no-match text.
- Prefer `entrypoint_id == "ringcentral.video.top.meeting-info"` so the answer
  stays tied to the relevant surface without opening it.
- Keep `can_operate is False`.
- Ensure `create_question_interrupt_step(package, response) is None`.
- Do not open Meeting information, copy to clipboard, read values aloud, or
  queue any UI step.
- Do not claim the meeting is encrypted, unencrypted, E2EE-enabled, verified,
  or policy-compliant from static package data alone.
- Do not invent, mask, summarize, copy, validate, or expose concrete encryption
  values, account details, meeting IDs, links, dial-in details, host names, or
  other private meeting metadata.
- Answer text should say AiPresenter can explain where encryption details live,
  but current status or exact values require explicit user intent and verified
  visible context.

## Acceptance Criteria

- The seven exact prompts are authored under the existing Meeting information
  privacy Q&A item, not entrypoint `questionAliases`.
- The base answer and localized answers for that Q&A are updated to include
  encryption/end-to-end encryption details as private or state-verification
  sensitive Meeting information.
- Each prompt returns `entrypoint_id == "ringcentral.video.top.meeting-info"`,
  `can_operate is False`, and no question interrupt.
- No response starts with or contains the thin fallback label
  `Meeting information:`.
- No response contains `I could not find a matching control`.
- No response claims `encrypted`, `not encrypted`, `E2EE is on`, `verified`,
  `copied`, `read aloud`, or any concrete private-looking value as a completed
  action or fact. Boundary wording such as "visible context is verified" is OK.
- Existing meeting-link, host/dial-in, invite, chat/participants, host/security
  actions, captions/transcript, recording, leave/end, and location-style
  Meeting information tests continue to pass.
- From the current Cycle167 baseline of `173` Q&A question prompts, adding all
  seven variants should move Q&A prompt-count expectations to `180`. Recompute
  with diagnostics before hard-coding the number.
- Package-owned alias count should remain `157`; Q&A alias substring-risk count
  should be verified and should not be changed by assumption.
- `.coverage` remains untouched and unstaged.

## Focused Verification Recommendation

Do not run the full suite for this narrow slice unless the coordinator asks.
Use coverage-disabled focused checks:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first tests\unit\test_questions.py::test_ringcentral_participant_host_action_requests_stay_answer_only tests\unit\test_questions.py::test_ringcentral_captions_and_translation_questions_are_answer_only
```

If diagnostics or doctor prompt counts change, also run:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

## Backlog

1. Meeting lock/security status prompts such as `Is the meeting locked?` and
   `Is the waiting room on?` need a separate state-verification slice. Do not
   mix them with encryption because their evidence comes from Participants,
   host controls, and adapter state rather than Meeting information.
2. Waiting-room/prejoin prompts can build on adapter evidence in
   `tests/integration/test_ringcentral_profile.py`, but they need a different
   answer shape because they describe live/prejoin state, not Meeting
   information details.
3. Localized encryption-status prompts can follow after English exact routing
   and answer copy are stable.
4. Password/passcode/access-code prompts remain blocked. No package or
   knowledge-doc product evidence currently proves RingCentral Video exposes
   those fields in Meeting information or another verified surface.
5. Already-safe caption/transcript variants remain a separate exact-pinning
   backlog item; do not combine them with encryption status.
