# Validation Target Index Design

## Problem

Validation target discovery validates that target IDs are unique, but later direct lookup is still linear. As RingCentral Video acceptance documentation grows, the runtime shape should make the unique-ID contract explicit and cheap to use.

## Design

`ValidationTargetCatalog` will include a read-only `targets_by_id` mapping keyed by target ID. `discover_validation_targets()` will build this mapping from the final target tuple after duplicate validation, using `MappingProxyType` so callers can inspect it without mutating catalog state.

`target_by_id()` will become a thin lookup helper over the mapping and will keep the existing unknown-target error format, including the available target list.

## Testing

Unit tests will verify that the mapping exposes the same target objects as `target_by_id()`, preserves target insertion order for available-target messages, and rejects mutation. Existing validation target and CLI tests continue to protect rendering behavior.
