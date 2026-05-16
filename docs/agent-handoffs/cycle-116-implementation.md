# Cycle 116 Implementation: Executive Tone Alias

Date: 2026-05-16
Scope: small runtime tone-vocabulary expansion.

## Decision

Cycle 116 implemented the technical scan's smallest safe slice: add operator-facing business presentation aliases that normalize to the existing `formal` tone.

New aliases:

- `executive`
- `briefing`
- `boardroom`

They all resolve to `formal`, so the change expands how operators can request tone without adding a new canonical tone, changing provider routing, changing RingCentral safety policy, or changing package localization semantics.

## Why Runtime Spanish Was Deferred

The first red-test exploration checked whether Spanish could become a runtime presenter language. The demand, technical, and risk handoffs all showed that this would be premature in Cycle 116:

- Spanish package coverage is still report-only and incomplete.
- `localization-report --language es --require-complete` should continue to fail.
- Runtime voices should still list English, Chinese, and Japanese only.
- `PresenterVoiceSettings(language="es")` should remain unsupported until a larger Spanish package and voice-readiness slice exists.

The exploratory Spanish tests were removed before implementation. No Spanish runtime behavior was enabled.

## Files Changed

- `src/ai_presenter/runtime/voice.py`
  - Maps `executive`, `briefing`, and `boardroom` to the existing `formal` canonical tone.
- `tests/unit/test_voice.py`
  - Proves the new aliases normalize to `formal` and are exposed by `presenter_tone_aliases()`.
- `tests/unit/test_cli.py`
  - Proves the public `voices` catalog displays the new alias while remaining ASCII-safe.
- `README.md`
  - Updates the tone-alias example to include `executive`.

## Focused Red/Green Evidence

Red command:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py::test_voice_settings_normalize_expanded_tones tests\unit\test_voice.py::test_presenter_tone_aliases_and_description_are_public tests\unit\test_cli.py::test_voices_lists_language_tone_choices tests\unit\test_cli.py::test_voices_catalog_output_is_ascii_safe_for_legacy_windows_console
```

Initial result:

- `3 failed, 1 passed`
- Failures were the expected unsupported `executive` tone and missing `executive` catalog output.

Green result after implementation:

- `4 passed`

## Boundaries Preserved

- No package YAML changed.
- No runtime language changed.
- No profile changed.
- No provider route changed.
- No RingCentral evidence or live acceptance claim changed.
- No safety routing, `questionPolicy`, `can_operate`, or interrupt behavior changed.
- `.coverage` remains out of scope and must not be staged.
