# Cycle 118 Technical Scan: Spanish Demo Narration Completion

Scope: technical scan only. This handoff is the only file changed by this subagent. Do not stage or commit from this scan.

## Findings

Cycle 117 left Spanish in a clean report-only state:

- `localization-report --package ringcentral-video --language es` exits `0`.
- Current Spanish coverage is `0/51` demo steps, `12/12` Q&A questions, `12/12` Q&A answers.
- `questionAliases.es` is intentionally limited to `1/27` entrypoints with `3` aliases on `ringcentral.video.settings.background`.
- `localization-report --language es --require-complete` exits `1` only because demo narration is missing.
- Runtime Spanish remains unsupported. `demo --language es --dry-run` is rejected by `PresenterVoiceSettings` with `Unsupported presenter language: es`.

The package/report surfaces already support arbitrary localization keys:

- `packages/ringcentral-video.yaml` owns `narration.localizedText.<language>`, `localizedQuestions.<language>`, `localizedAnswers.<language>`, and `questionAliases.<language>`.
- `src/ai_presenter/packages/localization_status.py` marks required localization complete only when all demo narration, Q&A questions, and Q&A answers are localized. Alias coverage is reported but not required.
- `src/ai_presenter/runtime/voice.py` supports only `en`, `zh`, and `ja`, so package Spanish can become report-complete without becoming a presenter runtime language.

## Chosen Recommendation

Recommend completing Spanish demo narration coverage while keeping runtime Spanish unsupported.

This is the smallest slice that advances the Spanish localization lifecycle after Cycle 117. A runtime promotion plan is premature because voice/provider readiness, catalog output, no-match text, CLI validation, and profile compatibility would all need deliberate design. A diagnostics guard is smaller technically, but it does not advance the Spanish coverage gap that now blocks `--require-complete`.

## File Map

Change:

- `packages/ringcentral-video.yaml`
  - Add `narration.localizedText.es` to all 51 demo steps across all 4 flows.
  - Preserve English UI labels where the UI shows English, such as `Settings`, `Background`, `Blur`, `Invite`, `Chat`, `Participants`, `More`, `Notes`, `Leave`, and `Start recording`.
  - Do not add new `questionAliases.es` in this slice.

Update tests:

- `tests/unit/test_material_packages.py`
  - Add or update Spanish demo coverage test: every demo step has nonblank `localizedText.es`.
  - Assert per-flow Spanish counts: `vbg-blur-demo 4/4`, `meeting-basics-demo 3/3`, `meeting-controls-tour 22/22`, `meeting-control-map-demo 22/22`.
  - Assert Spanish report totals: `demo_localized_steps == 51`, `qa_localized_questions == 12`, `qa_localized_answers == 12`, `required_localization_complete is True`.
  - Keep alias expectations at `entrypoints_with_aliases == 1`, `alias_total == 3`.
- `tests/unit/test_cli.py`
  - Update Spanish report test to expect `Localization report: 51/51 demo steps`.
  - Replace/rename the current Spanish `--require-complete` failure test so it expects exit `0`, no `Localization coverage incomplete for es.`, and no `missing:` lines.
  - Keep `test_demo_rejects_unknown_language_before_runtime` unchanged.
- `tests/unit/test_diagnostics.py`
  - Add direct diagnostics coverage for `diagnose_configuration(..., require_localization=True, localization_language="es")` returning `[OK] localization: required es localization complete`.
  - Do not add CLI `doctor --language es` expectations; CLI language parsing should still reject Spanish until runtime promotion.
- `tests/unit/test_voice.py`
  - No production change expected, but keep the existing unsupported-language guard green.

Do not change:

- `src/ai_presenter/runtime/voice.py`
- `src/ai_presenter/runtime/questions.py`
- provider/profile files
- README runtime language examples
- `.coverage`

## Red/Green Plan

Red checks before package narration edits:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -o addopts="" tests\unit\test_material_packages.py::test_ringcentral_spanish_demo_narration_is_complete
.\.venv\Scripts\python.exe -m pytest -q -o addopts="" tests\unit\test_cli.py::test_localization_report_require_complete_passes_for_spanish
```

Expected red state today: Spanish demo narration is `0/51`, and `--require-complete` exits `1`.

Green checks after implementation:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe demo --profile ringcentral-video --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
.\.venv\Scripts\python.exe -m pytest -q -o addopts="" tests\unit\test_material_packages.py tests\unit\test_cli.py::test_localization_report_outputs_spanish_report_only_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_passes_for_spanish tests\unit\test_cli.py::test_demo_rejects_unknown_language_before_runtime tests\unit\test_diagnostics.py::test_diagnostics_require_localization_passes_for_ringcentral_spanish
```

Expected final CLI behavior:

- Spanish localization report exits `0` and reports `51/51 demo steps`, `12/12 Q&A questions`, `12/12 Q&A answers`.
- Spanish `--require-complete` exits `0` and prints no incomplete message.
- Spanish runtime demo still exits nonzero with `Unsupported presenter language: es`.
- `voices` still lists only English, Chinese, and Japanese.

## Diagnostics Guard Alternative

If Cycle 118 chooses the diagnostics guard instead, make it a focused diagnostics-index invariant, not a package-content change.

Exact production change:

- In `src/ai_presenter/runtime/diagnostics.py`, add a helper such as `_diagnose_qa_prompt_index(material_package)`.
- Compute `expected_count` directly from package Q&A text: one canonical `question` plus every nonblank localized question for each item.
- Compare it with `len(material_package.qa_question_candidates)`.
- Return `OK` when they match, for example: `84 Q&A question prompts indexed from package Q&A text`.
- Return `FAIL` when they differ, for example: `indexed 0 Q&A question prompts; expected 84 from package Q&A text`.
- Append this check in `_diagnose_material_package()` before duplicate Q&A diagnostics so stale prompt indexing fails visibly.

Exact tests:

- `tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_prompt_index_ok_for_ringcentral_package`
  - Load RingCentral package and assert the new check is `OK` with `84`.
- `tests/unit/test_diagnostics.py::test_diagnostics_fails_when_qa_prompt_index_drifts`
  - Build or mutate a small package so `_qa_question_candidates = ()`, then assert the new check is `FAIL`.
- `tests/unit/test_cli.py::test_doctor_loads_profile_package_and_flow`
  - Assert the doctor output includes the new `[OK] qa prompt index:` line.

## Risks

- The Spanish demo texts are safety-sensitive. Preserve the English source boundaries around private chat, participant names, meeting links, recordings, transcripts, captions, post-meeting artifacts, destructive leave/end actions, and state-changing media controls.
- Do not let a report-complete Spanish package imply runtime Spanish support. Runtime promotion is a separate slice.
- Adding Spanish aliases while adding narration would widen route-matching risk. Keep aliases unchanged.
- Large YAML edits can create encoding churn. Use UTF-8 and avoid unrelated formatting changes.
- `.coverage` is already modified in the worktree and remains out of scope.

## Verification Observed During Scan

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es
```

Observed: exit `0`; `0/51` demo steps, `12/12` localized questions, `12/12` localized answers, `1/27` Spanish alias entrypoints with `3` aliases.

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
```

Observed: exit `1`; same counts plus `Localization coverage incomplete for es.`

```powershell
.\.venv\Scripts\ai-presenter.exe demo --profile ringcentral-video --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
```

Observed: exit `1` in this shell invocation; CLI rejected Spanish with `Unsupported presenter language: es`.

```powershell
.\.venv\Scripts\python.exe -m pytest -q -o addopts="" tests\unit\test_material_packages.py tests\unit\test_cli.py::test_localization_report_outputs_spanish_report_only_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_spanish_report_only_qa tests\unit\test_cli.py::test_demo_rejects_unknown_language_before_runtime tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package
```

Observed: `93 passed`.
