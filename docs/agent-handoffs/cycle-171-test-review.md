# Cycle 171 Test Review

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Role: Cycle171 test-review handoff

## Verdict

No blocking findings.

The current dirty diff covers the requested Cycle171 routing behavior:

- Bare `status`, `security`, `secure`, and `verify` no longer route to the
  encryption-status Q&A.
- Action-like `Read`, `Copy`, and `Share` prompts for meeting
  information/details route to the Meeting information privacy Q&A.
- `share secure`, `share verify`, `copy status`, `copy security`,
  `copy secure`, and `copy verify` route to the encryption-status Q&A,
  stay answer-only, do not route to Share, and create no interrupt.
- Diagnostics and doctor expectations are updated to `212` Q&A question
  prompts.

## Findings

Blocking: none.

Non-blocking test-hardening finding: the broad-word matcher guard is correct for
the current diff, but it is narrow. `src/ai_presenter/runtime/questions.py`
blocks exact user prompts in `_BROAD_QA_FRAGMENT_TOKENS` only on the
`normalized_question in candidate.normalized_question` fragment path. The
reverse substring path and token-overlap path remain available. This is fine
because the package does not add exact one-word Q&A prompts for `status`,
`security`, `secure`, or `verify`, but a future exact one-word Q&A row could
still shadow longer prompts unless the matcher or tests are expanded at that
time.

Non-blocking assertion-strength finding: the encryption-status tests now check
route, no interrupt, no Share route, `Encryption status:` answer copy, no
`https://`, no `ringcentral.com`, no sample meeting ID, and no
copied/read/dialed claims. A future hardening pass could add focused negatives
for broader URL forms and outcome claims such as "I shared", "I opened", or
"I verified" while preserving the required caveat phrase `visible status is
verified`.

## Reviewed Diff

- `packages/ringcentral-video.yaml`
  - Adds Meeting information privacy prompts:
    `Read meeting information`, `Read meeting information aloud`,
    `Copy meeting information`, `Share meeting information`,
    `Copy meeting details`, and `Share meeting details`.
  - Adds encryption-status prompts:
    `Share secure`, `Share verify`, `Copy status`, `Copy security`,
    `Copy secure`, and `Copy verify`.
- `src/ai_presenter/runtime/questions.py`
  - Adds `_BROAD_QA_FRAGMENT_TOKENS = {"secure", "security", "status", "verify"}`.
  - Rejects those exact one-word prompts from Q&A fragment matching.
- `tests/unit/test_questions.py`
  - Adds privacy-Q&A rows for Meeting information/details action prompts.
  - Adds no-match coverage for bare broad status/security words.
  - Adds encryption-status rows for Share/Copy status/security/secure/verify
    prompt variants.
- `tests/unit/test_cli.py` and `tests/unit/test_diagnostics.py`
  - Update Q&A prompt-count expectations from `200` to `212`.

The dirty `.coverage` file was present before this review and was not touched
intentionally. I did not edit code, tests, package YAML, staging, commits, or
coverage artifacts.

## Route Probe

Read-only probe against the current dirty tree confirmed:

| Prompt family | Result |
| --- | --- |
| `status`, `security`, `secure`, `verify` | no entrypoint, `can_operate=False`, no interrupt, no encryption Q&A |
| `Read/Copy/Share meeting information/details` | `ringcentral.video.top.meeting-info`, Meeting information privacy Q&A, `can_operate=False`, no interrupt |
| `Share secure`, `Share verify` | `ringcentral.video.top.meeting-info`, encryption-status Q&A, `can_operate=False`, no interrupt |
| `Copy status/security/secure/verify` | `ringcentral.video.top.meeting-info`, encryption-status Q&A, `can_operate=False`, no interrupt |
| `Share status`, `Share security` | `ringcentral.video.top.meeting-info`, encryption-status Q&A, `can_operate=False`, no interrupt |
| `Security status`, `Is the meeting secure?`, `Can you verify meeting security?`, `Share meeting security status` | `ringcentral.video.top.meeting-info`, encryption-status Q&A, `can_operate=False`, no interrupt |

## Privacy Assertions

Meeting information privacy tests assert:

- route is `ringcentral.video.top.meeting-info`
- `can_operate is False`
- no question interrupt
- privacy answer copy is used instead of the thin `Meeting information:`
  entrypoint fallback
- no `https://`, no `ringcentral.com`, no sample `123456789`
- no copied or dialed outcome claim

Encryption-status tests assert:

- route is `ringcentral.video.top.meeting-info`
- route is not Share, Participants, Leave, Network quality, Background
  settings, More settings, or RingCentralDevelop
- `can_operate is False`
- no question interrupt
- answer starts with `Encryption status:`
- answer keeps the `visible status is verified` caveat
- no thin `Meeting information:` entrypoint fallback
- no `https://`, no `ringcentral.com`, no sample `123456789`
- no copied, read, or dialed outcome claim

## Verification

Focused pytest command used coverage disabled with `--no-cov` and pytest cache
disabled with `-p no:cacheprovider`:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first tests\unit\test_questions.py::test_ringcentral_bare_status_words_do_not_match_encryption_status tests\unit\test_questions.py::test_ringcentral_encryption_status_questions_stay_meeting_info_answer_only tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

Result: `58 passed in 12.03s`.

```powershell
git diff --check -- src/ai_presenter/runtime/questions.py packages/ringcentral-video.yaml tests/unit/test_questions.py tests/unit/test_cli.py tests/unit/test_diagnostics.py
```

Result: exit `0`; only LF-to-CRLF working-copy warnings were printed.

## Status

Blocking status: no blocking issues found.

Non-blocking status: preserve the matcher-risk note for any future exact
one-word Q&A prompts, and consider adding broader privacy/outcome negative
assertions in a later hardening pass.
