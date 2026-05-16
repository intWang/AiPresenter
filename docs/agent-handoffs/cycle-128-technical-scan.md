# Cycle 128 Technical Scan: Spanish Runtime Presenter Promotion

Date: 2026-05-16

Scope: technical scan only. This is the only intended file change. Do not edit source code, package YAML, existing docs, stage files, or commit from this scan.

## Executive Finding

Spanish is package-local complete but not a runtime presenter language yet.

Current evidence:

- `packages/ringcentral-video.yaml` has complete Spanish required localization: `51/51` demo steps, `12/12` Q&A questions, and `12/12` Q&A answers.
- `questionAliases.es` is present on `26/27` entrypoints with `69` aliases.
- `src/ai_presenter/runtime/voice.py` defines `PresenterLanguage = Literal["en", "zh", "ja"]`; `_LANGUAGE_ALIASES` has no `es`, `es-es`, `es-mx`, or `spanish`.
- `ai-presenter voices` lists English, Chinese, and Japanese only.
- `doctor --require-localization --localization-language es` currently reports `[OK] localization` and `[FAIL] runtime language support`.
- `demo --language es` currently fails before runtime with `Unsupported presenter language: es`.

The safe minimal promotion path is OpenAI-backed Spanish first. Existing local speech routes are English- or Chinese-specific: Piper defaults to `en_US-lessac-medium`, Windows SAPI English uses `Zira`, and Windows SAPI Chinese uses `Huihui`. Do not mark Spanish supported on local profiles unless a Spanish local voice route and asset check are explicitly added.

## Files To Change For Implementation

Required runtime files:

- `src/ai_presenter/runtime/voice.py`
  - Add `es` to `PresenterLanguage`.
  - Add `("Spanish", "es")` to `PRESENTER_LANGUAGE_CHOICES`.
  - Add `_LANGUAGE_LABELS["es"] = "Spanish"`.
  - Add aliases such as `es`, `es-es`, `es-mx`, `spanish`, and `espanol`. Consider the accented Spanish self-name too; the CLI catalog escapes non-ASCII aliases safely.
  - Let `render_presenter_text()` treat Spanish like Japanese for authored local text: no English tone prefixes. For fallback English text, either return the source text unchanged or add a very small Spanish branch only if tests define that behavior. Prefer relying on `localizedText.es`.
  - Update `validate_profile_voice()` so `language == "es"` is supported only when `resolve_speech_provider_name()` returns `openai`.

- `src/ai_presenter/runtime/diagnostics.py`
  - No structural change should be needed if `normalize_presenter_language("es")` succeeds. Existing runtime language support diagnostics will flip from FAIL to OK.

- `src/ai_presenter/cli.py`
  - Usually no direct code change: CLI language choices and `voices` output are data-driven by `PRESENTER_LANGUAGE_CHOICES`.

- `src/ai_presenter/runtime/controller.py`
  - Usually no direct code change: the controller language menu uses `PRESENTER_LANGUAGE_CHOICES`.

Likely no source change:

- `src/ai_presenter/runtime/factory.py`
  - Provider creation already registers `openai` speech when `providers.speech == "openai"` and routes speech through `resolve_speech_provider_name()`.
  - Do not add Spanish local routing here unless implementing a real `windows-sapi-es` or Spanish Piper route.

- `src/ai_presenter/runtime/voice_assets.py`
  - No change for OpenAI-only Spanish, because OpenAI and fake routes return `None` for asset checks today.
  - Add checks only if adding a local Spanish route.

- `profiles/*.yaml` and `src/ai_presenter/profiles/*.yaml`
  - No required profile change for OpenAI-only Spanish. Use `profiles/ringcentral-video-openai.example.yaml` for runnable Spanish.
  - Do not add Spanish support claims to fake, Piper, or Windows SAPI profiles without matching local voice support.

- `packages/ringcentral-video.yaml`
  - No package localization change required for runtime promotion. Spanish package content is already complete.

- `pyproject.toml`
  - No required runtime promotion change. Note: package data currently includes bundled profiles and presenter docs, not root `packages/*.yaml`; this is existing behavior and should not be mixed into the runtime-language change unless the release goal includes packaged material packages.

## Tests To Update Or Add

Focused tests:

- `tests/unit/test_voice.py`
  - Update `test_voice_settings_normalize_language_aliases()` for Spanish aliases.
  - Add or update public alias test for `presenter_language_aliases("es-MX")`.
  - Change `test_voice_settings_reject_unknown_language_and_tone()` to reject another unknown language, not `es`.
  - Add `render_voice_instruction(PresenterVoiceSettings(language="es"))` includes `Spanish`.
  - Add `render_narration_text()` prefers `localizedText.es` and keeps Spanish text free of English prefixes for non-concise tones.
  - Add concise Spanish localized text first-sentence behavior if Spanish shares `_apply_tone_to_localized_text()`.
  - Add OpenAI profile validation passes for Spanish.
  - Add fake, Windows SAPI, and Piper validation failures for Spanish with clear error text.

- `tests/unit/test_cli.py`
  - Update `test_demo_rejects_unknown_language_before_runtime()` to use a still-unknown language such as `fr`.
  - Add `demo --profile profiles/ringcentral-video-openai.example.yaml --language es --dry-run` passes when provider environment checks are not involved.
  - Add `controller --profile profiles/ringcentral-video-openai.example.yaml --language es --dry-run` passes.
  - Add fake profile Spanish rejection before runtime runner is called.
  - Update `test_voices_lists_language_tone_choices()` to expect Spanish.
  - Update `test_voices_profile_reports_supported_and_unsupported_languages()` to show Spanish unsupported for fake.
  - Add `voices --profile profiles/ringcentral-video-openai.example.yaml --language es` reports supported via `openai`.
  - Update doctor localization tests: `--localization-language es` should now produce `[OK] runtime language support`.

- `tests/unit/test_diagnostics.py`
  - Update package-only Spanish runtime-language tests to expect OK, or retarget package-only behavior to another complete-but-runtime-unsupported fixture language.
  - Add Spanish OpenAI voice diagnostic OK.
  - Add Spanish fake or Piper voice diagnostic FAIL.

- `tests/unit/test_runtime_factory.py`
  - Add an existing-window material demo test that uses the OpenAI profile with `PresenterVoiceSettings(language="es")` and verifies the runner resolves speech provider `openai` and applies `localizedText.es`.
  - Do not instantiate real OpenAI clients; inject a registry as existing tests do.

- `tests/unit/test_controller.py` and `tests/unit/test_controller_view_model.py`
  - Only update if assertions enumerate language labels or blocked voice-readiness text. The controller menu itself is data-driven.

- `tests/unit/test_voice_assets.py`
  - Add a Spanish OpenAI route check only if useful: `check_voice_asset_availability(openai_profile, PresenterVoiceSettings(language="es")) is None`.
  - Add Spanish local asset tests only if implementing local Spanish routes.

Existing package tests should remain valid:

- `tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_complete_spanish_package`
- `tests/unit/test_material_packages.py::test_ringcentral_spanish_qas_and_demo_flows_are_localized`
- `tests/unit/test_material_packages.py::test_ringcentral_package_owns_spanish_aliases_for_location_routes`

## Expected Profile Behavior After Minimal Promotion

Fake profile, `profiles/ringcentral-video.yaml`:

- `--language en`: supported via `fake`, unchanged.
- `--language es`: unsupported. Expected error should mention `Spanish / <Tone>`, `speech provider fake`, and `openai`.
- Rationale: fake is currently treated as English-only for runtime language validation, even though the test provider can synthesize arbitrary WAV bytes.

OpenAI profile, `profiles/ringcentral-video-openai.example.yaml`:

- `--language es`: supported via `openai`.
- `render_narration_text()` should use `localizedText.es` when present.
- Voice asset preflight should not require local assets.
- Runtime still requires OpenAI environment only when actual provider construction or doctor provider-environment checks run.

Windows SAPI profiles:

- `profiles/ringcentral-video-bind-speaker.yaml` with `speech: windows-sapi-en`: Spanish unsupported.
- `profiles/ringcentral-video-codex-cli-speaker.yaml` with `speech: windows-sapi`: Spanish unsupported for minimal promotion.
- Any `speech: windows-sapi-zh`: Spanish unsupported.
- Rationale: current registry selects generic SAPI, Zira, or Huihui only; voice asset checks know only generic, Zira, and Huihui routes. A safe Spanish local route would need a named Spanish SAPI voice target and asset check, probably `windows-sapi-es`.

Piper profile, `profiles/ringcentral-video-piper-speaker.yaml`:

- `--language en`: supported via `piper`, unchanged.
- `--language zh`: supported via `windows-sapi-zh` fallback, unchanged.
- `--language es`: unsupported for minimal promotion.
- Rationale: current Piper provider defaults to `en_US-lessac-medium`; no Spanish Piper voice asset model/config or route exists.

## Minimal Implementation Plan

1. Update `tests/unit/test_voice.py` first for Spanish normalization, labels, localized narration rendering, OpenAI validation success, and local-provider validation failures.
2. Implement the smallest `voice.py` change: add Spanish choices, labels, aliases, localized-text behavior, and OpenAI-only validation.
3. Update CLI and diagnostics tests whose current assertions intentionally preserve package-only Spanish.
4. Add runtime factory coverage proving OpenAI Spanish uses `localizedText.es` and routes to `openai` with an injected registry.
5. Run focused tests, then broaden to runtime/CLI/package localization tests.
6. Update durable docs only in the implementation cycle if requested: `docs/knowledge/language-lifecycle.md` will need its "Current Spanish State" changed from package-only to runtime-promoted/OpenAI-backed.

## Test Plan

Focused command set:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py tests\unit\test_voice_assets.py
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_voices_lists_language_tone_choices tests\unit\test_cli.py::test_voices_profile_reports_supported_and_unsupported_languages tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py tests\unit\test_runtime_factory.py
```

CLI smoke commands:

```powershell
.\.venv\Scripts\ai-presenter.exe voices
.\.venv\Scripts\ai-presenter.exe voices --profile profiles/ringcentral-video-openai.example.yaml --language es
.\.venv\Scripts\ai-presenter.exe voices --profile ringcentral-video --language es
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe doctor --profile profiles/ringcentral-video-openai.example.yaml --package ringcentral-video --require-localization --localization-language es
.\.venv\Scripts\ai-presenter.exe demo --profile profiles/ringcentral-video-openai.example.yaml --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
```

Expected smoke results after minimal promotion:

- `voices` lists Spanish aliases.
- OpenAI profile selected Spanish voice is supported via `openai`.
- Fake profile selected Spanish voice exits nonzero as unsupported.
- Spanish localization report remains complete.
- Doctor with OpenAI profile and `--localization-language es` reports runtime language support OK, but may still fail provider environment if required OpenAI env vars are absent.
- Demo dry run with OpenAI profile and Spanish succeeds because dry-run returns before provider construction.

## Likely Pitfalls

- Accidentally treating package localization completion as local TTS readiness. Spanish package content is complete, but local Spanish speech assets are not modeled.
- Letting `PRESENTER_LANGUAGE_CHOICES` expose Spanish before validation is updated. The controller and `voices` command consume that tuple directly.
- Leaving tests that assert `Unsupported presenter language: es`; those should be retargeted to a still-unsupported language.
- Forgetting diagnostics: `_diagnose_runtime_language_support()` will automatically flip once `normalize_presenter_language("es")` works, so tests expecting package-only Spanish must change.
- Adding English tone prefixes to Spanish localized narration. Spanish should behave like Japanese/localized text: authored text stays authored except concise first-sentence trimming.
- Assuming `python -m ai_presenter.cli ...` runs the Typer app. Existing handoffs note the console script path is the reliable smoke path.
- Mixing packaging changes into runtime promotion. `pyproject.toml` package data does not include root material packages today; changing that is a separate release/package-distribution concern.
- Staging `.coverage`; it was already modified at the start of this scan and should be left alone.

## Verification Performed During Scan

Commands run from `C:\Users\rcadmin\Documents\Repos\AiPresenter`:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py tests\unit\test_voice_assets.py tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_cli.py::test_doctor_require_localization_accepts_package_only_spanish_language tests\unit\test_diagnostics.py::test_diagnostics_require_localization_flags_package_only_runtime_language
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es
.\.venv\Scripts\ai-presenter.exe voices
```

Observed:

- Focused current-state tests: `33 passed`.
- Spanish localization report: `51/51` demo steps, `12/12` Q&A questions, `12/12` Q&A answers, `questionAliases.es` on `26/27` entrypoints with `69` aliases.
- Voices catalog lists English, Chinese, and Japanese only.
