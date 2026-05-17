# Cycle 190 Technical Development: Metadata-First Target Reminder

Date: 2026-05-17

## Files Changed

- `src/ai_presenter/acceptance/validation_targets.py`
  - Adds a gated `Evidence reminder` header line for RingCentralVideo P0/P1 unblocked targets.
- `tests/unit/test_validation_targets.py`
  - Covers P1 inclusion and P2, blocked-only, and non-RingCentral suppression.
- `tests/unit/test_cli.py`
  - Covers CLI P0 output and placement before the first `draft:` line.
- `docs/runbooks/ringcentral-manual-acceptance.md`
  - Points operators to `validation-targets --package ringcentral-video --priority P0`.
- `tests/unit/test_material_packages.py`
  - Guards the runbook command reminder.

## Behavior

`validation-targets` now shows:

```text
Evidence reminder: P0/P1 manual evidence is metadata-first. Prefer UIA/window metadata and sanitized product-control labels; screenshots require a clear verification need and privacy review path; redact or omit private meeting content before recording results.
```

The reminder appears only for RingCentralVideo P0/P1 unblocked selections. It does not appear
for P2-only output, blocked-only output, or non-RingCentral catalogs.
