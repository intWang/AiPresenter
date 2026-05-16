# Cycle 130 Technical Scan: Spanish Q&A Runtime Copy

Date: 2026-05-16
Cycle: 130
Scope: documentation-only technical scan. This scan writes only
`docs/agent-handoffs/cycle-130-technical-scan.md`.

## Summary

Cycle129 proved Spanish OpenAI runtime wiring, but the remaining Q&A quality
boundary is runtime answer copy. Package-owned Spanish Q&A answers are already
used when a prompt matches a `qa` item. Entrypoint-generated answers now use a
Spanish `questionAliases.es` label for Spanish voices when one exists, but they
still append the English `OperationEntrypoint.purpose`. The controller
Spanish question test is currently behind that behavior: it expects English
`Participants` while runtime now returns `panel de participantes: Open
participant list and meeting people controls.`

This should be handled as a small source/test alignment slice. Do not edit
`packages/ringcentral-video.yaml` unless the cycle explicitly expands into
entrypoint title/purpose localization fields.

## Current Worktree Context

Observed before writing this handoff:

- `.coverage` is modified; treat it as generated and do not stage unless the
  owner explicitly asks.
- `src/ai_presenter/runtime/questions.py` and `tests/unit/test_questions.py`
  already contain in-flight changes by another worker.
- `docs/agent-handoffs/cycle-130-demand-analysis.md` and
  `docs/agent-handoffs/cycle-130-risk-scan.md` are untracked and should be
  preserved.

Do not revert any of those.

## Code Findings

- `src/ai_presenter/runtime/questions.py::answer_question` logs language/tone
  and delegates to `_answer_question`.
- `src/ai_presenter/runtime/questions.py::_answer_question` routes in this
  order: Q&A match, entrypoint match, no-match fallback.
- `src/ai_presenter/runtime/questions.py::_qa_answer_text` already prefers
  `QuestionAnswer.localized_answers[voice.language]` when present and nonblank.
- `src/ai_presenter/runtime/questions.py::_render_entrypoint_answer` now calls
  `_entrypoint_answer_label(entrypoint, voice)` and appends
  `entrypoint.purpose`.
- `src/ai_presenter/runtime/questions.py::_entrypoint_answer_label` uses the
  first nonblank `entrypoint.question_aliases["es"]` for Spanish voices;
  otherwise it falls back to `entrypoint.title`.
- `src/ai_presenter/runtime/questions.py::_NO_MATCH_ANSWERS` includes Spanish:
  `No encontre un control que coincida en el contexto activo de la app.`
- `src/ai_presenter/packages/models.py::QuestionAnswer` supports
  `localizedQuestions` and `localizedAnswers`; `OperationEntrypoint` does not
  support localized title or purpose fields.
- `src/ai_presenter/packages/models.py::_qa_questions` indexes all localized
  questions across languages, so Spanish Q&A prompts can match even when tests
  use `PresenterVoiceSettings(language="en")`.
- `src/ai_presenter/runtime/controller.py::PresenterController.submit_question`
  passes the current `PresenterVoiceSettings` into `answer_question`, builds a
  `question-answer-demo` interrupt when `can_operate` is true, and forwards the
  same voice into the runner.

## Test Findings

- `tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_complete_spanish_package`
  expects Spanish package localization complete: 51/51 demo steps, 12/12 Q&A
  questions, 12/12 Q&A answers, 26/27 entrypoints with aliases, 69 aliases.
- `tests/unit/test_material_packages.py::test_ringcentral_spanish_qas_and_demo_flows_are_localized`
  checks all Spanish Q&A questions/answers are present and all expected Spanish
  demo narration steps exist.
- `tests/unit/test_material_packages.py::test_ringcentral_package_owns_spanish_aliases_for_location_routes`
  asserts curated Spanish entrypoint aliases, including
  `panel de participantes`.
- `tests/unit/test_questions.py::test_ringcentral_spanish_location_questions_match_package_aliases_without_legacy_table`
  exercises Spanish aliases with the legacy alias table disabled, but currently
  uses English voice settings; it proves matching, not Spanish answer copy.
- `tests/unit/test_questions.py::test_spanish_entrypoint_answer_uses_package_alias_label`
  proves Spanish voice output starts with `panel de participantes:` and not
  `Participants panel:`.
- `tests/unit/test_questions.py::test_spanish_no_match_fallback_is_localized_and_not_operable`
  proves Spanish no-match fallback is not English.
- `tests/unit/test_controller.py::test_presenter_controller_starts_spanish_openai_question_demo_when_idle`
  currently fails against the in-flight entrypoint-label behavior because it
  asserts `"Participants" in result.answer_text`.

Focused command run during this scan:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_spanish_entrypoint_answer_uses_package_alias_label tests\unit\test_questions.py::test_spanish_no_match_fallback_is_localized_and_not_operable tests\unit\test_controller.py::test_presenter_controller_starts_spanish_openai_question_demo_when_idle
```

Observed result: `2 passed, 1 failed`. Failure:

```text
assert 'Participants' in 'panel de participantes: Open participant list and meeting people controls.'
```

Direct runtime probe also showed:

- `panel de participantes` with Spanish voice returns
  `panel de participantes: Open participant list and meeting people controls.`
- Spanish chat/participants privacy Q&A returns the Spanish
  `localizedAnswers.es` text.
- `quantum waffle` with Spanish voice returns the Spanish no-match fallback.

## Quality Gap

There are two distinct Spanish answer paths:

- Q&A path: good enough for package-owned safety/support questions because it
  uses `localizedAnswers.es`.
- Entrypoint path: partial Spanish. The label can be Spanish via
  `questionAliases.es`, but purpose remains English because the package model
  only has `OperationEntrypoint.purpose`.

This means controller Spanish questions against safe controls can start a demo
with a Spanish label and English purpose. That is acceptable as a minimal
runtime fallback if documented and tested honestly, but it should not be called
fully localized entrypoint copy.

## Minimal Safe Implementation Options

Recommended narrow option:

- Keep the in-flight source behavior in
  `src/ai_presenter/runtime/questions.py::_entrypoint_answer_label`.
- Update `tests/unit/test_controller.py::test_presenter_controller_starts_spanish_openai_question_demo_when_idle`
  to assert the actual Spanish alias label, for example
  `assert result.answer_text.startswith("panel de participantes:")`.
- Add `assert "Participants panel:" not in result.answer_text`.
- Keep the runner/voice assertions unchanged so the test continues to prove
  `question-answer-demo` and `PresenterVoiceSettings(language="es")`.
- Do not edit package YAML.

Optional copy-polish option:

- Update only `src/ai_presenter/runtime/questions.py::_NO_MATCH_ANSWERS["es"]`
  from `No encontre ...` to accented Spanish if the team accepts non-ASCII
  source copy.
- Update `tests/unit/test_questions.py::test_spanish_no_match_fallback_is_localized_and_not_operable`
  to assert the final exact string or a stable accented fragment.
- This is not required for correctness.

Broader option, defer unless explicitly approved:

- Add localized entrypoint title/purpose fields to `OperationEntrypoint`, loader
  tests, localization status accounting, package YAML, diagnostics, and runtime
  answer rendering.
- This is a package schema and content change, not a minimal Cycle130 fix.

## Exact Recommendations

1. In `tests/unit/test_controller.py::test_presenter_controller_starts_spanish_openai_question_demo_when_idle`,
   replace the English copy assertion with Spanish alias-label expectations:

```python
assert result.answer_text.startswith("panel de participantes:")
assert "Participants panel:" not in result.answer_text
```

2. In `tests/unit/test_questions.py::test_spanish_entrypoint_answer_uses_package_alias_label`,
   keep the current assertions. This is the focused unit proof for
   `_entrypoint_answer_label`.

3. Add a small fallback test only if reviewers want explicit title fallback
   coverage:

```python
def test_spanish_entrypoint_answer_falls_back_to_title_without_spanish_alias() -> None:
    package = MaterialPackage.model_validate(
        {
            "appId": "demo",
            "appName": "Demo",
            "version": 1,
            "profileIds": ["demo-profile"],
            "operationEntrypoints": [
                {
                    "id": "demo.panel",
                    "title": "Panel",
                    "area": "Main",
                    "purpose": "Open panel.",
                    "openSteps": [],
                }
            ],
            "demoFlows": [],
            "manualControls": [],
        }
    )

    response = answer_question(
        package=package,
        question="panel",
        voice=PresenterVoiceSettings(language="es"),
    )

    assert response.answer_text.startswith("Panel:")
```

4. Do not modify `packages/ringcentral-video.yaml` for the recommended narrow
   option. The existing Spanish aliases and Q&A localized answers are already
   sufficient for this runtime-copy alignment.

## Verification Commands

Focused red/green:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_spanish_entrypoint_answer_uses_package_alias_label tests\unit\test_questions.py::test_spanish_no_match_fallback_is_localized_and_not_operable tests\unit\test_controller.py::test_presenter_controller_starts_spanish_openai_question_demo_when_idle
```

Package localization guardrails:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_package_owns_spanish_aliases_for_location_routes tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_complete_spanish_package tests\unit\test_material_packages.py::test_ringcentral_spanish_qas_and_demo_flows_are_localized
```

Runtime/controller Spanish smoke without live RingCentral:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py::test_voice_validation_allows_spanish_openai_profile tests\unit\test_voice.py::test_voice_validation_rejects_spanish_non_openai_profiles tests\unit\test_runtime_factory.py::test_existing_window_material_demo_uses_injected_openai_registry_for_spanish tests\unit\test_controller_view_model.py::test_spanish_openai_view_model_is_startable_without_local_assets tests\unit\test_cli.py::test_demo_openai_profile_accepts_spanish_dry_run tests\unit\test_cli.py::test_controller_openai_profile_accepts_spanish_dry_run
```

Final hygiene:

```powershell
git diff --check
git status --short
```

Expected final state for the implementation cycle: focused tests pass,
`git diff --check` exits 0, `.coverage` remains unstaged unless explicitly
requested, and package YAML remains untouched for the narrow fix.
