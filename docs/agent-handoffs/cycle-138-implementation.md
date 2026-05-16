# Cycle 138 Implementation: Package-Local CLI Language Alias Normalization

Date: 2026-05-16

## Summary

Implemented package-local language key normalization for CLI inspection commands.
Known presenter language aliases such as `Spanish` and `es-MX` now resolve to
canonical package key `es` for `entrypoints` and `localization-report`, while
unknown package-only keys such as `de` remain accepted raw lookup keys.

This change intentionally does not alter runtime voice validation, demo,
controller, doctor, voices, package YAML, matching behavior, provider validation,
or Spanish support boundaries.

## Files Changed

- `src/ai_presenter/cli.py`
  - Imported `normalize_presenter_language`.
  - Added `resolve_package_language_key(language: str) -> str`.
  - Applied the helper only in `entrypoints()` and `localization_report()`.
- `tests/unit/test_cli.py`
  - Added Spanish alias normalization coverage for `localization-report`.
  - Added Spanish regional alias normalization coverage for `entrypoints`.
  - Added raw unknown package language key coverage for `de`.
- `docs/agent-handoffs/cycle-138-implementation.md`
  - Recorded implementation and verification.

## Red Verification

Command:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_localization_report_normalizes_spanish_language_aliases tests\unit\test_cli.py::test_entrypoints_language_normalizes_spanish_alias_for_display_metadata tests\unit\test_cli.py::test_localization_report_keeps_unknown_package_language_key_raw
```

Observed failures before source changes:

- `test_localization_report_normalizes_spanish_language_aliases` failed because
  output contained `Language: Spanish` and all-zero Spanish coverage instead of
  canonical `Language: es`.
- `test_entrypoints_language_normalizes_spanish_alias_for_display_metadata`
  failed because output contained `Language: es-MX` and fallback display
  metadata instead of canonical `Language: es` with Spanish localized metadata.
- `test_localization_report_keeps_unknown_package_language_key_raw` passed
  before implementation, confirming unknown package keys were already accepted.

## Green Verification

Focused tests:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_localization_report_normalizes_spanish_language_aliases tests\unit\test_cli.py::test_entrypoints_language_normalizes_spanish_alias_for_display_metadata tests\unit\test_cli.py::test_localization_report_keeps_unknown_package_language_key_raw
```

Result: `3 passed in 1.41s`.

Regression tests:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_entrypoints_language_uses_package_local_metadata_without_runtime_voice_validation tests\unit\test_cli.py::test_demo_openai_profile_accepts_spanish_dry_run tests\unit\test_cli.py::test_demo_rejects_spanish_local_profile_before_runtime tests\unit\test_voice.py::test_voice_settings_normalize_language_aliases tests\unit\test_voice.py::test_presenter_spanish_language_aliases_are_public_and_canonical
```

Result: `7 passed in 2.01s`.

Manual CLI probes:

- `.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language Spanish`
  exited `0`, printed `Language: es`, and reported Spanish `51/51`, `12/12`,
  `12/12`, `questionAliases.es` on `26/27`, and display metadata `5/27`.
- `.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es-MX --require-complete`
  exited `0` and printed complete Spanish package coverage for `Language: es`.
- `.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language de`
  exited `0`, printed `Language: de`, and reported `0/51` demo steps without
  unsupported presenter language text.
- `.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting top bar" --language Spanish`
  exited `0`, printed `Language: es`, showed Spanish localized Network quality
  and Views metadata, and kept Meeting information fallback metadata.
- `.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting top bar" --language es-MX`
  exited `0` with the same canonical Spanish localized/fallback output.

Static checks:

```powershell
.\.venv\Scripts\python.exe -m ruff check src\ai_presenter\cli.py tests\unit\test_cli.py
git diff --check
```

Results:

- Ruff: `All checks passed!`
- `git diff --check`: no whitespace errors; Git emitted existing CRLF
  normalization warnings for the touched Python files.

## Residual Risks

- Package-local alias normalization now follows the presenter voice alias table
  for known languages, so future changes to that table can affect inspection
  command canonicalization.
- Unknown language keys remain raw by design; they can still produce all-zero
  package reports when the package has no matching localization data.
- Spanish optional entrypoint display metadata remains partial at `5/27`; this
  change does not expand Spanish content or runtime voice support.
