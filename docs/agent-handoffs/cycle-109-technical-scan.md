# Cycle 109 Technical Scan: Presenter Tone Expansion

Date: 2026-05-16
Role: technical scan
Scope: inspect-only scan for a small tone-type expansion. This document is the only file edited by this scan.

## Workspace Note

The worktree is shared. At scan time, uncommitted edits already existed in:

- `.coverage`
- `src/ai_presenter/runtime/voice.py`
- `tests/unit/test_voice.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_controller.py`

Those edits appear to implement and test a new `careful` tone. I did not revert, overwrite, or edit those files.

## Current Behavior

The tone model is centralized in `src/ai_presenter/runtime/voice.py`.

- `PresenterVoiceSettings.__init__()` normalizes language and tone strings through `normalize_presenter_language()` and `normalize_presenter_tone()`.
- `PresenterTone` is the canonical type surface. The committed baseline supports `professional`, `conversational`, `concise`, `friendly`, `coach`, `formal`, and `support`; the current live dirty worktree also includes `careful`.
- `PRESENTER_TONE_CHOICES`, `_TONE_DESCRIPTIONS`, `_TONE_LABELS`, and `_TONE_ALIASES` are the single source for dropdown labels, CLI catalog output, public alias lists, and prompt descriptions.
- `render_voice_instruction()` says `Speak in <language>. Use a <description> tone.`
- `render_presenter_text()` applies deterministic English tone prefixes, applies Chinese replacement/prefix behavior through `_render_chinese()`, and keeps Japanese text localized without English prefixes.
- `render_narration_text()` prefers package `localized_text` for the selected canonical language. Localized narration bypasses English-style prefixes and only applies the existing concise first-sentence trimming.
- `sapi_rate_for_voice()` changes only Chinese SAPI pacing: conversational/friendly/support use `-1`, concise uses `1`, and the rest use `0`.
- `validate_profile_voice()` and `resolve_speech_provider_name()` are language/provider checks. Tone choice does not affect provider compatibility or asset routing.

The CLI and controller already consume shared tone metadata.

- `src/ai_presenter/cli.py::resolve_voice_settings()` accepts raw `--tone` strings and lets `PresenterVoiceSettings` normalize or reject them.
- `src/ai_presenter/cli.py::_print_voice_catalog()` lists tones from `PRESENTER_TONE_CHOICES`, with aliases from `presenter_tone_aliases()` and copy from `presenter_tone_description()`.
- `src/ai_presenter/runtime/controller.py::run_controller()` builds the tone option menu from `PRESENTER_TONE_CHOICES` and maps the selected label back to the canonical tone.
- `src/ai_presenter/runtime/controller_view_model.py::render_voice_label()` uses `tone_label()`, so new canonical tones automatically show in status labels.

## Proposed Minimal Implementation

Preferred slice: finish a single canonical `careful` tone for privacy-sensitive and boundary-focused guidance.

Modify only:

- `src/ai_presenter/runtime/voice.py`
- `tests/unit/test_voice.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_controller.py`

Implementation details:

- Extend `PresenterTone` with `careful`.
- Add `("Careful", "careful")` to `PRESENTER_TONE_CHOICES`.
- Add `_TONE_DESCRIPTIONS["careful"]` with copy that includes `privacy-aware` and `boundary-focused`.
- Add `_TONE_LABELS["careful"] = "Careful"`.
- Add `_TONE_ALIASES` entries for `careful`, `safety`, `safe`, `privacy`, `guarded`, and `compliance`.
- Add an English deterministic prefix in `render_presenter_text()`, for example `Safety note. {text}`.
- Add a Chinese prefix in `_render_chinese()` for `careful`.
- Do not change `render_narration_text()` for localized package narration; package-authored localized text should remain final except for the existing concise trim.
- Do not change `validate_profile_voice()`, `resolve_speech_provider_name()`, provider assets, CLI option parsing, or controller wiring.
- Leave `sapi_rate_for_voice()` at the default `0` for `careful` unless product explicitly wants careful Chinese speech slower than support. If changed, add an explicit rate assertion.

Smaller alias-only fallback:

- If Cycle 109 should avoid a new visible dropdown/catalog option, map `safety`, `safe`, `privacy`, `guarded`, and `compliance` to existing `support` in `_TONE_ALIASES`.
- That is lower risk but weaker UX: `ai-presenter voices` and controller labels would still say `Support`, not a privacy-specific tone. It also would not meet a true tone-type expansion goal as cleanly as canonical `careful`.

Do not add a second canonical tone in this slice. If one extra input synonym is needed, prefer another alias to `careful` rather than another `PresenterTone` member.

## Focused Red Tests

If starting from a clean branch, write these tests first and verify they fail before implementing. In the current dirty worktree, equivalent tests already exist.

`tests/unit/test_voice.py`

- Extend `test_voice_settings_normalize_expanded_tones()`:
  - `PresenterVoiceSettings(tone="careful").tone == "careful"`
  - `PresenterVoiceSettings(tone="safety").tone == "careful"`
  - `PresenterVoiceSettings(tone="privacy").tone == "careful"`
  - `PresenterVoiceSettings(tone="guarded").tone == "careful"`
- Extend `test_presenter_tone_aliases_and_description_are_public()`:
  - `presenter_tone_aliases("privacy") == ("careful", "safety", "safe", "privacy", "guarded", "compliance")`
  - `presenter_tone_description("careful")` contains `privacy-aware`.
- Extend `test_voice_instruction_describes_expanded_tones()`:
  - `render_voice_instruction(PresenterVoiceSettings(tone="privacy"))` contains `boundary-focused`.
- Extend `test_render_presenter_text_applies_expanded_english_tones()`:
  - `render_presenter_text("Recording requires consent.", PresenterVoiceSettings(tone="privacy"))` starts with `Safety note.`
- Add `test_render_presenter_text_applies_chinese_careful_tone_without_english_prefix()`:
  - Use `PresenterVoiceSettings(language="zh", tone="safety")`.
  - Assert the Chinese careful prefix is present.
  - Assert `Safety note` is not present.
- Optional explicit no-rate-change assertion in `test_sapi_rate_for_voice_maps_chinese_tones_to_practical_rates()`:
  - `sapi_rate_for_voice(PresenterVoiceSettings(language="zh", tone="careful")) == 0`.

`tests/unit/test_cli.py`

- Extend `test_voices_lists_language_tone_choices()`:
  - assert `Careful aliases:` appears.
  - assert `privacy-aware` appears.

`tests/unit/test_controller.py`

- Extend `test_render_voice_label_uses_controller_labels()`:
  - `render_voice_label(PresenterVoiceSettings(tone="safety")) == "English / Careful"`.

Optional adjacent coverage:

- Add or extend `tests/unit/test_controller_view_model.py::test_operator_view_model_labels_expanded_tone` only if the implementation touches view-model rendering directly. It should not be necessary for this centralized metadata slice.

## Verification Commands

Focused tone slice:

```powershell
.\.venv\Scripts\python.exe -m pytest --no-cov -q tests\unit\test_voice.py tests\unit\test_cli.py::test_voices_lists_language_tone_choices tests\unit\test_controller.py::test_render_voice_label_uses_controller_labels
```

Type and lint checks:

```powershell
.\.venv\Scripts\ruff.exe check --no-cache src\ai_presenter\runtime\voice.py tests\unit\test_voice.py tests\unit\test_cli.py tests\unit\test_controller.py
.\.venv\Scripts\mypy.exe --no-incremental src\ai_presenter\runtime\voice.py tests\unit\test_voice.py tests\unit\test_cli.py tests\unit\test_controller.py
```

Optional broader regression around voice propagation:

```powershell
.\.venv\Scripts\python.exe -m pytest --no-cov -q tests\unit\test_voice.py tests\unit\test_cli.py::test_demo_passes_language_and_tone_to_runtime tests\unit\test_cli.py::test_controller_passes_language_and_tone_to_runtime tests\unit\test_cli.py::test_doctor_accepts_language_and_tone_voice_preflight tests\unit\test_controller.py::test_render_voice_label_uses_controller_labels tests\unit\test_controller_view_model.py::test_operator_view_model_labels_expanded_tone tests\unit\test_runtime_factory.py::test_existing_window_material_demo_uses_tone_rate_when_creating_registry
```

Verification run during this scan:

```text
.\.venv\Scripts\python.exe -m pytest --no-cov -q tests\unit\test_voice.py tests\unit\test_cli.py::test_voices_lists_language_tone_choices tests\unit\test_controller.py::test_render_voice_label_uses_controller_labels
28 passed in 3.01s
```

## Expected Compatibility Risks

- `ai-presenter voices` output changes by listing a new `Careful` tone and aliases. Exact-output consumers must update expectations.
- The Tk controller tone dropdown gains a new visible option because it is generated from `PRESENTER_TONE_CHOICES`.
- `PresenterTone` type expansion requires every tone metadata dict to include `careful`; missing entries would fail at runtime when labels, aliases, or descriptions are requested.
- Alias wording such as `safe` and `safety` may imply operational safety. Keep the description and prefix framed as careful narration only. Tone must not change `can_operate`, safety matching, or package facts.
- English dynamic rendering gains a `Safety note.` prefix for `careful`; localized package narration remains unchanged, so existing Chinese/Japanese authored demo lines should not be rewritten.
- The exact alias tuple order is insertion-order dependent. Keep alias ordering stable if tests assert the public alias list.

## Package YAML, Diagnostics, And Localization Counts

No package YAML should change for this slice.

Expected count impact:

- Operation entrypoint count: unchanged.
- Package-owned alias count: unchanged.
- Q&A prompt count: unchanged.
- Chinese/Japanese demo and Q&A localization coverage: unchanged.
- Diagnostics duplicate/overlap counts: unchanged.
- Voice provider diagnostics: unchanged except the displayed selected voice label can now be `English / Careful`, `Chinese / Careful`, or `Japanese / Careful` when that tone is explicitly selected.
- CLI voice catalog output: intentionally changed because the tone catalog gains `Careful`.

No localization-report command is required for the tone-only slice, because package content is untouched. Run localization reports only as a guard if implementation accidentally touches `packages/ringcentral-video.yaml` or package-loading code.
