# Cycle 035 Technical Scan: Package Alias Match-Order Index

Date: 2026-05-16
Role: technical discovery
Scope: read-only technical scan. No implementation changes were made in this pass.

## Recommendation

Add a package-local runtime index for package-owned entrypoint aliases sorted by match order.

## Files

- `src/ai_presenter/packages/models.py`
- `src/ai_presenter/runtime/questions.py`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_questions.py`

## Data Structure

In `MaterialPackage`:

- Add `_entrypoint_question_aliases_by_match_order: tuple[EntrypointQuestionAlias, ...]` as a `PrivateAttr`.
- Add read-only property `entrypoint_question_aliases_by_match_order`.
- Keep existing `entrypoint_question_aliases` in original source order.

## Build Rule

- Construct existing alias list as today.
- Build match-order tuple with `enumerate()`.
- Sort by `(-len(alias.normalized_alias), original_index)` so longest aliases match first and equal-length aliases keep source order.

## Runtime

- Change `_match_package_entrypoint_alias()` to iterate `package.entrypoint_question_aliases_by_match_order` and return on first substring match.
- Keep package-owned aliases before legacy `_ENTRYPOINT_ALIASES`.
- Keep legacy alias table dynamic for monkeypatch tests.

## Tests

- Add `test_material_package_exposes_entrypoint_question_aliases_by_match_order`.
- Add equal-length alias order coverage in `test_questions.py`.
- Extend model dump leakage test for `entrypointQuestionAliasesByMatchOrder` and `_entrypoint_question_aliases_by_match_order`.
- Extend `with_demo_flow()` runtime-index rebuild coverage.

## Risks

- Do not precompute legacy aliases.
- Do not expose the new index as a Pydantic field.
- Do not use `model_copy()` in `with_demo_flow()`.
- Do not mutate existing alias source-order index.
- Do not alter package alias before legacy alias precedence.
