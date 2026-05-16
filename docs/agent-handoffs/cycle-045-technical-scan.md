# Cycle 045 Technical Scan

## Current State

`runtime.questions` renders the no-match fallback through `_render_text()`, but the base fallback string is hard-coded in English. `PresenterVoiceSettings.language` is already normalized to `en` or `zh`, so the branch can select localized base text without changing matching behavior.

## Proposed Implementation

- Add a small `_NO_MATCH_ANSWERS` mapping in `src/ai_presenter/runtime/questions.py`.
- Change the no-match branch to render `_NO_MATCH_ANSWERS[voice.language]`.
- Add a unit test for Chinese no-match fallback text.
- Keep existing English no-match tests and behavior.

## TDD Plan

1. Add `test_chinese_no_match_fallback_is_localized_and_not_operable`.
2. Run that single test and observe it fail because the fallback is English.
3. Add the localized fallback mapping.
4. Re-run focused question tests and adjacent voice/controller-view-model tests.

## Risk Notes

Risk is low. The text becomes a visible contract, but entrypoint matching, `can_operate`, package content, and logging privacy all remain unchanged.
