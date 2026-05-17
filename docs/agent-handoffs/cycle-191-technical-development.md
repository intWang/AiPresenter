# Cycle 191 Technical Development: Entrypoint Draft Examples

Date: 2026-05-17

## Files Changed

- `src/ai_presenter/acceptance/validation_targets.py`
  - Adds detail-only per-entrypoint draft examples for selected multi-entrypoint targets.
- `tests/unit/test_validation_targets.py`
  - Covers grouped target examples, priority-list suppression, and single-entrypoint detail.
- `tests/unit/test_cli.py`
  - Covers CLI grouped target examples.
- `docs/runbooks/ringcentral-manual-acceptance.md`
  - Mentions `--target <target-id>` as the way to get per-entrypoint draft examples.
- `tests/unit/test_material_packages.py`
  - Guards the runbook breadcrumb.

## Behavior

`validation-targets --package ringcentral-video --target rcv-top-bar-routes` now keeps the
existing checklist-only group draft and adds:

```text
entrypoint draft examples:
  - ai-presenter acceptance-draft --package ringcentral-video --entrypoint ...
```

`validation-targets --package ringcentral-video --priority P1` remains compact and does not
include the examples.
