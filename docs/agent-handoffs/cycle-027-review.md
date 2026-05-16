# Cycle 027 Review: CLI Provider Import Hygiene

Date: 2026-05-16
Role: review
Scope: review-only; no implementation edits.

## Verdict

No blocking issues found.

The current `src/ai_presenter/cli.py` change addresses the technical scan's main caveat: both direct voice asset imports and the indirect `runtime.diagnostics` import path are now behind CLI-level lazy wrappers. Importing `ai_presenter.cli` no longer loads `runtime.diagnostics`, `runtime.voice_assets`, or the Piper/Windows speech provider modules, while command behavior remains covered for `doctor`, `voices`, and `localization-report`.

## Findings

None.

## Review Notes

- Lazy wrapper seams are preserved:
  - `ai_presenter.cli.check_voice_asset_availability` remains a public CLI module name and is still patched by the voice CLI tests.
  - `ai_presenter.cli.diagnose_configuration` and `ai_presenter.cli.format_diagnostic_report` remain patchable at the CLI layer because doctor resolves those names at call time.
  - Existing tests that patch internals on `ai_presenter.runtime.diagnostics` still work because the lazy wrapper imports the same module object when `doctor` executes.
- `doctor` behavior remains covered by existing and new tests:
  - Profile/package/flow diagnostics still execute.
  - Voice preflight with `--language`/`--tone` still reaches diagnostics and voice asset checks.
  - Unsupported voice routing still exits nonzero.
- `voices` behavior remains covered:
  - Catalog output still works without a profile.
  - Profile compatibility still reports supported and unsupported languages.
  - Asset OK/FAIL paths still use the `ai_presenter.cli.check_voice_asset_availability` monkeypatch seam.
- `localization-report` behavior remains covered:
  - Chinese coverage output is asserted.
  - Explicit uncovered language output is asserted.
  - A subprocess test confirms the command runs without loading `runtime.diagnostics`, `runtime.voice_assets`, or provider modules.
- Type and lint posture looks clean:
  - The wrappers use `Any` for variadic arguments and lazy return values, which is acceptable for preserving dynamic Typer command seams without importing heavy runtime types at module load.
  - Focused ruff and mypy checks passed.
- Windows subprocess tests look robust:
  - They use `[sys.executable, "-c", code]`, so they run with the active test interpreter rather than relying on a shell command or PATH lookup.
  - They inherit the pytest working directory and environment, which matches the current test suite's editable/source setup.
  - They parse JSON from stdout and include command output in the localization-report assertion failure message.

## Verification

Command:

```powershell
.\.venv\Scripts\python -m pytest tests\unit\test_cli.py::test_cli_import_does_not_load_desktop_runtime_modules tests\unit\test_cli.py::test_localization_report_does_not_load_voice_asset_providers tests\unit\test_cli.py::test_voices_profile_reports_local_asset_status tests\unit\test_cli.py::test_voices_targeted_missing_assets_exits_nonzero tests\unit\test_cli.py::test_doctor_accepts_language_and_tone_voice_preflight tests\unit\test_cli.py::test_localization_report_outputs_ringcentral_chinese_coverage --no-cov
```

Result:

```text
6 passed in 3.71s
```

Command:

```powershell
.\.venv\Scripts\ruff check src\ai_presenter\cli.py tests\unit\test_cli.py
```

Result:

```text
All checks passed!
```

Command:

```powershell
.\.venv\Scripts\mypy src\ai_presenter\cli.py
```

Result:

```text
Success: no issues found in 1 source file
```

## Residual Risks

- I did not run the full pytest suite in this review-only pass; the focused checks cover the import-hygiene slice and the affected command paths.
- `tests/unit/test_cli.py` still imports `runtime.diagnostics` and `runtime.voice_assets` at module load for test fixtures/types, but the import-hygiene assertions execute in fresh subprocesses, so this does not weaken the production import boundary test.
- The subprocess probes depend on the same environment pytest uses. If future packaging tests run outside an editable install or without `PYTHONPATH`/package installation, they may need an explicit environment setup.
