# Cycle 188 Test Review

Date: 2026-05-17

## Focused Verification

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_knowledge_docs_preserve_evidence_boundaries tests\unit\test_material_packages.py::test_ringcentral_knowledge_docs_are_registered_in_navigation_indexes tests\unit\test_questions.py::test_ringcentral_chat_content_requests_stay_answer_only tests\unit\test_questions.py::test_ringcentral_english_recording_action_questions_stay_qa_first tests\unit\test_questions.py::test_ringcentral_english_transcript_content_requests_stay_answer_only tests\unit\test_controller.py::test_presenter_controller_keeps_sensitive_mixed_meta_question_text_only_while_running tests\unit\test_controller_session.py::test_session_does_not_create_interrupt_for_notes_question_policy
```

Result: `24 passed`.

## Docs Review

Independent review found no blocking wording issues.

- The examples explicitly say they document existing routing boundaries only.
- The privacy matrix says examples are not new permissions, live acceptance, or locator confidence.
- The evidence index says docs-only examples do not upgrade evidence states.
- The validation checklist says examples are policy guidance only and do not permit private-content capture.

## Required Before Commit

Run:

```powershell
git diff --check
git diff --name-only -- packages profiles src\ai_presenter\profiles pyproject.toml
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m mypy src tests
git diff --cached -- .coverage
```
