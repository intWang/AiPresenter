# Cycle 182 Technical Scan: Spanish Accent And Participant Privacy

Date: 2026-05-17

## Files Inspected

- `src/ai_presenter/packages/models.py`
- `src/ai_presenter/runtime/questions.py`
- `packages/ringcentral-video.yaml`
- `tests/unit/test_questions.py`
- `tests/unit/test_material_packages.py`

## Current Behavior

`normalize_question_prompt()` strips Latin accents with NFD decomposition and preserves punctuation. This means:

- `Muéstrame` normalizes to `muestrame`.
- `¿Dónde está?` normalizes to `¿donde esta?`.
- Inverted punctuation remains part of the normalized string.

Existing Cycle 181 Spanish terms already covered many accented singular variants after normalization:

- `Muéstrame los participantes` -> participant privacy Q&A.
- `Muéstrame el panel de participantes` -> Participants panel.
- `¿Quién está en la reunión?` -> participant privacy Q&A.
- `¿Quién está en el panel de participantes?` -> participant privacy Q&A.

Missing behavior found by main-session probes:

- `¿Quiénes están en la reunión?` was non-operable but matched the wrong privacy family.
- `¿Quiénes están en el panel de participantes?` was operable through the Participants panel alias.
- `¿Quiénes están en la lista de participantes?` was operable through the Participants panel alias.

## Implementation Guidance

- Do not change global normalization or strip punctuation. That could alter exact Q&A keys and diagnostics.
- Do not add YAML aliases for accented variants.
- Harden runtime participant privacy terms for the missing plural who-is intent.
- Add a small normalization contract test so future changes do not accidentally remove accent folding or punctuation preservation.

## Tests Added

- Spanish plural participant identity prompts in `tests/unit/test_questions.py`.
- Accented Spanish panel navigation prompts in `tests/unit/test_questions.py`.
- Accent/punctuation normalization contract in `tests/unit/test_material_packages.py`.

## Risks

- Global punctuation removal could produce broad matching changes outside participant privacy.
- YAML alias expansion could increase substring-risk diagnostics and make disclosure prompts operable.
- Spanish controller/session coverage still requires an OpenAI speech profile if execution behavior becomes in scope.
