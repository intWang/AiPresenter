# Cycle 194 Technical Scan: Invalid Scan Metadata Cleanup

Date: 2026-05-17

## Finding

`_RunningAppScanState` already clears its internal scanned-window key when the selected running app
changes or disappears. Before this cycle, `run_controller()` kept related local variables alive:

- scanned package id
- scanned flow id
- scan summary
- temporary material package
- window handle

The UI and start path were gated by `scan_state.has_scanned_selection`, so behavior was protected,
but stale metadata remained available to future code.

## Implementation Strategy

- Introduce `_ScannedRunningAppMetadata` as the single holder for scanned running-app metadata.
- Add `_clear_scanned_running_app_metadata_if_invalid()` to clear that holder only when a
  previously scanned selection becomes unscanned.
- Use the holder in `refresh_operator_view()`, `sync_target_choice()`, `scan_selected_app()`, and
  `start()`.
- Call the invalidation helper from `choose_running_app()` and `refresh_running_windows()` after
  `_RunningAppScanState` updates.

## Guardrails

- Do not clear metadata on refresh if the same scanned window is still present.
- Do not mutate the active `PresenterController` target as part of this cleanup.
- Keep `scan_state` as the source of truth for scan validity.
- Keep scan summary content unchanged and metadata-only.
