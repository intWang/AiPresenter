# Cycle 035 Demand Analysis: Package Alias Match-Order Index

Date: 2026-05-16
Role: demand discovery
Scope: read-only demand analysis. No implementation changes were made in this pass.

## Goal

Add a small runtime-only match-order index for `MaterialPackage` package-owned entrypoint question aliases.

The index should pre-sort aliases by normalized alias length descending, preserving declaration order for equal lengths, so runtime matching can return the first substring hit without maintaining best-length state per query.

## Value

The performance benefit is modest, but the determinism benefit is useful: package-owned alias behavior becomes explicit and structural.

The key contract is:

- longest package alias wins;
- same-length aliases are stable by package source order;
- package aliases still beat legacy aliases.

## Minimum Scope

- Keep existing `entrypoint_question_aliases` in source order.
- Add a separate `PrivateAttr` and read-only tuple property for match order.
- Build it during `MaterialPackage` validation from existing normalized aliases.
- Use it only in `_match_package_entrypoint_alias()`.
- Do not change legacy `_ENTRYPOINT_ALIASES`, YAML, Q&A matching, token fallback, answer text, `can_operate`, or add global caches/trie/benchmarks.

## Invariants

- Q&A match before entrypoint match.
- Package-owned aliases before legacy aliases.
- Alias match remains casefolded substring match.
- Blank aliases remain skipped.
- Longest package alias wins; equal length keeps declaration order.
- Runtime indexes do not leak into `model_dump()`.
- `with_demo_flow()` rebuilds runtime indexes.

## Recommended Tests

- `MaterialPackage` exposes sorted/stable alias match-order tuple and it is absent from `model_dump()`.
- Runtime package alias tie test proves equal-length stability.
- Existing longest alias, package-over-legacy, legacy monkeypatch, and package alias coverage tests continue passing.

## Out Of Scope

- No legacy alias precompute.
- No trie/Aho-Corasick.
- No wall-clock benchmark.
- No package YAML changes.
- No answer text or safety behavior changes.
