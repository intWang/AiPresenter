# Cycle 042 Summary: Direct Acceptance Draft Safety

Date: 2026-05-16
Cycle: 042
Commit target: `fix: reject no-step acceptance drafts`

## Outcome

Cycle 042 hardened direct `acceptance-draft --entrypoint` requests.

Entry points with no executable `openSteps`, such as Recording and Leave, now fail before any manual acceptance draft is printed or written. Flow-only drafts remain supported, so tours can still document explain-only steps without selecting them as direct live-operation targets.

## Files Changed

- `src/ai_presenter/acceptance/manual_record.py`
- `tests/unit/test_acceptance_manual_record.py`
- `tests/unit/test_cli.py`
- `docs/agent-handoffs/cycle-042-demand-analysis.md`
- `docs/agent-handoffs/cycle-042-technical-scan.md`
- `docs/agent-handoffs/cycle-042-review.md`
- `docs/agent-handoffs/cycle-042-summary.md`
- `docs/superpowers/specs/2026-05-16-direct-acceptance-draft-safety-design.md`
- `docs/superpowers/plans/2026-05-16-direct-acceptance-draft-safety.md`

## Behavior

- Direct no-step entrypoint draft requests fail with a clear refusal.
- Refusals mention no executable open steps and separate confirmation workflow.
- Refused requests do not print draft text.
- Refused requests do not write output files.
- Executable direct entrypoints still render and write drafts.
- Flow-only drafts still render.

## TDD And Review

Red phase:

- Direct Leave/Recording drafts still rendered and could write files.

Green phase:

- Added `_reject_direct_no_step_entrypoint()` in `manual_record.py`.
- Replaced the warning-only unit test with a refusal test.
- Added CLI refusal and no-output-file tests.

Review:

- Reviewer found no issues.
- Residual risk: benign no-step direct entrypoints are also rejected; future read-only draft mode can address that explicitly.

## Verification

Focused verification:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_acceptance_manual_record.py tests\unit\test_cli.py::test_acceptance_draft_outputs_entrypoint_template tests\unit\test_cli.py::test_acceptance_draft_outputs_flow_template tests\unit\test_cli.py::test_acceptance_draft_rejects_no_open_step_entrypoint tests\unit\test_cli.py::test_acceptance_draft_refusal_does_not_write_output_file tests\unit\test_cli.py::test_acceptance_draft_can_write_to_output_file tests\unit\test_cli.py::test_validation_targets_blocked_target_omits_draft_command
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\acceptance\manual_record.py tests\unit\test_acceptance_manual_record.py tests\unit\test_cli.py
.\.venv\Scripts\mypy --no-incremental src\ai_presenter\acceptance\manual_record.py tests\unit\test_acceptance_manual_record.py tests\unit\test_cli.py
```

Result:

- `14 passed`
- `All checks passed!`
- `Success: no issues found in 3 source files`

Full verification:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
.\.venv\Scripts\ruff check --no-cache .
.\.venv\Scripts\mypy --no-incremental src tests
git diff --check
```

Result:

- `572 passed, 1 warning`
- `All checks passed!`
- `Success: no issues found in 81 source files`
- `git diff --check` reported only LF-to-CRLF working-copy warnings; no whitespace errors.

## Next Handoff Ideas

- Add an explicit read-only/explain-only draft mode for non-executable context routes.
- Continue tightening confirmation-required RingCentral controls around direct CLI surfaces.
