# Cycle 194 Demand Analysis: Clear Invalid Running-App Scan Metadata

Date: 2026-05-17

## User Need

Cycle 193 prevents stale running-app scan summaries from rendering after scan invalidation, but the
controller still kept the old scanned package id, flow id, scan summary, package object, and window
handle in memory. Operators benefit from the stricter invariant that invalidated running-app
selections have no retained scanned target metadata.

## User / Operator Value

- Reduces privacy exposure from stale running-app scan state held in controller memory.
- Makes controller state easier to reason about: if the selected running app is not scanned, there
  should be no usable scanned package, flow, summary, package object, or handle.
- Lowers the risk of future UI/controller changes accidentally reusing stale scan data that Cycle
  193 only hid at the view-model boundary.

## Chosen Slice

Clear all controller-owned scanned running-app metadata whenever the running-app scan selection
becomes invalid.

## Acceptance Criteria

- When a previously scanned running-app selection becomes invalid, the controller clears:
  `scanned_package_id`, `scanned_flow_id`, `scanned_scan_summary`, `scanned_package`, and
  `scanned_handle`.
- The operator view still shows existing "needs scan" / "Scan required" behavior after
  invalidation.
- Start and question submission remain blocked until the selected or refreshed running app is
  scanned again.
- Successful scan behavior remains unchanged.
- Material-package mode remains unchanged.

## Non-Goals

- No UI redesign or copy changes.
- No telemetry or log format changes.
- No scan caching, async scan, or performance work.
- No package YAML, localization, RingCentral route, validation target, or acceptance evidence
  changes.
