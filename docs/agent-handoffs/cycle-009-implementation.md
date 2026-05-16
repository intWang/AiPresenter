# Cycle 009 Implementation: Voice Language And Tone Expansion

Date: 2026-05-16

## Objective

Expand presenter language and tone inputs without overpromising new TTS languages or changing existing demo safety behavior.

## Scope

Implemented the narrow normalization and additive-tone plan:

- Canonical language families remain `en` and `zh`.
- Common aliases such as `English`, `en-US`, `zh-CN`, `zh-Hans`, `zh-TW`, `Chinese`, and `中文` normalize at `PresenterVoiceSettings` construction.
- Unknown languages now raise `ValueError`.
- Added canonical tones:
  - `friendly`
  - `coach`
  - `formal`
- Added tone aliases:
  - `warm` -> `friendly`
  - `mentor` / `coaching` -> `coach`
  - `structured` -> `formal`
- Unknown tones now raise `ValueError`.
- Controller language/tone option menus now use shared metadata from `runtime.voice`.
- Controller and operator view-model labels now use shared label helpers from `runtime.voice`.

Out of scope and intentionally unchanged:

- No new canonical languages such as Spanish/Japanese/French.
- No new TTS providers or profile downloads.
- No CLI voice flags.
- No package YAML localization changes.

## Files Changed

- `src/ai_presenter/runtime/voice.py`
  - Expanded `PresenterTone`.
  - Added `PRESENTER_LANGUAGE_CHOICES` and `PRESENTER_TONE_CHOICES`.
  - Added normalization helpers and label helpers.
  - Replaced generated dataclass init with a normalizing frozen init.
  - Added deterministic text prefixes for `friendly`, `coach`, and `formal`.
  - Kept existing `professional`, `conversational`, and `concise` behavior stable.
- `src/ai_presenter/runtime/controller_view_model.py`
  - Removed local voice label maps.
  - Uses shared `language_label()` and `tone_label()`.
- `src/ai_presenter/runtime/controller.py`
  - Builds language/tone selectors from shared voice choice metadata.
- `tests/unit/test_voice.py`
  - Added normalization, rejection, provider-routing, localized narration alias, `中文` alias, new tone rendering, new-tone SAPI rate, and old Chinese concise behavior coverage.
- `tests/unit/test_controller.py`
  - Added expanded label coverage through the public controller label wrapper.
- `tests/unit/test_controller_view_model.py`
  - Added expanded tone label coverage.
- `tests/unit/test_questions.py`
  - Added telemetry coverage proving language aliases log canonical `language=zh`.

## TDD Evidence

Initial red tests:

- `test_voice_settings_normalize_language_aliases`
- `test_voice_settings_normalize_expanded_tones`
- `test_voice_settings_reject_unknown_language_and_tone`
- `test_voice_instruction_describes_expanded_tones`
- `test_render_presenter_text_applies_expanded_english_tones`
- `test_language_aliases_use_existing_provider_routing`
- `test_render_voice_label_uses_controller_labels`
- `test_operator_view_model_labels_expanded_tone`

Red result:

- Voice tests failed because aliases/new tones were not normalized and new tones were missing from descriptions/routing.
- Controller label tests failed because local label maps did not know `zh-CN`, `friendly`, or `coach`.

Later drift guard:

- Added `test_render_presenter_text_keeps_existing_chinese_concise_behavior`.
- It failed when `_render_chinese()` briefly truncated Chinese concise question text.
- Fixed by preserving old Chinese question-answer rendering and keeping concise truncation limited to authored localized narration.

## Verification

- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py tests\unit\test_controller.py tests\unit\test_controller_view_model.py tests\unit\test_controller_session.py tests\unit\test_runtime_factory.py tests\unit\test_questions.py`
  - Result: `91 passed in 13.28s`
- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py::test_voice_settings_normalize_language_aliases`
  - Result: `1 passed in 0.44s`
- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py`
  - Result: `17 passed in 0.82s`
- `.\.venv\Scripts\ruff check --no-cache src\ai_presenter\runtime\voice.py src\ai_presenter\runtime\controller.py src\ai_presenter\runtime\controller_view_model.py src\ai_presenter\runtime\questions.py tests\unit\test_voice.py tests\unit\test_controller.py tests\unit\test_controller_view_model.py tests\unit\test_questions.py`
  - Result: `All checks passed!`
- `.\.venv\Scripts\ruff check --no-cache tests\unit\test_voice.py src\ai_presenter\runtime\voice.py`
  - Result: `All checks passed!`
- `.\.venv\Scripts\mypy --no-incremental src\ai_presenter\runtime\voice.py src\ai_presenter\runtime\controller.py src\ai_presenter\runtime\controller_view_model.py src\ai_presenter\runtime\questions.py tests\unit\test_voice.py tests\unit\test_controller.py tests\unit\test_controller_view_model.py tests\unit\test_questions.py`
  - Result: `Success: no issues found in 8 source files`
- `.\.venv\Scripts\mypy --no-incremental src\ai_presenter\runtime\voice.py tests\unit\test_voice.py`
  - Result: `Success: no issues found in 2 source files`
- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests`
  - Result: `394 passed, 1 warning in 17.43s`
- `git diff --check`
  - Result: no whitespace errors; Git reported expected CRLF conversion warnings for touched files.

## Risks And Follow-Ups

- `zh-TW` and `zh-Hant` normalize to the generic Chinese family; this is compatibility, not Traditional Chinese content support.
- True new languages should be added one at a time with package-authored localization and provider acceptance.
- CLI `--language` / `--tone` flags would be useful later, but should call the same normalization helpers.
- Provider-level prosody remains limited; new tones are currently deterministic text style and instruction metadata.
