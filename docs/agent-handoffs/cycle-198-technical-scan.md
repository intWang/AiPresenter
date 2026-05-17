# Cycle 198 Technical Scan: Language Support And Provider Compatibility

Date: 2026-05-17

## Read-Only Findings

Runtime presenter language support is defined in
`src/ai_presenter/runtime/voice.py`:

- Canonical runtime languages: `en`, `zh`, `ja`, `es`.
- Public language catalog: `PRESENTER_LANGUAGE_CHOICES`.
- Public aliases: `presenter_language_aliases(...)`.
- Package-language lookup: `src/ai_presenter/cli.py::resolve_package_language_key(...)`.

Provider compatibility is runtime-gated:

- English supports normal configured speech routes except direct
  `windows-sapi-zh`, which routes back to `windows-sapi-en`.
- Chinese requires `openai` or resolved `windows-sapi-zh`.
- Chinese local fallback resolves `piper`, `windows-sapi`, `windows-sapi-en`,
  and `windows-sapi-zh` to `windows-sapi-zh`.
- Japanese requires `openai`.
- Spanish requires `openai`.

Current RingCentral package localization is complete for `zh`, `ja`, and `es`:

- `zh`: `51/51` demo steps, `16/16` Q&A questions, `16/16` Q&A answers;
  `questionAliases.zh` on `15/27` entrypoints.
- `ja`: `51/51` demo steps, `16/16` Q&A questions, `16/16` Q&A answers;
  `questionAliases.ja` on `13/27` entrypoints.
- `es`: `51/51` demo steps, `16/16` Q&A questions, `16/16` Q&A answers;
  `questionAliases.es` on `26/27` entrypoints.

Package localization completeness is not provider compatibility, voice asset
readiness, controller/demo readiness, or live RingCentral acceptance.

## Recommended Durable Doc

Update `docs/knowledge/language-lifecycle.md` with a
`## Current Language State Matrix` section. This belongs in the lifecycle doc,
not the tone matrix, because it covers package localization, runtime language
support, provider compatibility, and live acceptance boundaries.

Recommended table columns:

- Runtime key
- Label
- Aliases
- Package localization state
- Runtime presenter language
- Provider compatibility
- Local voice assets
- Live acceptance evidence

## Docs-Contract Test

Use `tests/unit/test_cli.py`, next to the existing package-language
documentation contract. The test should iterate over
`cli.PRESENTER_LANGUAGE_CHOICES`, require each language row and alias list in
the doc, and lock the phrases that separate package checks from runtime voice
selection and live evidence.

## Runtime Phrases To Guard

- `PRESENTER_LANGUAGE_CHOICES`
- `presenter_language_aliases(...)`
- `resolve_package_language_key(...)`
- `validate_profile_voice(...)`
- `resolve_speech_provider_name(...)`
- `--localization-language` checks package text
- `--language` selects runtime presenter voice
- Chinese can use OpenAI speech or `windows-sapi-zh`
- Japanese requires OpenAI speech
- Spanish requires OpenAI speech
- local SAPI/Piper Spanish remains future work
- Live acceptance requires a dated acceptance run

## Commands

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests/unit/test_cli.py::test_language_lifecycle_matrix_matches_runtime_language_contract
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests/unit/test_voice.py tests/unit/test_cli.py::test_voices_profile_reports_supported_and_unsupported_languages tests/unit/test_cli.py::test_voices_targeted_openai_spanish_profile_is_supported tests/unit/test_cli.py::test_doctor_openai_profile_accepts_spanish_runtime_language tests/unit/test_cli.py::test_doctor_rejects_package_only_language_after_complete_localization
git diff --check
git status --short
```

## Non-Goals

Do not change runtime provider behavior, profiles, package YAML, voice assets,
or RingCentral acceptance claims in this docs-contract slice.
