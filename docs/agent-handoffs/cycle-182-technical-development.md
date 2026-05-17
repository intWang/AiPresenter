# Cycle 182 Technical Development: Spanish Plural Participant Privacy

Date: 2026-05-17

## Files Changed

- `src/ai_presenter/runtime/questions.py`
  - Added Spanish plural who-is terms for participant identity routing.
  - Covered `quienes estan en la reunion`, `quienes estan en el panel de participantes`, and `quienes estan en la lista de participantes`.
  - Added `quienes` / `quiénes` as identity-intent terms.
- `tests/unit/test_questions.py`
  - Added accented Spanish identity prompts with `Quiénes`, `están`, `reunión`, panel, and list wording.
  - Added accented Spanish safe navigation prompts.
- `tests/unit/test_material_packages.py`
  - Added a normalization contract for Latin accent folding while preserving inverted punctuation.
- `docs/knowledge/ringcentral-video/privacy-matrix.md`
  - Added durable Spanish participant privacy examples.
- `docs/agent-handoffs/cycle-182-*.md`
  - Added cycle handoff docs for demand, technical scan, risk scan, development, test review, and experience.

No package YAML changes were made.

## Behavior Added

The following Spanish prompts now return the participant privacy Q&A instead of post-meeting guidance, generic no-match, or an operable Participants panel:

- `¿Quiénes están en la reunión?`
- `¿Quiénes están en el panel de participantes?`
- `¿Quiénes están en la lista de participantes?`
- `Explícame quién está en la lista de participantes`

Safe navigation remains operable:

- `Muestrame el panel de participantes`
- `Muéstrame el panel de participantes`
- `Donde esta la lista de participantes?`
- `¿Dónde está la lista de participantes?`

## Implementation Notes

`normalize_question_prompt()` folds Latin accents before runtime matching, so the runtime constants include both readable accented variants and normalized unaccented variants where it improves clarity.

The change stays inside participant privacy matching. It does not add aliases, so package alias counts and localization diagnostics should not drift.
