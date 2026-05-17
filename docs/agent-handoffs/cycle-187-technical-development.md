# Cycle 187 Technical Development: Sanitize Controller Status Errors

Date: 2026-05-17

## Files Changed

- `src/ai_presenter/runtime/controller.py`
  - Adds `describe_controller_error(...)`.
  - Adds `describe_controller_action_error(...)`.
  - Uses the public controller error formatter in `resolve_controller_status(...)`.
  - Sanitizes app refresh, scan, start, and voice asset checker exception paths.
- `tests/unit/test_controller.py`
  - Adds helper and status tests for private runtime errors.
  - Preserves known public `Unknown demo flow: ...` behavior.
  - Verifies voice checker exception text does not enter readiness details.
- `tests/unit/test_controller_view_model.py`
  - Adds a sanitized run-status operator summary sentinel.
- `docs/knowledge/ai-presenter-maintenance.md`
  - Documents controller exception text as private by default.

## Behavior Added

Arbitrary runtime exceptions now surface as:

```text
Error: Controller error: action could not continue safely.
Scan error: action could not continue safely.
Start error: action could not continue safely.
App refresh error: action could not continue safely.
```

Known public flow configuration errors continue to surface:

```text
Error: Unknown demo flow: missing-flow. Available flows: demo
```

Voice asset checker exceptions now use:

```text
voice asset check failed; retry or check local voice setup.
```

## Focused Verification

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_controller.py::test_controller_voice_readiness_converts_checker_exception_to_failure tests\unit\test_controller.py::test_describe_controller_error_hides_private_runtime_exception_text tests\unit\test_controller.py::test_describe_controller_error_preserves_known_public_flow_error tests\unit\test_controller.py::test_describe_controller_action_error_hides_exception_text tests\unit\test_controller.py::test_resolve_controller_status_hides_private_runtime_error_text tests\unit\test_controller.py::test_resolve_controller_status_uses_unquoted_key_error_message tests\unit\test_controller_view_model.py::test_operator_summary_uses_privacy_safe_run_status
```

Result: `7 passed`.
