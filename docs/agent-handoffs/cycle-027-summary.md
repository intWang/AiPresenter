# Cycle 027 Summary: CLI Provider Import Hygiene

Date: 2026-05-16
Role: orchestration summary

## Objective

Keep package-only CLI commands lightweight by preventing `ai_presenter.cli` from loading diagnostics, voice asset, Piper, or Windows speech provider modules at import time.

## Inputs

- Demand analysis: `docs/agent-handoffs/cycle-027-demand-analysis.md`
- Technical scan: `docs/agent-handoffs/cycle-027-technical-scan.md`
- Review: `docs/agent-handoffs/cycle-027-review.md`
- Design: `docs/superpowers/specs/2026-05-16-cli-provider-import-hygiene-design.md`
- Plan: `docs/superpowers/plans/2026-05-16-cli-provider-import-hygiene.md`

## Changes

- Removed top-level CLI import paths that eagerly loaded `runtime.diagnostics` and `runtime.voice_assets`.
- Added CLI-level lazy wrappers for:
  - `diagnose_configuration`
  - `format_diagnostic_report`
  - `check_voice_asset_availability`
- Extended import-hygiene subprocess coverage so `import ai_presenter.cli` must leave these unloaded:
  - `ai_presenter.runtime.diagnostics`
  - `ai_presenter.runtime.voice_assets`
  - `ai_presenter.providers.base`
  - `ai_presenter.providers.piper_provider`
  - `ai_presenter.providers.windows_speech`
- Added a package-only subprocess probe for `localization-report --package ringcentral-video --language zh` to ensure the command does not load diagnostics, voice assets, or provider modules.

## Verification

Focused red check before implementation:

```text
2 failed
```

Failures confirmed `runtime.diagnostics`, `runtime.voice_assets`, and provider modules were loaded by the old import chain.

Focused green check after implementation:

```powershell
.\.venv\Scripts\python -m pytest tests\unit\test_cli.py::test_cli_import_does_not_load_desktop_runtime_modules tests\unit\test_cli.py::test_localization_report_does_not_load_voice_asset_providers --no-cov
```

```text
2 passed in 3.02s
```

Affected CLI/voice suite:

```powershell
.\.venv\Scripts\python -m pytest tests\unit\test_cli.py tests\unit\test_voice_assets.py --no-cov
```

```text
54 passed in 10.18s
```

Manual import probe after implementation:

```json
{
  "ai_presenter.desktop.windows": false,
  "ai_presenter.providers.base": false,
  "ai_presenter.providers.piper_provider": false,
  "ai_presenter.providers.windows_speech": false,
  "ai_presenter.runtime.controller": false,
  "ai_presenter.runtime.diagnostics": false,
  "ai_presenter.runtime.factory": false,
  "ai_presenter.runtime.voice_assets": false
}
```

Full verification:

```powershell
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\python -m mypy src tests
.\.venv\Scripts\python -m ruff check src tests
```

```text
513 passed, 1 warning in 123.31s
Success: no issues found in 80 source files
All checks passed!
```

The warning is the existing pywinauto STA COM threading warning.

## Review Result

Cycle 027 review found no blocking issues. Residual risk: the test module itself imports diagnostics and voice asset fixtures for command tests, but the production import boundary is protected through fresh subprocess probes.
