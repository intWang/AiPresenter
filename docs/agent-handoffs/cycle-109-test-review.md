# Cycle 109 Test/Code Review: Careful Presenter Tone

Date: 2026-05-16
Reviewer: Codex
Scope: review current Cycle 109 code/test diff only. No production code or tests were edited by this review.

## Verdict

Approve.

I found no blocking issues in the Cycle 109 implementation. The new canonical `careful` tone is centralized in voice metadata/rendering, and the reviewed diff does not change RingCentral package YAML, Q&A matching, route authorization, `can_operate`, interrupt-step creation, localization counts, or provider validation.

Existing `.coverage` dirtiness was ignored.

## Reviewed Changes

- `src/ai_presenter/runtime/voice.py`
- `tests/unit/test_voice.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_controller.py`
- `tests/unit/test_questions.py`

Context handoffs reviewed:

- `docs/agent-handoffs/cycle-109-demand-analysis.md`
- `docs/agent-handoffs/cycle-109-technical-scan.md`
- `docs/agent-handoffs/cycle-109-risk-scan.md`
- `docs/agent-handoffs/cycle-109-experience.md`

## Findings

No blocking findings.

Key review notes:

- Metadata coverage is complete for the new canonical tone: `PresenterTone`, `PRESENTER_TONE_CHOICES`, `_TONE_DESCRIPTIONS`, `_TONE_LABELS`, and `_TONE_ALIASES` all include `careful` with aliases `safety`, `safe`, `privacy`, `guarded`, and `compliance` (`src/ai_presenter/runtime/voice.py:8`, `src/ai_presenter/runtime/voice.py:23`, `src/ai_presenter/runtime/voice.py:34`, `src/ai_presenter/runtime/voice.py:49`, `src/ai_presenter/runtime/voice.py:76`).
- Rendering remains a hint only: English dynamic text gets `Safety note.`, Chinese dynamic text gets localized careful wording, and localized narration/Q&A paths avoid careful-tone prefixing (`src/ai_presenter/runtime/voice.py:178`, `src/ai_presenter/runtime/voice.py:200`, `src/ai_presenter/runtime/voice.py:248`, `src/ai_presenter/runtime/voice.py:263`; `src/ai_presenter/runtime/questions.py:395`).
- SAPI rate handling is deliberate: `careful` falls through to neutral `0`, with an explicit test assertion (`src/ai_presenter/runtime/voice.py:234`; `tests/unit/test_voice.py:306`).
- CLI/controller label coverage flows through shared metadata and has focused tests for `Careful aliases:` and `English / Careful` (`src/ai_presenter/cli.py:522`; `src/ai_presenter/runtime/controller.py:603`; `src/ai_presenter/runtime/controller_view_model.py:124`; `tests/unit/test_cli.py:841`; `tests/unit/test_controller.py:644`).
- Route parity is preserved by implementation shape: `answer_question(...)` computes Q&A/entrypoint matches and `can_operate` independently of tone, while `create_question_interrupt_step(...)` still gates on `entrypoint_id` and `can_operate` only (`src/ai_presenter/runtime/questions.py:274`, `src/ai_presenter/runtime/questions.py:514`; `src/ai_presenter/runtime/session.py:88`).
- The added RingCentral tests cover careful-tone route parity for a privacy-sensitive English answer and preservation of authored Chinese Q&A text under `privacy` (`tests/unit/test_questions.py:382`, `tests/unit/test_questions.py:478`).

## Test Gaps

- Route parity coverage is focused, not exhaustive. A future guard could run recording, notes/transcript, meeting info, invite, share, chat, participants, shared-screen, and leave/end prompts across `professional`, `support`, and `careful`, asserting identical `entrypoint_id`, `can_operate`, and interrupt behavior.
- Individual `PresenterVoiceSettings(tone="safe")` and `PresenterVoiceSettings(tone="compliance")` assertions are not present, though the public alias tuple test proves those aliases map to `careful`.
- I did not run localization count/package diagnostics because `packages/ringcentral-video.yaml` has no diff. If package YAML changes before merge, rerun localization/package count checks.

## Verification

Commands run:

```powershell
.\.venv\Scripts\python.exe -m pytest --no-cov -q tests\unit\test_voice.py tests\unit\test_cli.py::test_voices_lists_language_tone_choices tests\unit\test_cli.py::test_voices_catalog_output_is_ascii_safe_for_legacy_windows_console tests\unit\test_controller.py::test_render_voice_label_uses_controller_labels tests\unit\test_questions.py::test_ringcentral_careful_tone_preserves_privacy_question_route tests\unit\test_questions.py::test_ringcentral_chinese_safety_qas_keep_authored_text_under_careful_tone tests\unit\test_questions.py::test_ringcentral_localized_caption_translation_questions_are_answer_only
```

Result: `34 passed in 3.37s`.

```powershell
.\.venv\Scripts\ruff.exe check --no-cache src\ai_presenter\runtime\voice.py tests\unit\test_voice.py tests\unit\test_cli.py tests\unit\test_controller.py tests\unit\test_questions.py
```

Result: `All checks passed!`

```powershell
.\.venv\Scripts\mypy.exe --no-incremental src\ai_presenter\runtime\voice.py tests\unit\test_voice.py tests\unit\test_cli.py tests\unit\test_controller.py tests\unit\test_questions.py
```

Result: `Success: no issues found in 5 source files`.

Recommended before merge if time allows:

```powershell
.\.venv\Scripts\python.exe -m pytest --no-cov -q tests\unit\test_voice.py tests\unit\test_cli.py tests\unit\test_controller.py tests\unit\test_questions.py
```

## Commit Readiness

Ready to commit after the implementation owner reviews the residual test-gap notes. Do not include `.coverage` in the commit. The Cycle 109 production/test diff is narrow and consistent with the handoff constraints; this review adds only `docs/agent-handoffs/cycle-109-test-review.md`.
