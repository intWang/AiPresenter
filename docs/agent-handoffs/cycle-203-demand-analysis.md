# Cycle 203 Demand Analysis: RingCentralVideo Accepted Evidence Traceability

## Value

RingCentralVideo evidence docs already state that `Accepted` requires dated live/manual passing acceptance, but enforcement was mostly prose-level. Existing tests validated evidence table coverage, valid evidence-level names, and boundary wording, yet they would not fail if a future row in `docs/knowledge/ringcentral-video/evidence-index.md` were changed to `Accepted` without a matching eligible run in `docs/knowledge/ringcentral-video/acceptance-runs.md`.

Cycle 203 turns that policy into a testable contract: every `Accepted` entrypoint row must trace to a dated passing live/manual acceptance record for that route, with recovery/cleanup and privacy notes, and must not be justified by automated baselines, dry runs, `doctor`, read-only observations, failed, blocked, incomplete, or skipped records.

## Acceptance Criteria

- Add a machine-checkable guard for `Accepted` rows in `docs/knowledge/ringcentral-video/evidence-index.md`.
- The guard requires a matching record in `docs/knowledge/ringcentral-video/acceptance-runs.md` that is:
  - dated in the run heading;
  - live/manual, not automated baseline, dry-run, `doctor`, repo-only, or read-only observation;
  - `Outcome: pass`;
  - `Accepted promotion eligible: yes`;
  - tied to the specific entrypoint ID being marked `Accepted`;
  - includes non-empty cleanup/restoration evidence;
  - includes non-empty privacy notes.
- Failed, blocked, incomplete, skipped, automated-only, dry-run, `doctor`, and read-only records must fail to justify `Accepted`.
- Add focused unit tests with synthetic evidence/acceptance text for missing acceptance records, automated false positives, missing cleanup/recovery, and a valid manual pass.
- Update docs contract tests in `tests/unit/test_material_packages.py` to pin new template and guard wording.
- Add an explicit manual-template field such as `- Entrypoint IDs tested:` so promotion evidence can be tied to exact routes.

## Non-Goals

- Do not mark any current RingCentralVideo route as `Accepted`.
- Do not append to or fabricate `acceptance-runs.md`.
- Do not perform live RingCentral manual validation.
- Do not weaken existing evidence levels, checklist terminology, or draft-only protections.
- Do not treat `validation-checklist-index.md`, runbook checkboxes, source docs, package tests, or generated drafts as acceptance evidence.

## Privacy Constraints

- Preserve the metadata-first evidence policy.
- Do not require screenshots for promotion.
- Eligible run records must keep private content out of evidence: chat text, participant names/roles, invite links, meeting IDs, dial-in details, emails, device lists, account/profile content, notes/transcripts, recordings, shared content, and room imagery.
- Cleanup/privacy fields should prove boundaries were respected, not expose sensitive data.

## Suggested Verification

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_validation_targets.py
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_material_packages.py
.\.venv\Scripts\python.exe -m pytest -q
```

Useful RED shape: synthesize an `Accepted` evidence row for `ringcentral.video.toolbar.chat` while `acceptance-runs.md` contains only Cycle 001-004 style automated/read-only/ineligible records; validation should reject it until a dated eligible manual pass fixture is provided.
