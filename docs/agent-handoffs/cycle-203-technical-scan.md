# Cycle 203 Technical Scan: Accepted Evidence Guard

## Read-Only Finding

`docs/knowledge/ringcentral-video/evidence-index.md` already states the right rule: `Accepted` requires a dated live/manual passing acceptance record in `acceptance-runs.md`, and the current real Entry Point Evidence Table has no `Accepted` rows.

Current parser hook is `src/ai_presenter/acceptance/validation_targets.py`:

- `validate_entrypoint_evidence_index()` validates package coverage.
- `_parse_entrypoint_evidence()` extracts the `## Entry Point Evidence Table`.
- `_parse_first_table()` already handles markdown table headers and row cells.
- `_ALLOWED_EVIDENCE_LEVELS` includes `Accepted`, but there was no cross-file guard.

Focused verification during scan:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_validation_targets.py::test_evidence_index_integrity_covers_every_ringcentral_entrypoint_once tests\unit\test_validation_targets.py::test_evidence_index_integrity_rejects_invalid_evidence_level tests\unit\test_material_packages.py::test_ringcentral_acceptance_runs_define_outcome_promotion_rules
```

Result reported by subagent: `3 passed in 0.77s`.

Current evidence state reported by subagent:

```text
entrypoints=27
evidence_rows=27
accepted=[]
```

## Recommended Implementation

Add an optional `acceptance_text` argument to `validate_entrypoint_evidence_index()`:

```python
def validate_entrypoint_evidence_index(
    package: MaterialPackage,
    evidence_text: str,
    *,
    acceptance_text: str | None = None,
) -> EvidenceIndexIntegrityReport:
```

Keep existing callers working. If `acceptance_text` is omitted, preserve existing behavior. If it is provided, run a new guard after `_validate_entrypoint_evidence_integrity()`.

Guard behavior:

- Find entrypoint IDs whose evidence level is exactly `Accepted`.
- If none exist, return without requiring a live/manual record.
- For each `Accepted` entrypoint, require at least one dated manual acceptance section in `acceptance-runs.md` that includes:
  - heading beginning with `## YYYY-MM-DD`;
  - heading containing `Manual RingCentral Acceptance`;
  - the entrypoint ID in the section;
  - `- Outcome: pass`;
  - `- Accepted promotion eligible: yes`;
  - non-empty `- Promotion rationale:`;
  - non-empty recovery/cleanup evidence;
  - non-empty `- Privacy notes:`.

Do not treat old `- Pass/fail: pass for read-only observation` records as promotion evidence.

## Test Plan

- Add a RED test where an `Accepted` synthetic evidence row is rejected because no matching manual pass exists.
- Add a current-state guard test that real docs validate when no rows are `Accepted`.
- Add a synthetic valid manual pass record test.
- Add a synthetic automated false-positive rejection test.
- Add a synthetic manual pass with missing recovery/cleanup rejection test.

## Risks

- Markdown table parsing is intentionally simple and pipe-sensitive; avoid unescaped `|` characters inside Evidence Table cells.
- Exact heading names matter: `## Entry Point Evidence Table` and `## YYYY-MM-DD ... Manual RingCentral Acceptance`.
- Free-form acceptance text can create false positives if the guard only searches for `pass`; require heading type, outcome, eligibility, entrypoint ID, rationale, recovery/cleanup, and privacy notes together.
- False negatives are acceptable if a manual record omits the entrypoint ID. Promotion evidence should be explicit.
- Do not count Cycle 003 read-only observation as acceptance, even though it says pass for observation scope.
- Do not update `manual_record.py` unless separately scoped; current tests intentionally assert generated drafts do not contain `Accepted`.
