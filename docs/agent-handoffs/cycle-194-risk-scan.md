# Cycle 194 Risk Scan: Metadata Clearing

Date: 2026-05-17

## Risks Checked

- Accidentally clearing a still-valid scan when the same window is present after refresh.
- Leaving a stale package, flow, scan summary, package object, or handle after invalidation.
- Changing scan telemetry or operator copy outside the intended cleanup.
- Mutating the active controller target while a demo may still be running.

## Mitigations

- The helper clears only when `previously_scanned` is true and
  `scan_state.has_scanned_selection` becomes false.
- Focused tests cover clear-after-selection-change, clear-after-no-windows refresh, and keep-after
  matching refresh.
- `scan_selected_app()` still uses the same `RunningAppScanResult` and status message.
- The cleanup does not call `controller.set_target()` or `controller.end()` during invalidation.

## Residual Risk

There is still no full Tk callback harness test for `run_controller()`. The coverage is a focused
unit test around the new state holder/helper plus static review of the closure call sites.
