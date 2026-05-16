# Cycle 038 Technical Scan

Date: 2026-05-16
Role: technical scan
Scope: read-only scan. No implementation changes were made by the technical agent.

## Candidate A: Evidence Integrity Guard

Demand-side priority is a pure acceptance helper that validates the RingCentral evidence index against the material package.

Implementation fit:

- Existing parser: `src/ai_presenter/acceptance/validation_targets.py`.
- Existing tests: `tests/unit/test_validation_targets.py`.
- Existing docs: `docs/knowledge/ringcentral-video/evidence-index.md`.
- Existing CLI path: `validation-targets` already loads the evidence index and can benefit from stricter validation without adding a new command.

Risk:

- Keep validation offline and avoid promoting evidence levels from repository tests alone.
- Preserve `validation-targets` output shape when the current docs are valid.

## Candidate B: Doctor Alias Readiness

The technical scan also identified a useful follow-up from Cycle 035: add a `doctor` check that warns when package-owned `questionAliases` duplicate a normalized alias across multiple entrypoints.

Decision:

- Defer Candidate B to Cycle 039.
- Cycle 038 will take Candidate A because it directly strengthens the RingCentral资料包 trust boundary.

## Verification Shape

Focused verification should include:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_validation_targets.py tests\unit\test_material_packages.py
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\acceptance\validation_targets.py tests\unit\test_validation_targets.py
.\.venv\Scripts\mypy --no-incremental src\ai_presenter\acceptance\validation_targets.py tests\unit\test_validation_targets.py
```

