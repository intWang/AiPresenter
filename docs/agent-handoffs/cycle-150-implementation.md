# Cycle 150 Implementation: Validation Target Evidence Fallback Guard

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Scope

Implemented a test-only renderer guard for `validation-targets` catalogs that
do not have an evidence file attached. The renderer must show `Evidence: none`
as traceability state, keep the non-evidence note visible, and still render
checklist-derived targets with `unknown` evidence levels.

Touched files:

- `tests/unit/test_validation_targets.py`
- `docs/agent-handoffs/cycle-150-implementation.md`

No production code, package YAML, profiles, runtime/provider behavior, live
RingCentral evidence, or generated artifacts were intentionally changed.
`.coverage` was already dirty and was not staged or reverted.

## Changes

- Added
  `test_render_validation_target_lines_marks_missing_evidence_source_as_none`.
- The test builds a catalog with checklist text and no `evidence_text` or
  `evidence_path`.
- It asserts the rendered output keeps:
  - checklist traceability;
  - `Evidence: none`;
  - `repo-derived planning list only; not live acceptance evidence`;
  - the P0 checklist target row;
  - the entrypoint row;
  - `unknown` evidence for the entrypoint.

## Red/Green Verification

Red check:

1. Added the fallback renderer test.
2. Temporarily changed
   `src/ai_presenter/acceptance/validation_targets.py` so the no-evidence path
   rendered `Evidence: missing`.
3. Ran:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_validation_targets.py::test_render_validation_target_lines_marks_missing_evidence_source_as_none
```

Result: failed on the missing `Evidence: none` line.

Green check:

1. Restored `validation_targets.py`.
2. Ran:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_validation_targets.py::test_render_validation_target_lines_marks_missing_evidence_source_as_none tests\unit\test_validation_targets.py::test_render_validation_target_lines_keeps_normal_draft_command
```

Result: `2 passed`.

Additional focused hygiene:

```powershell
.\.venv\Scripts\ruff.exe check --no-cache tests\unit\test_validation_targets.py
```

Result: passed.

## Boundaries

- `Evidence: none` means no evidence file is attached to this rendered catalog.
- It is not live RingCentral acceptance proof.
- It is not evidence-gap resolution.
- Checklist-derived target rows may still render, but their evidence level
  remains `unknown` without the evidence index.

## Follow-Up

The next narrow cycle could add a CLI-level smoke for a custom checklist with no
evidence path, or shift back to language/tone expansion after this evidence
boundary chain.
