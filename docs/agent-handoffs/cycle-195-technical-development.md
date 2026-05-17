# Cycle 195 Technical Development: Executive Tone

Date: 2026-05-17

## Files Changed

- `src/ai_presenter/runtime/voice.py`
  - Adds canonical `executive` tone.
  - Adds label, description, aliases, English rendering, and Chinese dynamic prefix.
- `src/ai_presenter/runtime/questions.py`
  - Adds phrase-level `executive tone` presenter-meta recognition.
- `tests/unit/test_voice.py`
  - Guards normalization, aliases, labels, instruction text, rendering, and Chinese SAPI rate.
- `tests/unit/test_cli.py`
  - Guards CLI catalog and alias normalization output.
- `tests/unit/test_controller.py` and `tests/unit/test_controller_view_model.py`
  - Guard controller/operator labels.
- `tests/unit/test_questions.py`
  - Guards presenter-meta answer-only behavior and RingCentralVideo route parity.
- `docs/knowledge/ringcentral-video/runtime-safety-routing.md`
  - Documents executive as style-only and updates route-parity wording.

## Behavior

`--tone executive`, `--tone briefing`, and `--tone boardroom` now render as `Executive`.
English dynamic text starts with `Executive brief.`; Chinese dynamic text uses a short
executive-summary prefix. RingCentralVideo routing remains unchanged.
