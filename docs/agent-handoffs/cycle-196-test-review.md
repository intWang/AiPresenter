# Cycle 196 Test Review

Date: 2026-05-17

## RED Verification

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ai_presenter_maintenance_playbook_preserves_optimization_protocol
```

Result before implementation: failed because `## Continuous Optimization Cycle Protocol` was not
present in the playbook.

## Focused Verification

To run after implementation:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ai_presenter_maintenance_playbook_preserves_optimization_protocol
```

## Required Before Commit

Run the standard final gate and cached-diff checks:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m mypy src tests
git diff --cached --check
git diff --cached -- .coverage
git diff --cached --stat
git diff --cached --name-only
```
