# Cycle 193 Risk Scan: Operator Summary Privacy

Date: 2026-05-17

## Risks Checked

- Stale scan summary appears after a window refresh invalidates the selected scan.
- Private running-app title appears in rendered summary after a successful scan.
- Arbitrary captured control text appears in rendered summary.
- Existing snapshots fail because a new required field was added.

## Mitigations

- `_scan_label()` only uses `scan_summary` when `has_scanned_running_app` is true.
- The field is optional and defaults to an empty string.
- Tests assert the rendered summary includes safe scan metadata but excludes representative private
  title/control text.
- Material-package behavior and existing fallback labels are unchanged.

## Residual Risk

The controller still keeps the last scan summary in memory after invalidation, but the view-model
does not render it while `has_scanned_running_app` is false. A future cleanup can clear all scanned
metadata on invalidation if broader controller state cleanup is prioritized.
