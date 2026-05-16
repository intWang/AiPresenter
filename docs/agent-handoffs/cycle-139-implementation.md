# Cycle 139 Implementation: Package Alias Lifecycle Docs Guard

Date: 2026-05-17

## Summary

Implemented the post-alias-normalization docs/test guard for package-local
language inspection. The durable language lifecycle doc no longer describes
`entrypoints --language <lang>` as a raw language-key lookup for known presenter
aliases. It now documents that known presenter language aliases such as
`Spanish`, `es-MX`, and `zh-CN` normalize to canonical package keys before
package-local inspection, while unknown package-only keys remain raw package
metadata lookup keys.

The doc also states that output prints `Language: <key>` using the resolved
package key and keeps the package-inspection boundary separate from runtime
voice support, providers, speech assets, controller/demo language choices, local
SAPI/Piper, and live RingCentral Video acceptance.

## Files Changed

- `docs/knowledge/language-lifecycle.md`
- `tests/unit/test_cli.py`
- `docs/agent-handoffs/cycle-139-implementation.md`

No package YAML, source code, README, runtime voice tables, providers, profiles,
Spanish counts, staged files, commits, or `.coverage` changes were made by this
implementation slice.

## Red Verification

Ran the focused command after adding
`test_package_language_alias_normalization_is_documented` and before updating
the lifecycle doc:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_package_language_alias_normalization_is_documented tests\unit\test_cli.py::test_localization_report_normalizes_spanish_language_aliases tests\unit\test_cli.py::test_entrypoints_language_normalizes_spanish_alias_for_display_metadata tests\unit\test_cli.py::test_localization_report_keeps_unknown_package_language_key_raw
```

Observed result: `1 failed, 3 passed`. The new test failed because
`docs/knowledge/language-lifecycle.md` still contained `raw language-key lookup`.

## Green Verification

Focused command after the lifecycle doc update:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_package_language_alias_normalization_is_documented tests\unit\test_cli.py::test_localization_report_normalizes_spanish_language_aliases tests\unit\test_cli.py::test_entrypoints_language_normalizes_spanish_alias_for_display_metadata tests\unit\test_cli.py::test_localization_report_keeps_unknown_package_language_key_raw
```

Observed result: `4 passed in 1.01s`.

Additional verification:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_spanish_display_metadata_counts_match_durable_docs
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language Spanish
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting top bar" --language es-MX
rg -n "raw language-key lookup|known presenter language aliases|Unknown package-only keys remain raw|resolved package key|runtime voice support|live RingCentral Video acceptance|SAPI|Piper" docs\knowledge\language-lifecycle.md README.md
.\.venv\Scripts\python.exe -m ruff check tests\unit\test_cli.py
git diff --check
```

Observed results:

- Material package count guard: `1 passed in 0.85s`.
- `localization-report --language Spanish` printed `Language: es`, complete
  required Spanish package localization, `questionAliases.es` on `26/27`
  entrypoints with `69` aliases, and Spanish optional display metadata at
  `5/27` titles and `5/27` purposes.
- `entrypoints --language es-MX` printed `Language: es` and showed localized
  top-bar metadata where present with fallback metadata where unseeded.
- `rg` found the new alias/resolved-key wording and preserved runtime boundary
  wording; it did not find the stale `raw language-key lookup` phrase.
- Ruff: `All checks passed!`.
- `git diff --check`: exit code `0`; PowerShell output included line-ending
  warnings for touched files only.

## Residual Risks

- Unknown package-only keys still intentionally produce raw package lookup
  reports and can show all-zero coverage without being runtime errors.
- Package-local alias normalization depends on the presenter language alias
  table, so future alias-table changes can affect inspection command
  canonicalization.
- Spanish optional entrypoint display metadata remains partial at `5/27`.
- Package inspection still does not validate runtime Spanish support for local
  SAPI/Piper, provider readiness, controller/demo execution, or live
  RingCentral Video acceptance.

## Main-Session Review Note

The main session adjusted the doc guard to normalize whitespace before checking
short lifecycle phrases, so Markdown line wrapping does not create false
failures while the stale `raw language-key lookup` wording remains blocked.
