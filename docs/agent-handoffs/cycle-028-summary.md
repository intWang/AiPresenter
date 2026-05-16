# Cycle 028 Summary: Localization Completion Gate

Date: 2026-05-16
Role: orchestration summary

## Objective

Turn `localization-report` from a human-only visibility tool into an optional package-only quality gate for future language expansion and agent handoffs.

## Inputs

- Demand analysis: `docs/agent-handoffs/cycle-028-demand-analysis.md`
- Technical scan: `docs/agent-handoffs/cycle-028-technical-scan.md`
- Review: `docs/agent-handoffs/cycle-028-review.md`
- Follow-up review: `docs/agent-handoffs/cycle-028-followup-review.md`
- Design: `docs/superpowers/specs/2026-05-16-localization-report-require-complete-design.md`
- Plan: `docs/superpowers/plans/2026-05-16-localization-report-require-complete.md`

Demand discovery recommended stable RingCentral validation target IDs as the next strong RingCentral knowledge slice. The main session selected the localization completion gate first because it directly builds on Cycles 026 and 027 and provides an immediate CI/handoff guardrail.

## Changes

- Added `LocalizationStatusReport.required_localization_complete`.
- Added `ai-presenter localization-report --require-complete`.
- Kept default `localization-report` behavior unchanged: partial coverage still exits `0` unless the new flag is supplied.
- With `--require-complete`, incomplete required localization prints the normal report, appends `Localization coverage incomplete for <language>.`, and exits `1`.
- Required localization includes:
  - demo-flow narration localized text,
  - Q&A localized question variants,
  - Q&A localized answers.
- `questionAliases.<language>` remains informational and does not fail the completion gate.
- Updated the package-only import-hygiene subprocess test so the `--require-complete` success path also avoids diagnostics, voice assets, and provider modules.
- Added a README example for strict localization checks.

## Verification

Focused RED before implementation:

```text
5 failed
```

Failures confirmed the missing completion property and unknown `--require-complete` option.

Focused GREEN:

```powershell
.\.venv\Scripts\python -m pytest tests\unit\test_material_packages.py::test_localization_status_marks_required_chinese_coverage_complete tests\unit\test_material_packages.py::test_localization_status_marks_uncovered_language_incomplete tests\unit\test_cli.py::test_localization_report_require_complete_passes_for_chinese tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_uncovered_language tests\unit\test_cli.py::test_localization_report_does_not_load_voice_asset_providers --no-cov
```

```text
5 passed in 2.65s
```

Affected suite:

```powershell
.\.venv\Scripts\python -m pytest tests\unit\test_cli.py tests\unit\test_material_packages.py --no-cov
```

```text
84 passed in 18.42s
```

Manual smoke:

```powershell
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language zh --require-complete
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja --require-complete
```

Results:

- `zh --require-complete` exits `0` and reports `51/51` demo steps, `8/8` Q&A questions, and `8/8` Q&A answers.
- `ja --require-complete` exits `1`, reports all missing demo/Q&A localization, and appends `Localization coverage incomplete for ja.`

Full verification after follow-up review test:

```powershell
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\python -m mypy src tests
.\.venv\Scripts\python -m ruff check src tests
```

```text
518 passed, 1 warning in 129.58s
Success: no issues found in 80 source files
All checks passed!
```

The warning is the existing pywinauto STA COM threading warning.

## Review Result

Cycle 028 review and follow-up review found no blocking issues.

One review residual risk was converted into a permanent test: `test_localization_status_completion_ignores_alias_coverage_gaps` proves alias-only gaps do not fail the required completion property.

## Recommended Next Slice

Use the demand recommendation for the next cycle: add stable explicit RingCentral validation target IDs to the knowledge checklist and teach `validation-targets` to prefer those IDs over generated slugs.
