# Package Runtime Index Design

Date: 2026-05-16

## Context

AiPresenter now has richer RingCentral Video package metadata, localized question aliases, and timing telemetry. The next performance increment should remove repeated linear lookup work from hot runtime paths without changing package YAML, UI behavior, or safety policy.

Current hot spots:

- `MaterialPackage.entrypoint_by_id()` linearly scans `operation_entrypoints`.
- `runtime.questions._match_package_entrypoint_alias()` scans every entrypoint and alias for every question.
- `PackageActionExecutor._execute_action()` depends on `entrypoint_by_id()` during live operations.

## Design

`MaterialPackage` will build validated runtime indexes during Pydantic model validation:

- A private `dict[str, OperationEntrypoint]` for entrypoint lookup by id.
- A private tuple of package-owned question alias records. Each record stores the entrypoint id, language key, original alias text, and normalized alias text.

The public behavior remains conservative:

- `entrypoint_by_id()` keeps the same signature and error message shape.
- A read-only `entrypoints_by_id` mapping exposes the validated index for tests and diagnostics without allowing accidental mutation.
- `entrypoint_question_aliases` exposes an immutable tuple for question matching.
- Package YAML schema and serialized model data do not change.

`runtime.questions` will consume `package.entrypoint_question_aliases` instead of rebuilding package-owned alias candidates on each question. Legacy aliases stay as a fallback after package-owned aliases, preserving the current precedence rule.

## Non-Goals

- No changes to fuzzy scoring semantics.
- No migration of the remaining legacy alias table in this cycle.
- No structured metrics sink beyond the timing telemetry added in Cycle 007.
- No caching that depends on mutable post-validation package edits.

## Acceptance Criteria

- Entry point lookup is served by a validated index while preserving `KeyError` behavior for unknown ids.
- Package-owned question aliases are pre-normalized once per package model.
- Longest package-owned alias still wins.
- Package-owned aliases still take precedence over legacy aliases.
- `PackageActionExecutor` and question answering keep existing observable behavior.
- Focused tests, ruff, mypy, and full tests pass.

## Risks

- Pydantic private attributes must not leak into model dumps or break validation.
- The model remains mutable; callers should continue treating loaded material packages as immutable runtime inputs.
- The alias index is intentionally package-owned only. Legacy aliases remain runtime constants until a later migration.
