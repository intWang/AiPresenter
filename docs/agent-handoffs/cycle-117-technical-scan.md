# Cycle 117 Technical Scan: Spanish Report-Only Q&A Completion

Scope: technical scan only. This handoff creates only this file and does not edit production code, tests, profiles, packages, coverage artifacts, or Codex home files.

## Summary

The right Spanish slice is package/report Q&A completion only:

- Keep runtime `PresenterLanguage` unsupported for Spanish.
- Complete Spanish `localizedQuestions.es` and `localizedAnswers.es` for all RingCentral Q&A items.
- Keep Spanish demo narration intentionally incomplete at `0/51`.
- Keep `localization-report --language es --require-complete` failing because required localization includes demo narration.
- Do not add Spanish to voice catalogs, controller language choices, profile routing, no-match runtime answers, or README runtime examples.

At scan time, a parallel implementation was already in progress in `packages/ringcentral-video.yaml` and several tests. Do not overwrite that work. The main remaining stale assertion I found is `tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_spanish_seed_coverage`, which still expects `1/12` Spanish Q&A despite the package now reporting `12/12`.

## Current Shape

Runtime language support is still intentionally limited in `src/ai_presenter/runtime/voice.py`:

- `PresenterLanguage = Literal["en", "zh", "ja"]`
- `PRESENTER_LANGUAGE_CHOICES` lists English, Chinese, and Japanese only.
- `PresenterVoiceSettings(language="es")` raises `ValueError("Unsupported presenter language: es")`.

Package localization is language-key based and can grow independently:

- `src/ai_presenter/packages/models.py` accepts arbitrary language keys under `localizedText`, `localizedQuestions`, `localizedAnswers`, and `questionAliases`.
- `_build_qa_question_candidates()` indexes all localized Q&A prompts, regardless of runtime voice support.
- `src/ai_presenter/packages/localization_status.py` reports arbitrary language strings and does not require those strings to be runtime presenter languages.

Question matching can use Spanish report-only prompts without runtime Spanish:

- `src/ai_presenter/runtime/questions.py::_match_qa()` matches precomputed Q&A candidates before entrypoint aliases.
- The response voice can remain English, so `_qa_answer_text()` returns English unless the selected runtime language has a localized answer.
- Do not add `_NO_MATCH_ANSWERS["es"]` in this slice; that belongs to runtime Spanish.

Diagnostics counts Q&A prompt candidates across all languages:

- Before the Spanish Q&A completion, RingCentral had `73` Q&A prompt candidates.
- Adding one Spanish prompt for each of the remaining 11 Q&A items raises the count to `84`.
- Package-owned alias count remains `90`; the Spanish report-only slice should not expand `questionAliases.es`.
- Existing substring-risk count remains `11` if only the current Spanish Q&A prompts are added.

## Exact Implementation Surface

Primary package file:

- `packages/ringcentral-video.yaml`

Add Spanish `localizedQuestions.es` and `localizedAnswers.es` for Q&A items #2 through #12:

- `Can the presenter describe shared-screen content?`
- `How can I bring people into the meeting?`
- `Can the presenter read meeting messages or participant names?`
- `Where are host controls for participants?`
- `Can AiPresenter send a reaction or raise my hand safely?`
- `How do I make sure my audio and video are ready?`
- `How do I troubleshoot choppy audio or video?`
- `Where are notes and transcript controls?`
- `Where are captions, live transcription, and translation controls?`
- `Where can I find post-meeting recordings, transcripts, summaries, or insights?`
- `How do I handle meeting recording safely?`

Leave these unchanged for this slice:

- No `localizedText.es` under demo narration.
- No new Spanish runtime language aliases.
- No Spanish profile or speech provider routing.
- No extra `questionAliases.es` unless a separate entrypoint-routing slice deliberately requests it.

## Exact Test Surface

Package localization tests:

- `tests/unit/test_material_packages.py::test_ringcentral_spanish_seed_qa_and_aliases_are_present`
  - Can remain focused on the original background privacy seed and its three `questionAliases.es`.
- `tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_spanish_seed_coverage`
  - Must update stale expectations from `1/12` to `12/12` for questions and answers.
  - Should continue asserting `demo_localized_steps == 0`, `demo_total_steps == 51`, `entrypoints_with_aliases == 1`, `entrypoint_total == 27`, `alias_total == 3`, and `required_localization_complete is False`.
  - Consider renaming to `test_ringcentral_localization_status_reports_spanish_report_only_qa_coverage`.
- `tests/unit/test_material_packages.py::test_ringcentral_spanish_qas_are_report_only_complete`
  - Good additional coverage: all Q&A items have `localizedQuestions.es`, all Q&A items have `localizedAnswers.es`, and no demo step has `localizedText.es`.

CLI localization-report tests:

- `tests/unit/test_cli.py::test_localization_report_outputs_spanish_report_only_qa_coverage`
  - Expected output: `Localization report: 0/51 demo steps`, `localized questions: 12/12`, `localized answers: 12/12`, `questionAliases.es present on 1/27 entrypoints (3 aliases)`.
  - Expected exit code: `0`.
- `tests/unit/test_cli.py::test_localization_report_require_complete_fails_for_spanish_report_only_qa`
  - Same Spanish Q&A counts.
  - Expected exit code: `1`.
  - Expected incomplete message remains `Localization coverage incomplete for es.`
- `tests/unit/test_cli.py::test_demo_rejects_unknown_language_before_runtime`
  - Must remain unchanged and continue asserting `Unsupported presenter language: es`.
- `tests/unit/test_cli.py::test_doctor_loads_profile_package_and_flow`
  - Update Q&A prompt count assertions from `73` to `84`.
  - Keep alias count at `90`.

Question matching tests:

- `tests/unit/test_questions.py::test_ringcentral_spanish_safety_questions_match_qas_without_runtime_spanish`
  - Use `PresenterVoiceSettings(language="en", tone="professional")`.
  - Assert Spanish Q&A prompts match Q&A items while `response.can_operate is False`.
  - Assert `create_question_interrupt_step(package, response) is None`.
  - This proves report-only Spanish prompts participate in Q&A matching without enabling Spanish runtime voice.

Diagnostics count tests:

- `tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package`
  - Update expected detail to `84 Q&A question prompts have no cross-item duplicates`.
- `tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package`
  - Update expected detail to `84 Q&A question prompts have no unsafe package-owned alias overlaps`.
- `tests/unit/test_diagnostics.py::test_diagnostics_reports_question_aliases_ok_for_ringcentral_package`
  - Keep expected `90 package-owned aliases`.
- `tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package`
  - Keep existing substring-risk expectation unless the Spanish prompt wording introduces new alias substrings.

Runtime Spanish guard tests:

- `tests/unit/test_voice.py::test_voice_settings_reject_unknown_language_and_tone`
  - Must keep `PresenterVoiceSettings(language="es")` rejected.
- `tests/unit/test_cli.py::test_demo_rejects_unknown_language_before_runtime`
  - Must keep Spanish runtime blocked before demo execution.

## Validation Observed

Commands run with the local `.venv` and without pytest coverage addopts:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe demo --profile ringcentral-video --package ringcentral-video --flow meeting-controls-tour --language es --dry-run
.\.venv\Scripts\python.exe -m pytest -q -o addopts="" tests\unit\test_material_packages.py::test_ringcentral_spanish_qas_are_report_only_complete tests\unit\test_cli.py::test_localization_report_outputs_spanish_report_only_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_spanish_report_only_qa tests\unit\test_questions.py::test_ringcentral_spanish_safety_questions_match_qas_without_runtime_spanish tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package
.\.venv\Scripts\python.exe -m pytest -q -o addopts="" tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_spanish_seed_coverage
```

Observed results:

- Spanish localization report now exits `0` and reports `0/51` demo steps, `12/12` Q&A questions, `12/12` Q&A answers, and `questionAliases.es present on 1/27 entrypoints (3 aliases)`.
- Spanish `--require-complete` exits `1` and reports `Localization coverage incomplete for es.`
- `demo --language es --dry-run` exits `1` with `Unsupported presenter language: es`.
- The focused updated test set passed: `8 passed in 1.99s`.
- The stale package localization-status test failed because it still expects `report.qa_localized_questions == 1`; current report value is `12`.

## Worktree Notes

Concurrent out-of-scope changes were present during this scan and were left untouched:

- `.coverage`
- `packages/ringcentral-video.yaml`
- `tests/unit/test_cli.py`
- `tests/unit/test_diagnostics.py`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_questions.py`
- `docs/agent-handoffs/cycle-117-demand-analysis.md`
- `docs/agent-handoffs/cycle-117-risk-scan.md`

This scan's ownership is only `docs/agent-handoffs/cycle-117-technical-scan.md`.
