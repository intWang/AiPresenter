# Cycle 151 Technical Scan: Minimal Tone And Language Extension Slice

Date: 2026-05-17
Cycle: 151
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Scope

This scan reviews the current runtime presenter tone/language definitions,
aliases, CLI `voices` catalog output, tests, README guidance, and language
lifecycle boundaries.

No source, test, package, or `.coverage` files were modified for this scan.
The recommended follow-up is a small test-first runtime voice alias change.

Read inputs:

- `src/ai_presenter/runtime/voice.py`
- `src/ai_presenter/cli.py` `voices` output path
- `tests/unit/test_voice.py`
- `tests/unit/test_cli.py` `voices` tests
- `README.md`
- `docs/knowledge/language-lifecycle.md`

## Existing Structure

Runtime presenter voice support is centralized in
`src/ai_presenter/runtime/voice.py`.

Language support currently includes these canonical runtime languages:

- `en` / English
- `zh` / Chinese
- `ja` / Japanese
- `es` / Spanish

The language surface is represented in several parallel structures:

- `PresenterLanguage` literal
- `PRESENTER_LANGUAGE_CHOICES`
- `_LANGUAGE_LABELS`
- `_LANGUAGE_ALIASES`
- provider compatibility in `validate_profile_voice(...)`
- provider routing in `resolve_speech_provider_name(...)`

Tone support currently includes these canonical tones:

- `professional`
- `conversational`
- `concise`
- `friendly`
- `coach`
- `formal`
- `support`
- `careful`

The tone surface is represented in parallel structures:

- `PresenterTone` literal
- `PRESENTER_TONE_CHOICES`
- `_TONE_DESCRIPTIONS`
- `_TONE_LABELS`
- `_TONE_ALIASES`
- tone-specific rendering in `render_presenter_text(...)`
- localized concise handling in `_apply_tone_to_localized_text(...)`
- Chinese SAPI rate tuning in `sapi_rate_for_voice(...)`

`supportive` is already an alias for canonical tone `support`.
`concise` is already a canonical tone, with `brief` as an alias.

## CLI Voices Output

`src/ai_presenter/cli.py` renders the voice catalog through
`_print_voice_catalog()`.

The catalog does not maintain a separate CLI-specific alias list. It calls:

- `presenter_language_aliases(language_value)` for each
  `PRESENTER_LANGUAGE_CHOICES` entry.
- `presenter_tone_aliases(tone_value)` for each `PRESENTER_TONE_CHOICES` entry.
- `presenter_tone_description(tone_value)` for tone descriptions.

The output is intentionally ASCII-safe through `_format_voice_aliases(...)`,
which escapes non-ASCII aliases with `backslashreplace` for legacy Windows
console compatibility.

Current CLI tests around `voices` live in `tests/unit/test_cli.py`:

- `test_voices_lists_language_tone_choices`
- `test_voices_catalog_output_is_ascii_safe_for_legacy_windows_console`
- `test_voices_profile_reports_supported_and_unsupported_languages`
- `test_voices_profile_reports_local_asset_status`
- `test_voices_targeted_incompatible_profile_voice_exits_nonzero`
- `test_voices_targeted_openai_spanish_profile_is_supported`
- `test_voices_targeted_missing_assets_exits_nonzero`

The most relevant catalog test already asserts that language and tone sections
render and that expanded tone aliases/descriptions such as `calm`, `executive`,
`recovery-focused`, and `privacy-aware` appear.

## Existing Voice Tests

`tests/unit/test_voice.py` already covers:

- default settings are English/professional;
- language aliases normalize for English, Chinese, Japanese, and Spanish;
- public language alias tuples are canonical and ordered;
- expanded tone aliases normalize;
- public tone alias tuples and descriptions are canonical and ordered;
- unknown languages and tones raise `ValueError`;
- tone instructions include expanded descriptions;
- English tone rendering for friendly, coach, formal, support, and careful;
- localized text keeps Japanese/Spanish free of English prefixes;
- concise handling for localized narration;
- provider compatibility and routing for Chinese, Japanese, Spanish, and local
  SAPI fallbacks;
- Chinese SAPI rate tuning per tone.

Because alias tuple order is asserted exactly, any new alias added to an
existing canonical tone should update that exact tuple assertion.

## Recommended Minimal Test-First Change

Add one tone alias:

```python
"empathetic": "support",
```

Recommended rationale:

- It is a true minimal extension of the tone/language surface.
- It does not introduce a new canonical tone, label, description, provider
  route, localized behavior, or SAPI rate.
- It maps naturally to existing `support`, whose description is
  `calm, diagnostic, recovery-focused, and reassuring`.
- It exercises both runtime normalization and CLI `voices` catalog output.
- It avoids duplicating existing `supportive` and `concise` support.

Expected implementation footprint:

- Modify `src/ai_presenter/runtime/voice.py` only in `_TONE_ALIASES`.
- Modify `tests/unit/test_voice.py` for normalization and public alias tuple
  expectations.
- Modify `tests/unit/test_cli.py` to assert `empathetic` appears in
  `ai-presenter voices` output.

No package YAML, profile YAML, README, lifecycle doc, or `.coverage` changes
should be needed.

## Expected Assertions

Recommended voice test updates in `tests/unit/test_voice.py`:

- Extend `test_voice_settings_normalize_expanded_tones`:

```python
assert PresenterVoiceSettings(tone="empathetic").tone == "support"
```

- Extend the support tuple in
  `test_presenter_tone_aliases_and_description_are_public`:

```python
assert voice.presenter_tone_aliases("calm") == (
    "support",
    "supportive",
    "helpdesk",
    "troubleshooting",
    "recovery",
    "calm",
    "steady",
    "reassuring",
    "empathetic",
)
```

Recommended CLI test update in `tests/unit/test_cli.py`:

- Extend `test_voices_lists_language_tone_choices`:

```python
assert "empathetic" in result.stdout
```

This proves the public CLI catalog sees the alias through the shared runtime
alias map, without adding CLI-only logic.

## TDD Red-Light Method

Use a direct test-first red light:

1. Add the `test_voice.py` and `test_cli.py` assertions above.
2. Run the focused tests before editing `voice.py`.
3. Confirm failures:
   - `PresenterVoiceSettings(tone="empathetic")` raises
     `Unsupported presenter tone: empathetic`.
   - `presenter_tone_aliases("calm")` lacks `empathetic`.
   - `voices` output lacks `empathetic`.
4. Add `"empathetic": "support"` to `_TONE_ALIASES` in
   `src/ai_presenter/runtime/voice.py`, preferably after `reassuring` to keep
   support-family aliases grouped.
5. Re-run the focused tests and confirm they pass.

Focused test command:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider tests\unit\test_voice.py tests\unit\test_cli.py -k "expanded_tones or presenter_tone_aliases or voices_lists_language_tone_choices"
```

## Documentation Need

README update is optional and not recommended for this smallest slice.

The README currently documents examples of tone aliases such as `warm`,
`mentor`, and `executive`, not an exhaustive alias list. The `voices` command is
the discoverability mechanism for the full alias catalog.

`docs/knowledge/language-lifecycle.md` should not change for this alias-only
tone slice. That document focuses on package-local language coverage versus
runtime language promotion. No new runtime language is being promoted.

If a later cycle adds a new canonical language, then the lifecycle doc should be
updated because runtime support, provider routing, localization readiness, and
live acceptance boundaries all become relevant.

## Risk Boundary

Do not add `supportive` as a new canonical tone. It already exists as an alias
for canonical `support`; promoting it to a canonical tone would require changes
to `PresenterTone`, choices, labels, descriptions, render behavior, CLI output,
and tests.

Do not add `concise` as a new tone. It is already canonical and has localized
first-sentence behavior.

Do not add a new runtime language as the minimal slice unless the cycle expands
scope. A runtime language promotion touches normalization, labels, provider
compatibility, routing, CLI catalog behavior, controller/demo choices, doctor
checks, package lifecycle documentation, and acceptance boundaries.

Do not treat package-local localization keys as runtime presenter language
support. The language lifecycle doc explicitly separates package coverage from
runtime voice readiness.

Do not update package YAML, profiles, generated artifacts, `.coverage`, or
unrelated files from other agents.

## Validation Commands

For this handoff document:

```powershell
rg -n "[ \t]+$" docs\agent-handoffs\cycle-151-technical-scan.md
git diff --check -- docs\agent-handoffs\cycle-151-technical-scan.md
```

For the later implementation:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider tests\unit\test_voice.py tests\unit\test_cli.py -k "expanded_tones or presenter_tone_aliases or voices_lists_language_tone_choices"
git diff --check -- src\ai_presenter\runtime\voice.py tests\unit\test_voice.py tests\unit\test_cli.py
git diff -- packages profiles README.md docs\knowledge\language-lifecycle.md .coverage
```

Expected final implementation footprint:

- `src/ai_presenter/runtime/voice.py`
- `tests/unit/test_voice.py`
- `tests/unit/test_cli.py`

Expected untouched files:

- package YAML
- profile YAML
- README, unless the cycle explicitly asks for user-facing alias examples
- `docs/knowledge/language-lifecycle.md`, unless adding/promoting a runtime
  language
- `.coverage`
