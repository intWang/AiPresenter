# Cycle 202 Technical Scan: Acceptance Run Pass/Fail Boundaries

## Read-Only Finding

The evidence taxonomy is strong in `docs/knowledge/ringcentral-video/evidence-index.md`: failed live/manual runs may be recorded, but cannot promote a route to `Accepted`.

The weaker spot was the manual run template in `docs/knowledge/ringcentral-video/acceptance-runs.md`. It had `Pass/fail`, `Failures`, and `Recovery`, but did not explicitly tell operators how to distinguish a passing acceptance run from a failed live/manual run, an automated baseline, or a read-only observation.

## Recommended Wording

Add explicit outcome and promotion fields to the manual template:

- `Outcome: pass | fail | blocked | incomplete | skipped`
- `Accepted promotion eligible: yes | no`
- `Promotion rationale:`

Add an evidence-level rule section stating:

- Only a dated passing live/manual acceptance run with cleanup restored and privacy notes complete can justify promotion to `Accepted`.
- Failed live/manual runs and read-only observations are recorded evidence, but must not promote evidence level.
- Automated baselines, dry runs, and `doctor` checks can support repository baseline evidence only.

Also tighten `validation-checklist-index.md` from "dated manual/live record" to "dated passing manual/live record" so a failed record cannot be misread as sufficient.

## Recommended Test Changes

- Add a material-package test that asserts `acceptance-runs.md` contains the new outcome fields and promotion rules.
- Update the existing evidence-boundary test to require the stricter checklist wording.
- Keep the existing status taxonomy test; it already locks the failed-run boundary in `evidence-index.md`.

Generated acceptance drafts were intentionally left unchanged in this cycle because adding `Accepted` wording to drafts could weaken draft-only semantics and collide with CLI boundary tests.

## Risks

- A failed manual run could be misread as sufficient for `Accepted` if the template stays ambiguous.
- Automated tests, dry runs, `doctor`, and read-only UIA observations must remain non-promoting evidence.
- Do not stage `.coverage`; it is a generated coverage artifact and unrelated to the cycle.

## Verification Used By Subagent

Read-only scan commands used by the subagent:

```powershell
rg -n "acceptance-runs|evidence|manual|live run|promotion|promote|failed|passing|pass" .
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_knowledge_docs_preserve_evidence_boundaries tests\unit\test_material_packages.py::test_ringcentral_evidence_status_taxonomy_maps_checklist_terms tests\unit\test_acceptance_manual_record.py tests\unit\test_cli.py::test_acceptance_draft_outputs_entrypoint_template tests\unit\test_cli.py::test_acceptance_draft_can_write_to_output_file tests\unit\test_cli.py::test_acceptance_draft_rejects_acceptance_runs_output_file tests\unit\test_validation_targets.py::test_evidence_index_integrity_rejects_invalid_evidence_level tests\unit\test_validation_targets.py::test_render_validation_target_lines_keeps_normal_draft_command
git status --short
```

Verification result reported by subagent: `16 passed in 3.30s`.
