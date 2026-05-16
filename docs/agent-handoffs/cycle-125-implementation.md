# Cycle 125 Implementation: Spanish Location Alias Expansion

Date: 2026-05-17

## Goal

Improve Spanish question discovery for the RingCentral Video package without
promoting Spanish to a runtime presenter language.

Cycle 124 made Spanish package content complete (`51/51` demo steps and `12/12`
Q&A). Cycle 125 expands package-owned `questionAliases.es` so Spanish location
and control-discovery prompts can resolve to RingCentral Video entrypoints while
`--language es` remains unsupported.

## Implemented Changes

- Added `questionAliases.es` to 26 of 27 RingCentral Video entrypoints.
- Preserved the existing Spanish background aliases and added `ajustes de fondo`.
- Intentionally left `ringcentral.video.settings.background.blur` without a
  Spanish alias because that entrypoint selects Blur directly and should not be
  exposed as a generic location alias.
- Added Spanish alias ownership and localization-count tests.
- Added Spanish alias routing tests with the legacy alias table disabled.
- Added Spanish Q&A-first safety tests for chat/participants privacy, shared
  content, recording safety, and reaction/raise-hand safety.
- Updated diagnostics and CLI expectations from `90` to `156` package-owned
  aliases and from `1/27 (3 aliases)` to `26/27 (69 aliases)` for Spanish.
- Updated runtime question matching so curated package aliases are not overridden
  by the final fuzzy Q&A token fallback. Exact Q&A, safety Q&A, and fragment Q&A
  still run before aliases.

## Safety Boundary

This cycle does not enable Spanish runtime support:

- No changes to presenter language normalization.
- No changes to voice labels, voice providers, voice assets, controller language
  menus, profiles, or acceptance evidence.
- No changes to operation `openSteps`, cleanup, locators, demo flows, or
  `questionPolicy`.

Sensitive controls are covered only by explicit location/control labels. The
tests assert that sensitive aliases remain non-operable where existing runtime
policy requires it.

## Verification So Far

Red phase:

- Focused tests failed before the YAML/runtime implementation because Spanish
  aliases were still `1/27`, alias total was `3`, diagnostics still reported
  `90`, and Spanish location prompts did not route to package aliases.

Green phase:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_spanish_seed_qa_and_aliases_are_present tests\unit\test_material_packages.py::test_ringcentral_package_owns_spanish_aliases_for_location_routes tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_complete_spanish_package tests\unit\test_questions.py::test_ringcentral_spanish_location_questions_match_package_aliases_without_legacy_table tests\unit\test_questions.py::test_ringcentral_spanish_safety_questions_stay_qa_first_with_aliases tests\unit\test_diagnostics.py::test_diagnostics_reports_question_aliases_ok_for_ringcentral_package tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

Result: `11 passed`.

Broader focused tests:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_diagnostics.py
```

Result: `299 passed`.

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_cli.py::test_localization_report_require_complete_passes_for_spanish_package tests\unit\test_cli.py::test_demo_rejects_unknown_language_before_runtime tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow tests\unit\test_cli.py::test_doctor_require_localization_accepts_package_only_spanish_language tests\unit\test_cli.py::test_doctor_require_localization_language_overrides_runtime_voice
```

Result: `6 passed`.

CLI checks:

- `ai-presenter localization-report --package ringcentral-video --language es`
  reports `26/27` Spanish alias entrypoints and `69` aliases.
- `ai-presenter doctor --profile ringcentral-video-bind-speaker --package
  ringcentral-video --flow meeting-control-map-demo` reports `156`
  package-owned aliases, duplicate checks OK, Q&A overlap OK, substring risk
  unchanged at `11`, and `0 warnings, 0 failed`.

## Review Notes

Reviewer should focus on:

- Whether the runtime matching tweak is appropriately scoped to fuzzy Q&A token
  fallback and does not weaken exact Q&A safety.
- Whether any Spanish alias is too broad or action-like.
- Whether `settings.background.blur` should remain intentionally without a
  Spanish alias.
- Whether Spanish runtime support remains unsupported after full verification.
