# Cycle 153 Demand Analysis: Tone Alias Question-Routing Invariance

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Decision

Recommendation: add a focused RingCentral Video regression guard proving tone
aliases remain question-routing invariant.

This is the next smallest user-valuable slice after adding `empathetic ->
support`. It is better than adding another alias because the public tone
vocabulary has just expanded, and the immediate product risk is not that users
lack one more word. The risk is that aliases such as `empathetic`, `calm`,
`supportive`, or `privacy` might later be treated as behavior modes that change
which RingCentral Video control is matched, whether AiPresenter may operate it,
or whether a question creates an interrupt step.

This is also better than editing product copy. Copy changes could make a useful
alias sound like a broader support promise, and RingCentral Video copy already
has separate safety, localization, and acceptance boundaries. A routing guard
protects actual user behavior without changing product claims.

## User Value

Users ask RingCentral Video questions while the presenter is running: where to
find participants, whether it can read messages, how to invite people, how to
share, how to leave, or how to handle recording and transcripts safely. Those
questions must route by product intent and safety policy, not by presenter tone.

The value of the guard is practical trust:

- If an operator chooses `empathetic`, `calm`, or another support-family alias,
  safe answer-only questions stay answer-only.
- If an operator chooses a privacy/careful alias, operable controls do not
  become blocked merely because the voice is more cautious.
- Interrupt eligibility remains tied to the matched RingCentral Video
  entrypoint and its policy, not to tone wording.
- Future tone-alias additions have a clear place to prove they do not alter
  RingCentral Video question behavior.

The user-visible outcome is stable presenter behavior: tone affects how the
answer is spoken, while routing still decides what the question means and
whether it can safely open a control.

## Recommended Minimum Scope

Make this a test-only guard.

Expected implementation footprint:

- `tests/unit/test_questions.py`

Recommended shape:

1. Extend the existing
   `test_ringcentral_sensitive_prompt_routing_is_tone_invariant` coverage or
   add a neighboring test with the same RingCentral Video question matrix.
2. Compare each alias tone against the established baseline for
   `entrypoint_id`, `can_operate`, and interrupt creation via
   `create_question_interrupt_step`.
3. Include the newly added `empathetic` alias and enough neighboring aliases to
   make the intent clear:
   - support-family aliases: `supportive`, `helpdesk`, `troubleshooting`,
     `recovery`, `calm`, `steady`, `reassuring`, `empathetic`
   - careful-family aliases: `safety`, `safe`, `privacy`, `guarded`,
     `compliance`
   - at least one non-sensitive style alias such as `warm`, `mentor`, or
     `structured`
4. Do not compare full answer text. Tone rendering is allowed to change wording
   and prefixes; this guard is only about routing, operability, and interrupt
   eligibility.

No runtime implementation should be required if tone aliases continue to
normalize through `PresenterVoiceSettings` before the question router sees
them. A newly added test may pass immediately; that is acceptable for this
regression slice.

## Do Not Touch

- Do not edit `.coverage`.
- Do not revert or clean up other workers' edits.
- Do not edit source files.
- Do not edit packages, profiles, README, existing docs, or product copy.
- Do not add another tone alias in this cycle.
- Do not add a new canonical tone or split canonical `support`.
- Do not change RingCentral Video entrypoints, Q&A, localized strings,
  question policies, open steps, or acceptance evidence.
- Do not change provider routing, speech output, SAPI/Piper/OpenAI behavior,
  language support, or local voice assets.
- Do not assert answer-text equality for tone aliases.
- Do not claim live RingCentral Video acceptance or improved support quality
  from this guard.

## Acceptance Criteria

The next implementation slice is complete only when these contracts hold:

- RingCentral Video sensitive prompt routing is invariant for canonical tones
  and representative aliases, including `empathetic`.
- For each guarded question and alias, `entrypoint_id` matches the professional
  baseline.
- For each guarded question and alias, `can_operate` matches the professional
  baseline.
- For each guarded question and alias,
  `create_question_interrupt_step(package, response) is not None` matches the
  professional baseline.
- The test explicitly covers answer-only prompts such as recording,
  transcript/message privacy, invite, share, and leave.
- The test explicitly covers operable prompts such as participants and network
  quality.
- The test does not require identical answer text across tones.
- The implementation diff is limited to `tests/unit/test_questions.py`.
- Focused tests pass:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py -k "tone_invariant"
```

- Diff hygiene passes:

```powershell
git diff --check -- tests\unit\test_questions.py
git status --short
```

The final status may still show pre-existing `.coverage` changes from another
worker, but this cycle must not modify or stage them.

## Implementation Handoff Prompt

```text
Cycle153 implementation task. You are not alone in the repo; do not revert
other workers' edits and do not touch `.coverage`.

Repository: C:\Users\rcadmin\Documents\Repos\AiPresenter

Goal: add the smallest useful post-`empathetic -> support` guard by proving
RingCentral Video question routing remains invariant across tone aliases.

Read first:
- docs/agent-handoffs/cycle-153-demand-analysis.md
- tests/unit/test_questions.py around
  `test_ringcentral_sensitive_prompt_routing_is_tone_invariant`
- src/ai_presenter/runtime/voice.py only to confirm current public aliases
- src/ai_presenter/runtime/questions.py only to understand the routing surface
- src/ai_presenter/runtime/session.py around `create_question_interrupt_step`

Scope:
- Test-only change.
- Prefer extending the existing RingCentral Video tone-invariance test or adding
  a neighboring test with the same question matrix.
- Include `empathetic` and representative aliases from the support, careful,
  friendly, coach, and formal families.
- Assert only routing-relevant fields:
  `entrypoint_id`, `can_operate`, and whether `create_question_interrupt_step`
  returns a step.
- Keep answer text out of the invariant assertion because tone may affect
  rendering.

Do not:
- Edit source, packages, profiles, README, existing docs, product copy, or
  `.coverage`.
- Add another alias, canonical tone, provider route, speech behavior, package
  Q&A, localized string, or RingCentral Video acceptance claim.
- Force a red implementation change if the new guard passes immediately; this
  is a regression guard for behavior that should already be true.

Acceptance:
- Run:
  `$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py -k "tone_invariant"`
- Run:
  `git diff --check -- tests\unit\test_questions.py`
- Confirm the final diff is limited to `tests/unit/test_questions.py` and does
  not include `.coverage`.
```
