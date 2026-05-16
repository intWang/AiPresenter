# Cycle 147 Implementation: Acceptance Draft Boundary Guard

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Scope

Implemented a test-only guard for successful `acceptance-draft` output paths.
The command may render a Markdown template to stdout or write it to a separate
draft file, but every successful draft must remain explicitly draft-only and
must not claim live RingCentral action or acceptance evidence.

Touched files:

- `tests/unit/test_cli.py`
- `docs/agent-handoffs/cycle-147-implementation.md`

No production code, package YAML, profiles, runtime/provider behavior,
`acceptance-runs.md`, live RingCentral evidence, or generated artifacts were
intentionally changed. `.coverage` was already dirty and was not staged or
reverted.

## Changes

- Added `assert_acceptance_draft_boundary` in `tests/unit/test_cli.py`.
- Applied the helper to three successful `acceptance-draft` paths:
  - entrypoint stdout;
  - flow stdout;
  - file output.
- The helper checks for:
  - `Draft only`;
  - `not acceptance evidence`;
  - `No live RingCentral action has been performed by this helper.`
- It also rejects conclusion-style wording in the generated draft:
  - `accepted`;
  - `passed`;
  - `live validated`.
- The file-output test now also confirms the CLI success message itself does
  not say `acceptance evidence`.

## Red/Green Verification

Red check:

1. Added the helper and three call sites.
2. Temporarily changed
   `src/ai_presenter/acceptance/manual_record.py` from
   `No live RingCentral action has been performed by this helper.` to a
   proof-like live-action note.
3. Ran:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_acceptance_draft_outputs_entrypoint_template tests\unit\test_cli.py::test_acceptance_draft_outputs_flow_template tests\unit\test_cli.py::test_acceptance_draft_can_write_to_output_file
```

Result: `3 failed`, all failing on the missing no-live-action sentence.

Green check:

1. Restored `manual_record.py`.
2. Re-ran the same command.

Result: `3 passed`.

Additional focused hygiene:

```powershell
.\.venv\Scripts\ruff.exe check --no-cache tests\unit\test_cli.py
```

Result: passed.

## Boundaries

- `acceptance-draft` output remains a template, not evidence.
- Generated files are draft files only and are not written to
  `acceptance-runs.md`.
- The helper did not perform a live RingCentral action.
- No route, cleanup, privacy, provider, profile, language, or runtime readiness
  claim was added.

## Follow-Up

The next narrow cycle could add a renderer-level helper in
`tests/unit/test_acceptance_manual_record.py` so flow and mixed renderer unit
tests share the same draft-only boundary currently guarded through CLI tests.
