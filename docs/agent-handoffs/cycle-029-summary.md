# Cycle 029 Summary: Stable RingCentral Validation Target IDs

Date: 2026-05-16
Role: orchestration summary

## Objective

Make RingCentral validation target IDs stable for operator commands, subagent handoffs, and runbooks by moving canonical IDs into the checklist instead of deriving them from mutable priority and label text.

## Inputs

- Demand analysis: `docs/agent-handoffs/cycle-029-demand-analysis.md`
- Technical scan: `docs/agent-handoffs/cycle-029-technical-scan.md`
- Review: `docs/agent-handoffs/cycle-029-review.md`
- Design: `docs/superpowers/specs/2026-05-16-stable-validation-target-ids-design.md`
- Plan: `docs/superpowers/plans/2026-05-16-stable-validation-target-ids.md`

## Changes

- Added optional `Target ID` parsing to `src/ai_presenter/acceptance/validation_targets.py`.
- `validation-targets` now prefers explicit `Target ID` cells when the column is present.
- Checklists without a `Target ID` column still fall back to the existing generated ID behavior.
- If a table has `Target ID` but a row leaves it blank, discovery fails with `blank validation target id for <route>`.
- Duplicate resolved IDs still fail through the existing uniqueness check.
- Added `Target ID` columns to RingCentral `Priority Checklist` and `Do Not Execute Yet` tables.
- RingCentral checklist IDs now use stable `rcv-*` names without priority or blocked state:
  - `rcv-add-coworkers-modal`
  - `rcv-controller-chat-question`
  - `rcv-recording`
  - `rcv-leave-end-meeting`
- Blocked rows remain opt-in via `--include-blocked`; only their IDs changed from generated `blocked-*` names to status-neutral `rcv-*` names.

## Verification

Parser RED before implementation:

```text
3 failed, 1 passed
```

Failures confirmed the parser ignored `Target ID`, did not reject blank explicit IDs, and did not catch duplicate explicit IDs because explicit IDs were not being read.

Focused parser GREEN:

```powershell
.\.venv\Scripts\python -m pytest tests\unit\test_validation_targets.py::test_discover_validation_targets_uses_explicit_target_ids tests\unit\test_validation_targets.py::test_discover_validation_targets_rejects_duplicate_validation_target_ids tests\unit\test_validation_targets.py::test_discover_validation_targets_rejects_blank_explicit_target_id tests\unit\test_validation_targets.py::test_discover_validation_targets_falls_back_to_generated_ids_without_target_id_header --no-cov
```

```text
4 passed in 1.34s
```

Affected validation/CLI tests:

```powershell
.\.venv\Scripts\python -m pytest tests\unit\test_validation_targets.py tests\unit\test_cli.py::test_validation_targets_lists_ringcentral_targets tests\unit\test_cli.py::test_validation_targets_detail_outputs_draft_command tests\unit\test_cli.py::test_validation_targets_rejects_unknown_target_with_available_ids tests\unit\test_cli.py::test_validation_targets_include_blocked_lists_do_not_execute_routes --no-cov
```

```text
17 passed in 5.15s
```

Manual CLI smoke:

```powershell
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video --priority P0
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video --target rcv-add-coworkers-modal
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video --include-blocked
```

Results:

- P0 output lists `rcv-add-coworkers-modal` and `rcv-controller-chat-question`.
- Detail output for `rcv-add-coworkers-modal` still includes Add coworkers cleanup, privacy notes, evidence, and draft command.
- Blocked output lists `rcv-recording` and `rcv-leave-end-meeting` only when `--include-blocked` is supplied.

Full verification:

```powershell
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\python -m mypy src tests
.\.venv\Scripts\python -m ruff check src tests
git diff --check
```

```text
522 passed, 1 warning in 134.41s
Success: no issues found in 80 source files
All checks passed!
git diff --check: exit 0 with existing LF-to-CRLF warnings only
```

The pytest warning is the existing pywinauto STA COM threading warning.

## Review Result

Cycle 029 review found no blockers. It specifically checked explicit parsing, fallback compatibility, blank/duplicate failures, `rcv-*` checklist IDs, and blocked-row opt-in behavior.

Residual risk: mixed flow-plus-entrypoint targets still emit a draft command with checklist-target context only. That is existing behavior and was left unchanged in this ID-stability slice.

## Recommended Next Slice

Consider improving mixed flow-plus-entrypoint acceptance draft guidance so targets like `rcv-controller-chat-question` can produce a clearer draft command or helper text for the combined flow/question workflow.
