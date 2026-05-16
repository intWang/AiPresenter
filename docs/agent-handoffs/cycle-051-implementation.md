# Cycle 051 Implementation

## Changes

- Added a `qa alias overlap` package diagnostic.
- The diagnostic compares `qa_question_candidates` with `entrypoint_question_aliases`.
- Unsafe overlaps warn when a Q&A prompt shadows a package-owned alias without referencing that alias entrypoint.
- Same-entrypoint overlaps remain OK.
- CLI doctor now exposes the new diagnostic in normal package checks.

## TDD Evidence

Initial red run:

- New diagnostics tests could not find any `qa alias overlap` check.
- New CLI test reported `0 warnings` because the overlap was not diagnosed.

Green focused run:

- `29 passed` for diagnostics and doctor-focused tests.
- Targeted `ruff check --no-cache` passed.
- `mypy --no-incremental src tests` passed.
