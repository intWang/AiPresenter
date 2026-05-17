# Cycle 194 Technical Development: Scanned Metadata Holder

Date: 2026-05-17

## Files Changed

- `src/ai_presenter/runtime/controller.py`
  - Adds `_ScannedRunningAppMetadata`.
  - Adds `_clear_scanned_running_app_metadata_if_invalid()`.
  - Replaces scattered scanned running-app locals with the metadata holder.
  - Clears the holder after selection/window refresh invalidates the scan.
- `tests/unit/test_controller.py`
  - Adds tests for applying and clearing scan-result metadata.
  - Adds tests for invalidation clearing and same-window refresh preservation.

## Behavior

Successful scan still populates the generated package id, flow id, scan summary, temporary package,
and window handle. When the selected scanned app changes or disappears during refresh, the metadata
holder clears those values before the operator view is refreshed.

## Compatibility

The material-package path is unchanged. Running-app start behavior is still guarded by
`scan_state.has_scanned_selection`, but now the dependent package/flow/handle state also matches
that validity signal.
