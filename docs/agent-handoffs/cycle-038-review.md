# Cycle 038 Review: Evidence Integrity Guard

Date: 2026-05-16
Role: test/review
Scope: review of the Cycle 038 evidence-index integrity guard.

## Finding

Reviewer found one medium issue:

- Evidence-table rows whose `Entrypoint` cell omitted backticks were silently skipped by the parser. A malformed row such as `ringcentral.video.toolbar.typo` could be present alongside the 27 valid rows and the integrity report would still pass.

## Resolution

Added a regression test:

- `test_evidence_index_integrity_rejects_unbackticked_entrypoint_cell`

Updated `_parse_entrypoint_evidence()` so every non-empty evidence row must include exactly one backticked entrypoint ID. Missing backticks now fail clearly with:

```text
evidence row missing backticked entrypoint id: <cell>
```

## Review Verification

Focused review checks:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_validation_targets.py
```

Result:

```text
21 passed
```

No misleading RingCentral acceptance promotions were found in the Cycle 038 docs.

