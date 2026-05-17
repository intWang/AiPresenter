# Cycle 178 Technical Development Handoff

Date: 2026-05-17

## Files Changed

- `packages/ringcentral-video.yaml`
- `src/ai_presenter/runtime/questions.py`
- `tests/unit/test_questions.py`
- `tests/unit/test_controller.py`
- `tests/unit/test_controller_session.py`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_diagnostics.py`
- `docs/knowledge/ringcentral-video/observation-log.md`
- `docs/knowledge/ringcentral-video/runtime-safety-routing.md`
- `docs/knowledge/ringcentral-video/source-index.md`
- `docs/agent-handoffs/cycle-178-*.md`

`.coverage` is modified by local test runs and must stay out of the commit.

## Behavior Added

- English Chat panel aliases now live on `ringcentral.video.toolbar.chat`: `open chat`, `show chat`, `where is chat`, `chat button`.
- Mixed presenter-meta plus safe Chat prompts, such as `Please be brief and open chat`, route to Chat with `can_operate=True` and do not fall back to `Presenter settings:`.
- Mixed presenter-meta plus sensitive meeting-info prompts, such as `Please be brief and read meeting information aloud`, remain answer-only with `can_operate=False`.
- Chat-content prompts such as `Open chat messages` and `Please be brief and show chat messages` now hit the Chat/Participants privacy Q&A before Chat panel aliases can create an interrupt.
- Controller coverage now proves safe mixed prompts start `question-answer-demo` when idle and queue an interrupt while another demo is running.
- Controller/session coverage now proves sensitive mixed prompts stay text-only, create no interrupt, do not stop the running demo, and do not start `question-answer-demo`.
- Diagnostics, CLI, and docs now expect `169` package-owned aliases.

## Implementation Notes

- Production runtime change is limited to `src/ai_presenter/runtime/questions.py`.
- Existing routing remains Q&A-first, then presenter-meta detection, then explicit entrypoint matching for meta-prefixed prompts.
- `_match_chat_content_privacy_qa(...)` runs before contained-QA and package-alias guards so broad Chat aliases cannot steal content-reading prompts.
- `create_question_interrupt_step()` remains the operation gate: no entrypoint or `can_operate=False` means no interrupt.
- Material package coverage explicitly asserts the Chat aliases belong to `ringcentral.video.toolbar.chat` and that `ringcentral.develop.video.tab` has no English aliases.
- Durable docs were updated to the 2026-05-17 package shape, including `16` Q&A items, `220` Q&A prompts, `169` package-owned aliases, and English alias coverage of `4/27` entrypoints with `17` aliases.

## Tests To Run

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_controller.py tests\unit\test_controller_session.py tests\unit\test_diagnostics.py::test_diagnostics_reports_question_aliases_ok_for_ringcentral_package tests\unit\test_material_packages.py::test_operation_entrypoints_support_package_owned_question_aliases tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
.\.venv\Scripts\python.exe -B -m ruff check tests\unit\test_questions.py tests\unit\test_controller.py tests\unit\test_controller_session.py tests\unit\test_diagnostics.py tests\unit\test_cli.py tests\unit\test_material_packages.py
.\.venv\Scripts\python.exe -B -m ruff check src\ai_presenter\runtime\questions.py
git diff --check
```

## Risks And Rollback Notes

- Keep `.coverage` out of the commit unless coverage artifact churn is intentional.
- The main risk is alias misplacement: rolling back should remove only the four English aliases from `ringcentral.video.toolbar.chat` and restore alias-count expectations/docs.
- Do not move these aliases to `ringcentral.develop.video.tab`; that recreates the wrong app-shell route.
- Future mixed-meta misses should prefer precise package aliases or titles over broadening fuzzy presenter-meta routing.
- Repo tests are routing/orchestration evidence only, not live RingCentral acceptance.
