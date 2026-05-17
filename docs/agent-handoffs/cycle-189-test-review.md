# Cycle 189 Test Review

Date: 2026-05-17

## RED Verification

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_acceptance_manual_record.py::test_manual_acceptance_draft_includes_evidence_redaction_checklist
```

Result before implementation: failed because `### Evidence Redaction Checklist` was absent from
the generated draft.

## Focused Verification

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_acceptance_manual_record.py tests\unit\test_cli.py::test_acceptance_draft_outputs_entrypoint_template tests\unit\test_cli.py::test_acceptance_draft_can_write_to_output_file
```

Result: `11 passed`.

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_knowledge_docs_preserve_evidence_boundaries tests\unit\test_material_packages.py::test_ringcentral_knowledge_docs_are_registered_in_navigation_indexes
```

Result: `2 passed`.

```powershell
.\.venv\Scripts\ai-presenter.exe acceptance-draft --package ringcentral-video --entrypoint ringcentral.video.toolbar.chat
```

Result: output included draft-only/no-live-action boundary text and the new
`Evidence Redaction Checklist`.

## Boundary Scan

```powershell
rg -n "Evidence Redaction Checklist|validated live|works in RingCentral|live validated" docs\agent-handoffs docs\runbooks docs\knowledge\ringcentral-video src\ai_presenter\acceptance tests\unit\test_acceptance_manual_record.py
```

Result: only the new checklist, existing guardrail docs/tests, and historical handoff warnings
matched. No generated draft claim used `validated live`, `works in RingCentral`, or `live
validated`.

## Review Follow-Up

An independent review found no P0/P1 wording issue. It flagged two lower-risk items:

- Keep tracked `.coverage` out of the commit with explicit path staging.
- Add a docs guard so the mirrored `acceptance-runs.md` checklist and runbook reminder cannot
  drift silently.

The docs guard was added to
`tests/unit/test_material_packages.py::test_ringcentral_knowledge_docs_preserve_evidence_boundaries`.

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_knowledge_docs_preserve_evidence_boundaries tests\unit\test_acceptance_manual_record.py tests\unit\test_cli.py::test_acceptance_draft_outputs_entrypoint_template tests\unit\test_cli.py::test_acceptance_draft_can_write_to_output_file
```

Result: `12 passed`.

## Required Before Commit

Run full repository verification and cached-diff checks:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m mypy src tests
git diff --cached --check
git diff --cached -- .coverage
git diff --cached --stat
git diff --cached --name-only
```
