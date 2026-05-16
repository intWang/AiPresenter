# Cycle 033 Review: Q&A Matcher Candidate Precompute

Date: 2026-05-16
Role: code review
Scope: review of Cycle 033 matcher candidate changes

## Result

No blockers or must-fix issues were found.

## Review Answers

- Matching priority was preserved: Q&A still runs before entrypoint matching, and entrypoint matching still checks package aliases before legacy aliases before token fallback.
- Q&A candidate order is equivalent to the previous `_qa_questions()` nested loop: base question first, then localized question values in current order for each Q&A item.
- `PrivateAttr` usage is appropriate for runtime-only candidate indexes.
- `with_demo_flow()` remains safe because it uses `model_dump(by_alias=True)` plus `MaterialPackage.model_validate(data)`, which rebuilds private attrs instead of copying stale ones.
- Matcher candidates do not leak into `model_dump()` or YAML; new tests cover public alias names and private attr names.
- `can_operate` and risky safety logic remain independent from matcher candidates.

## Residual Risk

If callers mutate a validated `MaterialPackage` in place after validation, precomputed candidates can become stale. This is the same risk category as existing private runtime indexes. Current code treats material packages as validated runtime objects, and `with_demo_flow()` covers the known package-copy path.
