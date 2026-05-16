# Cycle 039 Review: Doctor Alias Readiness

Date: 2026-05-16
Role: test/review
Scope: review of the Cycle 039 doctor question-alias readiness diagnostic.

## Findings

Reviewer found no code issues.

Reviewed points:

- Diagnostic groups aliases by `normalized_alias`, matching runtime behavior that ignores alias language.
- Warnings trigger only for cross-entrypoint conflicts.
- Same-entrypoint duplicate aliases stay non-warning.
- Runtime matching in `questions.py` is unchanged.
- `doctor` remains non-fatal because alias conflicts are `WARN`, not `FAIL`.

## Residual Risk

The new `[OK] question aliases` line intentionally changes `doctor --package` output and OK counts. External exact-output consumers would need to expect the new readiness line.

## Follow-Up Applied

Added a cross-language duplicate test to lock in the runtime-facing grouping rule:

- `test_diagnostics_warns_for_cross_language_question_alias_duplicates`

This prevents future changes from accidentally grouping by `(language, normalized_alias)` when runtime routing is alias-only.

