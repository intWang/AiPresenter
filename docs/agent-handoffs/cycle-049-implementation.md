# Cycle 049 Implementation

## Changes

- Added a `qa questions` material-package diagnostic.
- The diagnostic groups precomputed Q&A question candidates by normalized question text.
- It reports OK when all normalized prompts are unique across Q&A items.
- It reports WARN when one normalized prompt appears in multiple Q&A items.
- CLI doctor now prints the new check alongside existing package readiness checks.

## TDD Evidence

Initial red run:

- RingCentral OK check could not find `qa questions`.
- Duplicate English Q&A test could not find `qa questions`.
- Duplicate localized Q&A test could not find `qa questions`.
- Same-item duplicate test could not find `qa questions`.
- CLI doctor did not print `[OK] qa questions` or `[WARN] qa questions`.

After implementation:

- Focused run: `6 passed`.

## Root Cause Adjustment

The first RingCentral count expectation was `32`, but the actual package has 36 Q&A prompts: 9 primary questions plus 27 localized question prompts. The assertion now reflects the candidate count built by the runtime model.

