# Cycle 211 Technical Scan

Date: 2026-05-17
Cycle: 211
Role: Technical scan subagent

## Implementation Map

- `src/ai_presenter/cli.py`
  - Use `len(loaded_flow.steps)` in the existing `Loaded flow` echo for
    `demo`.
  - Do the same for `controller`.
- `tests/unit/test_cli.py`
  - Tighten `test_demo_dry_run_loads_profile_package_and_flow`.
  - Tighten `test_controller_dry_run_loads_profile_package_and_flow`.

## Focused Verification

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests/unit/test_cli.py::test_demo_dry_run_loads_profile_package_and_flow tests/unit/test_cli.py::test_controller_dry_run_loads_profile_package_and_flow tests/unit/test_cli.py::test_demo_dry_run_reports_normalized_voice_aliases tests/unit/test_cli.py::test_demo_reports_available_flows_when_flow_is_missing tests/unit/test_cli.py::test_controller_reports_available_flows_when_flow_is_missing tests/unit/test_cli.py::test_demo_openai_profile_accepts_spanish_dry_run tests/unit/test_cli.py::test_controller_openai_profile_accepts_spanish_dry_run tests/unit/test_cli.py::test_flows_lists_material_package_demo_flows
```

## Risk Notes

- The `Loaded flow` line is printed before the dry-run branch, so the count also
  appears for real runs. This preserves the existing loading summary shape while
  adding detail.
- Unsupported voice/profile failures will still print loaded-flow information
  before validation, now with a count. That follows the existing ordering.
- Keep `.coverage` unstaged because it is test-run output.
