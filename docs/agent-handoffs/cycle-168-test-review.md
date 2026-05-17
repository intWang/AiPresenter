# Cycle 168 Test Review: Meeting Security And Lock Prompts

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Role: Cycle168 test-review subagent

## Findings

No blocking findings.

The current Cycle168 diff covers the intended narrow host/security prompt slice:
five exact English Q&A prompts were added under the existing participant host
controls answer, and the focused tests pin the safety behavior that matters for
this change.

## Reviewed Diff

- `packages/ringcentral-video.yaml`: adds `Unlock the meeting`, `Change meeting
  security`, `Where are security settings?`, `Open meeting security settings`,
  and `Meeting security settings` under `Where are host controls for
  participants?`.
- `tests/unit/test_questions.py`: extends
  `test_ringcentral_participant_host_action_requests_stay_answer_only` for the
  five prompts.
- `tests/unit/test_diagnostics.py` and `tests/unit/test_cli.py`: update Q&A
  prompt totals from `173` to `178` for duplicate and alias-overlap diagnostics.
- Reviewed Cycle168 handoffs:
  `docs/agent-handoffs/cycle-168-demand-analysis.md`,
  `docs/agent-handoffs/cycle-168-risk-scan.md`, and
  `docs/agent-handoffs/cycle-168-technical-scan.md`.

## Assertion Coverage Checked

The focused question test asserts the new prompts remain answer-only:

- `response.entrypoint_id is None`
- `response.entrypoint_id != "ringcentral.video.toolbar.participants"`
- `response.can_operate is False`
- `create_question_interrupt_step(package, response) is None`

It also asserts the response does not fall into unsafe or wrong fallback copy:

- no `Participants panel:` entrypoint fallback label
- no `Background settings:` fallback label
- no `I could not find a matching control` no-match fallback

The expected host/security answer text is pinned through:

- `Do not mute others`
- `lock the meeting`
- `change security settings`
- `explicitly asks`
- `verified`

Diagnostics coverage moves both Q&A count strings together to `178`, and the
doctor test also keeps the unchanged alias substring-risk count at `11`.

## Focused Verification Run

Coverage was disabled with `--override-ini addopts=` and pytest cache disabled
with `-p no:cacheprovider`.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_participant_host_action_requests_stay_answer_only tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

Result: `11 passed in 2.58s`.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package
```

Result: `1 passed in 0.66s`.

```powershell
git diff --check -- packages\ringcentral-video.yaml tests\unit\test_questions.py tests\unit\test_diagnostics.py tests\unit\test_cli.py docs\agent-handoffs\cycle-168-demand-analysis.md docs\agent-handoffs\cycle-168-risk-scan.md docs\agent-handoffs\cycle-168-technical-scan.md
```

Result: exit `0`; only existing LF-to-CRLF working-copy warnings were printed.

`.coverage` was already dirty before this review. Its SHA-256 stayed unchanged
before and after focused pytest runs:

`0C21AF2DF37FCF928691294CE35A07A4D36A7EA98BB757525EA7A38B976B90CC`

## Backlog Boundary

Encryption-status prompts should remain a future Meeting information privacy
slice, as described in the demand-analysis and risk-scan handoffs. They should
not be folded into this host/security prompt diff.

Full-screen routing should also remain future backlog, as described in the
technical-scan handoff. It changes entrypoint alias behavior and should not be
mixed with this Q&A prompt-count update.
