# Cycle 052 Demand Analysis

## Recommended Slice

Normalize Q&A prompt keys before adding more RingCentral Video Q&A content.

## User Value

AiPresenter now has growing Q&A coverage and doctor guardrails. Operators need package authoring to be predictable: whitespace around a Q&A prompt should not change exact matching, duplicate diagnostics, or alias-overlap diagnostics. Blank localized prompts should not become runtime match candidates.

## Acceptance Criteria

- Q&A prompt candidates use `strip().casefold()` for normalized keys.
- Blank base or localized Q&A prompts are skipped from runtime candidates and exact indexes.
- Exact Q&A lookup works for an authored prompt with leading or trailing spaces.
- Blank user input does not match blank authored Q&A content.
- Duplicate Q&A diagnostics warn for trim/casefold duplicates across items.
- RingCentral Video prompt counts, localization completeness, and doctor baseline remain unchanged.

## Out Of Scope

- No new RingCentral Q&A content.
- No matcher ordering change.
- No fuzzy or substring diagnostic expansion.
- No mutation of authored package text.

## Suggested Files And Tests

- `src/ai_presenter/packages/models.py`
- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/runtime/diagnostics.py`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_questions.py`
- `tests/unit/test_diagnostics.py`
