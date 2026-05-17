# Cycle 192 Test Review

Date: 2026-05-17

## RED Verification

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_controller.py::test_running_app_scan_telemetry_logs_bounded_success_metadata tests\unit\test_controller.py::test_running_app_scan_telemetry_logs_bounded_error_metadata tests\unit\test_cli.py::test_package_language_alias_normalization_is_documented
```

Result before implementation: all three failed. The scan helper did not exist, and
`language-lifecycle.md` still reported Spanish Q&A as `12/12`.

## Focused Verification

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_controller.py::test_running_app_scan_telemetry_logs_bounded_success_metadata tests\unit\test_controller.py::test_running_app_scan_telemetry_logs_bounded_error_metadata tests\unit\test_cli.py::test_package_language_alias_normalization_is_documented
```

Result: `3 passed`.

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_controller.py -k "scan"
```

Result: `6 passed, 71 deselected`.

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_runtime_logging.py tests\unit\test_controller_session.py tests\unit\test_temporary_package.py
```

Result: `33 passed`.

```powershell
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --require-localization --localization-language es
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
```

Result: doctor reported `14 ok, 1 info, 0 warnings, 0 failed`; localization report showed
`51/51` demo steps, `16/16` Q&A questions, and `16/16` Q&A answers.

## Independent Review

An independent review found no P0-P3 findings.

- Telemetry fields are bounded metadata only.
- Window title, control names, and exception text are not logged.
- The error path logs telemetry and re-raises for existing controller error handling.
- UI status uses package id, counts, and duration instead of the window title.
- Spanish lifecycle count correction is documented and guarded by tests.
- `.coverage` was still modified but unstaged.

Reviewer verification included `git diff --check`, scope checks for no package/routing/evidence
changes, focused scan tests, and the Spanish localization report.

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
