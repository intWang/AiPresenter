# Cycle 038 Summary: Evidence Entrypoint Integrity Guard

Date: 2026-05-16
Cycle: 038
Commit target: `fix: validate evidence entrypoint ids`

## Outcome

Cycle 038 added an offline integrity guard for the RingCentral Video evidence index.

The validation-target loader now validates `docs/knowledge/ringcentral-video/evidence-index.md` against the RingCentral material package whenever evidence text is supplied. This makes the evidence index safer as a planning artifact for future live/manual acceptance work.

## Files Changed

- `src/ai_presenter/acceptance/validation_targets.py`
- `tests/unit/test_validation_targets.py`
- `docs/agent-handoffs/cycle-038-demand-analysis.md`
- `docs/agent-handoffs/cycle-038-technical-scan.md`
- `docs/agent-handoffs/cycle-038-review.md`
- `docs/agent-handoffs/cycle-038-summary.md`
- `docs/superpowers/specs/2026-05-16-evidence-entrypoint-validation-design.md`
- `docs/superpowers/plans/2026-05-16-evidence-entrypoint-validation.md`

## Behavior

- Real RingCentral evidence index must cover all 27 package entrypoints.
- Evidence rows may reference only real package entrypoint IDs.
- Duplicate evidence entrypoint rows fail immediately.
- Evidence levels must be one of `Accepted`, `Observed`, `Repo-tested`, `Backlog`, or `Blocked`.
- Evidence rows without a backticked entrypoint ID fail instead of being silently skipped.
- Callers without evidence text still get the existing `unknown` fallback behavior.

## TDD And Review

Red phase:

- New integrity helper import failed before implementation.
- Missing, unknown, duplicate, invalid-level, and unbackticked-row tests reproduced the missing guard behavior.

Green phase:

- Added `EvidenceIndexIntegrityReport`.
- Added `validate_entrypoint_evidence_index()`.
- Routed `discover_validation_targets()` through the integrity guard when evidence text is supplied.
- Preserved validation-target rendering and acceptance-draft behavior for valid docs.

Review:

- Reviewer found the unbackticked-row false-negative path.
- Added a regression test and parser error for evidence rows without exactly one backticked entrypoint ID.

## Verification

Focused verification:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_validation_targets.py tests\unit\test_material_packages.py tests\unit\test_cli.py::test_validation_targets_lists_ringcentral_targets tests\unit\test_cli.py::test_validation_targets_include_blocked_lists_do_not_execute_routes
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\acceptance\validation_targets.py tests\unit\test_validation_targets.py
.\.venv\Scripts\mypy --no-incremental src\ai_presenter\acceptance\validation_targets.py tests\unit\test_validation_targets.py
```

Result:

- `59 passed`
- `All checks passed!`
- `Success: no issues found in 2 source files`

Full verification:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
.\.venv\Scripts\ruff check --no-cache .
.\.venv\Scripts\mypy --no-incremental src tests
git diff --check
```

Result:

- `562 passed, 1 warning`
- `All checks passed!`
- `Success: no issues found in 81 source files`
- `git diff --check` reported only LF-to-CRLF working-copy warnings; no whitespace errors.

## Next Handoff Ideas

- Cycle 039 can add the deferred `doctor` question-alias conflict readiness warning from the technical scan.
- A future strict CLI flag could expose the evidence integrity report directly, but this cycle keeps the existing command surface unchanged.
