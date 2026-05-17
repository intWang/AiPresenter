# Cycle 201 Technical Scan: RingCentral Evidence Status Vocabulary

Date: 2026-05-17

## Read-Only Finding

RingCentral evidence/status language already has the right home:
`docs/knowledge/ringcentral-video/evidence-index.md`.

The exact section to use is `## Status Vocabulary Map`, placed immediately
after `## Evidence Levels`. This keeps the canonical vocabulary next to the
entrypoint evidence table and lets `validation-checklist-index.md` remain a
procedure doc, not the source of truth.

## Recommendation

Keep the `Status Vocabulary Map` with explicit distinctions for:

- `Do Not Execute Yet`: checklist state, not an evidence level.
- `Blocked`: non-executable until privacy, role, confirmation, locator, or
  side-effect risk is resolved.
- `Repo-tested`: local repository evidence only; does not promote live
  confidence.
- `Observed`: dated environment context exists, such as build, locale, DPI,
  bounds, and scenario.
- `Accepted`: only after `acceptance-runs.md` records a dated live/manual
  passing acceptance record with cleanup/privacy notes. Failed runs can be
  recorded, but they must not promote an evidence level to `Accepted`.
- Checklist procedure: `validation-checklist-index.md` plans safe validation
  work; it is procedure, not proof.
- Live acceptance evidence: `acceptance-runs.md` is the dated evidence source.

Recommended docs-contract test:
`tests/unit/test_material_packages.py::test_ringcentral_evidence_status_taxonomy_maps_checklist_terms`.

## Source Locations

- `docs/knowledge/ringcentral-video/evidence-index.md` - evidence level table,
  status vocabulary map, and acceptance run requirements.
- `docs/knowledge/ringcentral-video/validation-checklist-index.md` - procedure,
  `Do Not Execute Yet`, and evidence upgrade rules.
- `docs/knowledge/ringcentral-video/acceptance-runs.md` - dated evidence
  purpose and manual acceptance template.
- `docs/runbooks/ringcentral-manual-acceptance.md` - runbook checkboxes are not
  acceptance evidence.
- `src/ai_presenter/acceptance/validation_targets.py` - allowed evidence levels
  and evidence table parser.
- `tests/unit/test_material_packages.py` - docs contracts.
- `tests/unit/test_validation_targets.py` - invalid evidence level rejection and
  blocked target behavior.

## Verification

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests/unit/test_material_packages.py::test_ringcentral_knowledge_docs_preserve_evidence_boundaries tests/unit/test_material_packages.py::test_ringcentral_evidence_status_taxonomy_maps_checklist_terms tests/unit/test_validation_targets.py::test_evidence_index_integrity_rejects_invalid_evidence_level tests/unit/test_validation_targets.py::test_discover_validation_targets_can_include_blocked_rows tests/unit/test_validation_targets.py::test_render_validation_target_lines_suppresses_blocked_draft_command
git diff --check
```

## Risks

- Do not treat `validation-checklist-index.md` rows or runbook checkboxes as
  acceptance evidence.
- Do not promote `Observed` routes to `Accepted` without a dated
  `acceptance-runs.md` record.
- Do not let automated tests, dry runs, `doctor`, or read-only UIA observation
  imply live acceptance.
- Do not generate draft commands for blocked routes.
- Do not stage `.coverage`.
