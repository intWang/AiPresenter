# Cycle 195 Technical Scan: Canonical Executive Tone

Date: 2026-05-17

## Existing State

Tone surfaces are centralized in `src/ai_presenter/runtime/voice.py`:

- `PresenterTone`
- `PRESENTER_TONE_CHOICES`
- `_TONE_DESCRIPTIONS`
- `_TONE_LABELS`
- `_TONE_ALIASES`
- `render_presenter_text()`
- `_render_chinese()`

Before this cycle, `_TONE_ALIASES["executive"]` normalized to `formal`. CLI catalog and controller
menus consume the shared choices, so making `executive` canonical in `voice.py` propagates through
the UI.

## Implementation Strategy

- Add `executive` to the canonical tone literal and choices.
- Give it a distinct description and label.
- Move `briefing` and `boardroom` aliases to `executive`; keep `structured` as `formal`.
- Add an English prefix and Chinese dynamic-text prefix.
- Add phrase-level `executive tone` presenter-meta recognition only; avoid bare `executive`,
  `briefing`, or `boardroom` in routing.
- Extend RingCentralVideo route-parity coverage to include `executive`.

## Risk Notes

- Tone must remain style-only: it cannot change route, `can_operate`, question policy, Q&A
  matching, or interrupt creation.
- Do not add package YAML aliases for presenter expression requests.
- Chinese local SAPI rate should stay default `0` for executive.
