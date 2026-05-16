# Cycle 114 Implementation: Legacy Alias Match Precomputation

Date: 2026-05-16

## Scope

Cycle 114 adds a small runtime question-matching performance improvement. It does not change package YAML, package schema, localization data, profiles, diagnostics output, knowledge indexes, route policy, or live RingCentral evidence.

## Main Decision

The demand scan recommended a diagnostics indexing refactor. The technical scan recommended a runtime question-matching optimization. The implementation chose an even narrower runtime slice: precompute the legacy fallback alias table into normalized, longest-first match entries.

Why this slice:

- It is on the live question path.
- It preserves existing package-owned alias precedence.
- It avoids broad matcher-context refactoring in this cycle.
- It keeps dynamic monkeypatch behavior in tests by rebuilding when `_ENTRYPOINT_ALIASES` is replaced.

Diagnostics index reuse remains a good later performance cycle.

## Implementation

Updated `src/ai_presenter/runtime/questions.py`:

- Added `_legacy_entrypoint_alias_matches()`.
- The helper normalizes legacy alias strings once per `_ENTRYPOINT_ALIASES` source object.
- The helper sorts by normalized alias length descending, preserving the previous longest-alias behavior.
- `_match_entrypoint_alias()` now iterates the precomputed tuples instead of recomputing `casefold()` and best-length tracking on every question.

Updated `tests/unit/test_questions.py`:

- Added `test_legacy_alias_matches_are_precomputed_longest_first`.
- Kept the existing `test_legacy_alias_table_remains_dynamic_for_runtime_matching` green, confirming test/runtime replacement of `_ENTRYPOINT_ALIASES` still rebuilds the match list.
- Kept package-owned alias precedence covered by the existing focused test.

## TDD Notes

Red check:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_legacy_alias_matches_are_precomputed_longest_first
```

Expected result before implementation: `AttributeError` because `_legacy_entrypoint_alias_matches()` did not exist.

Green check:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_legacy_alias_matches_are_precomputed_longest_first tests\unit\test_questions.py::test_legacy_alias_table_remains_dynamic_for_runtime_matching tests\unit\test_questions.py::test_package_owned_alias_takes_precedence_over_legacy_alias_table
```

Result: `3 passed`.

```powershell
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\runtime\questions.py tests\unit\test_questions.py
```

Result: `All checks passed`.

## Review Focus

- Confirm route precedence is unchanged: Q&A, safety matching, and package-owned aliases still run before legacy aliases.
- Confirm legacy aliases are still matched longest-first.
- Confirm replacing `_ENTRYPOINT_ALIASES` in tests or future runtime hooks rebuilds the precomputed tuple.
- Confirm no raw user questions or answer text are cached.
- Confirm `.coverage` remains unstaged.

## Post-Review Adjustment

The review noted that the first cache invalidation shape only detected replacement of `_ENTRYPOINT_ALIASES`, not in-place mutation of the same dict. The cache now uses a content signature built from the legacy alias table, and a focused red/green test covers in-place alias additions. The cache still stores only static alias metadata, not raw user questions or answers.
