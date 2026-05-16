# Cycle 043 Technical Scan

## Context

`discover_validation_targets()` builds a list of `ValidationTarget` objects and calls `_validate_unique_target_ids()` before returning a frozen `ValidationTargetCatalog`. The natural ID index is not retained, so `target_by_id()` currently loops over `catalog.targets`.

## Proposed Implementation

- Add `targets_by_id: Mapping[str, ValidationTarget]` to `ValidationTargetCatalog`.
- Build it in `discover_validation_targets()` after duplicate ID validation.
- Wrap the backing dict with `MappingProxyType` to make it read-only.
- Change `target_by_id()` to use `catalog.targets_by_id` while preserving the existing error text.

## TDD Plan

1. Add a focused unit test that expects `catalog.targets_by_id` to exist, preserve target order, return the same objects as `target_by_id()`, and reject mutation.
2. Run the focused test and confirm it fails because `targets_by_id` is missing.
3. Implement the catalog index.
4. Re-run focused validation target tests, then full verification.

## Risk Notes

The risk is low because duplicate IDs are already rejected before catalog construction. The main compatibility concern is direct construction of `ValidationTargetCatalog`; current tests and production paths construct it through `discover_validation_targets()`.
