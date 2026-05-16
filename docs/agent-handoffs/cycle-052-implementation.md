# Cycle 052 Implementation

## Changes

- Added `normalize_question_prompt()` in package models.
- Q&A candidates now use trimmed casefolded normalized keys.
- Blank Q&A prompts are skipped from runtime candidates and exact indexes.
- Runtime question normalization now uses the same helper.
- Q&A/alias overlap diagnostics now group by `candidate.normalized_question`.

## TDD Evidence

Initial red run:

- Candidate/index test showed padded normalized keys and a blank candidate.
- Exact lookup test fell through to the entrypoint alias.
- Duplicate-trim diagnostic test reported OK.
- Blank localized prompt still inflated doctor prompt count.

Focused green run:

- New normalization tests: `6 passed`.
- Targeted `ruff check --no-cache` passed.

## Wider Verification So Far

- Related material package, question, diagnostics, and CLI tests: `126 passed`.
- `mypy --no-incremental src tests` passed.
