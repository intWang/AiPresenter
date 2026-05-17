# Cycle 194 Test Review

Date: 2026-05-17

## RED Verification

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_controller.py::test_scanned_running_app_metadata_can_clear_scan_result_state tests\unit\test_controller.py::test_scanned_running_app_metadata_clears_when_selection_is_invalidated tests\unit\test_controller.py::test_scanned_running_app_metadata_keeps_current_scan_after_matching_refresh tests\unit\test_controller.py::test_scanned_running_app_metadata_clears_when_refresh_removes_all_windows
```

Result before implementation: collection failed because `_ScannedRunningAppMetadata` did not exist.

## Focused Verification

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_controller.py::test_scanned_running_app_metadata_can_clear_scan_result_state tests\unit\test_controller.py::test_scanned_running_app_metadata_clears_when_selection_is_invalidated tests\unit\test_controller.py::test_scanned_running_app_metadata_keeps_current_scan_after_matching_refresh tests\unit\test_controller.py::test_scanned_running_app_metadata_clears_when_refresh_removes_all_windows
```

Result: `4 passed`.

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_controller.py tests\unit\test_controller_view_model.py -k "running_app or scan"
```

Result: `15 passed, 89 deselected`.

## Required Before Commit

Run full repository verification and cached-diff checks:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m mypy src tests
git diff --cached --check
git diff --cached -- .coverage
git diff --cached --stat
git diff --cached --name-only
```
