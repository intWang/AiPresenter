# Cycle 204 Technical Scan: Validation Targets Acceptance Text Wiring

## Scope

Read-only scan. No files were edited by the subagent.

Goal: make common validation-target tooling reject synthetic `Accepted` evidence rows unless `acceptance-runs.md` contains a matching dated passing manual acceptance record.

## Current Finding

Cycle 203 added the core guard in `src/ai_presenter/acceptance/validation_targets.py`, but only callers that pass `acceptance_text` enforce it.

Relevant signatures:

- `validate_entrypoint_evidence_index(package, evidence_text, *, acceptance_text=None)`
- `discover_validation_targets(package, *, checklist_text, checklist_path, evidence_text=None, evidence_path=None, acceptance_text=None, include_blocked=False)`

The pure discovery path forwards `acceptance_text` into `validate_entrypoint_evidence_index()`. The remaining gap was CLI/common tooling: `ai-presenter validation-targets` read checklist and evidence files only, then called `discover_validation_targets(...)` without `acceptance_text`.

## Evidence

Focused verification command run during scan:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_validation_targets.py::test_accepted_evidence_requires_dated_passing_manual_acceptance_run tests\unit\test_validation_targets.py::test_accepted_evidence_guard_accepts_matching_manual_pass_record tests\unit\test_cli.py::test_validation_targets_rejects_unbacked_accepted_evidence
```

Result reported by subagent before CLI wiring: `2 passed, 1 failed`.

Failing test:

- `tests/unit/test_cli.py::test_validation_targets_rejects_unbacked_accepted_evidence`
- Actual before wiring: CLI exit code `0`
- Expected: nonzero with the accepted-evidence guard message

## Recommended Implementation

- Add optional `acceptance_text` to `discover_validation_targets` and pass it to `validate_entrypoint_evidence_index`.
- In `validation-targets`, read the sibling `acceptance-runs.md` for the selected evidence index when present.
- Add `--acceptance-runs` for custom evidence indexes and positive tests.
- Preserve direct library calls that intentionally omit acceptance text.

## Edge Cases To Preserve

- CLI should validate the full evidence index before target filtering, so `--target` cannot hide an unbacked `Accepted` row elsewhere.
- Automated baseline, dry-run, `doctor`, read-only observation, failed, blocked, incomplete, and skipped records must not satisfy `Accepted`.
- Entrypoint mention must be in `Entrypoint IDs tested`, not only `Follow-up`, notes, failures, or steps.
- Missing recovery/cleanup or missing privacy notes should reject promotion evidence.
- Do not update `manual_record.py`; draft tests intentionally guard against acceptance-claim wording in generated drafts.
- Do not edit `evidence-index.md` or fabricate live acceptance evidence.

## Suggested Verification

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_validation_targets.py::test_discover_validation_targets_enforces_accepted_evidence_guard tests\unit\test_validation_targets.py::test_accepted_evidence_requires_dated_passing_manual_acceptance_run tests\unit\test_validation_targets.py::test_accepted_evidence_guard_accepts_matching_manual_pass_record tests\unit\test_cli.py::test_validation_targets_rejects_unbacked_accepted_evidence tests\unit\test_cli.py::test_validation_targets_accepts_backed_accepted_evidence
.\.venv\Scripts\python.exe -m ruff check src\ai_presenter\acceptance\validation_targets.py src\ai_presenter\cli.py tests\unit\test_validation_targets.py tests\unit\test_cli.py
```
