# Cycle 124 Follow-up Review

Date: 2026-05-16

## Scope

Follow-up after the Cycle 124 review found one stale test assertion.

## Resolution

The stale assertion in `test_doctor_require_localization_language_overrides_runtime_voice` was updated to match the new Spanish package-complete state:

- localization check is now expected to be `[OK] localization: required es localization complete`;
- detail includes `51/51 demo steps`;
- runtime language support is still expected to fail;
- the supported runtime voice selected by `--language zh-CN` still reports Chinese voice readiness.

This closes the review P1 without changing runtime Spanish support.

## Verification

Focused follow-up:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_doctor_require_localization_language_overrides_runtime_voice tests\unit\test_cli.py::test_doctor_require_localization_accepts_package_only_spanish_language tests\unit\test_diagnostics.py::test_diagnostics_require_localization_flags_package_only_runtime_language tests\unit\test_diagnostics.py::test_diagnostics_runtime_language_support_stays_separate_after_package_localization_complete
```

Result: `4 passed`.

Full verification:

- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests` -> `793 passed, 1 warning`.
- `.\.venv\Scripts\ruff check --no-cache .` -> passed.
- `.\.venv\Scripts\mypy --no-incremental src tests` -> passed.
- `git diff --check` -> passed with expected CRLF warnings.

## Decision

Pass. Remaining submit hygiene item: keep `.coverage` unstaged.
