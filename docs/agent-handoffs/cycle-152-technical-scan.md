# Cycle 152 Technical Scan

## Scan Scope

Inspected current tone alias and voice catalog behavior in:

- `src/ai_presenter/runtime/voice.py`
- `tests/unit/test_voice.py`
- `tests/unit/test_cli.py`

The repository already has a modified `.coverage` file. Leave it untouched.
This handoff is documentation only and does not edit source, tests, README,
packages, profiles, or existing docs.

## Current State

`src/ai_presenter/runtime/voice.py` centralizes presenter tone support:

- `PresenterTone` currently has canonical tones `professional`,
  `conversational`, `concise`, `friendly`, `coach`, `formal`, `support`, and
  `careful`.
- `PRESENTER_TONE_CHOICES` exposes the same canonical tones to the CLI.
- `_TONE_DESCRIPTIONS` describes canonical tone instructions.
- `_TONE_ALIASES` maps user-facing aliases to canonical tones.
- `presenter_tone_aliases()` returns aliases in dictionary insertion order for
  the canonical tone.
- `render_presenter_text()` and `sapi_rate_for_voice()` branch only on
  canonical tones, so alias-only additions do not need new render or SAPI
  behavior.

Current support aliases are:

```python
"support": "support",
"supportive": "support",
"helpdesk": "support",
"troubleshooting": "support",
"recovery": "support",
"calm": "support",
"steady": "support",
"reassuring": "support",
```

`tests/unit/test_voice.py` already covers the relevant runtime surface:

- `test_voice_settings_normalize_expanded_tones`
- `test_presenter_tone_aliases_and_description_are_public`
- `test_voice_instruction_describes_expanded_tones`
- `test_render_presenter_text_applies_expanded_english_tones`
- `test_sapi_rate_for_voice_maps_chinese_tones_to_practical_rates`

`tests/unit/test_cli.py::test_voices_lists_language_tone_choices` covers the
CLI catalog. The command implementation prints tone aliases by iterating
`PRESENTER_TONE_CHOICES` and calling `presenter_tone_aliases(tone_value)` plus
`presenter_tone_description(tone_value)`, so a runtime alias added to
`_TONE_ALIASES` should surface in `ai-presenter voices` without CLI-specific
wiring.

## Smallest TDD Slice

Add one alias:

```python
"empathetic": "support",
```

This is the smallest useful tone expansion because it:

- extends an existing canonical tone instead of creating a new one;
- maps naturally to `support`, whose description is already calm,
  diagnostic, recovery-focused, and reassuring;
- reuses existing English, localized, provider routing, and SAPI behavior;
- proves runtime normalization and public CLI catalog discoverability;
- avoids README, package YAML, profile YAML, lifecycle docs, and `.coverage`.

## Exact Files For The Implementation Cycle

Modify only these files during the implementation cycle:

- `tests/unit/test_voice.py`
- `tests/unit/test_cli.py`
- `src/ai_presenter/runtime/voice.py`

Do not modify this handoff during implementation unless the user explicitly
asks for a follow-up documentation update.

## Red Tests First

Add these assertions before editing `src/ai_presenter/runtime/voice.py`.

In `tests/unit/test_voice.py::test_voice_settings_normalize_expanded_tones`,
add:

```python
assert PresenterVoiceSettings(tone="empathetic").tone == "support"
```

In
`tests/unit/test_voice.py::test_presenter_tone_aliases_and_description_are_public`,
extend the support alias tuple to:

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

In `tests/unit/test_cli.py::test_voices_lists_language_tone_choices`, add:

```python
assert "empathetic" in result.stdout
```

Run the focused red-light command:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider tests\unit\test_voice.py tests\unit\test_cli.py -k "test_voice_settings_normalize_expanded_tones or test_presenter_tone_aliases_and_description_are_public or test_voices_lists_language_tone_choices"
```

Expected red failures:

- `PresenterVoiceSettings(tone="empathetic")` raises
  `Unsupported presenter tone: empathetic`.
- `presenter_tone_aliases("calm")` does not include `empathetic`.
- `ai-presenter voices` output does not include `empathetic`.

If the tests pass before the implementation edit, stop and re-check the current
code because the alias may already have been added by another agent.

## Green Implementation

Make the minimal runtime change in `src/ai_presenter/runtime/voice.py` by adding
`empathetic` to `_TONE_ALIASES` in the support group, after `reassuring`:

```python
"support": "support",
"supportive": "support",
"helpdesk": "support",
"troubleshooting": "support",
"recovery": "support",
"calm": "support",
"steady": "support",
"reassuring": "support",
"empathetic": "support",
```

Do not add a new canonical tone, label, description, renderer branch, SAPI rate,
provider route, profile entry, or CLI catalog branch.

## Verification Commands

After the green edit, rerun the focused test command:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider tests\unit\test_voice.py tests\unit\test_cli.py -k "test_voice_settings_normalize_expanded_tones or test_presenter_tone_aliases_and_description_are_public or test_voices_lists_language_tone_choices"
```

Then run the broader impacted unit files:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider tests\unit\test_voice.py tests\unit\test_cli.py
```

Optional manual catalog check:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m ai_presenter.cli voices
```

Expected catalog signal:

- The `Support aliases:` line includes `empathetic`.
- The catalog remains ASCII safe.

## No-Go Scope

Do not include any of the following in the smallest slice:

- new canonical tone such as `empathetic` or `supportive`;
- changes to `PresenterTone`, `PRESENTER_TONE_CHOICES`, `_TONE_LABELS`, or
  `_TONE_DESCRIPTIONS`;
- changes to `render_presenter_text()`, `_render_chinese()`,
  `_apply_tone_to_localized_text()`, or `sapi_rate_for_voice()`;
- changes to profile compatibility, speech provider routing, or voice assets;
- README, lifecycle docs, packages, profiles, generated artifacts, or
  `.coverage`;
- broad alias cleanup or reordering outside the support tuple.

The slice is complete when the new alias normalizes to `support`, the public
support alias tuple includes it in the expected order, and the CLI `voices`
catalog prints it through the existing shared runtime helpers.
