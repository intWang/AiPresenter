# Cycle 121 Technical Scan: Diagnostics Index Guard

Scope: technical scan only. This handoff is the only file changed by this subagent. Do not stage or commit.

## Current Baseline

Confirmed from current code and focused commands:

- Spanish package report is `7/51` demo steps, `12/12` Q&A questions, `12/12` Q&A answers, and `questionAliases.es` on `1/27` entrypoints with `3` aliases.
- Spanish demo coverage is only `vbg-blur-demo 4/4` and `meeting-basics-demo 3/3`; both `meeting-controls-tour` and `meeting-control-map-demo` remain `0/22`.
- Runtime Spanish remains unsupported. `doctor --require-localization --localization-language es` reaches diagnostics, reports incomplete Spanish package localization, and fails `runtime language support`.
- Existing RingCentral diagnostics currently report `90` package-owned aliases, `84` Q&A question prompts, `84` Q&A alias-overlap prompts, and `11` Q&A alias-substring risks.

Focused verification run:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --localization-language es
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_cli.py::test_doctor_require_localization_accepts_package_only_spanish_language
```

Result: localization report exited `0`, doctor exited `1` for the expected Spanish localization/runtime failures, and pytest reported `3 passed`.

## Candidate Surface Scan

### Next Spanish narration wedge

Exact package surface:

- `packages/ringcentral-video.yaml`
  - `meeting-controls-tour`: 22 missing Spanish narration steps, including meeting info, network quality, report issue, invite, participants, chat, microphone, share, recording, notes, settings, and leave.
  - `meeting-control-map-demo`: 22 missing Spanish narration steps with the same broad control families plus summary.

Exact tests:

- `tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_spanish_short_demo_wedges`
- `tests/unit/test_cli.py` Spanish localization-report tests around `7/51`, `meeting-controls-tour: 0/22`, and `meeting-control-map-demo: 0/22`
- `tests/unit/test_questions.py::test_ringcentral_spanish_safety_questions_match_qas_without_runtime_spanish`

Assessment: valid but not the smallest safe Cycle 121 slice. The next Spanish wedge must translate one of the large 22-step flows and review safety-sensitive narration around recording, notes/transcripts, invite links, chat, participants, and leave/end. Runtime Spanish must remain unsupported.

### Performance/index guard

Exact production surface:

- `src/ai_presenter/runtime/diagnostics.py`
  - `_diagnose_material_package(...)`
  - `_diagnose_question_aliases(...)`
  - `_diagnose_qa_questions(...)`
  - `_diagnose_qa_alias_overlaps(...)`
  - `_diagnose_qa_alias_substring_risks(...)`
  - `_qa_question_language(...)`
- `src/ai_presenter/packages/models.py`
  - `MaterialPackage.entrypoint_question_aliases`
  - `MaterialPackage.qa_question_candidates`
  - `MaterialPackage.qa_questions_by_normalized`
  - `MaterialPackage.entrypoint_question_aliases_by_match_order`

Exact tests:

- `tests/unit/test_diagnostics.py`
  - RingCentral OK/INFO count tests for aliases, Q&A questions, alias overlap, and substring risk.
  - Duplicate alias and duplicate Q&A tests.
  - Exact alias-overlap, substring-risk, related-entrypoint allowance, exact-overlap exclusion, and non-ASCII escaping tests.
- `tests/unit/test_cli.py::test_doctor_loads_profile_package_and_flow` for user-visible doctor output preservation if needed.

Assessment: recommended. Package model indexes already exist; the remaining small performance slice is a private diagnostics index built once per material-package diagnostic pass and reused by the four alias/Q&A checks.

### Diagnostics/report usability polish

Exact surface:

- `src/ai_presenter/cli.py`
  - `doctor(...)`
  - `localization_report(...)`
- `src/ai_presenter/packages/localization_status.py`
  - `build_localization_status(...)`
  - `render_localization_status_lines(...)`
- `src/ai_presenter/runtime/diagnostics.py`
  - `_diagnose_required_localization(...)`
  - `_diagnose_runtime_language_support(...)`

Assessment: lower priority immediately after Cycle 120. The new `--localization-language` guard already handles the main Spanish/report usability gap.

### Docs/playbook/skill candidate

Exact surface:

- `docs/knowledge/ai-presenter-maintenance.md`
- `presenter/skills/*.md`
- `src/ai_presenter/presenter/skills/*.md`
- `tests/unit/test_presenter_skill_packaging.py`

Assessment: docs-only changes are safe but lower product value. Do not create or edit active presenter skills for Cycle 121; that changes prompt context and requires packaged-skill parity.

## Recommendation

Implement the performance/index guard in `src/ai_presenter/runtime/diagnostics.py`.

Smallest safe file map:

- Modify `src/ai_presenter/runtime/diagnostics.py`
  - Add a private frozen dataclass, for example `_PackageDiagnosticsIndex`.
  - Build it once inside `_diagnose_material_package(...)`.
  - Include:
    - `aliases_by_normalized: dict[str, list[EntrypointQuestionAlias]]`
    - `aliases_by_language: dict[str, list[EntrypointQuestionAlias]]`
    - `qa_candidates_by_normalized: dict[str, list[QuestionAnswerMatchCandidate]]`
    - `qa_candidates_by_normalized_and_item: dict[tuple[str, int], list[QuestionAnswerMatchCandidate]]`
  - Pass the index into `_diagnose_question_aliases`, `_diagnose_qa_questions`, `_diagnose_qa_alias_overlaps`, and `_diagnose_qa_alias_substring_risks`.
  - Preserve diagnostic names, order, statuses, and detail strings.
- Modify `tests/unit/test_diagnostics.py`
  - Add index structure/usage tests and keep existing behavior tests unchanged.

No expected changes:

- `packages/ringcentral-video.yaml`
- `src/ai_presenter/packages/models.py`
- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/cli.py`
- `src/ai_presenter/packages/localization_status.py`
- presenter skills, profiles, README, or knowledge docs

## Measurable Target

Use structural performance proof, not a brittle wall-clock gate:

- `_diagnose_material_package(...)` builds `_PackageDiagnosticsIndex` exactly once per call.
- `_diagnose_qa_alias_substring_risks(...)` scans only `index.aliases_by_language[question_language]`, not all `material_package.entrypoint_question_aliases`, for each Q&A candidate.
- For a synthetic package with many unrelated-language aliases and one English Q&A prompt, the substring-risk diagnostic must ignore unrelated-language aliases structurally and produce the same `OK` detail.
- Optional same-machine timing evidence: 200 in-process `diagnose_configuration(...)` calls for RingCentral should be no slower than the pre-change baseline; record before/after numbers in the implementation handoff only, not as a unit-test assertion.

Suggested structural parity tests:

- `test_package_diagnostics_index_groups_aliases_and_qa_candidates`
  - Build a small package with English and Japanese aliases plus localized Q&A.
  - Call a private `_build_package_diagnostics_index(package)`.
  - Assert grouping by normalized alias, language, normalized question, and `(normalized_question, id(item))`.
- `test_diagnostics_substring_risk_uses_language_scoped_alias_index`
  - Build English Q&A containing `chat`.
  - Add a Japanese-only alias with normalized English-looking text if needed, plus an English unrelated alias.
  - Assert only same-language aliases can produce substring risk and the existing detail text is preserved.
- Keep existing RingCentral parity tests unchanged:
  - `test_diagnostics_reports_question_aliases_ok_for_ringcentral_package`
  - `test_diagnostics_reports_qa_questions_ok_for_ringcentral_package`
  - `test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package`
  - `test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package`

## TDD Plan

Red first:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_package_diagnostics_index_groups_aliases_and_qa_candidates tests\unit\test_diagnostics.py::test_diagnostics_substring_risk_uses_language_scoped_alias_index
```

Expected red:

- Missing `_build_package_diagnostics_index(...)` or equivalent helper.
- Missing language-scoped substring-risk behavior test target.

Green implementation:

1. Add the private index dataclass and builder.
2. Thread the index through the four diagnostics helpers.
3. Change substring-risk alias lookup from package-wide iteration to the language-scoped index list.
4. Keep formatter helpers and conflict ordering unchanged.

Green focused command:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_package_diagnostics_index_groups_aliases_and_qa_candidates tests\unit\test_diagnostics.py::test_diagnostics_substring_risk_uses_language_scoped_alias_index tests\unit\test_diagnostics.py::test_diagnostics_reports_question_aliases_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package
```

Broader focused regression:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow tests\unit\test_cli.py::test_doctor_require_localization_accepts_package_only_spanish_language
```

Manual CLI checks:

```powershell
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --localization-language es
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es
```

Optional timing probe:

```powershell
@'
from pathlib import Path
from time import perf_counter
from ai_presenter.config.loader import load_profile
from ai_presenter.packages.loader import load_material_package
from ai_presenter.runtime.diagnostics import diagnose_configuration

profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))
package = load_material_package(Path("packages/ringcentral-video.yaml"))
start = perf_counter()
for _ in range(200):
    diagnose_configuration(profile=profile, material_package=package, flow_id="meeting-control-map-demo")
print(round((perf_counter() - start) * 1000, 3))
'@ | .\.venv\Scripts\python.exe -
```

Diff hygiene:

```powershell
git diff --check -- src\ai_presenter\runtime\diagnostics.py tests\unit\test_diagnostics.py
git status --short
```

## If Spanish Is Chosen Instead

Do not combine it with the performance slice. The smallest Spanish-only fallback is one complete 22-step flow, preferably `meeting-control-map-demo` because it is explanatory and map-like rather than the primary live action tour.

Required flow/steps:

- Add `narration.localizedText.es` for all `meeting-control-map-demo` steps:
  - `control-map-overview`
  - `control-map-meeting-info`
  - `control-map-network`
  - `control-map-views`
  - `control-map-report`
  - `control-map-add-coworkers`
  - `control-map-participants`
  - `control-map-chat`
  - `control-map-microphone`
  - `control-map-audio-menu`
  - `control-map-camera`
  - `control-map-camera-menu`
  - `control-map-share`
  - `control-map-reactions`
  - `control-map-raise-hand`
  - `control-map-more`
  - `control-map-recording`
  - `control-map-notes`
  - `control-map-background`
  - `control-map-settings`
  - `control-map-leave`
  - `control-map-summary`

Spanish test updates would change totals from `7/51` to `29/51`, set `meeting-control-map-demo` to `22/22`, keep `meeting-controls-tour` at `0/22`, keep Q&A `12/12`, keep aliases `1/27`, and keep runtime Spanish unsupported.

## Non-Goals

- Do not add Spanish runtime support.
- Do not change package YAML in the recommended performance slice.
- Do not change route ordering, Q&A-first behavior, `questionPolicy`, `can_operate`, or interrupt creation.
- Do not change diagnostic wording or doctor output except for any unavoidable internal performance evidence in implementation notes.
- Do not add process-global caches, file-mtime caches, or raw question/answer memoization.
- Do not stage `.coverage`.
