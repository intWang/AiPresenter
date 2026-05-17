# Cycle 193 Technical Development: Structured Scan Summary

Date: 2026-05-17

## Files Changed

- `src/ai_presenter/runtime/controller.py`
  - Stores the successful running-app scan status in `scanned_scan_summary`.
  - Passes the summary into `ControllerOperatorSnapshot`.
- `src/ai_presenter/runtime/controller_view_model.py`
  - Adds optional `scan_summary`.
  - Displays it in the scan label only for scanned running-app selections.
- `tests/unit/test_controller_view_model.py`
  - Guards the structured scanned summary.
  - Guards that stale summaries are ignored for unscanned selections.

## Behavior

When the operator scans a running desktop app, the summary row can now show:

```text
State: Ready after question | scan: Scanned temp.demo.10: 2 controls, 3 entrypoints, 50 ms
```

The target row continues to use the generated package id, so private window titles and control text
stay out of the rendered operator summary.

## Compatibility

Existing snapshots do not need to pass `scan_summary`; it defaults to an empty string and falls back
to `Scanned <package id>`.
