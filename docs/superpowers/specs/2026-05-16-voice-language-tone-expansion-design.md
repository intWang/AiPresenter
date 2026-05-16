# Voice Language And Tone Expansion Design

Date: 2026-05-16

## Context

AiPresenter currently supports two presenter language values (`en`, `zh`) and three tones (`professional`, `conversational`, `concise`). This is enough for the first RingCentral Video flow, but it is brittle: regional language codes such as `zh-CN` fail type checks, and the operator UI cannot choose softer or more coaching-oriented tones.

## Design

Add a small normalized voice settings layer:

- `PresenterVoiceSettings` accepts common language aliases such as `en-US`, `en-GB`, `English`, `zh-CN`, `zh-Hans`, `zh-TW`, and `Chinese`.
- The settings object stores canonical runtime languages only: `en` or `zh`.
- Unknown language values raise `ValueError` early.
- Add three new canonical tones:
  - `friendly`: warmer and reassuring.
  - `coach`: step-by-step guidance.
  - `formal`: polished and restrained.
- Accept simple tone aliases such as `warm`, `mentor`, and `structured`, but store canonical tone values.
- Unknown tone values raise `ValueError` early.

The controller should consume shared voice choice metadata instead of hard-coded labels. The UI remains intentionally simple: language selection stays English/Chinese because providers and package localization currently support those output families, while tone selection expands to Professional, Conversational, Concise, Friendly, Coach, and Formal.

## Behavior

- Existing `PresenterVoiceSettings()` remains English / Professional.
- Existing `en`, `zh`, `professional`, `conversational`, and `concise` behavior remains compatible.
- `PresenterVoiceSettings(language="zh-CN", tone="friendly")` stores `language == "zh"` and `tone == "friendly"`.
- `render_voice_instruction()` describes new tones.
- `render_presenter_text()` applies simple prefixes for friendly/coach/formal English responses.
- Chinese text routing remains provider-compatible because regional aliases normalize to `zh`.
- Localized package narration still uses authored localized text; only concise truncation changes localized narration, preserving existing scripted copy.

## Non-Goals

- No new TTS providers or voice model downloads.
- No Spanish/Japanese/French output until profile/provider/package localization exists.
- No package YAML migration in this cycle.
- No CLI voice flags in this cycle; the immediate operator surface is the local controller and Python runtime API.

## Acceptance Criteria

- `PresenterVoiceSettings` normalizes common English/Chinese language aliases.
- `PresenterVoiceSettings` normalizes common tone aliases and rejects unknown tones.
- Controller labels and option menus use shared voice option metadata.
- Controller/operator view model labels support the expanded tones.
- Existing voice validation and SAPI provider routing still work with regional aliases.
- Focused voice/controller/runtime tests, ruff, mypy, and full tests pass.

## Risks

- Runtime language support is not the same as natural-language translation support. Regional aliases should map only to current English/Chinese output families.
- Adding new tones can accidentally change scripted narration. Keep localized narration untouched except for existing concise behavior.
- Controller label maps can drift if they remain duplicated. Centralize choice metadata in `runtime.voice`.
