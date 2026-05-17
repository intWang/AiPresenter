# Cycle 185 Technical Scan: Question Policy Diagnostics

Date: 2026-05-17

## Current Source Shape

`OperationEntrypoint.question_policy` is defined in `src/ai_presenter/packages/models.py` and accepts `default` or `answerOnly` from package YAML.

Runtime operation permission already enforces the policy in `src/ai_presenter/runtime/questions.py` through `_can_operate(...)`.

`src/ai_presenter/runtime/diagnostics.py` already emits package-level checks for:

- package load and profile support
- package-owned question alias duplicates
- Q&A duplicate prompts
- Q&A alias overlap
- Q&A alias substring risk
- explainer coverage

## Implementation Surface

Add `_diagnose_question_policy_coverage(...)` in `runtime/diagnostics.py` and append it from `_diagnose_material_package(...)` before explainer coverage.

The check should:

- Count package operation entrypoints with `question_policy == "answerOnly"`.
- Report an OK status for both zero and nonzero counts.
- Include entrypoint IDs only when the count is nonzero.

## Test Targets

- `tests/unit/test_diagnostics.py::test_diagnostics_reports_question_policy_for_ringcentral_package`
- `tests/unit/test_diagnostics.py::test_diagnostics_reports_no_answer_only_question_policy`
- `tests/unit/test_cli.py::test_doctor_loads_profile_package_and_flow`

## Risks

- Do not confuse Q&A answer-only routing with entrypoint `questionPolicy`.
- Exact counts are intentionally brittle because package count drift should be reviewed.
- Keep output package-metadata-only and privacy-safe.
