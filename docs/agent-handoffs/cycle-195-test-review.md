# Cycle 195 Test Review

Date: 2026-05-17

## RED Verification

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_voice.py::test_voice_settings_normalize_expanded_tones tests\unit\test_voice.py::test_presenter_tone_aliases_and_description_are_public tests\unit\test_voice.py::test_voice_instruction_describes_expanded_tones tests\unit\test_voice.py::test_render_presenter_text_applies_expanded_english_tones tests\unit\test_voice.py::test_sapi_rate_for_voice_maps_chinese_tones_to_practical_rates tests\unit\test_cli.py::test_voices_lists_language_tone_choices tests\unit\test_controller_view_model.py::test_operator_view_model_labels_executive_tone tests\unit\test_questions.py::test_presenter_meta_requests_do_not_route_to_ringcentral_controls tests\unit\test_questions.py::test_presenter_meta_modifiers_do_not_steal_ringcentral_intents tests\unit\test_questions.py::test_ringcentral_sensitive_prompt_routing_is_tone_invariant
```

Result before implementation: `7 failed, 33 passed`. Failures showed `executive` still normalized
to `formal`, CLI lacked `Executive aliases:`, operator labels showed `Formal`, and `Use executive
tone` returned no-match instead of presenter-meta.

## Focused Verification

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_voice.py::test_voice_settings_normalize_expanded_tones tests\unit\test_voice.py::test_presenter_tone_aliases_and_description_are_public tests\unit\test_voice.py::test_voice_instruction_describes_expanded_tones tests\unit\test_voice.py::test_render_presenter_text_applies_expanded_english_tones tests\unit\test_voice.py::test_sapi_rate_for_voice_maps_chinese_tones_to_practical_rates tests\unit\test_cli.py::test_voices_lists_language_tone_choices tests\unit\test_cli.py::test_voices_targeted_executive_alias_reports_canonical_tone tests\unit\test_controller.py::test_render_voice_label_uses_controller_labels tests\unit\test_controller_view_model.py::test_operator_view_model_labels_executive_tone tests\unit\test_questions.py::test_presenter_meta_requests_do_not_route_to_ringcentral_controls tests\unit\test_questions.py::test_presenter_meta_modifiers_do_not_steal_ringcentral_intents tests\unit\test_questions.py::test_ringcentral_sensitive_prompt_routing_is_tone_invariant
```

Result: `42 passed`.

## Required Before Commit

Run full repository verification and cached-diff checks:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m mypy src tests
git diff --cached --check
git diff --cached -- .coverage
git diff --cached --stat
git diff --cached --name-only
```
