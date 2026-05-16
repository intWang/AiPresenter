# Cycle 109 Experience Handoff: Careful Presenter Tone

Date: 2026-05-16
Scope: documentation/experience capture only. This file is the only file edited by this handoff.

## Decision Record

Cycle 109 should treat `careful` as a small presenter tone expansion, not a RingCentral Video package change.

- Add one canonical tone: `careful`.
- Normalize `privacy`, `safety`, `safe`, `guarded`, and `compliance` to `careful`.
- Keep `careful` visible in shared tone choices as `Careful`.
- Keep tone as a rendering hint: it may shape prefixes, voice instructions, labels, and speech pacing, but it must not change package facts, route matching, operation eligibility, or safety policy.
- Prefer short, boundary-first phrasing such as `Safety note.` over broad rewrites.
- Preserve authored RingCentral Video content, localized Q&A, demo flow shape, package routes, alias counts, and localization counts.

The product reason is practical: presenters need calmer privacy/safety-aware language around recording, transcript, notes, invite links, meeting info, participant names, chat, shared-screen content, and host/security controls. `careful` fills the gap between `formal` polish and `support` recovery without claiming legal or regulatory compliance.

## Reusable Tone-Expansion Checklist

Use this pattern for any future canonical tone.

1. Define the canonical tone in the shared voice type surface.
2. Add it to `PRESENTER_TONE_CHOICES` only if it should be visible in CLI/controller UI.
3. Add one label, one description, and a complete alias group in the central voice metadata.
4. Make aliases normalize through `PresenterVoiceSettings`; do not duplicate accepted strings in CLI or controller code.
5. Update `render_voice_instruction(...)` through the shared description path.
6. Add deterministic rendering only where it is already safe: English prefix behavior and, if needed, Chinese localized prefix behavior.
7. Keep Japanese and package-authored localized narration free of English prefixes.
8. Review `sapi_rate_for_voice(...)` deliberately for the new canonical tone and assert the expected rate.
9. Let CLI catalog output and controller labels consume shared metadata instead of adding one-off branches.
10. Add focused tests for normalization, aliases, descriptions, instruction text, rendered English/Chinese output, CLI catalog, controller label, unknown-tone rejection, and regression coverage for existing tones.

Alias-only additions should still go through the central alias table and tests. Do not add a second canonical tone when an alias to an existing tone would express the user intent.

## Safety Notes

- Tone must never influence `can_operate`, `questionPolicy`, Q&A-first matching, interrupt-step creation, cleanup behavior, or provider validation.
- Do not prepend casual reassurance such as `Sure`, `Happy to help`, or `Let's walk through it` before privacy boundaries, refusals, recording guidance, transcript/notes answers, chat/participant answers, invite links, meeting info, shared-screen content, or leave/end controls.
- `privacy`, `safety`, and `compliance` are wording aliases, not claims that AiPresenter has verified policy, consent, or legal compliance.
- Localized RingCentral privacy/safety answers should remain exact authored copy unless a separate package-localization task explicitly approves changes.
- `concise` remains a special risk: do not let first-sentence trimming remove the only consent, privacy, or explain-only boundary in a safety answer.
- Logs may record the canonical tone, but should not start capturing raw private prompt text or private answer content because of tone work.
- Treat package YAML changes as out of scope for this slice. If package content changes, rerun localization and package count checks as a separate review.

## Verification Checklist

Focused implementation verification:

```powershell
.\.venv\Scripts\python.exe -m pytest --no-cov -q tests\unit\test_voice.py tests\unit\test_cli.py::test_voices_lists_language_tone_choices tests\unit\test_controller.py::test_render_voice_label_uses_controller_labels
```

Static checks for the narrow tone slice:

```powershell
.\.venv\Scripts\ruff.exe check --no-cache src\ai_presenter\runtime\voice.py tests\unit\test_voice.py tests\unit\test_cli.py tests\unit\test_controller.py
.\.venv\Scripts\mypy.exe --no-incremental src\ai_presenter\runtime\voice.py tests\unit\test_voice.py tests\unit\test_cli.py tests\unit\test_controller.py
```

Before closing a tone cycle, confirm:

- `PresenterVoiceSettings(tone="careful").tone == "careful"`.
- `privacy`, `safety`, `safe`, `guarded`, and `compliance` normalize to `careful`.
- `ai-presenter voices` lists `Careful aliases:` and remains readable in a Windows console.
- Controller/status labels render `English / Careful`, `Chinese / Careful`, and `Japanese / Careful` when selected.
- English careful rendering uses a short safety prefix without rewriting facts.
- Chinese careful rendering uses localized phrasing and does not emit `Safety note`.
- Japanese/localized package text does not receive English prefixes.
- Chinese SAPI rate for `careful` is explicit, preferably neutral `0` unless product listening review chooses otherwise.
- Unknown tones still fail before runtime.
- RingCentral Video package YAML, Q&A count, package aliases, localization coverage, route eligibility, and diagnostic behavior are unchanged.
- Recording, notes/transcript, meeting info, invite, share, chat, participant, shared-screen, and leave/end prompts route the same way across `professional`, `support`, and `careful`.

## Next-Cycle Opportunities

- Add route-parity regression tests that run sensitive RingCentral prompts across all tones and prove `entrypoint_id`, `can_operate`, and interrupt behavior do not drift.
- Revisit alias-only coaching terms such as `guided`, `guide`, `trainer`, `training`, and `walkthrough` as mappings to `coach`, without adding another visible tone unless demand is clear.
- Build a small tone/language golden matrix for EN/ZH/JA privacy answers so future tone work can be reviewed by examples instead of only metadata assertions.
- Audit `concise` against safety copy and add a sentinel test where the second sentence carries the consent or verified-context boundary.
- Decide whether `compliance` should stay as a public alias after wording review, or whether it should be hidden/deferred to avoid implying policy validation.
- Consider future `technical` or `executive` tones only after collecting real demo scripts; keep them separate from privacy/safety tone work.
- Add a short maintainer note near the voice metadata explaining that tone is style-only and package/runtime gates own safety.
