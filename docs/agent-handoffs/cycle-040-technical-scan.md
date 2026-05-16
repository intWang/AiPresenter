# Cycle 040 Technical Scan

Date: 2026-05-16
Role: technical scan
Scope: read-only technical scan. No files were edited by the technical agent.

## Recommendation

Add a provider-agnostic tone expansion. The technical scan suggested `calm`; Cycle 040 will use canonical `support` and include `calm`, `steady`, and `reassuring` as aliases so the UX is both domain-specific and low-risk.

## Files

- Modify: `src/ai_presenter/runtime/voice.py`
- Modify: `tests/unit/test_voice.py`
- Modify: `tests/unit/test_cli.py`
- Modify: `tests/unit/test_controller.py`
- Add Cycle 040 handoff, spec, plan, review, and summary docs.

## Implementation Sketch

- Extend `PresenterTone` with `support`.
- Add `("Support", "support")` to `PRESENTER_TONE_CHOICES`.
- Add `_TONE_DESCRIPTIONS`, `_TONE_LABELS`, and `_TONE_ALIASES` entries.
- Add English dynamic text prefix in `render_presenter_text()`.
- Add Chinese SAPI rate mapping for support to a calm practical rate.
- Do not change provider routing or asset checks.

## Verification

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py tests\unit\test_cli.py::test_voices_lists_language_tone_choices tests\unit\test_controller.py::test_render_voice_label_uses_controller_labels
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\runtime\voice.py tests\unit\test_voice.py tests\unit\test_cli.py tests\unit\test_controller.py
.\.venv\Scripts\mypy --no-incremental src\ai_presenter\runtime\voice.py tests\unit\test_voice.py tests\unit\test_cli.py tests\unit\test_controller.py
```

