# Cycle 182 Test Review

Date: 2026-05-17

## Red-Green Notes

New Spanish plural identity tests initially failed:

- `¿Quiénes están en la reunión?` routed to a post-meeting artifacts privacy answer instead of participant privacy.
- `¿Quiénes están en el panel de participantes?` routed operably to `ringcentral.video.toolbar.participants`.
- `¿Quiénes están en la lista de participantes?` routed operably to `ringcentral.video.toolbar.participants`.
- `Explícame quién está en la lista de participantes` routed operably to `ringcentral.video.toolbar.participants`.

The focused slice passed after adding Spanish plural who-is terms and the normalization contract:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py::test_localized_participant_identity_requests_stay_answer_only tests\unit\test_questions.py::test_participants_panel_location_requests_stay_operable_with_meta tests\unit\test_material_packages.py::test_normalize_question_prompt_strips_latin_accents_but_preserves_punctuation
```

Result: `30 passed`.

## Review Notes

- The tests assert both privacy rejection and safe panel navigation in the same localized matrix.
- `¿Dónde está...` remains a location request and may create an interrupt.
- `¿Quiénes están...` is identity disclosure and must not create an interrupt, even when panel/list words are present.
- `normalize_question_prompt()` strips Latin accents while preserving inverted punctuation.
- `.coverage` remains local generated output and must stay unstaged.

## Pending Verification

Run before commit:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m mypy src tests
```

Final verification results:

- `1166 passed, 1 warning`
- `All checks passed!`
- `Success: no issues found in 81 source files`
- Independent review: no findings; focused review slice `30 passed`.
