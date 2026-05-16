# Package Alias Match-Order Index Design

Date: 2026-05-16

## Goal

Precompute package-owned entrypoint alias match order so runtime alias matching can return the first matching alias while preserving existing behavior.

## Context

`runtime/questions.py` currently scans `package.entrypoint_question_aliases` and maintains `best_alias_length` on every question. Cycle 033 already moved stable Q&A and entrypoint fallback candidates into runtime-only package indexes. Package-owned aliases can follow the same pattern.

## Design

Add `MaterialPackage.entrypoint_question_aliases_by_match_order`, backed by a `PrivateAttr`.

The existing `entrypoint_question_aliases` property remains unchanged and preserves source order for reporting/localization code.

The new match-order tuple is built during package validation:

1. Take the existing normalized alias list.
2. Pair each alias with its original source index.
3. Sort by `-len(alias.normalized_alias)` then original index.
4. Store only the alias objects in the private tuple.

Runtime package alias matching iterates this tuple and returns on the first substring hit.

## Behavior Contract

- Q&A matching still precedes entrypoint matching.
- Package-owned aliases still precede legacy aliases.
- Legacy aliases remain dynamic and monkeypatchable.
- Blank aliases remain skipped during package validation.
- Longest package alias wins.
- Equal-length aliases keep source order.
- `can_operate`, answer text, localized answers, and token fallback behavior remain unchanged.

## Serialization

The new match-order tuple is runtime-only. It must not appear in `model_dump(by_alias=True)` or package YAML.

## Tests

Add structural tests for match-order exposure, sorting, stability, no dump leakage, and `with_demo_flow()` rebuild behavior. Add a runtime behavior test for equal-length package alias stability.

## Out Of Scope

- No legacy alias precompute.
- No trie or multi-pattern matcher.
- No wall-clock performance test.
- No package YAML changes.
- No answer or safety behavior changes.
