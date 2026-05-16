# Evidence Entrypoint Validation Design

Date: 2026-05-16

## Context

`validation-targets` reads the RingCentral validation checklist and evidence index to produce the next offline acceptance targets. Checklist entrypoint IDs are validated against the material package, but evidence-index rows can drift silently if a row is missing, duplicated, typoed, or assigned an unsupported evidence level.

That makes the evidence index less trustworthy as a planning artifact.

## Design

Add a pure validation helper in `ai_presenter.acceptance.validation_targets`:

```python
validate_entrypoint_evidence_index(package, evidence_text)
```

The helper parses the existing `Entry Point Evidence Table`, validates it against the supplied material package, and returns a small immutable report with entrypoint counts and evidence mappings for callers that need them.

`discover_validation_targets()` should use the helper whenever evidence text is supplied, so CLI and tests get the same guard. If no evidence text is supplied, existing unknown-evidence fallback behavior remains available.

## Rules

- Each package entrypoint must appear exactly once in the evidence table.
- Evidence rows may reference only package entrypoint IDs, not flow IDs or arbitrary strings.
- Evidence levels must be one of `Accepted`, `Observed`, `Repo-tested`, `Backlog`, or `Blocked`.
- Missing evidence text remains allowed for generic callers and produces existing `unknown` fallback values.
- The guard must not change package routing, evidence levels, or acceptance status.

## Acceptance Criteria

- Real RingCentral evidence index reports 27 package entrypoints and 27 evidence rows.
- Real validation catalog with blocked rows has no `unknown` evidence levels.
- Synthetic missing, unknown, duplicate, and invalid-level evidence rows fail clearly.
- Existing validation-target rendering and acceptance-draft behavior stay unchanged for valid docs.

## Non-Goals

- No live RingCentral automation.
- No new CLI command.
- No evidence promotion.
- No package schema change.

