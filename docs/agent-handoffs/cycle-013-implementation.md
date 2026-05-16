# Cycle 013 Voice Discovery Implementation

## Scope

- Implemented `docs/superpowers/plans/2026-05-16-voice-discovery.md`.
- Stayed within the user-approved paths.
- Did not create `cycle-013-review.md` or `cycle-013-summary.md` because the user only allowed creating `cycle-013-implementation.md`.

## Changes

- Added public voice metadata helpers for language aliases, tone aliases, and tone descriptions.
- Added optional voice compatibility checks to diagnostics.
- Added `ai-presenter voices` catalog/profile checks.
- Added `doctor --language` and `doctor --tone` voice preflight checks.
- Documented voice discovery commands in README and the RingCentral manual acceptance runbook.

## TDD Evidence

### Task 1 Voice Helpers

- Red: `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py::test_presenter_language_aliases_are_public_and_canonical tests\unit\test_voice.py::test_presenter_tone_aliases_and_description_are_public`
- Result: 2 failed, both `AttributeError` for missing helper functions.
- Green: same command.
- Result: 2 passed.

### Task 2 Diagnostics Voice Check

- Red: `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_supported_voice tests\unit\test_diagnostics.py::test_diagnostics_reports_unsupported_voice`
- Result: 2 failed, both `TypeError` for unexpected `voice` argument.
- Green: same command.
- Result: 2 passed.

### Task 3 CLI Voices And Doctor Flags

- Red: `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_voices_lists_language_tone_choices tests\unit\test_cli.py::test_voices_profile_reports_supported_and_unsupported_languages tests\unit\test_cli.py::test_voices_targeted_incompatible_profile_voice_exits_nonzero tests\unit\test_cli.py::test_doctor_accepts_language_and_tone_voice_preflight tests\unit\test_cli.py::test_doctor_rejects_unsupported_profile_voice`
- Result: 5 failed with exit-code mismatches because command/options were missing.
- Green: same command.
- Result: 5 passed.

## Verification Evidence

- Focused tests: `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py tests\unit\test_diagnostics.py tests\unit\test_voice.py`
- Result: 56 passed after the coordinator added the Windows console safety regression test.
- Ruff: `.\.venv\Scripts\ruff check --no-cache src\ai_presenter\cli.py src\ai_presenter\runtime\diagnostics.py src\ai_presenter\runtime\voice.py tests\unit\test_cli.py tests\unit\test_diagnostics.py tests\unit\test_voice.py`
- Result: All checks passed.
- Mypy: `.\.venv\Scripts\mypy --no-incremental src\ai_presenter\cli.py src\ai_presenter\runtime\diagnostics.py src\ai_presenter\runtime\voice.py tests\unit\test_cli.py tests\unit\test_diagnostics.py tests\unit\test_voice.py`
- Result: Success, no issues found in 6 source files.
- Full suite: `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests`
- Result: 417 passed, 1 known pywinauto STA warning after the coordinator regression test.

## Coordinator Regression Fix

Manual verification with the real installed script found that `ai-presenter voices` crashed on the
current Windows console when printing the literal `中文` alias:

```powershell
.\.venv\Scripts\ai-presenter voices --profile ringcentral-video-bind-speaker --language zh-CN --tone friendly
```

Root cause: `typer.echo()` wrote non-ASCII alias text to a cp1252 console. The internal alias remains
supported, but CLI catalog output now renders non-ASCII aliases with ASCII `\u....` escapes.

Additional red/green evidence:

- RED: `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_voices_catalog_output_is_ascii_safe_for_legacy_windows_console`
  - Result: failed because `voices` output contained non-ASCII alias text.
- GREEN: same command
  - Result: passed, `1 passed`.
- Manual script check:
  - Supported route exited 0 and printed `\u4e2d\u6587`.
  - Unsupported fake profile exited 1 and printed the expected profile/provider/voice message.

## Review Notes

- Independent review is expected from the coordinator after this implementation handoff.
- The shared worktree had pre-existing dirty changes in several allowed and unrelated files. This implementation preserved them and only added scoped changes.
