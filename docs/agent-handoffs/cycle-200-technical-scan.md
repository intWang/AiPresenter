# Cycle 200 Technical Scan: Localization Report Boundary

Date: 2026-05-17

## Read-Only Finding

`localization-report` should stay a package-text coverage command. It must not
imply runtime voice readiness, provider compatibility, local voice assets,
controller/demo support, or live RingCentral acceptance.

## Minimal Handoff

Accept the small renderer/test change:

- Add the static `Readiness boundary:` block in
  `src/ai_presenter/packages/localization_status.py::render_localization_status_lines`
  after entrypoint alias counts and before the final summary.
- Keep coverage calculations unchanged: `required_localization_complete` remains
  demo narration plus Q&A questions plus Q&A answers only.
- Keep package YAML unchanged.
- No `src/ai_presenter/cli.py` command logic change is needed.

No lifecycle doc change is required for this narrow slice.
`docs/knowledge/language-lifecycle.md` already separates package localization,
runtime presenter language, provider compatibility, local voice assets, and
live acceptance.

## Source Locations

- `src/ai_presenter/packages/localization_status.py` -
  `build_localization_status(...)` calculates package-local counts.
- `src/ai_presenter/packages/localization_status.py` -
  `render_localization_status_lines(...)` renders the shared CLI report lines.
- `src/ai_presenter/cli.py::resolve_package_language_key(...)` normalizes known
  presenter aliases and leaves unknown package keys raw.
- `src/ai_presenter/cli.py::localization_report(...)` renders package report
  lines and exits nonzero for `--require-complete` only when required package
  localization is incomplete.
- `tests/unit/test_cli.py::test_localization_report_does_not_load_voice_asset_providers`
  protects the no-provider-import boundary.
- `tests/unit/test_cli.py::test_localization_report_explains_readiness_boundaries`
  covers the new note.
- `tests/unit/test_cli.py::test_localization_report_keeps_unknown_package_language_key_raw`
  protects package-only language inspection.

## Exact Tests

Focused tests to keep:

- `tests/unit/test_cli.py::test_localization_report_does_not_load_voice_asset_providers`
- `tests/unit/test_cli.py::test_localization_report_explains_readiness_boundaries`
- `tests/unit/test_cli.py::test_package_language_alias_normalization_is_documented`
- `tests/unit/test_cli.py::test_language_lifecycle_matrix_matches_runtime_language_contract`
- `tests/unit/test_cli.py::test_localization_report_require_complete_passes_for_spanish_package`
- `tests/unit/test_cli.py::test_localization_report_keeps_unknown_package_language_key_raw`

Useful package-helper tests to avoid accidental calculation changes:

- `tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_chinese_coverage`
- `tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`
- `tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_complete_spanish_package`
- `tests/unit/test_material_packages.py::test_localization_status_completion_ignores_alias_coverage_gaps`

## Risks

- Do not change `LocalizationStatusReport.required_localization_complete`;
  alias and localized title/purpose coverage are informational.
- Do not change package YAML to satisfy this boundary clarification.
- Do not add provider, voice asset, diagnostics, controller, or desktop imports
  to `localization-report`.
- Do not describe Spanish as locally voice-ready or live accepted because
  `--require-complete` passes.
- Keep unknown package-only keys raw, for example `--language de`.
- Do not stage `.coverage`.
