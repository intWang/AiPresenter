# Cycle 041 Technical Scan

Date: 2026-05-16
Role: technical scan
Scope: read-only scan. No files were edited by the technical agent.

## Finding

Blocked targets are parsed correctly with `priority="P3"`, `current_state="Do not execute"`, and `blocked_reason`, but `_render_target_block()` appends `draft:` whenever `include_draft_command` is true.

That means rendered operator output currently includes runnable-looking `acceptance-draft` commands for Recording and Leave.

## Files

- Modify: `src/ai_presenter/acceptance/validation_targets.py`
- Modify: `tests/unit/test_validation_targets.py`
- Modify: `tests/unit/test_cli.py`
- Add Cycle 041 handoff, spec, plan, review, and summary docs.

## Implementation Sketch

In `_render_target_block()`:

```python
if target.blocked_reason is not None:
    lines.append(f"  blocked: {target.blocked_reason}")
if include_draft_command and target.blocked_reason is None:
    lines.append(f"  draft: {acceptance_draft_command(package_id, target)}")
```

Keep `acceptance_draft_command()` unchanged. The issue is rendered operator guidance, not the pure command builder.

## Verification

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_validation_targets.py tests\unit\test_cli.py::test_validation_targets_include_blocked_lists_do_not_execute_routes tests\unit\test_cli.py::test_validation_targets_detail_outputs_draft_command tests\unit\test_cli.py::test_validation_targets_mixed_target_outputs_flow_and_entrypoint_draft_command
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\acceptance\validation_targets.py tests\unit\test_validation_targets.py tests\unit\test_cli.py
.\.venv\Scripts\mypy --no-incremental src\ai_presenter\acceptance\validation_targets.py tests\unit\test_validation_targets.py tests\unit\test_cli.py
```

