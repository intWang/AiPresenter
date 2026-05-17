# Cycle 171 Technical Scan: Short Prompt Routing

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Head inspected: `a3fc826`

## Scope Guardrails

Scan-only pass. I did not edit source code, tests, package YAML, `.coverage`,
staging, or commits. The only file written by this pass is this handoff:
`docs/agent-handoffs/cycle-171-technical-scan.md`.

The worktree is active. I observed concurrent dirty files during the scan:

- `.coverage`
- `src/ai_presenter/runtime/questions.py`
- `packages/ringcentral-video.yaml`
- `tests/unit/test_questions.py`
- `tests/unit/test_diagnostics.py`
- `tests/unit/test_cli.py`
- untracked `docs/agent-handoffs/cycle-171-demand-analysis.md`
- untracked `docs/agent-handoffs/cycle-171-risk-scan.md`

Recommendations below describe the current dirty tree, not a clean baseline.

## Current Routing Rules

Question routing in `src/ai_presenter/runtime/questions.py` is still:

1. Normalize the prompt.
2. Try Q&A exact/safety/fragment/token-overlap matching.
3. Fall back to entrypoint matching.
4. Set `can_operate` from `questionPolicy`, `openSteps`, and risky words.

The current dirty tree adds `_BROAD_QA_FRAGMENT_TOKENS = {"secure",
"security", "status", "verify"}` and rejects those exact one-word fragments in
`_can_match_qa_fragment(...)`. That means bare `status`, `security`, `secure`,
and `verify` no longer get stolen by the encryption-status Q&A.

Interrupt creation remains gated in `src/ai_presenter/runtime/session.py`:
`create_question_interrupt_step(...)` returns `None` whenever
`entrypoint_id is None` or `can_operate is False`.

## Current Prompt Matrix

Read-only probe path: load `packages/ringcentral-video.yaml`, call
`answer_question(...)`, inspect internal Q&A/entrypoint match source, then call
`create_question_interrupt_step(...)`.

| Prompt | Route | Answer source | Answer kind | `can_operate` | Interrupt |
| --- | --- | --- | --- | --- | --- |
| `status` | `None` | no match | no-match fallback | `False` | no |
| `security` | `None` | no match | no-match fallback | `False` | no |
| `secure` | `None` | no match | no-match fallback | `False` | no |
| `verify` | `None` | no match | no-match fallback | `False` | no |
| `meeting status` | `None` | no match | no-match fallback | `False` | no |
| `meeting security` | `ringcentral.video.top.meeting-info` | `Where can I verify meeting encryption status?` | encryption-status Q&A | `False` | no |
| `show meeting information` | `ringcentral.video.top.meeting-info` | entrypoint fallback | generic Meeting information answer | `False` | no |
| `open meeting information` | `ringcentral.video.top.meeting-info` | entrypoint fallback | generic Meeting information answer | `False` | no |
| `read meeting information` | `ringcentral.video.top.meeting-info` | `How should AiPresenter handle meeting IDs and links safely?` | meeting-info privacy Q&A | `False` | no |
| `read meeting info aloud` | `ringcentral.video.top.meeting-info` | `How should AiPresenter handle meeting IDs and links safely?` | meeting-info privacy Q&A | `False` | no |
| `share meeting information` | `ringcentral.video.top.meeting-info` | `How should AiPresenter handle meeting IDs and links safely?` | meeting-info privacy Q&A | `False` | no |

Important nuance: `meeting security` and `read meeting info aloud` currently
route by broader Q&A matching, not by exact package prompt text. They are safe
today, but they are less explicit than the authored exact-prompt rows.

## Relevant Current Tests

`tests/unit/test_questions.py` now covers:

- `test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first`
  - Includes `Read meeting information`, `Read meeting information aloud`,
    `Copy meeting information`, `Share meeting information`, `Copy meeting
    details`, and `Share meeting details`.
- `test_ringcentral_bare_status_words_do_not_match_encryption_status`
  - Covers `status`, `security`, `secure`, and `verify` as no-match,
    non-operable, no-interrupt, and not `Encryption status:`.
- `test_ringcentral_encryption_status_questions_stay_meeting_info_answer_only`
  - Covers encryption and security-status prompts, including `Security status`,
    `What is the security status?`, `Is the meeting secure?`, `Can you verify
    meeting security?`, `Share meeting security status`, and
    `Open security tab in RingCentralDevelop`.
- `test_ringcentral_sensitive_prompt_routing_is_tone_invariant`
  - Pins selected sensitive routes across tone changes.

Diagnostics/CLI count assertions are updated in:

- `tests/unit/test_diagnostics.py`
- `tests/unit/test_cli.py`

Current counts in the dirty tree:

- Package-owned aliases: `165`
- Q&A question prompts: `206`
- Q&A alias-overlap prompt count: `206`
- Q&A alias substring risk: `11`
- Localized Q&A item coverage remains `16/16`

## Focused Verification

Command run with bytecode, pytest cache, and project addopts disabled:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first tests\unit\test_questions.py::test_ringcentral_bare_status_words_do_not_match_encryption_status tests\unit\test_questions.py::test_ringcentral_encryption_status_questions_stay_meeting_info_answer_only tests\unit\test_questions.py::test_ringcentral_sensitive_prompt_routing_is_tone_invariant tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

Result: `62 passed in 11.90s`.

No full pytest run was performed.

## Recommended Narrow Slice

Smallest useful implementation slice from the current tree:

1. Keep the broad-fragment guard for bare `status`, `security`, `secure`, and
   `verify`.
2. Keep the meeting-info privacy Q&A prompt additions for read/copy/share
   meeting information/details requests.
3. Add regression rows for the exact Cycle 171 probe list that are not already
   explicit:
   - `meeting status` remains no-match, non-operable, no interrupt.
   - `meeting security` returns the encryption-status Meeting information Q&A,
     non-operable, no interrupt, if product wants that behavior.
   - `show meeting information` and `open meeting information` stay answer-only
     Meeting information routes with no interrupt.
   - `read meeting info aloud` stays privacy Q&A, non-operable, no interrupt.

If the team only adds test rows, package prompt counts stay unchanged at `206`.
If the team chooses to make fuzzy routes explicit package prompts, each new
English prompt added under an existing Q&A item increments the diagnostics/CLI
Q&A prompt count by one. For example:

- Add exact `Meeting security`: `206 -> 207`
- Add exact `Read meeting info aloud`: `206 -> 207`
- Add both: `206 -> 208`

Localized Q&A item coverage remains `16/16` unless a new Q&A item is added.

## Blockers And Decisions

No technical blocker for the safety posture: all scanned prompts are currently
non-operable and create no interrupt.

Open product decision: `meeting security` currently means encryption-status
guidance. It could also reasonably mean host/security controls. Decide that
semantic owner before adding an exact package prompt.

Coordination blocker: the implementation files are already dirty from another
agent. Do not start a follow-up implementation until ownership of the dirty
`questions.py`, package YAML, and test edits is clear.
