# Cycle 129 Implementation Handoff: Spanish OpenAI Runtime Proof

Date: 2026-05-16
Cycle: 129
Scope: implementation evidence handoff only. This document summarizes the
current uncommitted Cycle129 diff and the demand, technical, and risk handoffs.
No source, tests, durable docs, package YAML, profiles, generated artifacts,
staging, commits, or live acceptance evidence were modified by this handoff.

## Summary

Cycle129 now has focused implementation evidence for Spanish as an
OpenAI-backed runtime presenter language, while preserving the explicit boundary
that Spanish local SAPI/Piper support and live RingCentral Video acceptance are
not proven.

The current uncommitted diff shows:

- `src/ai_presenter/runtime/controller.py`
  - `_check_controller_voice_readiness()` now calls
    `validate_profile_voice(profile, voice)` before local asset checks.
  - Incompatible profile/language combinations return
    `ControllerVoiceReadiness(status="FAIL", label="FAIL", detail=str(exc))`.
  - This prevents Spanish local profiles from falling through to SAPI/Piper
    asset availability checks.

- `src/ai_presenter/runtime/questions.py`
  - Adds a Spanish no-match fallback:
    `No encontre un control que coincida en el contexto activo de la app.`

- `tests/unit/test_runtime_factory.py`
  - Adds OpenAI Spanish material-demo evidence that
    `run_existing_window_material_demo()` routes Spanish speech through the
    OpenAI speech provider and applies `localizedText.es`.
  - Adds stricter injected-registry evidence proving the runtime can use a
    supplied `openai` speech provider without constructing
    `OpenAISpeechProvider`, while still passing Spanish localized narration to
    the timeline runner.

- `tests/unit/test_controller.py`
  - Adds readiness coverage proving local Spanish is rejected before the asset
    checker is called.
  - Adds question-path coverage proving a Spanish OpenAI controller question
    can start the safe `question-answer-demo` flow and forwards
    `PresenterVoiceSettings(language="es")` to the runner.

- `tests/unit/test_controller_view_model.py`
  - Adds local Spanish blocked-state coverage for Start and Submit.
  - Adds OpenAI Spanish startable-state coverage where voice assets are
    reported as `Not required`.

- `tests/unit/test_questions.py`
  - Adds Spanish no-match fallback coverage and confirms the English fallback
    is not used for Spanish.

## Evidence Observed From Context

The technical scan recorded this focused verification run:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_runtime_factory.py::test_existing_window_material_demo_routes_openai_spanish_and_uses_localized_text tests\unit\test_controller.py::test_controller_voice_readiness_rejects_incompatible_voice_before_asset_check tests\unit\test_controller_view_model.py::test_incompatible_spanish_local_voice_explains_start_and_submit_disabled
```

Observed result in the technical scan: `3 passed in 2.78s`.

Current diff inspection for this handoff showed the Cycle129 implementation
surface as:

```text
src/ai_presenter/runtime/controller.py   |   8 ++
src/ai_presenter/runtime/questions.py    |   1 +
tests/unit/test_controller.py            |  80 +++++++++++++
tests/unit/test_controller_view_model.py |  65 +++++++++++
tests/unit/test_questions.py             |  15 +++
tests/unit/test_runtime_factory.py       | 187 +++++++++++++++++++++++++++++++
```

`.coverage` is also modified in the working tree and should be treated as a
generated artifact unless the cycle owner explicitly decides otherwise.

## Requirement Coverage

- Controller voice readiness now validates profile/language compatibility
  before asset checks. This closes the risk where Spanish on a local profile
  could appear to be an asset-readiness problem instead of a provider
  compatibility failure.
- Runtime factory coverage now includes OpenAI Spanish provider routing and
  `localizedText.es` evidence. The injected-registry test is the stronger
  no-real-provider signal because construction of `OpenAISpeechProvider` is
  made to fail if it is accidentally reached.
- Controller question flow now forwards Spanish OpenAI voice settings into the
  safe question demo path.
- Operator view-model coverage distinguishes blocked local Spanish from
  startable OpenAI Spanish with no local asset preflight requirement.
- Questions fallback now has a Spanish no-match response.

## Residual Risks

- The full recommended Cycle129 verification bundle was not rerun by this
  handoff-only slice. Treat the technical scan's focused `3 passed` result and
  the current diff inspection as context evidence, not a fresh full-suite pass.
- CLI smoke commands for `voices`, `doctor`, `demo --dry-run`, and
  `controller --dry-run` should still be run and recorded before merging if the
  cycle owner wants command-level acceptance evidence in addition to unit tests.
- The Spanish no-match string intentionally uses ASCII-only `No encontre`
  rather than accented Spanish copy; this matches the current diff but may be a
  future copy-polish item.
- `.coverage` is dirty and should not be staged unless explicitly requested.
- Line-ending warnings appeared during diff inspection for modified source and
  test files; review with `git diff --check` before staging.

## No-Live-Acceptance Boundary

This cycle proves code-path and unit-test behavior for Spanish through
OpenAI-backed runtime selection. It does not prove:

- live OpenAI speech synthesis,
- real network behavior,
- live RingCentral Video automation,
- Spanish Windows SAPI support,
- Spanish Piper support,
- or production/live Spanish RingCentral acceptance.

Safe wording remains:

- Spanish is runtime-selectable with OpenAI-backed speech profiles.
- Spanish local SAPI/Piper support is not implemented.
- Spanish RingCentral Video package localization is complete.
- Live RingCentral Spanish acceptance remains unproven until a dated acceptance
  run records provider, profile, flow, audio, and RingCentral evidence.

## Suggested Next Verification

Before merging or staging Cycle129, run:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py::test_voice_validation_allows_spanish_openai_profile tests\unit\test_voice.py::test_voice_validation_rejects_spanish_non_openai_profiles tests\unit\test_voice.py::test_render_narration_text_prefers_localized_spanish_script_without_prefix tests\unit\test_runtime_factory.py::test_existing_window_material_demo_routes_openai_spanish_and_uses_localized_text tests\unit\test_runtime_factory.py::test_existing_window_material_demo_uses_injected_openai_registry_for_spanish tests\unit\test_controller.py::test_presenter_controller_starts_spanish_openai_question_demo_when_idle tests\unit\test_controller.py::test_controller_voice_readiness_rejects_incompatible_voice_before_asset_check tests\unit\test_controller_view_model.py::test_incompatible_spanish_local_voice_explains_start_and_submit_disabled tests\unit\test_controller_view_model.py::test_spanish_openai_view_model_is_startable_without_local_assets tests\unit\test_questions.py::test_spanish_no_match_fallback_is_localized_and_not_operable tests\unit\test_cli.py::test_demo_openai_profile_accepts_spanish_dry_run tests\unit\test_cli.py::test_controller_openai_profile_accepts_spanish_dry_run tests\unit\test_cli.py::test_voices_targeted_openai_spanish_profile_is_supported tests\unit\test_diagnostics.py::test_diagnostics_reports_spanish_openai_voice_supported tests\unit\test_diagnostics.py::test_diagnostics_reports_spanish_local_voice_unsupported
.\.venv\Scripts\ai-presenter.exe voices --profile profiles\ringcentral-video-openai.example.yaml --language es
.\.venv\Scripts\ai-presenter.exe voices --profile profiles\ringcentral-video-bind-speaker.yaml --language es
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe demo --profile profiles\ringcentral-video-openai.example.yaml --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
.\.venv\Scripts\ai-presenter.exe controller --profile profiles\ringcentral-video-openai.example.yaml --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
git diff --check
git status --short
```
