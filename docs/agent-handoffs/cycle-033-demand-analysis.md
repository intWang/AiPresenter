# Cycle 033 Demand Analysis: Q&A Matcher Candidate Precompute

Date: 2026-05-16
Role: demand discovery
Scope: read-only demand analysis. No implementation changes were made in this pass.

## User Value

Live Q&A should do less repeated per-question string and token work while preserving the exact answers, route matches, safety flags, localized language behavior, tone behavior, and privacy-safe logging already covered by tests.

The operator-facing value is modest but useful: repeated live questions should feel lighter and steadier, with no visible behavior change.

## Recommended Minimal Slice

Add validation-time private candidate indexes to `MaterialPackage`:

- Q&A candidates: source `QuestionAnswer`, original candidate text, normalized text, and meaningful token set.
- Entrypoint fallback candidates: source `OperationEntrypoint`, precomputed id/title/area/purpose token sets, and combined title/id token set.

Update `runtime/questions.py` to consume those candidates in the existing order. Keep query normalization and query tokenization per call because the live input changes.

Do not add global caches, do not change package YAML, do not alter legacy aliases, and do not pre-render answers because language and tone remain call-specific.

## Behavior To Preserve

- Q&A matching runs before entrypoint matching.
- Q&A substring pass remains before token-overlap fallback.
- Q&A and entrypoint ties keep the first existing package order.
- Package-owned aliases beat legacy aliases.
- Longest alias wins.
- Entrypoint fallback scoring weights stay the same: id 6, title 5, area 2, purpose 1, and title/id coverage bonus 3.
- Generic-only token filtering remains unchanged.
- Localized answers are returned exactly for `voice.language`; fallback answer rendering remains tone-aware.
- `can_operate` stays false for no route, no open steps, or risky id/title/purpose words.
- Logs continue to exclude raw question text, answer text, and exception text.

## Testing Guidance

Use structural and behavioral tests, not wall-clock timing.

Add tests for:

- private candidate construction;
- candidate ordering;
- normalized and token fields;
- no `model_dump()` leakage;
- `with_demo_flow()` rebuilding indexes against copied model objects;
- package alias match order if alias ordering is changed.

Keep the existing question matching regression suite as the semantic guard.

## Suggested Verification

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_material_packages.py tests\unit\test_package_demo.py
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\runtime\questions.py src\ai_presenter\packages\models.py tests\unit\test_questions.py tests\unit\test_material_packages.py tests\unit\test_package_demo.py
.\.venv\Scripts\mypy --no-incremental src\ai_presenter\runtime\questions.py src\ai_presenter\packages\models.py tests\unit\test_questions.py tests\unit\test_material_packages.py
```

## Out Of Scope

- No global or LRU cache.
- No embeddings or semantic search.
- No wall-clock performance assertions.
- No route safety policy changes.
- No package YAML edits.
- No answer rendering changes.
