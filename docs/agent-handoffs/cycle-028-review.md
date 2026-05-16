# Cycle 028 Review

Date: 2026-05-16
Mode: Review-only

## Result

No blocking issues found.

The current `localization-report --require-complete` implementation matches the Cycle 028
scope:

- Default `localization-report` remains report-only and exits `0` for partial coverage.
- `--require-complete` renders the normal report first, then exits `1` only when required
  demo narration, Q&A localized questions, or Q&A localized answers are incomplete.
- Entrypoint `questionAliases.<language>` remain informational and are not included in
  `LocalizationStatusReport.required_localization_complete`.
- The package-only import hygiene guard remains intact for the `--require-complete`
  success path.
- Tests use `sys.executable -c` subprocess probes, which is the right shape for Windows
  import-boundary checks.

## Reviewed Files

- `src/ai_presenter/packages/localization_status.py`
- `src/ai_presenter/cli.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_material_packages.py`
- `README.md`
- `docs/superpowers/specs/2026-05-16-localization-report-require-complete-design.md`
- `docs/superpowers/plans/2026-05-16-localization-report-require-complete.md`

## Verification

```powershell
.\.venv\Scripts\python -m pytest tests/unit/test_cli.py::test_cli_import_does_not_load_desktop_runtime_modules tests/unit/test_cli.py::test_localization_report_does_not_load_voice_asset_providers tests/unit/test_cli.py::test_localization_report_outputs_zero_for_explicit_uncovered_language tests/unit/test_cli.py::test_localization_report_require_complete_passes_for_chinese tests/unit/test_cli.py::test_localization_report_require_complete_fails_for_uncovered_language tests/unit/test_material_packages.py::test_localization_status_marks_required_chinese_coverage_complete tests/unit/test_material_packages.py::test_localization_status_marks_uncovered_language_incomplete --no-cov
```

Result: `7 passed in 4.61s`.

```powershell
.\.venv\Scripts\python -m ruff check src\ai_presenter\packages\localization_status.py src\ai_presenter\cli.py tests\unit\test_cli.py tests\unit\test_material_packages.py
```

Result: `All checks passed!`

```powershell
.\.venv\Scripts\python -m mypy src\ai_presenter\packages\localization_status.py src\ai_presenter\cli.py tests\unit\test_cli.py tests\unit\test_material_packages.py
```

Result: `Success: no issues found in 4 source files`.

```powershell
git diff --check -- src\ai_presenter\packages\localization_status.py src\ai_presenter\cli.py tests\unit\test_cli.py tests\unit\test_material_packages.py README.md docs\superpowers\specs\2026-05-16-localization-report-require-complete-design.md docs\superpowers\plans\2026-05-16-localization-report-require-complete.md
```

Result: exit code `0`; Git printed existing LF-to-CRLF working-copy warnings for README,
`cli.py`, and the two test files.

```powershell
@'
from ai_presenter.packages.localization_status import build_localization_status
from ai_presenter.packages.models import MaterialPackage

package = MaterialPackage.model_validate({
    "appId": "demo",
    "appName": "Demo",
    "version": 1,
    "profileIds": ["demo-profile"],
    "operationEntrypoints": [{
        "id": "demo.panel",
        "title": "Panel",
        "area": "Main",
        "purpose": "Open panel.",
        "openSteps": [],
    }],
    "demoFlows": [{
        "id": "complete-demo",
        "title": "Complete",
        "goal": "Show complete path.",
        "steps": [{
            "id": "intro",
            "title": "Intro",
            "action": {"entrypointId": "demo.panel", "operation": "explain"},
            "narration": {"text": "Show panel.", "localizedText": {"zh": "Open panel."}},
        }],
    }],
    "qa": [{
        "question": "Where is the panel?",
        "answer": "Open Panel.",
        "localizedQuestions": {"zh": ["Panel?"]},
        "localizedAnswers": {"zh": "Open panel."},
        "relatedEntrypointIds": ["demo.panel"],
    }],
    "manualControls": [],
})
report = build_localization_status(package, language="zh")
assert report.required_localization_complete is True
assert report.entrypoints_with_aliases == 0
assert report.alias_total == 0
print("alias-only gap does not fail required_localization_complete")
'@ | .\.venv\Scripts\python -
```

Result: `alias-only gap does not fail required_localization_complete`.

## Notes

- `src/ai_presenter/packages/localization_status.py:41` excludes alias coverage from the
  completion property, as intended.
- `src/ai_presenter/cli.py:272` keeps `--require-complete` opt-in, so default exit
  behavior is unchanged.
- `tests/unit/test_cli.py:63` protects the package-only command path from loading
  diagnostics, voice assets, or provider modules.

## Residual Risks

- I ran focused verification, not the full suite in this review pass.
- The test suite has broad `zh`/`ja` coverage and a one-off alias-only probe, but there is
  not yet a named unit test dedicated solely to "aliases missing while required localization
  is complete." The implementation shape is clear, but a permanent fixture would make that
  contract more explicit.
