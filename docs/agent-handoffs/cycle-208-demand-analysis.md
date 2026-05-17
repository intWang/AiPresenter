# Cycle 208 Demand Analysis

Date: 2026-05-17
Cycle: 208
Role: Demand analysis subagent

## Recommendation

Do not promote French to a runtime presenter language yet. Add a small
French package-localization seed instead.

## User Value

- Starts measurable French coverage without overpromising live demo readiness.
- Gives future cycles a concrete package-local wedge to expand.
- Preserves the lifecycle contract that package text, runtime voice support,
  provider compatibility, and live acceptance are separate gates.

## Selected Slice

- Seed French text for the small `meeting-basics-demo` flow.
- Seed one background privacy Q&A with French question and answer text.
- Add two French background aliases.
- Keep `PresenterVoiceSettings(language="fr")` unsupported.
- Keep `demo --language fr` and `controller --language fr` rejected before
  runtime starts.

## Non-Goals

- No `fr` runtime language.
- No OpenAI-only French voice promotion.
- No local SAPI/Piper French route.
- No full French RingCentral package localization.
- No live RingCentral acceptance claim.

## Acceptance Criteria

- `localization-report --package ringcentral-video --language fr` reports
  `3/51` demo steps and `1/16` Q&A question/answer coverage.
- `--require-complete` still fails for French.
- Doctor localization diagnostics show French package coverage separately from
  runtime language support.
- Lifecycle docs state that French remains package-only and does not prove
  runtime voice readiness or live acceptance.
