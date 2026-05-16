# Cycle 009 Review: Voice Language And Tone Expansion

Date: 2026-05-16
Role: review sidecar
Write scope: this file only

## Findings

No high-severity or blocking issues found in the voice language/tone expansion.

Low-risk follow-ups:

- `zh-TW` and `zh-Hant` normalize to the generic canonical `zh` family in `src/ai_presenter/runtime/voice.py`. This is acceptable as compatibility because the controller only labels the choice as `Chinese`, but it should not be described externally as Traditional Chinese support until package text, script expectations, and TTS acceptance exist.
- Provider-rate behavior for the new tones is only partially asserted. Existing tests lock Chinese `professional`, `conversational`, and `concise` SAPI rates, while `friendly`, `coach`, and `formal` rely on the implementation and broader runtime coverage. Add explicit assertions later if SAPI pacing for expanded tones becomes a product contract.

## Review Scope

Reviewed only the requested voice language/tone expansion surface:

- `src/ai_presenter/runtime/voice.py`
- `src/ai_presenter/runtime/controller_view_model.py`
- `src/ai_presenter/runtime/controller.py`
- `src/ai_presenter/runtime/questions.py` telemetry/localized-answer call sites
- `src/ai_presenter/runtime/factory.py` provider registry/rate call sites
- `tests/unit/test_voice.py`
- `tests/unit/test_controller.py`
- `tests/unit/test_controller_view_model.py`
- `tests/unit/test_questions.py`
- Related controller-session/runtime-factory tests for provider routing compatibility
- Cycle 009 demand analysis, technical scan, implementation handoff, design spec, and plan

The working tree already contains unrelated dirty and untracked files. I did not revert, overwrite, or edit production code.

## Behavior Review

Existing tone behavior looks preserved. The `professional` path still returns the original text for English, `conversational` still adds the existing English/Chinese conversational prefixes, and English `concise` still truncates to the first sentence. The added drift guard for Chinese concise question text keeps the prior non-truncating `_render_chinese()` behavior, while localized narration still applies concise first-sentence behavior only to authored localized narration.

Expanded tones are additive. `friendly`, `coach`, and `formal` have descriptions, labels, deterministic English prefixes, and Chinese prefixes for non-localized rendered text. Authored localized narration remains untouched for the new tones, which matches the plan's behavior-preservation boundary.

## Provider Routing

Provider routing remains canonical and compatible. `PresenterVoiceSettings` normalizes aliases at construction, so downstream provider code still compares only `en` or `zh`. The focused routing test confirms `PresenterVoiceSettings(language="zh-CN")` resolves a Piper profile to `windows-sapi-zh`; full tests also cover the existing controller-session and runtime-factory provider paths.

I did not find a new path where a regional alias can skip `localizedText["zh"]`, `localizedAnswers["zh"]`, or the Chinese SAPI fallback after normalization.

## Alias And Type Safety

Language normalization covers the intended English/Chinese families and rejects unsupported languages such as `es`. The additional assertion added after review start, `PresenterVoiceSettings(language="中文").language == "zh"`, is present and passed in the focused test run.

The custom frozen dataclass initializer intentionally accepts `str` so aliases can enter at the boundary. The stored fields remain typed as canonical `PresenterLanguage` and `PresenterTone`, and unknown strings raise `ValueError` early. The tradeoff is that mypy will not catch every misspelled constructor string anymore, but runtime validation now covers user/UI/API inputs that static typing never protected.

## Controller Consistency

Controller choices and labels are centralized enough for this cycle:

- `PRESENTER_LANGUAGE_CHOICES` and `PRESENTER_TONE_CHOICES` drive Tk `OptionMenu` values.
- `current_voice()` converts selected display labels through those shared choices.
- `controller_view_model.render_voice_label()` uses shared `language_label()` and `tone_label()` helpers.
- Controller-level `render_voice_label()` delegates to the view-model helper, so labels are not duplicated.

I did not find a mismatch where the controller can display a tone that `PresenterVoiceSettings` cannot normalize, or normalize a tone that the label helper cannot render.

## Test Adequacy

Coverage is strong for the requested behavior:

- Defaults and existing tone behavior.
- Language aliases: `zh-CN`, `zh-Hans`, `Chinese`, `中文`, `English`, `en-US`.
- Tone aliases: `warm`, `mentor`, `structured`.
- Unknown language/tone rejection.
- New tone instruction text and English render prefixes.
- Provider routing for a regional Chinese alias.
- Localized narration lookup through canonical `zh`.
- Controller and operator view-model labels for expanded tones.
- Telemetry logging canonical `language=zh` for `zh-CN`.
- Full test suite regression pass.

Remaining test gaps are non-blocking: direct assertions for `zh-TW`/`zh-Hant` compatibility aliases and explicit SAPI rate expectations for `friendly`/`coach`/`formal`.

## Verification Commands

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py tests\unit\test_controller.py tests\unit\test_controller_view_model.py tests\unit\test_controller_session.py tests\unit\test_runtime_factory.py tests\unit\test_questions.py
```

Result: `91 passed in 10.57s`

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py::test_voice_settings_normalize_language_aliases
```

Result: `1 passed in 0.46s`

```powershell
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\runtime\voice.py src\ai_presenter\runtime\controller.py src\ai_presenter\runtime\controller_view_model.py src\ai_presenter\runtime\questions.py tests\unit\test_voice.py tests\unit\test_controller.py tests\unit\test_controller_view_model.py tests\unit\test_questions.py
```

Result: `All checks passed!`

```powershell
.\.venv\Scripts\mypy --no-incremental src\ai_presenter\runtime\voice.py src\ai_presenter\runtime\controller.py src\ai_presenter\runtime\controller_view_model.py src\ai_presenter\runtime\questions.py tests\unit\test_voice.py tests\unit\test_controller.py tests\unit\test_controller_view_model.py tests\unit\test_questions.py
```

Result: `Success: no issues found in 8 source files`

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
```

Result: `394 passed, 1 warning in 21.19s`

```powershell
git diff --check
```

Result: exit code 0; Git emitted expected CRLF conversion warnings for existing dirty working-copy files.

## Recommendation

Approve the Cycle 009 voice language/tone expansion as implemented. The code keeps runtime language/provider behavior canonical, expands tone behavior additively, centralizes controller labels/options, and has adequate regression coverage for the current scope. The only follow-ups I would carry are documentation caution around Traditional Chinese-looking aliases and optional tests for new-tone SAPI rate decisions.
