# Cycle 043 Demand Analysis

## Recommended Slice

Add a read-only `targets_by_id` index to `ValidationTargetCatalog`.

## User Value

Ai Presenter now relies on validation target discovery for RingCentral Video manual acceptance planning and operator handoff. The catalog already validates unique target IDs, but later lookup still scans the target tuple each time. A stable index makes `--target` rendering, tests, and future automation easier to reason about while preserving the existing CLI surface.

## Acceptance Criteria

- `ValidationTargetCatalog` exposes a read-only `targets_by_id` mapping.
- `target_by_id(catalog, id)` returns the same target object as `catalog.targets_by_id[id]`.
- Missing-target errors keep the current helpful "Available targets" detail.
- Existing validation target rendering and CLI behavior remain unchanged.
- The implementation does not change checklist parsing, evidence validation, or blocked-target policy.

## Out Of Scope

- No new acceptance safety rules.
- No changes to RingCentral Video checklist content.
- No changes to acceptance-draft generation.
- No benchmark harness in this cycle.
