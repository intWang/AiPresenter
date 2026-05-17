# Cycle 193 Technical Scan: Scan Summary View-Model

Date: 2026-05-17

## Current Path

The controller already receives a privacy-safe `RunningAppScanResult.status_message` from
`_scan_running_app_for_controller()`. Before this slice, that message was assigned to the mutable
Tk status string, while `ControllerOperatorSnapshot` only carried the scanned package id and flow id.

## Implementation Strategy

- Add an optional `scan_summary` field to `ControllerOperatorSnapshot`.
- Set it from `RunningAppScanResult.status_message` after a successful running-app scan.
- Prefer `scan_summary` in `_scan_label()` only when `has_scanned_running_app` is true.
- Keep fallback labels for old snapshots and unscanned selections.

## Privacy Boundary

The scan summary must remain metadata-only:

- package id
- control count
- entrypoint count
- elapsed milliseconds

It must not contain window title, control labels, exception text, meeting data, user questions, or
screenshots.

## Risk Notes

- Snapshot dataclass ordering requires the new optional field to stay after existing required
  fields.
- View-model gating should ignore stale summaries when a selected app needs a fresh scan.
- Controller invalidation behavior should not be expanded in this slice unless tests expose a
  regression.
