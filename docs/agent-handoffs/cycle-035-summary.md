# Cycle 035 Summary: Package Alias Match-Order Index

Date: 2026-05-16
Cycle: 035
Commit target: `perf: precompute package alias match order`

## Outcome

Cycle 035 added a runtime-only match-order index for package-owned entrypoint question aliases.

The existing `entrypoint_question_aliases` tuple remains source ordered for reporting and localization workflows. A new `entrypoint_question_aliases_by_match_order` tuple is built during `MaterialPackage` validation and sorted by normalized alias length descending with source-order tie stability.

`runtime/questions.py` now uses the precomputed match-order tuple for package-owned alias matching, so it can return the first substring hit without recomputing longest-match state on every question.

## Files Changed

- `src/ai_presenter/packages/models.py`
- `src/ai_presenter/runtime/questions.py`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_questions.py`
- `docs/agent-handoffs/cycle-035-demand-analysis.md`
- `docs/agent-handoffs/cycle-035-technical-scan.md`
- `docs/agent-handoffs/cycle-035-review.md`
- `docs/agent-handoffs/cycle-035-summary.md`
- `docs/superpowers/specs/2026-05-16-package-alias-match-order-index-design.md`
- `docs/superpowers/plans/2026-05-16-package-alias-match-order-index.md`

## Behavior Preserved

- Q&A matching still runs before entrypoint matching.
- Package-owned aliases still take precedence over legacy aliases.
- Legacy `_ENTRYPOINT_ALIASES` remains dynamic and monkeypatchable.
- Alias matching remains casefolded substring matching.
- Blank aliases remain skipped during package validation.
- Longest package-owned alias wins.
- Equal-length package aliases keep package declaration order.
- Runtime-only indexes remain absent from `model_dump(by_alias=True)`.
- `with_demo_flow()` rebuilds runtime indexes through full package validation.

## Tests Added Or Extended

- Added structural coverage for `entrypoint_question_aliases_by_match_order`.
- Extended `with_demo_flow()` runtime index rebuild coverage.
- Extended serialization leakage coverage for the new private index.
- Added equal-length package alias source-order behavior coverage.
- Added positive coverage that a monkeypatched legacy alias table is still honored at runtime.

## Verification

Red phase:

- Targeted tests initially failed with missing `entrypoint_question_aliases_by_match_order`, confirming the structural test caught the missing feature.

Green and review phase:

- Targeted Cycle 035 tests passed.
- Focused package/question tests passed: `84 passed`.
- Reviewer found no critical or important issues.
- Review follow-up test for dynamic legacy alias monkeypatching was added and passed.

Final verification after the review follow-up:

- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests`
  - `546 passed, 1 warning`
- `.\.venv\Scripts\ruff check --no-cache .`
  - `All checks passed!`
- `.\.venv\Scripts\mypy --no-incremental src tests`
  - `Success: no issues found in 81 source files`
- `git diff --check`
  - Only LF-to-CRLF working-copy warnings were reported; no whitespace errors.

## Next Handoff Ideas

- Consider a future package diagnostics command that reports alias conflicts and same-length tie order before runtime.
- Consider applying the same explicit match-order documentation pattern to legacy aliases if that table remains long term.
