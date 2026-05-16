# Cycle 121 Implementation: Diagnostics Index Guard

Date: 2026-05-16
Scope: behavior-preserving diagnostics performance guard.

## Decision

Cycle 121 implemented the technical scan's diagnostics index guard instead of adding more Spanish narration.

The implementation builds a private `_PackageDiagnosticsIndex` once per material-package diagnostics pass and reuses it across package-owned alias and Q&A diagnostics. This keeps the current output stable while reducing repeated grouping/scanning work inside diagnostics.

## Files Changed

- `src/ai_presenter/runtime/diagnostics.py`
  - Added `_PackageDiagnosticsIndex`.
  - Added `_build_package_diagnostics_index(...)`.
  - Builds the index once inside `_diagnose_material_package(...)`.
  - Threads the index through:
    - `_diagnose_question_aliases(...)`
    - `_diagnose_qa_questions(...)`
    - `_diagnose_qa_alias_overlaps(...)`
    - `_diagnose_qa_alias_substring_risks(...)`
  - Keeps diagnostic names, order, statuses, and detail strings unchanged.
- `tests/unit/test_diagnostics.py`
  - Adds structural coverage for alias and Q&A candidate grouping.
  - Proves substring-risk diagnostics use the language-scoped alias index.
  - Keeps existing RingCentral diagnostic output tests unchanged.

## Red/Green Evidence

Red command before implementation:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_package_diagnostics_index_groups_aliases_and_qa_candidates tests\unit\test_diagnostics.py::test_diagnostics_substring_risk_uses_language_scoped_alias_index
```

Initial result:

- `2 failed`
- Both failures were expected `AttributeError` failures because `_build_package_diagnostics_index(...)` did not exist yet.

Green focused command after implementation:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_package_diagnostics_index_groups_aliases_and_qa_candidates tests\unit\test_diagnostics.py::test_diagnostics_substring_risk_uses_language_scoped_alias_index tests\unit\test_diagnostics.py::test_diagnostics_reports_question_aliases_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package
```

Result:

- `6 passed`

Broader focused regression:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow tests\unit\test_cli.py::test_doctor_require_localization_accepts_package_only_spanish_language
```

Result:

- `39 passed`

## Timing Probe

An in-process diagnostic probe ran 200 `diagnose_configuration(...)` calls for the RingCentral package and `meeting-control-map-demo`.

Observed local result:

- `1884.696 ms`

This is recorded as lightweight local evidence only. The committed tests use structural parity rather than brittle wall-clock assertions.

## Boundaries Preserved

- No package YAML changed.
- No Spanish runtime support changed.
- No CLI wording changed.
- No localization report behavior changed.
- No route ordering, Q&A-first behavior, alias precedence, `questionPolicy`, `can_operate`, or interrupt creation changed.
- No process-global or file-mtime cache was added.
- No live RingCentral acceptance claim was added.
- `.coverage` remains out of scope and must not be staged.
