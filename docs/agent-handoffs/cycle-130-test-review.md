# Cycle 130 Test Review

Date: 2026-05-16
Scope: review of the current uncommitted Cycle130 diff and handoffs only. This
review wrote only this file.

## Reviewed Diff

- `src/ai_presenter/runtime/questions.py`
- `tests/unit/test_questions.py`
- `tests/unit/test_controller.py`
- Cycle130 handoffs:
  - `cycle-130-demand-analysis.md`
  - `cycle-130-risk-scan.md`
  - `cycle-130-technical-scan.md`
  - `cycle-130-implementation.md`

Current diff does not modify `packages/`, profiles, or package YAML. `.coverage`
is modified in the working tree and should remain treated as generated noise.

## Commands And Results

```powershell
git status --short
```

Result: source/test diff plus generated `.coverage`; Cycle130 handoffs are
untracked.

```powershell
git diff --name-only
```

Result: `.coverage`, `src/ai_presenter/runtime/questions.py`,
`tests/unit/test_controller.py`, `tests/unit/test_questions.py`.

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_spanish_entrypoint_answer_uses_package_alias_label tests\unit\test_questions.py::test_spanish_no_match_fallback_is_localized_and_not_operable tests\unit\test_controller.py::test_presenter_controller_starts_spanish_openai_question_demo_when_idle
```

Result: `3 passed in 3.06s`.

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_package_owns_spanish_aliases_for_location_routes tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_complete_spanish_package tests\unit\test_material_packages.py::test_ringcentral_spanish_qas_and_demo_flows_are_localized tests\unit\test_questions.py::test_ringcentral_chinese_questions_match_package_aliases_without_legacy_table tests\unit\test_questions.py::test_ringcentral_japanese_meeting_control_questions_match_package_aliases_without_legacy_table
```

Result: `5 passed in 1.37s`.

```powershell
git diff -- packages profiles src\ai_presenter\packages --stat
```

Result: no output; no package/profile/model YAML diff observed.

```powershell
git diff --check
```

Result: exit 0; line-ending warnings only for touched Python files.

## Findings

Post-review hardening was applied in the main session after this review: the
final diff adds explicit English, Chinese, and Japanese label-preservation tests
and a controller-level negative assertion that `Participants panel:` is absent
from the Spanish answer. The final verification bundle reported `838 passed`,
`ruff` clean, and `mypy` clean.

### P2: Spanish-only behavior was implemented but initially not directly regression-tested

`_entrypoint_answer_label()` is correctly gated to `voice.language == "es"` in
`src/ai_presenter/runtime/questions.py`, which fixes the earlier broad
non-English direction in source. However, the new tests only assert the Spanish
positive path. They do not pin English, Chinese, or Japanese entrypoint label
behavior to the existing title-based output after alias matching.

This matters because a future or revived broad helper like
`if voice.language != "en"` could pass much of the current multilingual routing
suite: those tests mostly assert entrypoint IDs, safety flags, or broad answer
fragments, not the exact title-vs-alias label boundary. Add focused regression
coverage for at least one EN, one ZH, and one JA entrypoint answer showing the
label remains title-based/non-Spanish-specific.

Resolved after review by
`tests/unit/test_questions.py::test_non_spanish_entrypoint_answers_keep_canonical_title_label`.

### P3: Controller Spanish assertion initially lacked the old English title negative check

`tests/unit/test_controller.py` now asserts
`result.answer_text.startswith("panel de participantes:")`, which aligns the
controller path with the Spanish alias label behavior. The implementation
handoff recommended also asserting that `"Participants panel:"` is absent, but
the controller test does not include that negative assertion.

The unit-level question test has the negative assertion, so this is not a
functional blocker. Adding it to the controller test would better preserve the
original regression point at the controller boundary.

Resolved after review by adding `assert "Participants panel:" not in
result.answer_text` to the controller Spanish OpenAI question test.

## No Findings

- The source helper is Spanish-only and falls back to `entrypoint.title` for
  non-Spanish voices.
- The controller still forwards `PresenterVoiceSettings(language="es")` and
  starts only the `question-answer-demo` path for the safe participants match.
- No package YAML, profile, or package model edits are present in the current
  diff.
- The handoffs avoid claiming live Spanish acceptance. The implementation
  handoff's verification claims are unit/static claims only; this review did
  not rely on unrerun full-suite claims as live evidence.

## Residual Risks

- Entrypoint purpose text remains English by design:
  `panel de participantes: Open participant list and meeting people controls.`
  This is acceptable only as a partial Spanish fallback, not full localized
  Spanish Q&A output.
- Spanish no-match copy remains unaccented (`No encontre...`) and the test now
  locks that text. This is a copy-quality residual, not a regression from the
  alias-label patch.
- `.coverage` is modified and should not be staged for this cycle unless the
  owner explicitly asks.
- I ran focused tests and guardrails, not the full suite, ruff, or mypy.

## Go / No-Go

Go. Follow-up test hardening has been applied, the implementation is narrow, the
full final suite passed, and package YAML/live acceptance boundaries are
preserved.
