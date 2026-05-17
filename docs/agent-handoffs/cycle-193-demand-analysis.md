# Cycle 193 Demand Analysis: Operator Scan Summary

Date: 2026-05-17

## User Need

After Cycle 192 added privacy-safe scan telemetry, the operator still only saw the same short
scan message as transient status text. During a live demo, the summary row should keep the useful
scan facts visible without exposing the running window title or captured control text.

## Chosen Slice

Persist the structured scan status from the controller into the operator view-model summary.

## Acceptance Criteria

- A scanned running-app target shows package id, control count, entrypoint count, and elapsed time
  in the operator scan summary.
- The summary does not include the selected window title or arbitrary control text.
- Stale scan summaries are ignored unless the current running-app selection is marked scanned.
- Existing material-package scan label behavior remains unchanged.
- Existing start, scan, submit, and target-ready logic remains unchanged.

## Non-Goals

- No new telemetry fields.
- No scan caching or performance thresholds.
- No UI layout redesign.
- No package YAML, localization, RingCentral route, validation target, or acceptance evidence
  changes.
