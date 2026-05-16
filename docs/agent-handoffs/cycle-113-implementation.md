# Cycle 113 Implementation: Spanish RingCentral Video Localization Seed

Date: 2026-05-16

## Scope

Cycle 113 adds a Spanish package/report-only localization seed for RingCentral Video. It intentionally does not add Spanish as a runtime presenter voice, translate demo narration, change route policy, update profiles, or create live RingCentral acceptance evidence.

## Main Decision

The demand scan recommended Spanish because it is the higher-value user-facing next language. The technical scan recommended a report-only wedge to avoid opening a runtime language before demo narration and voice-provider behavior are ready.

This implementation combines those recommendations:

- language code: `es`;
- scope: one safe background/privacy Q&A item plus one background settings alias group;
- runtime: unchanged, so `PresenterVoiceSettings(language="es")` is still unsupported;
- completeness gate: `localization-report --language es --require-complete` still exits nonzero.

## Package Changes

Updated `packages/ringcentral-video.yaml`:

- Added `localizedQuestions.es` to `How do I protect my real background?`.
- Added `localizedAnswers.es` for the same Q&A item.
- Added `questionAliases.es` to `ringcentral.video.settings.background`:
  - `configuración de fondo`
  - `fondo virtual`
  - `desenfocar fondo`

The Spanish answer keeps UI labels `Settings`, `Background`, and `Blur` in English to match the current product labels in the RingCentral UI and the existing Chinese/Japanese localization pattern.

## Tests

Added focused tests:

- `tests/unit/test_material_packages.py::test_ringcentral_spanish_seed_qa_and_aliases_are_present`
- `tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_spanish_seed_coverage`
- `tests/unit/test_cli.py::test_localization_report_outputs_spanish_seed_coverage`
- `tests/unit/test_cli.py::test_localization_report_require_complete_fails_for_spanish_seed`

The tests assert:

- Spanish report coverage is partial: `0/51` demo steps, `1/12` Q&A questions, `1/12` Q&A answers.
- Spanish aliases are partial: `1/27` entrypoints, `3` aliases.
- `--require-complete` still fails for Spanish.
- The existing `es` runtime language rejection remains unchanged.

## TDD Notes

Red check:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_spanish_seed_qa_and_aliases_are_present tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_spanish_seed_coverage tests\unit\test_cli.py::test_localization_report_outputs_spanish_seed_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_spanish_seed
```

Expected result before YAML changes: 4 failures, with Spanish Q&A and alias counts still at zero.

Green check:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_spanish_seed_qa_and_aliases_are_present tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_spanish_seed_coverage tests\unit\test_material_packages.py::test_localization_status_reports_zero_for_explicit_uncovered_language tests\unit\test_cli.py::test_localization_report_outputs_spanish_seed_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_spanish_seed tests\unit\test_cli.py::test_demo_rejects_unknown_language_before_runtime
```

Result: `6 passed`.

CLI checks:

```powershell
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language es
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language es --require-complete
```

The first command passes and reports the seed coverage. The second command exits `1` with `Localization coverage incomplete for es.`, which is the intended result for this partial wedge.

## Review Focus

- Confirm Spanish is documented as partial package localization, not runtime voice support.
- Confirm the Spanish Q&A preserves the background privacy boundary.
- Confirm aliases are narrow and background-specific.
- Confirm Chinese and Japanese complete-localization baselines remain unchanged.
- Confirm `.coverage` remains unstaged.

## Post-Review Adjustment

The review found one minor maintainability issue: the first Spanish seed test asserted exact translated question text and exact alias order. The test now checks the intended safety/product signals instead: two Spanish questions, the background/privacy terms, required UI labels, and the three alias values as a set.

## Full-Suite Adjustment

The first full pytest run surfaced stale diagnostic-count assertions. The Spanish seed intentionally adds two Q&A prompts and three package-owned aliases, so the RingCentral diagnostic expectations moved from `71` to `73` Q&A prompts and from `87` to `90` aliases. The assertions were updated to match the new package facts while keeping the existing substring-risk count unchanged.
