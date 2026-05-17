# Cycle 213 Technical Scan

Date: 2026-05-17
Cycle: 213
Role: Technical scan and integration notes

## Implementation Map

- `packages/ringcentral-video.yaml`
  - Add one `localizedQuestions.fr` prompt and one `localizedAnswers.fr`
    answer under the existing recording safety Q&A.
- `tests/unit/test_material_packages.py`
  - Assert French Q&A coverage is `2/16`.
  - Assert recording safety has French text and no French alias.
  - Assert durable docs report `223` Q&A prompts.
- `tests/unit/test_cli.py`
  - Update French localization-report output and doctor prompt counts.
- `tests/unit/test_diagnostics.py`
  - Update French package-only detail and Q&A prompt diagnostics.
- Durable docs
  - Update `language-lifecycle.md`, `source-index.md`,
    `runtime-safety-routing.md`, and `observation-log.md`.

## Focused Verification

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests/unit/test_material_packages.py::test_localization_status_reports_french_package_seed tests/unit/test_material_packages.py::test_ringcentral_french_seed_qa_aliases_and_lifecycle_boundary_are_present tests/unit/test_material_packages.py::test_ringcentral_knowledge_docs_preserve_evidence_boundaries tests/unit/test_cli.py::test_localization_report_outputs_french_package_seed tests/unit/test_cli.py::test_localization_report_require_complete_fails_for_french_seed tests/unit/test_cli.py::test_doctor_loads_profile_package_and_flow tests/unit/test_diagnostics.py::test_diagnostics_french_seed_stays_package_only_runtime_unsupported tests/unit/test_diagnostics.py::test_diagnostics_reports_question_aliases_ok_for_ringcentral_package tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package
```

## Risk Notes

- Adding an alias would change query routing and alias diagnostics; keep this
  cycle answer-local only.
- French text remains package-local lookup data, not speech readiness or live
  acceptance evidence.
- Keep `.coverage` unstaged.
