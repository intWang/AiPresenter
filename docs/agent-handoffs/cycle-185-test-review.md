# Cycle 185 Test Review

Date: 2026-05-17

## Red/Green

Initial focused tests failed because no `question policy` diagnostic existed:

```text
3 failed
```

After adding `_diagnose_question_policy_coverage(...)`, the focused test set passed:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_question_policy_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_no_answer_only_question_policy tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

Result: `3 passed`.

## Manual Smoke

```powershell
$env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
```

Result: exit code `0`; `question policy` reports `2/27` answer-only entrypoints.

Focused diagnostics/CLI verification:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_diagnostics.py tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

Result: `46 passed`.

Package localization verification:

```powershell
$env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language zh --require-complete
$env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
$env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
```

Result: zh, ja, and es each report `51/51` demo steps, `16/16` Q&A questions, and `16/16` Q&A answers localized.

An attempted `doctor --language ja --require-localization` with the local Windows SAPI profile failed at voice compatibility, and an attempted OpenAI-profile Spanish doctor failed because OpenAI environment variables are not set. Those failures are provider/voice gates, not package localization failures.

## Independent Risk Review

- No must-fix privacy or safety issue in the diagnostic slice.
- `.coverage` is the main staging risk and must stay unstaged.
- Preserve zh/ja/es localization checks before commit.

## Required Before Commit

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m mypy src tests
git diff --cached --check
git diff --cached -- .coverage
```
