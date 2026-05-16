# Cycle 039 Demand Analysis: Doctor Alias Readiness

Date: 2026-05-16
Role: demand discovery
Scope: read-only demand analysis. No implementation changes were made by the demand agent.

## Recommended Slice

Add a `doctor` readiness check for package-owned `questionAliases` conflicts.

Cycle 035 made package alias matching deterministic by precomputing longest-first match order. That is useful at runtime, but it can hide authoring mistakes: if two entrypoints own the same normalized alias, the first package declaration silently wins. The operator will experience that as a surprising route choice during live Q&A.

## User Value

This improves pre-demo confidence:

- Operators can see that a healthy package has unambiguous package-owned aliases.
- Package authors get a fast signal when future edits introduce duplicate aliases.
- The warning can name the exact alias and competing entrypoints before a live demo.
- The package remains loadable because deterministic runtime behavior already exists.

## Product Contract

- Run the check only when a material package is loaded.
- Emit `[OK] question aliases` when no cross-entrypoint duplicate normalized aliases exist.
- Emit `[WARN] question aliases` when a normalized alias maps to more than one entrypoint.
- Keep `doctor` exit code `0` for alias warnings unless another diagnostic fails.
- Ignore blank aliases, matching existing package model behavior.
- Do not treat duplicate aliases on the same entrypoint as an operator-routing conflict.
- Do not change runtime question matching.

## Acceptance Criteria

- Healthy RingCentral package reports `49 package-owned aliases` and no cross-entrypoint duplicates.
- A synthetic package with `Chat` / ` chat ` on two different entrypoints warns.
- The warning includes normalized alias, language list, all conflicting entrypoint IDs, and the current first-match entrypoint.
- CLI output exposes the warning and keeps `doctor` non-fatal.
- Runtime package-owned alias match order is unchanged.

## Out Of Scope

- No package YAML cleanup.
- No package schema validation failure.
- No changes to legacy aliases.
- No semantic or fuzzy matching.
- No live RingCentral automation or acceptance promotion.

