# Cycle 199 Technical Scan: Voice Catalog Discoverability

Date: 2026-05-17

## Read-Only Finding

The smallest useful CLI discoverability improvement is to teach
`ai-presenter voices` to explain the boundary between runtime voice selection,
profile/provider checks, package localization, and live acceptance.

Current runtime behavior should not change. Provider compatibility remains owned
by `validate_profile_voice(...)` and `resolve_speech_provider_name(...)`.

## Exact Minimal Change

Add a short static note inside `src/ai_presenter/cli.py::_print_voice_catalog`,
after the language alias list and before tones:

- `Language readiness:`
- `--language selects a runtime presenter voice.`
- `--profile checks speech provider compatibility and local voice assets.`
- `Package localization and live acceptance are separate checks.`

Add one focused CLI test:

- `tests/unit/test_cli.py::test_voices_catalog_explains_language_readiness_boundaries`

No runtime provider code is touched.

## Source Locations

- `src/ai_presenter/cli.py` - `voices(...)` always prints the catalog, then
  optionally checks profile compatibility and selected voice assets.
- `src/ai_presenter/cli.py::_print_voice_catalog` - prints language aliases,
  readiness note, and tone aliases.
- `tests/unit/test_cli.py::test_voices_lists_language_tone_choices` - existing
  catalog coverage.
- `tests/unit/test_cli.py::test_voices_catalog_output_is_ascii_safe_for_legacy_windows_console`
  - ASCII-safe catalog coverage.
- `tests/unit/test_cli.py::test_voices_profile_reports_supported_and_unsupported_languages`
  - profile language matrix.
- `tests/unit/test_cli.py::test_voices_targeted_openai_spanish_profile_is_supported`
  - OpenAI Spanish selected voice support.
- `src/ai_presenter/runtime/voice.py` - runtime profile voice validation and
  speech provider routing.
- `docs/knowledge/language-lifecycle.md` - lifecycle doc separates localization,
  runtime language, provider compatibility, assets, and live acceptance.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests/unit/test_cli.py::test_voices_catalog_explains_language_readiness_boundaries
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests/unit/test_cli.py -k "voices"
git diff --check -- src/ai_presenter/cli.py tests/unit/test_cli.py
```

## Risks

- Keep the note static and catalog-only. Do not call provider validation from
  `_print_voice_catalog()`.
- Do not change `validate_profile_voice(...)`, `resolve_speech_provider_name(...)`,
  profiles, voice assets, or runtime provider behavior.
- The output remains ASCII-safe because the added strings are ASCII.
- `.coverage` is unrelated and should not be staged.
