# Cycle 049 Technical Scan

## Current State

`doctor` already has a `question aliases` readiness check that warns when a normalized package-owned alias maps to multiple entrypoints. Q&A questions now have an exact normalized lookup index, but there is no matching diagnostic to warn when the same normalized Q&A prompt appears across multiple Q&A items.

## Proposed Implementation

- Add `_diagnose_qa_questions()` in `src/ai_presenter/runtime/diagnostics.py`.
- Append the check near `_diagnose_question_aliases()` in material-package diagnostics.
- Group `material_package.qa_question_candidates` by `normalized_question`.
- Warn only when a normalized question maps to more than one distinct `QuestionAnswer` item.
- Format affected items as stable `#<index> <primary question>` labels.

## TDD Plan

1. Add failing OK test for the RingCentral package.
2. Add failing WARN tests for duplicate English and localized Q&A prompts.
3. Add a test proving duplicate prompts within the same Q&A item stay OK.
4. Add CLI doctor output coverage.
5. Implement the diagnostic.

## Risks

- Avoid noisy warnings for a repeated prompt inside the same Q&A item.
- Keep the check WARN-only so it does not break existing packages.
- Keep formatting stable enough for operators but narrow enough for tests.

