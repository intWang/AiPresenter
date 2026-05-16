# Cycle 153 Risk Scan: Tone-Invariant RingCentral Question Routing

Date: 2026-05-17
Cycle: 153
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Scope

Documentation-only risk scan for claims around tone-invariant RingCentral
question routing, especially assertions that compare question routing results
across presenter tones.

No source, tests, README, packages, profiles, existing docs, generated
artifacts, or `.coverage` files should be changed for this scan.

Relevant current unit-test shape:

- Use a fixed RingCentral package fixture.
- Resolve each covered question with a baseline tone.
- Resolve the same question with additional tones.
- Assert the same `entrypoint_id`, `can_operate`, and interrupt-step presence.

## Risk Summary

Tone-invariant routing is a narrow deterministic claim. It can show that, for
the covered prompt strings and package fixture, presenter tone does not change
the selected RingCentral entrypoint, operation gate, or interrupt creation
decision.

That does not prove live RingCentral acceptance, privacy safety, provider
behavior, or semantic AI understanding. It also does not prove that the product
understands the user's intent. The covered path is package question routing,
authored Q&A precedence, policy gates, and interrupt construction. Provider
speech, live app state, current RingCentral build behavior, meeting privacy,
and natural-language understanding remain separate evidence surfaces.

The highest wording risk is compressing "same route across tones" into
"privacy-safe," "accepted," "provider-stable," or "understands sensitive
questions." Keep the success story mechanical: same route, same operation
permission, same interrupt decision for the prompts under test.

## No-Go Claims

Do not claim or imply:

- Tone-invariant unit tests are live RingCentral Video acceptance.
- Tone-invariant routing proves RingCentral locators, menus, windows, or
  cleanup behavior work in the current live app.
- `can_operate=False` proves privacy safety, privacy compliance, consent
  handling, or safe handling of meeting messages, participant names,
  transcripts, notes, recordings, or shared content.
- `can_operate=True` proves a live RingCentral action is safe to perform in a
  real meeting.
- The `privacy`, `support`, `careful`, `empathetic`, or any other tone makes
  answers privacy-safe, clinically safe, emotionally safe, or compliance-ready.
- Presenter tone changes provider behavior, OpenAI behavior, SAPI behavior,
  Piper behavior, speech quality, virtual microphone routing, or audio
  acceptance.
- The routing code semantically understands user intent, privacy requests,
  participant data, transcripts, recording risk, or destructive action risk.
- Passing tone-invariant tests proves robust natural-language understanding,
  multilingual semantic matching, prompt-injection resistance, or broad
  paraphrase coverage.
- Authored Q&A precedence means the product can reason about privacy beyond the
  configured package content and policy gates.
- A tone alias such as `empathetic -> support` expands RingCentral routing,
  provider compatibility, privacy behavior, or live acceptance evidence.

Avoid wording such as `privacy-safe routing`, `RingCentral-accepted`, `provider
validated`, `AI understands the question`, `semantic safety`, `safe in live
meetings`, or `empathetic privacy handling` unless the sentence names separate,
dated evidence for that exact surface.

## Safe Wording

Preferred wording:

- "For the covered prompts, RingCentral question routing is tone-invariant."
- "The test asserts the same `entrypoint_id`, `can_operate`, and interrupt-step
  presence across the selected tones."
- "This is package question-routing evidence, not live RingCentral acceptance."
- "Privacy-sensitive prompts remain governed by authored Q&A, `questionPolicy`,
  `_can_operate`, and interrupt construction."
- "Presenter tone may affect answer style, but it should not change the route
  or operation gate for these prompts."
- "Provider output, speech routing, virtual microphone behavior, live UI
  locators, and RingCentral acceptance are out of scope."
- "The test compares deterministic routing outcomes; it does not prove semantic
  AI understanding."
- "The `empathetic` alias, if included, should be described as reusing the
  canonical `support` tone and preserving the same routing outcome."

Use narrow verbs such as `compares`, `preserves`, `routes`, `matches`,
`gates`, and `constructs`. Reserve `safe`, `accepted`, `validated`,
`understands`, and `supports` for surfaces with explicit evidence.

## Test-Risk Guidance

Safe test patterns:

- Keep the prompt table small, explicit, and mixed across privacy-sensitive,
  risky-action, location-only, and currently operable examples.
- Assert the baseline expected `entrypoint_id`, `can_operate`, and interrupt
  presence before comparing additional tones.
- Compare each non-baseline tone back to the baseline result instead of
  duplicating broad expectations in every branch.
- Include tone aliases only after they already canonicalize through
  `PresenterVoiceSettings`; the routing test should not become an alias
  normalization test.
- If `empathetic` is added to the tone loop, assert only that it preserves the
  same routing surface as `support`, not that it improves support quality or
  privacy handling.
- Keep provider calls, live automation, screenshots, acceptance markdown, and
  `.coverage` out of the routing test slice.
- Re-run focused question-routing tests when touching package Q&A,
  `questionAliases`, `questionPolicy`, `_can_operate`, `answer_question`,
  `create_question_interrupt_step`, controller question submission, or tone
  normalization.

No-go test patterns:

- Do not name tests or assertions as proving `privacy safety`, `semantic
  understanding`, `live acceptance`, or `provider stability`.
- Do not assert broad answer text snapshots that pressure future wording into
  privacy or support-quality claims.
- Do not add live RingCentral automation to prove a unit routing invariant.
- Do not add provider, speech, virtual microphone, SAPI, Piper, or OpenAI calls
  to prove tone-invariant routing.
- Do not relax `can_operate` expectations for sensitive actions because a tone
  sounds careful, supportive, private, or empathetic.
- Do not treat Q&A-first matching as proof that the model understands all
  privacy paraphrases.
- Do not update acceptance evidence records unless a separate live/manual
  acceptance task actually runs and records dated evidence.

The best test names should say what is mechanically proven, for example:
`test_ringcentral_sensitive_prompt_routing_is_tone_invariant`. Avoid names like
`test_privacy_questions_are_safe_for_all_tones` or
`test_ai_understands_sensitive_ringcentral_questions`.

## Go/No-Go

Go for wording and tests that present tone-invariant RingCentral question
routing as deterministic unit evidence: same covered prompt, same package
fixture, same selected entrypoint, same `can_operate`, and same interrupt-step
decision across tones.

No-go if the change or handoff implies live RingCentral acceptance, privacy
safety, provider behavior, virtual microphone readiness, semantic AI
understanding, robust paraphrase coverage, or better support quality.

Recommended risk level is medium. The routing assertion is small and valuable,
but the surrounding language sits close to privacy, live-app acceptance,
provider behavior, and AI-understanding claims that must remain explicitly out
of scope.
