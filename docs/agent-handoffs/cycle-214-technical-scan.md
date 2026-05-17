# Cycle 214 Technical Scan

Date: 2026-05-17
Cycle: 214
Role: Technical scan and integration notes

## Chosen Slice

Demand analysis recommended leaving/ending safety over another neutral
localization wedge because it covers a destructive meeting action. A parallel
technical scan recommended the same implementation pattern for French Q&A
seeds: one localized question, one localized answer, no aliases, and no runtime
language promotion.

## Implementation Map

- `packages/ringcentral-video.yaml`
  - Add `localizedQuestions.fr` and `localizedAnswers.fr` under the existing
    leaving/ending safety Q&A.
- `tests/unit/test_material_packages.py`
  - Assert French Q&A coverage is `3/16`.
  - Assert leaving/ending safety has French text and no French aliases.
  - Assert durable docs report `224` Q&A prompts.
- `tests/unit/test_cli.py`
  - Update French localization-report output and doctor prompt counts.
- `tests/unit/test_diagnostics.py`
  - Update French package-only detail and Q&A prompt diagnostics.
- Durable docs
  - Update `language-lifecycle.md`, `source-index.md`,
    `runtime-safety-routing.md`, and `observation-log.md`.

## Focused Verification

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests/unit/test_material_packages.py::test_localization_status_reports_french_package_seed tests/unit/test_material_packages.py::test_ringcentral_french_seed_qa_aliases_and_lifecycle_boundary_are_present tests/unit/test_material_packages.py::test_ringcentral_knowledge_docs_preserve_evidence_boundaries tests/unit/test_cli.py::test_localization_report_outputs_french_package_seed tests/unit/test_cli.py::test_localization_report_require_complete_fails_for_french_seed tests/unit/test_cli.py::test_doctor_loads_profile_package_and_flow tests/unit/test_diagnostics.py::test_diagnostics_french_seed_stays_package_only_runtime_unsupported tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package
```

## Risk Notes

- Adding a French alias would change routing and alias diagnostics; keep the
  slice Q&A-local.
- Safety wording must keep leaving/ending explain-only until the visible choice
  and impact are explicitly confirmed.
- Keep `.coverage` unstaged.
