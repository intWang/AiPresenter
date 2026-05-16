# Cycle 128 Test Review - Spanish Runtime Promotion

## Scope Reviewed

- Reviewed the current uncommitted Cycle128 diff for Spanish presenter runtime promotion.
- Focused on the boundary that Spanish is runtime-selectable only with OpenAI-backed speech.
- Checked that fake, Piper, `windows-sapi`, `windows-sapi-en`, and `windows-sapi-zh` reject Spanish before demo/controller runtime work begins.
- Checked that package-localization-only future languages remain distinct from presenter runtime support.
- Reviewed changed docs for the Spanish package-localization versus runtime/provider distinction.

## Commands and Results

- `git status --short`
  - Result: existing uncommitted changes include `.coverage`, docs, `src/ai_presenter/runtime/voice.py`, and focused tests. I did not modify source or tests.
- `git diff -- src/ai_presenter/runtime/voice.py tests/unit/test_voice.py tests/unit/test_cli.py tests/unit/test_diagnostics.py`
  - Result: reviewed Spanish aliases, language labels, localized text rendering, provider validation, and new CLI/diagnostics tests.
- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py::test_voice_validation_allows_spanish_openai_profile tests\unit\test_voice.py::test_voice_validation_rejects_spanish_non_openai_profiles tests\unit\test_cli.py::test_demo_openai_profile_accepts_spanish_dry_run tests\unit\test_cli.py::test_controller_openai_profile_accepts_spanish_dry_run tests\unit\test_cli.py::test_demo_rejects_spanish_local_profile_before_runtime tests\unit\test_cli.py::test_doctor_openai_profile_accepts_spanish_runtime_language tests\unit\test_cli.py::test_doctor_rejects_package_only_language_after_complete_localization tests\unit\test_diagnostics.py::test_diagnostics_reports_spanish_openai_voice_supported tests\unit\test_diagnostics.py::test_diagnostics_reports_spanish_local_voice_unsupported tests\unit\test_diagnostics.py::test_diagnostics_runtime_language_support_stays_separate_after_package_localization_complete`
  - Result: `14 passed in 2.07s`.
- `.\.venv\Scripts\ai-presenter.exe demo --profile profiles/ringcentral-video-openai.example.yaml --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run`
  - Result: exit `0`; loaded `Spanish / Professional`; dry run completed.
- `.\.venv\Scripts\ai-presenter.exe demo --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run`
  - Result: exit `1`; rejected before runtime with `windows-sapi-en cannot use Spanish / Professional` and `requires speech provider openai`.
- `.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language es --require-localization`
  - Result: exit `1`; package localization and runtime language recognition were OK, but voice compatibility failed for local `windows-sapi-en`.
- `git diff --check`
  - Result: exit `0`; only line-ending warnings for pre-existing touched files.

## Findings by Severity

- Critical: none.
- High: none.
- Medium: none.
- Low: none.

## Residual Risks

- I ran a focused test slice, not the full suite.
- `doctor --require-localization --localization-language es` without `--language es` checks package localization and general runtime language recognition, not profile voice compatibility. The profile-specific OpenAI-only boundary is enforced when an actual Spanish voice is selected with `--language es`.
- No live OpenAI audio synthesis or live RingCentral Video acceptance was exercised; docs correctly keep those out of scope.
- `.coverage` was already modified in the working tree before this review and should remain unstaged unless intentionally regenerated.

## Recommendation

Go for the Cycle128 Spanish runtime promotion diff as reviewed. The focused evidence supports the intended contract: Spanish is accepted on OpenAI-backed speech, local fake/Piper/SAPI routes reject before runtime execution, and complete package localization for a future language such as `de` still does not imply presenter runtime support.
