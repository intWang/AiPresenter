# Cycle 185 Technical Development: Doctor Question Policy Check

Date: 2026-05-17

## Files Changed

- `src/ai_presenter/runtime/diagnostics.py`
  - Adds `_diagnose_question_policy_coverage(...)`.
  - Appends the check to package diagnostics.
- `tests/unit/test_diagnostics.py`
  - Adds RingCentralVideo expected count and zero-policy package coverage.
- `tests/unit/test_cli.py`
  - Asserts `doctor` prints the policy check.
- `docs/knowledge/ringcentral-video/source-index.md`
  - Records that doctor now reports answer-only policy counts.
- `docs/knowledge/ringcentral-video/runtime-safety-routing.md`
  - Adds the expected two answer-only policy entrypoints to current package signals.

## Behavior Added

`ai-presenter doctor --package ringcentral-video` now prints:

```text
[OK] question policy: 2/27 entrypoints use answerOnly question policy: ringcentral.video.top.meeting-info, ringcentral.video.more.notes
```

Packages with no policy-protected entrypoints print:

```text
[OK] question policy: 0/1 entrypoints use answerOnly question policy
```

## Focused Verification

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_question_policy_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_no_answer_only_question_policy tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

Result: `3 passed`.

Manual doctor smoke:

```powershell
$env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
```

Result: exit code `0`; output includes the new `question policy` line.
