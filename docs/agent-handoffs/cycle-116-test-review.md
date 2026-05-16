# Cycle 116 Test Review: Executive Tone Aliases

Date: 2026-05-16
Scope: test-review handoff only. This file is the only file edited by this subagent.

## Findings

No blocking findings.

The current implementation is consistent with the tone-alias slice: `executive`, `briefing`, and `boardroom` normalize to the existing `formal` tone in `src/ai_presenter/runtime/voice.py`. The change stays inside voice normalization and public alias/catalog reporting. I did not see production changes to routes, `questionPolicy`, `can_operate`, interrupt creation, providers, profiles, package YAML, or localization status logic.

Spanish runtime support remains disabled. `PresenterVoiceSettings(language="es")` is still rejected through CLI validation, `voices` still lists runtime languages as English, Chinese, and Japanese only, and `localization-report --language es --require-complete` still fails because Spanish package coverage is incomplete.

Non-blocking coordination note: the Cycle 116 demand handoff recommends Spanish report-only Q&A completion, while the implementation and experience handoffs document that the landed slice is executive-style tone vocabulary. That is acceptable for the reviewed diff, but the cycle summary should name the chosen slice clearly so Spanish package work is not mistaken for completed work.

## Checks Run

- `git status --short`
  - Initial state included dirty out-of-scope `.coverage`, `README.md`, `src/ai_presenter/runtime/voice.py`, `tests/unit/test_cli.py`, `tests/unit/test_voice.py`, and several untracked Cycle 116 handoffs.
- `git diff --stat`
  - Reviewed production/test/doc delta: `.coverage`, `README.md`, `src/ai_presenter/runtime/voice.py`, `tests/unit/test_cli.py`, and `tests/unit/test_voice.py`.
- `git diff --unified=80 -- src/ai_presenter/runtime/voice.py`
  - Confirmed only new tone alias mappings were added.
- `git diff --unified=80 -- tests/unit/test_voice.py`
  - Confirmed alias normalization and public alias tests were added.
- `git diff --unified=80 -- tests/unit/test_cli.py`
  - Confirmed `voices` catalog test now expects `executive`.
- `git diff --unified=80 -- README.md`
  - Confirmed README only adds `executive` to tone-alias examples.
- `Get-Content` review of Cycle 116 implementation, technical scan, demand analysis, risk scan, and experience handoff.
  - Confirmed implementation and experience handoffs explicitly defer runtime Spanish support.
- `rg -n "settings\.tone|\.tone|tone ==|tone in|presenter_tone|can_operate|questionPolicy|safety|route" src\ai_presenter\runtime src\ai_presenter\cli.py tests\unit\test_questions.py tests\unit\test_material_runtime.py tests\unit\test_cli.py tests\unit\test_voice.py`
  - Confirmed tone is consumed by rendering/labels/provider checks, with route and safety behavior owned outside the alias map.
- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py::test_voice_settings_normalize_expanded_tones tests\unit\test_voice.py::test_presenter_tone_aliases_and_description_are_public tests\unit\test_voice.py::test_voice_settings_reject_unknown_language_and_tone tests\unit\test_cli.py::test_voices_lists_language_tone_choices tests\unit\test_cli.py::test_voices_catalog_output_is_ascii_safe_for_legacy_windows_console tests\unit\test_cli.py::test_demo_rejects_unknown_language_before_runtime tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_spanish_seed tests\unit\test_questions.py::test_ringcentral_sensitive_prompt_routing_is_tone_invariant`
  - Result: `16 passed in 3.25s`.
- `.\.venv\Scripts\ai-presenter voices`
  - Result: exit `0`; languages listed English, Chinese, Japanese; Formal aliases listed `formal, structured, executive, briefing, boardroom`; output remained ASCII-safe.
- `.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video --package ringcentral-video --flow meeting-control-map-demo --language en-US --tone executive`
  - Result: exit `0`; `English / Formal supported via speech=fake`; doctor completed `12 ok, 1 info, 0 warnings, 0 failed`.
- `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language es`
  - Result: exit `0`; Spanish remains partial with `0/51` demo steps, `1/12` Q&A questions, `1/12` Q&A answers, and `questionAliases.es` on `1/27` entrypoints with `3 aliases`.
- `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language es --require-complete`
  - Result: expected exit `1`; output ended with `Localization coverage incomplete for es.`
- `.\.venv\Scripts\ai-presenter demo --profile ringcentral-video --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run`
  - Result: expected exit `1`; output reported `Unsupported presenter language: es`.
- Direct routing probe comparing `formal` to `executive`, `briefing`, and `boardroom` for `invite people`, `participants`, `network quality`, `leave meeting`, and `how do I handle meeting recording safely?`
  - Result: all three aliases matched `formal` for `entrypoint_id`, `can_operate`, and question-interrupt creation.
  - Note: the first probe command used positional arguments against keyword-only `answer_question()` and failed with `TypeError`; rerun with keyword arguments passed.
- `git diff --check`
  - Result: passed; Git emitted only existing LF-to-CRLF working-copy warnings for README, voice, and test files.
- `git diff --cached --name-status`
  - Result: no staged files.
- `git status --short .coverage`
  - Result: ` M .coverage`.

## Residual Risk

- The committed test changes prove alias normalization and CLI catalog visibility. Route/safety invariance for the new aliases was verified by a direct review probe, not by a new committed test. Because the implementation only adds aliases to an existing canonical tone, I do not consider this a blocker.
- The handoffs contain two product directions for Cycle 116: Spanish Q&A completion and executive tone aliases. Future coordination should keep Spanish report-only package work separate from runtime language support and from this tone-alias slice.
- No full test suite, mypy, or ruff run was performed; this review stayed focused on the touched files and Spanish/runtime safety boundary requested for the slice.

## Coverage And Staging Status

`.coverage` was modified before this review and remained modified after focused test runs. It is not staged, and I did not delete, reset, or edit it.

Current staging status during this review: `git diff --cached --name-status` returned no files.
