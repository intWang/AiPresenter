# Cycle 128 Implementation: Spanish OpenAI Runtime Promotion

Date: 2026-05-16

## Summary

Spanish is now a limited runtime presenter language for OpenAI-backed speech.
The promotion intentionally stops at the runtime voice boundary:

- `PresenterVoiceSettings(language="es")` normalizes to `es`.
- Public aliases include `es`, `es-es`, `es-mx`, `spanish`, and `espanol`.
- `language_label("es")` returns `Spanish`, and the voices catalog lists it.
- Spanish localized narration uses `localizedText.es`; non-concise authored
  Spanish text is not prefixed with English tone phrases.
- Concise Spanish localized narration uses the first sentence.
- `validate_profile_voice()` accepts Spanish only when the resolved speech
  provider is `openai`.

## Provider Boundary

Spanish remains unsupported for fake, Piper, `windows-sapi`,
`windows-sapi-en`, and `windows-sapi-zh`. Those profiles fail before runtime
with a profile voice compatibility error mentioning Spanish and OpenAI.

No local Spanish SAPI/Piper support was added. No package YAML or profile files
were changed. No live RingCentral Video acceptance is claimed.

## Verification Notes

Red command before implementation:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py tests\unit\test_cli.py::test_demo_rejects_unknown_language_before_runtime tests\unit\test_cli.py::test_demo_openai_profile_accepts_spanish_dry_run tests\unit\test_cli.py::test_controller_openai_profile_accepts_spanish_dry_run tests\unit\test_cli.py::test_demo_rejects_spanish_local_profile_before_runtime tests\unit\test_cli.py::test_voices_lists_language_tone_choices tests\unit\test_cli.py::test_voices_profile_reports_supported_and_unsupported_languages tests\unit\test_cli.py::test_voices_targeted_openai_spanish_profile_is_supported tests\unit\test_cli.py::test_doctor_require_localization_accepts_package_only_spanish_language tests\unit\test_cli.py::test_doctor_openai_profile_accepts_spanish_runtime_language tests\unit\test_cli.py::test_doctor_require_localization_language_overrides_runtime_voice tests\unit\test_diagnostics.py::test_diagnostics_reports_spanish_openai_voice_supported tests\unit\test_diagnostics.py::test_diagnostics_reports_spanish_local_voice_unsupported tests\unit\test_diagnostics.py::test_diagnostics_require_localization_accepts_spanish_runtime_language tests\unit\test_diagnostics.py::test_diagnostics_runtime_language_support_stays_separate_after_package_localization_complete
```

Expected red result observed: `25 failed, 26 passed`; failures were caused by
the current runtime rejecting `es` before normalization and provider checks.

Focused green after implementation: `51 passed`.

## Follow-Up Risks

- OpenAI profile doctor can still fail provider environment checks when required
  OpenAI environment variables are missing.
- Spanish local voice support needs a separate route, asset checks, and tests.
- Live RingCentral Spanish acceptance still needs dated manual or automated
  evidence before docs may claim demo acceptance.
