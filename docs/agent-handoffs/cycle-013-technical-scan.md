# Cycle 013 Technical Scan: Voice Discovery

Date: 2026-05-16

## Existing Seams

- `cli.py` already has `resolve_voice_settings()` and voice-aware `demo`/`controller`.
- `diagnostics.py` has structured `DiagnosticCheck` and `DiagnosticReport`.
- `runtime.voice` owns language/tone choices, alias maps, descriptions, normalization, routing, and validation.
- `test_cli.py`, `test_diagnostics.py`, and `test_voice.py` have focused CLI/diagnostic/voice coverage.

## Recommended Changes

- Add public metadata helpers in `runtime.voice`:
  - `presenter_language_aliases(language)`
  - `presenter_tone_aliases(tone)`
  - `presenter_tone_description(tone)`
- Extend `diagnose_configuration()` with optional `voice`.
- Add `_diagnose_voice()` using `validate_profile_voice()` and `resolve_speech_provider_name()`.
- Add CLI `voices` command near `flows` and `entrypoints`.
- Extend `doctor` with optional `--language` and `--tone`; only pass a voice diagnostic when either is supplied.

## Test Strategy

- Voice helper tests for aliases/descriptions.
- Diagnostics tests for supported and unsupported voice checks.
- CLI tests for catalog output, profile support rows, targeted incompatible validation, and doctor opt-in checks.

## Risks

- Existing doctor tests should remain stable when no voice options are supplied.
- Avoid scraping private alias dictionaries from CLI; use public helper functions.
- Keep the compatibility source of truth in `validate_profile_voice()`.
