# Cycle 042 Technical Scan

Date: 2026-05-16
Role: technical scan
Scope: read-only scan. No files were edited by the technical agent.

## Finding

`manual_record.py` already warns for entrypoints with no `openSteps`, but direct `acceptance-draft --entrypoint` still succeeds and renders a manual acceptance template.

The remaining gap after Cycle 041 is direct invocation safety.

## Files

- Modify: `src/ai_presenter/acceptance/manual_record.py`
- Modify: `tests/unit/test_acceptance_manual_record.py`
- Modify: `tests/unit/test_cli.py`
- Add Cycle 042 handoff, spec, plan, review, and summary docs.

## Implementation Sketch

Add a guard in `build_acceptance_target_summary()` after resolving the entrypoint:

```python
if entrypoint is not None and not entrypoint.open_steps:
    raise ValueError(
        f"Entrypoint {entrypoint.id} has no executable open steps; "
        "direct acceptance drafts require a separate confirmation workflow before live execution."
    )
```

Flow-only drafts remain supported because they do not select a direct entrypoint.

## Verification

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_acceptance_manual_record.py tests\unit\test_cli.py::test_acceptance_draft_rejects_no_open_step_entrypoint tests\unit\test_cli.py::test_acceptance_draft_refusal_does_not_write_output_file tests\unit\test_cli.py::test_acceptance_draft_outputs_entrypoint_template tests\unit\test_cli.py::test_acceptance_draft_outputs_flow_template tests\unit\test_cli.py::test_validation_targets_blocked_target_omits_draft_command
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\acceptance\manual_record.py tests\unit\test_acceptance_manual_record.py tests\unit\test_cli.py
.\.venv\Scripts\mypy --no-incremental src\ai_presenter\acceptance\manual_record.py tests\unit\test_acceptance_manual_record.py tests\unit\test_cli.py
```

