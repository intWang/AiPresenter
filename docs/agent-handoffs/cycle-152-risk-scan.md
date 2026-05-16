# Cycle 152 Risk Scan: Empathetic Tone Alias Boundary

Date: 2026-05-17
Cycle: 152
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Scope

Documentation-only risk scan for a future tone-alias expansion, especially
`empathetic -> support`.

No source, tests, README, packages, profiles, existing docs, generated
artifacts, or `.coverage` files should be changed for this scan.

Read basis:

- `docs/agent-handoffs/cycle-151-risk-scan.md`
- `docs/agent-handoffs/cycle-151-technical-scan.md`
- `docs/agent-handoffs/cycle-151-technical-development.md`
- `src/ai_presenter/runtime/voice.py`
- `tests/unit/test_voice.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_questions.py` tone-invariant RingCentral routing coverage

## Risk Summary

The safe product meaning of `empathetic` is narrow: it can normalize user input
to the existing canonical `support` tone. It should not create a new canonical
tone, label, provider route, runtime language, RingCentral behavior, privacy
policy, clinical safety posture, or support-quality guarantee.

The risky word is "empathetic." It can sound like the system has emotional
judgment, clinical suitability, or improved customer-support outcomes. The code
surface does not prove those things. The existing `support` tone is a presenter
style that uses the current support description and rendering path. It is not a
promise that the product can sense distress, deliver crisis support, make better
support decisions, or satisfy a privacy/compliance review.

Keep the success story modest: alias normalization and catalog discoverability
only.

## Boundary Model

- Tone aliases normalize input to an existing canonical tone.
- Canonical tones may influence presenter instruction text or simple rendering
  prefixes.
- Profile/provider compatibility stays controlled by profile speech settings
  and voice validation.
- Runtime language support stays controlled by language normalization,
  provider routing, and diagnostics.
- RingCentral action routing, `can_operate`, question interrupts, and privacy
  handling stay controlled by package policy and safety routing.
- Live RingCentral acceptance requires a dated manual or automated acceptance
  record; tone aliases do not create that evidence.
- Emotional safety, clinical safety, and support quality are not validated by
  alias tests.

## No-Go Claims

Do not claim or imply:

- `empathetic` is a new presenter tone.
- `empathetic` changes provider compatibility, SAPI readiness, Piper readiness,
  OpenAI availability, or speech quality.
- A tone alias enables a runtime language or makes any profile accept a
  language/provider combination that previously failed.
- A tone alias is live RingCentral Video acceptance.
- A tone alias changes privacy behavior, consent handling, meeting-data access,
  Notes/Transcript handling, recording safety, or chat/participant-name safety.
- `empathetic`, `support`, `supportive`, `calm`, or `reassuring` makes output
  clinically safe, therapeutic, trauma-informed, crisis-ready, or emotionally
  safe.
- `empathetic` improves support quality, reduces escalations, diagnoses user
  problems better, or provides customer-care-grade support.
- Tone selection detects user emotion, adapts to distress, or chooses safer
  actions from emotional context.
- Passing unit tests proves live provider behavior, live RingCentral behavior,
  privacy compliance, clinical suitability, or support effectiveness.

Avoid wording such as `empathetic mode`, `emotionally safe`, `clinically safe`,
`support-ready`, `better support`, `provider-ready`, `privacy-safe by tone`,
`accepted live`, or `validated with RingCentral` unless the sentence names
separate evidence outside the alias change.

## Safe Wording

Preferred wording:

- "The `empathetic` alias normalizes to the existing canonical `support` tone."
- "This is an input and catalog discoverability change."
- "The alias reuses existing `support` tone behavior."
- "Provider compatibility remains profile, language, and speech-provider
  specific."
- "Runtime language support is unchanged."
- "RingCentral privacy and action routing remain tone-invariant."
- "This change does not certify emotional safety, clinical suitability, support
  quality, provider readiness, or live RingCentral acceptance."

Use narrow verbs such as `normalizes`, `lists`, `maps`, `reuses`, and
`preserves`. Reserve `supports`, `ready`, `accepted`, `validated`, and `safe`
for sentences that identify the exact evidence and the surface being proven.

## Test-Risk Guidance

Safe test additions for a future alias-only implementation:

- Add a normalization assertion that `PresenterVoiceSettings(tone="empathetic")`
  canonicalizes to `support`.
- Extend the public `support` alias tuple assertion to include `empathetic`.
- Extend the `voices` catalog assertion to show `empathetic` through shared
  runtime metadata.
- If question routing is touched, include `empathetic` in a focused
  tone-invariant RingCentral routing check and assert the same entrypoint,
  `can_operate`, and interrupt behavior as `support` or `professional`.
- If controller labels are touched, assert the label remains `Support`, not a
  new `Empathetic` canonical option.

No-go test patterns:

- Do not add provider compatibility tests that pass because of a tone alias.
- Do not relax language/profile rejection tests because of a tone alias.
- Do not add live RingCentral automation, screenshots, provider calls, SAPI
  inspection, Piper downloads, or acceptance evidence to prove an alias.
- Do not assert human-quality claims such as more empathetic, calmer, safer,
  therapeutic, or better support.
- Do not snapshot broad CLI or README wording in a way that pressures future
  docs to overclaim alias behavior.
- Do not treat `support` tone output as evidence of privacy or clinical safety.

The best failing-test shape is small and mechanical: normalization, public
alias metadata, CLI catalog visibility, and optional tone-invariant routing if
that surface is edited.

## Go/No-Go

Go for an alias-only implementation that maps `empathetic` to `support`, keeps
`Support` as the canonical label, preserves existing provider and runtime
language gates, and avoids user-facing claims beyond input normalization.

No-go if the work introduces a new canonical tone, changes profile/provider
compatibility, changes runtime language support, changes RingCentral action or
privacy routing, updates live acceptance evidence, touches `.coverage`, or
claims emotional safety, clinical safety, or better support quality.

Recommended risk level for the alias-only slice is low to medium. The code
change is small, but wording and tests must keep the boundaries explicit.
