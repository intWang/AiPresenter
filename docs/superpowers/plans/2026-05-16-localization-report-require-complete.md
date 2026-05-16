# Localization Report Require Complete Plan

Date: 2026-05-16
Cycle: 028

## Steps

1. Add failing helper tests for `required_localization_complete` on complete RingCentral Chinese coverage and incomplete uncovered language coverage.
2. Add failing CLI tests for `--require-complete` success on `zh` and failure on `ja`.
3. Update the package-only subprocess import probe so the `--require-complete` success path remains import-light.
4. Implement the pure completion property on `LocalizationStatusReport`.
5. Add `--require-complete` to `localization-report`, preserving default output and exit behavior.
6. Add a README example for using the localization gate before demos or in CI.
7. Run focused tests, static checks, full verification, and a review subagent.

## Verification Targets

- `python -m pytest tests/unit/test_material_packages.py::test_localization_status_marks_required_chinese_coverage_complete tests/unit/test_material_packages.py::test_localization_status_marks_uncovered_language_incomplete tests/unit/test_cli.py::test_localization_report_require_complete_passes_for_chinese tests/unit/test_cli.py::test_localization_report_require_complete_fails_for_uncovered_language tests/unit/test_cli.py::test_localization_report_does_not_load_voice_asset_providers --no-cov`
- `python -m pytest tests/unit/test_cli.py tests/unit/test_material_packages.py --no-cov`
- `python -m pytest`
- `python -m mypy src tests`
- `python -m ruff check src tests`
