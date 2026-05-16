# Cycle 148 Implementation: Renderer Draft Boundary Guard

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Scope

Implemented a test-only renderer-level guard for manual acceptance drafts.
Cycle147 guarded the CLI success paths; this cycle protects direct calls to
`render_manual_acceptance_draft(...)` so flow-only and mixed flow/entrypoint
drafts cannot lose the draft-only boundary.

Touched files:

- `tests/unit/test_acceptance_manual_record.py`
- `docs/agent-handoffs/cycle-148-implementation.md`

No production code, package YAML, profiles, runtime/provider behavior,
`acceptance-runs.md`, live RingCentral evidence, or generated artifacts were
intentionally changed. `.coverage` was already dirty and was not staged or
reverted.

## Changes

- Added `assert_manual_draft_boundary(...)` in
  `tests/unit/test_acceptance_manual_record.py`.
- Reused the helper in the existing entrypoint renderer test.
- Added the helper to the flow-only renderer test.
- Added the helper to the mixed flow plus entrypoint renderer test.
- The helper checks for:
  - `Draft only`;
  - `not acceptance evidence`;
  - `No live RingCentral action has been performed by this helper.`
- The helper also rejects two conclusion-style phrases:
  - `Accepted`;
  - `live validated`.

## Red/Green Verification

Red check:

1. Added the helper and three renderer call sites.
2. Temporarily changed
   `src/ai_presenter/acceptance/manual_record.py` from
   `No live RingCentral action has been performed by this helper.` to a
   proof-like live-action note.
3. Ran:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_acceptance_manual_record.py::test_manual_acceptance_draft_prefills_entrypoint_context_without_claiming_acceptance tests\unit\test_acceptance_manual_record.py::test_manual_acceptance_draft_prefills_flow_steps tests\unit\test_acceptance_manual_record.py::test_manual_acceptance_draft_prefills_mixed_flow_and_entrypoint_steps
```

Result: `3 failed`, all failing on the missing no-live-action sentence.

Green check:

1. Restored `manual_record.py`.
2. Re-ran the same command.

Result: `3 passed`.

Additional focused hygiene:

```powershell
.\.venv\Scripts\ruff.exe check --no-cache tests\unit\test_acceptance_manual_record.py
```

Result: passed.

## Boundaries

- Direct renderer output remains a template, not evidence.
- Flow-only and mixed renderer drafts now share the same boundary assertions as
  entrypoint drafts.
- The negative checks intentionally avoid banning `pass/fail` or `acceptance`
  because those are legitimate field labels or negated proof wording.
- No live acceptance, route readiness, provider readiness, or runtime language
  claim was added.

## Follow-Up

The next narrow cycle could guard `acceptance-draft` refusal paths so rejected
requests continue to avoid writing output files and avoid rendering manual
acceptance fields.
