# Cycle 039 Technical Scan

Date: 2026-05-16
Role: technical scan
Scope: read-only technical scan. No files were edited by the technical agent.

## Recommended Implementation

Add the diagnostic in `src/ai_presenter/runtime/diagnostics.py`, inside `_diagnose_material_package()`.

Do not modify `src/ai_presenter/runtime/questions.py` or `src/ai_presenter/packages/models.py`. `MaterialPackage.entrypoint_question_aliases` already exposes the normalized alias, language, and entrypoint ID needed for the check.

## Files

- Modify: `src/ai_presenter/runtime/diagnostics.py`
- Modify: `tests/unit/test_diagnostics.py`
- Modify: `tests/unit/test_cli.py`
- Add Cycle 039 handoff, spec, plan, review, and summary docs.

## Design Notes

- Group aliases by `normalized_alias`, not by `(language, normalized_alias)`, because runtime matching currently ignores alias language.
- Detect conflicts only when a normalized alias maps to more than one unique entrypoint ID.
- Keep same-entrypoint duplicate aliases non-fatal and non-warning for this cycle.
- Return `OK` for healthy packages and `WARN` for conflicts.
- Keep output compact by previewing the first conflict and summarizing additional conflicts.

## Test Plan

- Diagnostics-level OK for the real RingCentral package.
- Diagnostics-level WARN for a minimal package with two entrypoints sharing a normalized alias.
- Diagnostics-level OK for duplicate aliases repeated on the same entrypoint.
- CLI-level WARN for a temporary duplicate-alias package, with exit code `0`.

## Verification

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py tests\unit\test_cli.py tests\unit\test_questions.py tests\unit\test_material_packages.py
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\runtime\diagnostics.py tests\unit\test_diagnostics.py tests\unit\test_cli.py
.\.venv\Scripts\mypy --no-incremental src\ai_presenter\runtime\diagnostics.py tests\unit\test_diagnostics.py tests\unit\test_cli.py
```

