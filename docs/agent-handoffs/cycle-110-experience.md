# Cycle 110 Experience Handoff: Cross-Tone Route Parity

Date: 2026-05-16
Scope: documentation/experience capture only. This file is the only file edited by this handoff.

## Decision Record

Cycle 110 should be treated as a test-only route-parity guard, not a RingCentral Video package or runtime behavior change.

- Keep presenter tone as a style layer. Tone may change generated wording, prefixes, labels, and pacing, but not route matching, operation eligibility, package policy, or interrupt-step creation.
- Compare a `professional` baseline against higher-risk tone surfaces, especially `support` and the user-facing `privacy` alias for canonical `careful`.
- Use existing RingCentral Video prompts only. Do not add package YAML aliases, Q&A entries, routes, localization strings, demo flows, or production policy branches to make the matrix pass.
- Assert route and operation invariants: `entrypoint_id`, `can_operate`, and whether `create_question_interrupt_step(...)` returns a step. If a step exists, its target route and operation should stay aligned with the baseline.
- Do not assert full `answer_text` equality across tones. Tone-specific copy is allowed, but it must not invent private meeting data or imply that sensitive operations were performed.
- Include both blocked sensitive prompts and at least one operable positive sentinel so the guard cannot pass by making every route non-operable.

The key product lesson from Cycle 109 carries forward: `careful` and aliases such as `privacy` are wording choices, not safety-policy engines.

## Reusable Route-Parity Checklist

Use this checklist whenever tone, voice metadata, route matching, or question policy changes near sensitive routes.

1. Choose one baseline tone, normally `professional`.
2. Compare selected tones that are most likely to affect wording pressure: `support`, `careful` or `privacy`, and optionally `friendly` and `coach`.
3. Include representative blocked routes: recording, transcripts/notes content, meeting info, invite, screen share, participant privacy, chat or participant content, and leave/end meeting.
4. Include at least one allowed route such as `network quality` or another safe discovery/control prompt.
5. For each row, record the expected baseline `entrypoint_id`, `can_operate`, and interrupt presence in the table so baseline drift is visible.
6. Compare every non-baseline tone to the baseline route tuple, not to copied prose.
7. Treat `privacy` as an alias smoke for `careful`; do not multiply every alias across every prompt unless alias normalization itself is under test.
8. Keep localized authored Q&A separate from dynamic English tone rendering. For localized rows, protect authored safety copy and avoid English prefix expectations.
9. Keep the matrix compact enough that future maintainers can read every prompt and understand why it is there.

## Safety Notes

- Tone must not influence `questionPolicy`, `_can_operate(...)`, Q&A-first matching, risky-word gates, or interrupt creation.
- `privacy`, `safety`, `guarded`, and `compliance` wording aliases must not imply that AiPresenter verified legal compliance, consent, meeting roles, or visible context.
- Avoid answer assertions that bless tone prefixes such as `Safety note.` as route behavior. Prefix coverage belongs in voice rendering tests.
- Sensitive RingCentral Video prompts should not fabricate meeting IDs, links, host names, dial-in numbers, participant names, chat text, transcript content, notes content, recording state, or shared-screen content.
- Be careful with `concise`: if added later, it must preserve the only consent/privacy boundary in an answer.
- Do not infer safety from `can_operate=False` alone. Also assert no interrupt step, because interrupts are the user-visible operation path.
- Respect the dirty worktree. Cycle 110 handoff docs and `tests/unit/test_questions.py` may already contain work from other agents; do not revert or rewrite unrelated edits.

## Verification Checklist

For an implementation cycle, use the repo venv and keep coverage disabled for focused checks when avoiding `.coverage` churn.

```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit\test_questions.py::test_ringcentral_sensitive_prompt_routing_is_tone_invariant -q -o addopts=""
```

Recommended related cluster:

```powershell
.\.venv\Scripts\python.exe -m pytest `
  tests\unit\test_questions.py::test_ringcentral_careful_tone_preserves_privacy_question_route `
  tests\unit\test_questions.py::test_ringcentral_sensitive_prompt_routing_is_tone_invariant `
  tests\unit\test_questions.py::test_meeting_info_privacy_questions_are_answer_only `
  tests\unit\test_questions.py::test_notes_privacy_gate_does_not_depend_on_risky_words `
  -q -o addopts=""
```

Before closing the cycle, confirm:

- The diff is test-only for implementation, plus handoff docs.
- No production routing, voice, package YAML, localization, demo-flow, or diagnostics behavior changed.
- The matrix covers `professional`, `support`, and `privacy` at minimum.
- Each row asserts expected baseline route, expected baseline `can_operate`, and expected interrupt presence.
- Sensitive prompts remain blocked with no interrupt step.
- The positive sentinel remains operable and creates an interrupt across compared tones.
- Full answer text is not snapshotted across tones.
- Any localized authored-answer sentinel avoids English prefix requirements.

## Next-Cycle Opportunities

- Tighten the current matrix, if needed, so expected `can_operate` and expected interrupt presence live in the parameter table alongside expected route.
- Decide whether Cycle 111 should broaden from selected tones to all canonical tones, while keeping aliases limited to one or two smoke rows.
- Add a localized authored-answer sentinel only if an existing Chinese or Japanese safety prompt can be reused without package changes.
- Add a small helper that returns a route tuple only if the matrix expands enough to justify it.
- Audit `concise` against privacy/safety answers where truncation could remove the consent or visible-context boundary.
- Consider a maintainer note near voice metadata or question tests that states the invariant directly: tone renders style after route and eligibility are decided.
