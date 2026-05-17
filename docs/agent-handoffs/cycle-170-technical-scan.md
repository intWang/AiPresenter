# Cycle 170 Technical Scan: Meeting Information and Encryption Routing

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Head inspected: `de46eea`

## Scope Guardrails

Scan-only pass. I did not edit source code, tests, package YAML, `.coverage`,
staging, or commits. The only intended write from this pass is this file:
`docs/agent-handoffs/cycle-170-technical-scan.md`.

The worktree is active. During this scan, concurrent edits appeared in:

- `.coverage` (already dirty; left untouched)
- `packages/ringcentral-video.yaml`
- `tests/unit/test_questions.py`
- `tests/unit/test_diagnostics.py`
- `tests/unit/test_cli.py`
- untracked `docs/agent-handoffs/cycle-170-demand-analysis.md`

Recommendations below describe the current dirty tree, not a clean baseline.

## Relevant Entrypoints

Primary target:

- `ringcentral.video.top.meeting-info`
- Title: `Meeting information`
- Area: `Meeting top bar`
- `questionPolicy: answerOnly`
- `openSteps`: one `clickWindowRelative` target, `Meeting information`, with
  `cleanup: escape`
- Purpose: opens meeting title, host, meeting ID, copy link, dial-in info,
  encryption, and end-to-end encryption option

Existing package-owned aliases on that entrypoint:

- English: `meeting information`, `meeting details`, `meeting ID`,
  `meeting link`
- Spanish: meeting information location/details-panel phrases
- Japanese: meeting information location/details-entry phrases
- Chinese: meeting information, meeting number, meeting link phrases

Important adjacent route seen in probes:

- `ringcentral.video.settings.background` still incorrectly catches
  `Open encryption settings`, returns `can_operate=True`, and creates an
  interrupt.

## Existing Q&A

Existing Meeting information privacy Q&A:

- Question: `How should AiPresenter handle meeting IDs and links safely?`
- Related entrypoint: `ringcentral.video.top.meeting-info`
- English prompt coverage includes copy/read/paste meeting link, meeting URL,
  meeting ID, dial-in details, host info, and meeting details.
- Localized question and answer coverage exists for `es`, `ja`, and `zh`.
- Answer treats meeting IDs, links, dial-in details, and host info as private.

Current dirty tree also has a newly added encryption Q&A:

- Question: `Where can I verify meeting encryption status?`
- Related entrypoint: `ringcentral.video.top.meeting-info`
- English prompt coverage currently includes:
  - `Is this meeting encrypted?`
  - `Is the meeting encrypted?`
  - `Can you check encryption status?`
  - `Show encryption status`
  - `Show meeting encryption status`
  - `Where can I see encryption?`
  - `Where is end-to-end encryption?`
  - `Is end-to-end encryption enabled?`
- Localized question and answer coverage exists for `es`, `ja`, and `zh`.
- Answer starts with `Encryption status:` and avoids claiming enabled/disabled
  state unless visible status is verified.

This current dirty implementation is mostly aligned with the Cycle 170
candidate, but it does not yet cover `Open encryption settings`.

## Current Routing Probes

Read-only probe path: load `packages/ringcentral-video.yaml`, call
`answer_question(...)`, then check `create_question_interrupt_step(...)`.

| Prompt | Current route | `can_operate` | Interrupt | Notes |
| --- | --- | --- | --- | --- |
| `meeting information` | `ringcentral.video.top.meeting-info` | `False` | no | Generic entrypoint answer. |
| `where is the meeting ID` | `ringcentral.video.top.meeting-info` | `False` | no | Generic entrypoint answer. |
| `Copy meeting link` | `ringcentral.video.top.meeting-info` | `False` | no | Privacy Q&A answer. |
| `Is this meeting encrypted?` | `ringcentral.video.top.meeting-info` | `False` | no | Encryption Q&A answer. |
| `Is the meeting encrypted?` | `ringcentral.video.top.meeting-info` | `False` | no | Encryption Q&A answer. |
| `Can you check encryption status?` | `ringcentral.video.top.meeting-info` | `False` | no | Encryption Q&A answer. |
| `Can you verify encryption?` | `ringcentral.video.top.meeting-info` | `False` | no | Routes safely by Q&A overlap, not exact prompt coverage. |
| `Can you verify end-to-end encryption?` | `ringcentral.video.top.meeting-info` | `False` | no | Routes safely now; add explicit test coverage. |
| `Show encryption status` | `ringcentral.video.top.meeting-info` | `False` | no | Encryption Q&A answer. |
| `Show meeting encryption status` | `ringcentral.video.top.meeting-info` | `False` | no | Encryption Q&A answer. |
| `Where can I see encryption?` | `ringcentral.video.top.meeting-info` | `False` | no | Encryption Q&A answer. |
| `Where is end-to-end encryption?` | `ringcentral.video.top.meeting-info` | `False` | no | Encryption Q&A answer. |
| `Is end-to-end encryption enabled?` | `ringcentral.video.top.meeting-info` | `False` | no | Encryption Q&A answer. |
| `Open encryption settings` | `ringcentral.video.settings.background` | `True` | yes | Unsafe wrong route; should become answer-only Meeting information Q&A. |

Localized exact probes for the new Chinese, Japanese, and Spanish encryption
Q&A prompts route to `ringcentral.video.top.meeting-info`, stay
`can_operate=False`, and create no interrupt. A broader Chinese phrase meaning
`meeting encryption status` still returns no match; decide whether that belongs
in this slice or a later localized-alias slice.

## Count Movements

Current dirty tree after the concurrent encryption Q&A addition:

- Package-owned aliases: unchanged at `165`
- Q&A question prompts: `178 -> 190`
- Q&A alias-overlap prompt count: `178 -> 190`
- Q&A alias substring risk: unchanged at `11`
- Localized Q&A coverage: `15/15 -> 16/16` for `zh`, `ja`, and `es`
- Demo narration coverage remains `51/51`

If the remaining `Open encryption settings` prompt is added to the existing
encryption Q&A item, expected additional movement is:

- Q&A question prompts: `190 -> 191`
- Q&A alias-overlap prompt count: `190 -> 191`
- Localized Q&A item coverage remains `16/16`
- Package-owned alias count remains `165`

If the team also wants exact package prompt coverage for the two currently
safe overlap routes, add `Can you verify encryption?` and
`Can you verify end-to-end encryption?`; that would move prompt counts to
`193` instead of `191`.

## Expected Test Updates

Already present in the dirty tree:

- `tests/unit/test_questions.py` adds
  `test_ringcentral_encryption_status_questions_stay_meeting_info_answer_only`.
- `tests/unit/test_questions.py` adds
  `test_ringcentral_localized_encryption_status_questions_are_answer_only`.
- `tests/unit/test_diagnostics.py` already changed Q&A duplicate/overlap
  expectations from `178` to `190`.
- `tests/unit/test_cli.py::test_doctor_loads_profile_package_and_flow`
  already changed those doctor-output counts from `178` to `190`.

Still expected:

- Add `Open encryption settings` to the encryption-status Q&A prompts and the
  English encryption routing test. Assert it routes to
  `ringcentral.video.top.meeting-info`, is non-operable, creates no interrupt,
  and does not answer as `Background settings:`.
- Add explicit test rows for `Can you verify encryption?` and
  `Can you verify end-to-end encryption?` so the old Leave/background drift
  cannot regress silently.
- Update remaining localization count assertions from `15/15` to `16/16`:
  - `tests/unit/test_diagnostics.py` lines around the zh/es/ja
    `require_localization` checks.
  - `tests/unit/test_cli.py` localization-report checks for zh, ja, es,
    Spanish language alias normalization, Spanish `--require-complete`,
    Japanese `--require-complete`, and doctor `--require-localization`
    Spanish output.
- If `Open encryption settings` is added as a Q&A prompt, update diagnostics
  and doctor prompt-count assertions from `190` to `191` (or `193` if the two
  verify prompts are also added as exact localized questions).

## Likely Files Touched

No runtime matcher changes look necessary. The likely implementation files are:

- `packages/ringcentral-video.yaml`
- `tests/unit/test_questions.py`
- `tests/unit/test_diagnostics.py`
- `tests/unit/test_cli.py`

Do not touch `.coverage`. Coordinate with the current dirty edits before
overwriting or restaging any package/test changes.

## Verification Performed

Focused no-coverage command:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_encryption_status_questions_stay_meeting_info_answer_only tests\unit\test_questions.py::test_ringcentral_localized_encryption_status_questions_are_answer_only tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_cli.py::test_localization_report_outputs_ringcentral_chinese_coverage tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

Result: `14 passed, 3 failed`.

Passing in that slice:

- New English encryption routing test.
- New localized encryption routing test.
- Q&A diagnostics prompt-count checks at `190`.
- Doctor package/flow count output at `190`.

Failing in that slice:

- `tests/unit/test_cli.py::test_localization_report_outputs_ringcentral_chinese_coverage`
- `tests/unit/test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage`
- `tests/unit/test_cli.py::test_localization_report_outputs_complete_spanish_package`

All three failed only because they still expect `15/15` localized Q&A
questions/answers while current output is `16/16`.

## Blockers / Risks

- Active concurrent edits are already present; do not revert or overwrite them.
- `Open encryption settings` currently routes to operable Background settings.
  This is the remaining privacy/safety blocker for the candidate.
- Several CLI/diagnostics localization assertions still expect `15/15` even
  though the package now reports `16/16`.
- The answer must not claim encryption is enabled, disabled, or verified
  without visible UI evidence.
- Avoid broad aliases such as `encryption`, `security`, or `settings`; exact
  Q&A prompts keep unrelated security/settings questions from being stolen by
  Meeting information.
