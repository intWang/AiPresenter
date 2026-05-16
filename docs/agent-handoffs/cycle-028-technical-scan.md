# Cycle 028 Technical Scan: Localization Report Completion Gate

Date: 2026-05-16
Role: technical discovery
Scope: review-only; no production code edits.

## Recommendation

Use Cycle 028 for a small package-tooling slice: add an explicit
`localization-report --require-complete` flag.

Default `localization-report` should remain a read-only report that exits `0` for partial
coverage. When `--require-complete` is supplied, the command should still print the same report,
then exit `1` if required localization is incomplete. Required localization should mean:

- every demo-flow narration step has nonblank `narration.localizedText.<language>`;
- every Q&A item has at least one nonblank `localizedQuestions.<language>` entry;
- every Q&A item has a nonblank `localizedAnswers.<language>` value.

Do not require `questionAliases.<language>` coverage. Alias coverage is intentionally
informational because not every entrypoint needs localized aliases.

## Why This Is The Next Small Slice

Cycle 026 made localization coverage visible to operators, and Cycle 027 protected package-only
CLI commands from provider imports. The remaining gap is automation: maintainers can now see that
Japanese is `0/51`, but they cannot ask the CLI to fail when a package is not ready for a chosen
language. This blocks low-friction CI or pre-demo checks for future language expansion.

This is higher leverage than adding another language immediately because it creates the guardrail
needed before new language content starts landing. It is also safer than extending `doctor` because
`doctor` mixes profile, provider, voice asset, and RingCentral prerequisites, while localization
coverage is package-only.

## Evidence From Current Repo

- `src/ai_presenter/packages/localization_status.py` already computes all required counts and
  missing IDs/questions.
- `tests/unit/test_material_packages.py` already covers:
  - full RingCentral Chinese coverage;
  - partial synthetic package reporting;
  - blank localized question lists counting as missing;
  - explicit uncovered languages such as `ja`.
- `tests/unit/test_cli.py` already covers:
  - `localization-report` defaulting to `zh`;
  - explicit `--language ja` reporting zero coverage while exiting `0`;
  - `localization-report` not loading diagnostics, voice assets, or provider modules.
- `docs/agent-handoffs/cycle-026-technical-scan.md` explicitly left a future policy gate as a
  later option: `--fail-under` or `--require-complete`.
- `docs/agent-handoffs/cycle-025-technical-scan.md` and Cycle 026 notes both mention that future
  languages should move away from ad hoc hardcoded `zh` checks. A CLI gate supports that direction
  without changing the package schema yet.

Observed current command behavior:

```powershell
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language zh
```

exits `0` and reports:

```text
Localization report: 51/51 demo steps, 8/8 Q&A questions, 8/8 Q&A answers localized for zh.
```

```powershell
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja
```

also exits `0`, but reports `0/51`, `0/8`, and `0/8`, with all missing flow steps and Q&A items
listed. That should remain true unless `--require-complete` is supplied.

## Proposed Implementation Plan

### Files To Touch

- Modify `src/ai_presenter/packages/localization_status.py`
  - Add a package-only completion property or helper on `LocalizationStatusReport`, for example
    `required_localization_complete`.
  - It should compare demo-step, Q&A question, and Q&A answer counts against totals.
  - It should not include alias counts.
- Modify `src/ai_presenter/cli.py`
  - Add `require_complete: bool = typer.Option(False, "--require-complete", ...)` to
    `localization_report`.
  - Keep rendering the report exactly as today.
  - If `require_complete` is true and the report is incomplete, echo a short final line such as
    `Localization coverage incomplete for ja.` and raise `typer.Exit(1)`.
  - Keep the command package-only; do not import diagnostics, runtime factory, controller, voice
    assets, or providers.
- Modify `tests/unit/test_material_packages.py`
  - Add helper-level tests for complete `zh` and incomplete `ja` / synthetic partial package.
- Modify `tests/unit/test_cli.py`
  - Add CLI tests:
    - `localization-report --package ringcentral-video --language zh --require-complete` exits
      `0`.
    - `localization-report --package ringcentral-video --language ja --require-complete` exits
      `1` and still prints the missing coverage details.
    - The package-only subprocess import probe still passes when running the complete-gate path.
- Modify `README.md`
  - Add one optional pre-demo/CI example under the existing localization-report example.

### Suggested TDD Steps

1. Add failing helper tests:

```python
def test_localization_status_marks_required_chinese_coverage_complete() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    report = build_localization_status(package, language="zh")

    assert report.required_localization_complete is True
```

```python
def test_localization_status_marks_uncovered_language_incomplete() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    report = build_localization_status(package, language="ja")

    assert report.required_localization_complete is False
```

2. Run the new helper tests and verify RED because the property/helper does not exist.

3. Implement the minimal helper/property in `localization_status.py`.

4. Run helper tests and verify GREEN.

5. Add failing CLI tests:

```python
def test_localization_report_require_complete_passes_for_chinese() -> None:
    result = CliRunner().invoke(
        app,
        [
            "localization-report",
            "--package",
            "ringcentral-video",
            "--language",
            "zh",
            "--require-complete",
        ],
    )

    assert result.exit_code == 0
    assert "Localization report: 51/51 demo steps" in result.stdout
```

```python
def test_localization_report_require_complete_fails_for_uncovered_language() -> None:
    result = CliRunner().invoke(
        app,
        [
            "localization-report",
            "--package",
            "ringcentral-video",
            "--language",
            "ja",
            "--require-complete",
        ],
    )

    assert result.exit_code == 1
    assert "Language: ja" in result.stdout
    assert "missing: meeting-overview" in result.stdout
    assert "Localization coverage incomplete for ja." in result.stdout
```

6. Implement the CLI flag and final failure line.

7. Update or add a subprocess import-hygiene probe for the `--require-complete` success path:

```python
result = CliRunner().invoke(
    app,
    [
        "localization-report",
        "--package",
        "ringcentral-video",
        "--language",
        "zh",
        "--require-complete",
    ],
)
```

Assert diagnostics, voice assets, and provider modules remain unloaded.

8. Add a short README example:

```powershell
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language zh --require-complete
```

## Verification To Run

Focused:

```powershell
.\.venv\Scripts\python -m pytest tests\unit\test_material_packages.py::test_localization_status_marks_required_chinese_coverage_complete tests\unit\test_material_packages.py::test_localization_status_marks_uncovered_language_incomplete tests\unit\test_cli.py::test_localization_report_require_complete_passes_for_chinese tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_uncovered_language tests\unit\test_cli.py::test_localization_report_does_not_load_voice_asset_providers --no-cov
```

Affected suite:

```powershell
.\.venv\Scripts\python -m pytest tests\unit\test_cli.py tests\unit\test_material_packages.py --no-cov
```

Static checks:

```powershell
.\.venv\Scripts\python -m ruff check src\ai_presenter\packages\localization_status.py src\ai_presenter\cli.py tests\unit\test_cli.py tests\unit\test_material_packages.py
.\.venv\Scripts\python -m mypy src\ai_presenter\packages\localization_status.py src\ai_presenter\cli.py tests\unit\test_cli.py tests\unit\test_material_packages.py
```

Full verification before closing the cycle:

```powershell
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\python -m mypy src tests
.\.venv\Scripts\python -m ruff check src tests
```

## Risks And Boundaries

- Do not change the default exit behavior. Partial coverage should still exit `0` unless the new
  flag is supplied.
- Do not fold this into `doctor` in the first implementation. That would mix package localization
  policy with profile/provider readiness.
- Do not fail on missing localized aliases. Alias coverage remains useful visibility, not a
  completeness requirement.
- Avoid a broad `--fail-under` percentage in this slice. Counts are simple and the package has
  three clear required dimensions; percentages would create ambiguity about whether a missing
  answer can be hidden by many complete demo steps.
- Keep the implementation pure package/CLI. The Cycle 027 import-hygiene guard should stay green.
- A package with zero demo steps or zero Q&A items will be complete for that dimension under simple
  equality checks. That is acceptable for generic packages; RingCentral has nonzero totals.

## Alternatives Considered

- Add `--format json` to `localization-report`: useful later, but there is no caller yet. A
  completion gate gives immediate operator/CI value.
- Add `supportedLocalizedLanguages` to the package schema: valuable when multiple localization
  families exist, but a schema migration is larger than the next small slice.
- Add Japanese or another language now: too large for a technical-maintenance cycle because it
  requires real package copy, voice/provider policy, and likely content review.
- Extend `doctor` to fail on localization gaps: useful later for strict pre-demo runs, but it
  should delegate to a settled package-only policy first.

## Commands Run During This Scan

```powershell
git status --short
Get-Content -Path docs\agent-handoffs\cycle-027-demand-analysis.md -TotalCount 220
Get-Content -Path docs\agent-handoffs\cycle-027-technical-scan.md -TotalCount 260
Get-Content -Path docs\agent-handoffs\cycle-027-review.md -TotalCount 220
rg -n "TODO|FIXME|follow[- ]?up|follow up|Next|Out of scope|Residual|risk|gap|missing|P[0-3]|future|later" docs\agent-handoffs docs\superpowers\specs docs\superpowers\plans tests src packages README.md
rg -n "xfail|skip|TODO|FIXME|not implemented|missing|coverage|language|tone|localization|operator|UI|performance|RingCentral|knowledge|package" tests src docs\agent-handoffs docs\superpowers\specs docs\superpowers\plans
Get-ChildItem -Path docs\agent-handoffs -Filter "cycle-0*.md" | Sort-Object Name | Select-Object -ExpandProperty Name
Get-ChildItem -Path docs\superpowers\plans -Filter "2026-05-16-*.md" | Sort-Object Name | Select-Object -ExpandProperty Name
Get-Content -Path src\ai_presenter\packages\localization_status.py -TotalCount 260
rg -n "localization-report|LocalizationStatus|localization_status|localized|localized_text|localizedQuestions|localizedAnswer|questionAliases|PresenterLanguage|PresenterTone|tone|language" src\ai_presenter tests\unit packages\ringcentral-video.yaml README.md
Get-Content -Path src\ai_presenter\runtime\voice.py -TotalCount 220
Get-Content -Path tests\unit\test_cli.py -TotalCount 520
Get-Content -Path tests\unit\test_material_packages.py -TotalCount 620
Get-Content -Path docs\agent-handoffs\cycle-027-summary.md -TotalCount 180
Get-Content -Path docs\superpowers\specs\2026-05-16-localization-report-design.md -TotalCount 180
Get-Content -Path docs\superpowers\plans\2026-05-16-localization-report.md -TotalCount 260
Get-Content -Path docs\agent-handoffs\cycle-026-summary.md -TotalCount 140
Get-Content -Path docs\agent-handoffs\cycle-025-technical-scan.md -TotalCount 100
Get-Content -Path docs\agent-handoffs\cycle-021-summary.md -TotalCount 160
Get-Content -Path src\ai_presenter\acceptance\validation_targets.py -TotalCount 420
Get-Content -Path README.md -TotalCount 150
Get-Content -Path docs\knowledge\ringcentral-video\validation-checklist-index.md -TotalCount 220
Get-Content -Path docs\knowledge\ringcentral-video\evidence-index.md -TotalCount 220
Get-Content -Path docs\knowledge\ringcentral-video\acceptance-runs.md -TotalCount 220
Get-Content -Path pyproject.toml -TotalCount 260
rg -n "require|complete|fail-under|fail_under|format|json|markdown|strict|exit_code|coverage" src\ai_presenter\packages\localization_status.py src\ai_presenter\cli.py tests\unit\test_cli.py tests\unit\test_material_packages.py docs\agent-handoffs docs\superpowers\specs docs\superpowers\plans
rg -n -C 4 "localization_report|localization-report|validation_targets|acceptance_draft|voices\(" src\ai_presenter\cli.py
Get-Content -Path src\ai_presenter\packages\models.py -TotalCount 360
.\.venv\Scripts\python -m pytest tests\unit\test_cli.py::test_localization_report_outputs_ringcentral_chinese_coverage tests\unit\test_cli.py::test_localization_report_outputs_zero_for_explicit_uncovered_language tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_chinese_coverage tests\unit\test_material_packages.py::test_localization_status_reports_zero_for_explicit_uncovered_language --no-cov
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language zh
```

Focused verification result during scan:

```text
4 passed in 1.93s
```

One attempted `rg` command using the literal path `docs\agent-handoffs\cycle-0*.md` failed on
Windows because `rg` received the wildcard as part of the filename. The broader successful scans
above covered the same handoff directory.
