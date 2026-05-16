# Cycle 119 Technical Scan: Spanish Meeting Basics Wedge

Scope: technical scan only. This handoff is the only file changed by this subagent. Do not stage or commit from this scan.

## Current Baseline

Observed on 2026-05-16:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es
```

Spanish package coverage is:

- `vbg-blur-demo`: `4/4`
- `meeting-basics-demo`: `0/3`, missing `show-mic`, `show-participants`, `show-chat`
- `meeting-controls-tour`: `0/22`
- `meeting-control-map-demo`: `0/22`
- total demo narration: `4/51`
- Q&A questions: `12/12`
- Q&A answers: `12/12`
- aliases: `questionAliases.es present on 1/27 entrypoints (3 aliases)`

`--require-complete` exits `1` for Spanish because demo narration remains partial. Runtime Spanish is still unsupported:

```powershell
.\.venv\Scripts\ai-presenter.exe demo --profile ringcentral-video --package ringcentral-video --flow meeting-basics-demo --language es --dry-run
```

Observed: exit `1`, `Unsupported presenter language: es`.

## Candidate Surface Scan

### Spanish `meeting-basics-demo` narration

Exact package surface:

- `packages/ringcentral-video.yaml`
  - `meeting-basics-demo` -> `show-mic`
  - `meeting-basics-demo` -> `show-participants`
  - `meeting-basics-demo` -> `show-chat`

The three steps already have English, Japanese, and Chinese narration. They are low-complexity controls:

- `show-mic`: points to `ringcentral.video.toolbar.audio`; no panel state.
- `show-participants`: opens `ringcentral.video.toolbar.participants`; should not read participant names or private attendee details.
- `show-chat`: opens `ringcentral.video.toolbar.chat`; should preserve the existing privacy boundary that chat content is private unless explicitly requested.

Exact test surface:

- `tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_spanish_vbg_demo_wedge`
- `tests/unit/test_material_packages.py::test_ringcentral_spanish_qas_and_vbg_demo_are_localized`
- `tests/unit/test_cli.py::test_localization_report_outputs_spanish_vbg_demo_wedge`
- `tests/unit/test_cli.py::test_localization_report_require_complete_fails_for_spanish_vbg_demo_wedge`

### Diagnostics localization/runtime confusion guard

Exact production surface:

- `src/ai_presenter/runtime/diagnostics.py`
  - `diagnose_configuration(...)`
  - `_diagnose_required_localization(...)`
  - `_diagnose_voice(...)`
- `src/ai_presenter/cli.py`
  - `doctor(...)` parses runtime voice settings before diagnostics.
- `src/ai_presenter/runtime/voice.py`
  - `PresenterVoiceSettings` supports only `en`, `zh`, and `ja`.

This guard is useful, but it needs careful CLI design because `doctor --language es` currently fails before it can report localization status. A direct diagnostics unit test can pass `localization_language="es"` without a voice, but CLI behavior is a separate contract.

### Package/question index performance

Exact production surface:

- `src/ai_presenter/packages/models.py`
  - `MaterialPackage.validate_entrypoint_references`
  - `_build_qa_question_candidates`
  - `_build_qa_questions_by_normalized`
  - `_sort_entrypoint_question_aliases_by_match_order`
  - `_build_entrypoint_match_candidates`
- `src/ai_presenter/runtime/questions.py`
  - `_match_qa`
  - `_match_entrypoint`
  - `_match_package_entrypoint_alias`
- `src/ai_presenter/runtime/diagnostics.py`
  - `_diagnose_qa_questions`
  - `_diagnose_qa_alias_overlaps`
  - `_diagnose_qa_alias_substring_risks`

Relevant existing tests include `tests/unit/test_questions.py::test_exact_qa_match_uses_precomputed_question_index` and `tests/unit/test_questions.py::test_exact_qa_match_uses_trimmed_index_before_entrypoint_alias_fallback`. This is a broader source-code optimization slice and should use structural parity tests, not timing-only tests.

### Repo-local playbook/skill candidate docs

Exact doc surface:

- `docs/knowledge/ai-presenter-maintenance.md`

The playbook already distinguishes runtime presenter skills, material packages, durable knowledge, runbooks, cycle handoffs, Codex home skills, localization wedges, runtime performance hygiene, and skill candidates. Improvements here would be docs-only and safe, but lower product value than advancing the Spanish coverage wedge.

## Recommendation

Recommend the smallest safe Cycle 119 implementation slice: add Spanish narration for `meeting-basics-demo` only.

Why this slice:

- It directly advances the post-Cycle-118 Spanish localization path from `4/51` to `7/51`.
- It changes one package file and only focused localization-report tests.
- It avoids the higher-risk `meeting-controls-tour` and `meeting-control-map-demo` surfaces with recording, notes, meeting info, leave/end, and broader panel cleanup implications.
- It preserves the important distinction between package localization and runtime language support.

## File Map

Change:

- `packages/ringcentral-video.yaml`
  - Add `narration.localizedText.es` for:
    - `meeting-basics-demo` -> `show-mic`
    - `meeting-basics-demo` -> `show-participants`
    - `meeting-basics-demo` -> `show-chat`
  - Preserve literal UI labels: `Participants`, `Chat`, and any existing English control labels.
  - Do not add Spanish aliases, Q&A, routes, open steps, action offsets, cleanup behavior, presenter skills, provider config, or voice/runtime support.

Update tests:

- `tests/unit/test_material_packages.py`
  - Update Spanish report totals from `4/51` to `7/51`.
  - Update `meeting-basics-demo.localized_steps` from `0` to `3`.
  - Assert `meeting-basics-demo.missing_step_ids == ()`.
  - Keep `meeting-controls-tour` and `meeting-control-map-demo` at `0`.
  - Update the Spanish localized-demo step list test so it expects VBG plus the three basics steps.
  - Add text guard assertions for `Participants` and `Chat`, plus a privacy assertion that the chat line does not imply reading chat contents.
- `tests/unit/test_cli.py`
  - Update Spanish localization-report expectations from `4/51` to `7/51`.
  - Update `meeting-basics-demo: 0/3` to `meeting-basics-demo: 3/3`.
  - Keep `--require-complete` exit code `1` and the incomplete message.

No expected changes:

- `src/ai_presenter/runtime/voice.py`
- `src/ai_presenter/runtime/diagnostics.py`
- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/packages/models.py`
- `docs/knowledge/ai-presenter-maintenance.md`

## TDD Plan

Red first:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_spanish_vbg_demo_wedge tests\unit\test_material_packages.py::test_ringcentral_spanish_qas_and_vbg_demo_are_localized tests\unit\test_cli.py::test_localization_report_outputs_spanish_vbg_demo_wedge tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_spanish_vbg_demo_wedge
```

Expected red after updating tests but before YAML edits:

- Spanish total still reports `4/51`, not `7/51`.
- `meeting-basics-demo` still reports `0/3`, not `3/3`.
- Spanish localized demo step list still contains only the four `vbg-blur-demo` steps.

Green after package edits:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_spanish_vbg_demo_wedge tests\unit\test_material_packages.py::test_ringcentral_spanish_qas_and_vbg_demo_are_localized tests\unit\test_cli.py::test_localization_report_outputs_spanish_vbg_demo_wedge tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_spanish_vbg_demo_wedge tests\unit\test_cli.py::test_demo_rejects_unknown_language_before_runtime
```

Focused CLI verification:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe demo --profile ringcentral-video --package ringcentral-video --flow meeting-basics-demo --language es --dry-run
```

Diff hygiene:

```powershell
git diff --check -- packages\ringcentral-video.yaml tests\unit\test_material_packages.py tests\unit\test_cli.py
git status --short
```

## Expected Behavior After Slice

Spanish localization report should show:

- `vbg-blur-demo: 4/4 narration localized`
- `meeting-basics-demo: 3/3 narration localized`
- `meeting-controls-tour: 0/22 narration localized`
- `meeting-control-map-demo: 0/22 narration localized`
- `Localization report: 7/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for es.`
- `questionAliases.es present on 1/27 entrypoints (3 aliases)`

Spanish `--require-complete` should still exit `1` because 44 demo steps remain untranslated.

Doctor/localization behavior:

- Direct diagnostics with `require_localization=True, localization_language="es"` should still report `FAIL` and `required es localization incomplete: 7/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers`.
- Do not add `doctor --language es` CLI support in this slice; runtime language parsing should still reject Spanish.

Runtime behavior:

- `demo --language es --dry-run` should still exit nonzero with `Unsupported presenter language: es`.
- `voices` should still list only the currently supported runtime language families.

## Explicit Non-Goals

- Do not add Spanish runtime voice support.
- Do not add Spanish aliases beyond the existing background aliases.
- Do not translate `meeting-controls-tour` or `meeting-control-map-demo`.
- Do not change Q&A, route matching, package indexes, diagnostics guard behavior, presenter skills, or repo-local playbook docs in this slice.
- Do not claim live RingCentral acceptance.
