# Cycle 197 Lessons: Tone Docs As Runtime Contract

Date: 2026-05-17

## What Changed

Cycle 197 converted presenter tone behavior from scattered runtime facts into a
durable, tested knowledge matrix. The source of truth remains
`src/ai_presenter/runtime/voice.py`; the doc is a maintainer-facing catalog that
must stay aligned with that source.

## Reusable Prompt Pattern

For future tone or language cycles, ask subagents to answer these separately:

- What user/operator decision becomes easier after the change?
- Which runtime source owns the canonical contract?
- Which docs are durable knowledge versus cycle-local handoffs?
- Which words could accidentally imply routing, privacy policy, or live
  acceptance?
- What narrow test proves the doc has not drifted from source?

## Guardrails To Keep

- Tone aliases such as `privacy`, `safety`, `compliance`, `empathetic`,
  `briefing`, and `boardroom` are style hints only.
- RingCentral route and privacy boundaries stay in the RingCentral safety docs.
- Provider compatibility is not the same as package localization readiness.
- Repo tests are not live RingCentral acceptance evidence.
- `.coverage` stays out of cycle commits unless a future cycle explicitly owns
  that binary artifact.

## Next-Cycle Candidates

- Generate a `voices` command golden check from the same tone contract.
- Add a small language/provider lifecycle matrix that separates runtime
  language support, package localization, provider compatibility, and live
  acceptance evidence.
- Continue mining RingCentral Video state docs for surfaces that need
  answer-only safety boundaries before adding more aliases.
