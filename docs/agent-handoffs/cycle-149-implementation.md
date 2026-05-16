# Cycle 149 Implementation: Acceptance Draft Refusal Guard

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Scope

Implemented a test-only guard for `acceptance-draft` refusal paths. If the CLI
rejects a draft request, output must not look like a rendered manual acceptance
draft, must not claim a draft was written, and must not contain conclusion-style
acceptance wording.

Touched files:

- `tests/unit/test_cli.py`
- `docs/agent-handoffs/cycle-149-implementation.md`

No production code, package YAML, profiles, runtime/provider behavior,
`acceptance-runs.md`, live RingCentral evidence, or generated artifacts were
intentionally changed. `.coverage` was already dirty and was not staged or
reverted.

## Changes

- Added `assert_acceptance_draft_refusal_boundary(...)` in
  `tests/unit/test_cli.py`.
- Applied the helper to four refusal paths:
  - direct no-open-step entrypoint refusal;
  - no-open-step refusal with `--output`;
  - existing output file refusal;
  - `acceptance-runs.md` output refusal.
- The helper checks that refusal output does not include:
  - `Manual RingCentral Acceptance Draft`;
  - `### Manual Acceptance Fields`;
  - `Wrote acceptance draft`;
  - `accepted`;
  - `passed`;
  - `live validated`.
- Existing side-effect assertions remain:
  - blocked output files are not created;
  - existing output file contents are not overwritten;
  - `acceptance-runs.md` output is not created.

## Red/Green Verification

Red check:

1. Added the refusal helper and call sites.
2. Temporarily changed `src/ai_presenter/cli.py` so the existing-file refusal
   message included `Wrote acceptance draft`.
3. Ran:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_acceptance_draft_rejects_existing_output_file
```

Result: failed on the new refusal-boundary helper.

Green check:

1. Restored `src/ai_presenter/cli.py`.
2. Ran:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_acceptance_draft_rejects_no_open_step_entrypoint tests\unit\test_cli.py::test_acceptance_draft_refusal_does_not_write_output_file tests\unit\test_cli.py::test_acceptance_draft_rejects_existing_output_file tests\unit\test_cli.py::test_acceptance_draft_rejects_acceptance_runs_output_file
```

Result: `4 passed`.

Additional focused hygiene:

```powershell
.\.venv\Scripts\ruff.exe check --no-cache tests\unit\test_cli.py
```

Result: passed.

## Boundaries

- Refusal output is an error path, not a draft body.
- Refusal paths still do not create or overwrite draft files.
- The helper avoids broad bans on `acceptance`, `evidence`, `pass`, or `fail`
  so valid safety language and field labels remain possible.
- No live acceptance, route readiness, provider readiness, or runtime language
  claim was added.

## Follow-Up

The next narrow cycle could guard `validation-targets` fallback behavior when
an evidence file is omitted, making sure `Evidence: none` is traceability state
and not proof.
