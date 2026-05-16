# Cycle 146 Implementation: Validation Target Source Traceability Guard

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Scope

Implemented a narrow test-only guard for `validation-targets` source
traceability. The listing/detail output must keep pointing operators back to
the checklist and evidence docs that produced the planning list, while the
Cycle145 non-evidence note remains in the same output.

Touched files:

- `tests/unit/test_cli.py`
- `tests/unit/test_validation_targets.py`
- `docs/agent-handoffs/cycle-146-implementation.md`

No production code, package YAML, profiles, runtime/provider behavior, live
RingCentral evidence, or generated artifacts were intentionally changed.
`.coverage` was already dirty and was not staged or reverted.

## Changes

- Added shared CLI constants for the expected `Checklist:` and `Evidence:`
  source lines.
- Strengthened the `validation-targets --priority P0` CLI test so listing
  output must include both source paths and the non-evidence note.
- Strengthened the `validation-targets --target rcv-add-coworkers-modal` CLI
  test so detail output must include both source paths and the non-evidence
  note before printing target details or draft commands.
- Strengthened the renderer-level target-detail test so
  `render_validation_target_lines` also preserves checklist/evidence
  traceability outside the Typer CLI wrapper.

## Red/Green Verification

Red check:

1. Added the checklist/evidence path assertions.
2. Temporarily changed
   `src/ai_presenter/acceptance/validation_targets.py` so rendered output said
   `Evidence: none`.
3. Ran:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_validation_targets_lists_ringcentral_targets tests\unit\test_cli.py::test_validation_targets_detail_outputs_draft_command tests\unit\test_validation_targets.py::test_render_validation_target_lines_keeps_normal_draft_command
```

Result: `3 failed`, each failing on the missing `Evidence:` source path.

Green check:

1. Restored the renderer implementation.
2. Re-ran the same command.

Result: `3 passed`.

## Boundaries

- Source paths are traceability pointers, not proof of live RingCentral
  acceptance.
- Checklist rows and evidence docs remain planning/navigation surfaces unless
  a dated run is recorded in `acceptance-runs.md`.
- `acceptance-draft` commands remain draft helpers.
- No live acceptance, route-readiness, provider-readiness, or runtime language
  claim was added.

## Follow-Up

The next narrow cycle could guard `acceptance-draft` output itself so generated
drafts continue to say `Draft only`, `not acceptance evidence`, and no live
RingCentral action has been performed.
