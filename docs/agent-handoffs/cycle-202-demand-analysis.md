# Cycle 202 Demand Analysis: RingCentral Acceptance Run Outcome Rules

## Value

Tighten `docs/knowledge/ringcentral-video/acceptance-runs.md` so the template itself makes promotion rules unambiguous: failed, blocked, incomplete, or read-only runs may be recorded as evidence history, but they must never imply a route can move to `Accepted`.

The surrounding docs already carry this boundary:

- `evidence-index.md` says `Accepted` requires a dated live/manual passing acceptance record with cleanup/privacy notes, and failed live/manual runs must not promote to `Accepted`.
- `validation-checklist-index.md` says checklist work is procedure, not proof, and bars promotion from automated tests, dry runs, `doctor`, or read-only UIA observation alone.
- The runbook says pass/fail evidence belongs in `acceptance-runs.md`, while runbook checkboxes are not acceptance evidence.
- `tests/unit/test_material_packages.py` protects much of this vocabulary, especially status taxonomy and evidence-boundary wording.

The narrow gap was that `acceptance-runs.md` had `Pass/fail:` in the manual template and free-form `Results:` in the automated template, but no local rule beside the template explaining that only passing live/manual acceptance can support an `Accepted` evidence upgrade.

## Acceptance Criteria

- Add local acceptance-run rules stating that `Accepted` promotion requires a dated live/manual pass for the specific current build and route.
- Make failed, blocked, incomplete, skipped, automated-only, dry-run, `doctor`, and read-only observation records explicitly non-promoting.
- Make failed runs record failures, recovery, follow-up, and privacy notes, then leave evidence level unchanged or lower confidence if appropriate.
- Require evidence-level changes to happen only after the dated run is recorded and cross-checked against `evidence-index.md`.
- Preserve existing status vocabulary from `evidence-index.md`; do not invent a new evidence level.
- Update material package tests to assert the new `acceptance-runs.md` language.

## Non-Goals

- Do not change route evidence levels.
- Do not mark any RingCentral route as `Accepted`.
- Do not perform live RingCentral validation.
- Do not alter package YAML, locators, privacy matrix, source index, or runtime behavior.
- Do not rewrite the broader evidence taxonomy.

## Privacy Constraints

- Keep the metadata-first evidence rule: prefer UIA/window metadata and allowlisted product-control labels before screenshots.
- Failed runs must not preserve raw private artifacts.
- Continue to redact or omit chat text, participant names or roles, invite links, meeting IDs, dial-in details, emails, device lists, account/profile content, notes/transcripts, recordings, shared content, and room imagery.
- Failed or incomplete runs still require privacy notes describing what was redacted, omitted, deleted, or quarantined.

## Suggested Verification

- `.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_knowledge_docs_preserve_evidence_boundaries`
- `.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_evidence_status_taxonomy_maps_checklist_terms`

Read-only analysis completed by subagent; no files were modified by the subagent.
