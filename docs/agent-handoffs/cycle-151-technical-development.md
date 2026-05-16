# Cycle 151 Technical Development: Spanish Runtime Alias Display Slice

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Objective

Capture the Cycle151 implementation handoff for the Spanish runtime language
alias/display slice. The implementation improves operator input ergonomics for
Spanish by routing additional Spanish and Latin American Spanish spellings to
the existing canonical presenter language `es`.

This is alias and catalog polish only. It does not add a new runtime language,
provider route, package localization key, local voice asset, profile behavior,
or live RingCentral acceptance claim.

## Files Changed By Main Implementation

- `src/ai_presenter/runtime/voice.py`
- `tests/unit/test_voice.py`
- `tests/unit/test_cli.py`

This handoff adds only:

- `docs/agent-handoffs/cycle-151-technical-development.md`

`.coverage` was already dirty in the worktree and was not touched.

## Alias Behavior Implemented

`src/ai_presenter/runtime/voice.py` now maps these additional Spanish aliases
to canonical `es`:

- `es-419`
- `es-la`
- `latam-spanish`
- `latin-american-spanish`
- `espa\u00f1ol`

Existing Spanish aliases remain in place:

- `es`
- `es-es`
- `es-mx`
- `spanish`
- `espanol`

The existing key normalizer still strips surrounding whitespace, applies
`casefold()`, and converts underscores to hyphens before lookup. As a result,
inputs such as `es-LA` and `Espa\u00f1ol` resolve through the same canonical
`es` route.

The public alias tuple for Spanish was extended in stable order, and the CLI
`voices` catalog now exposes the added aliases through the shared runtime alias
map. The catalog keeps legacy-console-safe output through the existing
backslash-escaped formatter, so the non-ASCII alias is printed as an ASCII-safe
escaped value.

Package-local language lookup now also benefits from the shared presenter
normalizer: `resolve_package_language_key("es-419") == "es"` and
`resolve_package_language_key("Espa\u00f1ol") == "es"`. Unknown package-only
keys such as `de` still remain raw package lookup keys and are not rejected as
unsupported presenter languages.

## TDD Red/Green Evidence

Prompt-provided focused red evidence before the runtime alias map was updated:

- `PresenterVoiceSettings(language="es-419")` failed as unsupported.
- The public Spanish alias tuple was missing the new aliases.
- Package language lookup returned raw `es-419` instead of canonical `es`.
- The `voices` catalog did not list `es-419`.

Prompt-provided green evidence after adding the aliases to
`src/ai_presenter/runtime/voice.py`:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py tests\unit\test_cli.py::test_voices_lists_language_tone_choices tests\unit\test_cli.py::test_voices_catalog_output_is_ascii_safe_for_legacy_windows_console tests\unit\test_cli.py::test_package_language_alias_normalization_is_documented tests\unit\test_cli.py::test_voices_targeted_openai_spanish_profile_is_supported tests\unit\test_cli.py::test_voices_profile_reports_supported_and_unsupported_languages
```

Result: `42 passed`.

## Provider And Live RingCentral Boundaries

Spanish remains canonical runtime language `es`; `es-419` is not a new
canonical runtime language.

Spanish voice compatibility remains OpenAI-only. The implementation does not
add fake, Piper, `windows-sapi`, `windows-sapi-en`, or `windows-sapi-zh`
Spanish support, and it does not change `validate_profile_voice(...)` or
`resolve_speech_provider_name(...)`.

The alias work does not change RingCentral adapters, live automation,
acceptance records, provider environment checks, profile YAML, package YAML,
runtime controller behavior, demo execution, or local asset readiness.

`voices --profile ... --language ...` remains a profile compatibility check.
It is not live RingCentral Video acceptance. Package-local commands such as
`entrypoints --language ...` and `localization-report --language ...` inspect
package display/localization behavior only; they do not prove provider
availability, local voice assets, or live RingCentral readiness.

## Recommended Follow-Up

Keep the next slice similarly narrow. The deferred tone alias is:

- `empathetic -> support`

That follow-up should be implemented as a separate TDD slice by extending the
support tone alias normalization, public support alias tuple, and CLI `voices`
catalog assertion. It should not promote `empathetic` to a canonical tone or
change provider, profile, package, or live RingCentral behavior.
