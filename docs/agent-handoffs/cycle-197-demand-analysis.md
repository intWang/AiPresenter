# Cycle 197 Demand Analysis: Presenter Tone Behavior Matrix

Date: 2026-05-17

## User Need

Cycles 195 and 196 left the right next documentation slice: make tone behavior
durable and source-checkable. `executive` is now a canonical tone, but future
agents still need one compact matrix that separates labels, aliases,
deterministic rendering, Chinese/SAPI behavior, and style-only routing
constraints.

## Operator / Agent Value

- Gives operators a clear catalog of supported presenter tones and aliases.
- Helps agents avoid treating tone as routing, permission, or privacy policy.
- Reduces regressions when adding tones by making current behavior explicit.
- Makes Chinese/SAPI behavior visible, especially tones that affect local rate
  or localized prefixes.
- Keeps handoff notes from becoming the only place tone behavior is explained.

## Chosen Slice

Add a repo-wide durable knowledge doc at
`docs/knowledge/presenter-tone-behavior-matrix.md`.

This belongs under `docs/knowledge/`, not `docs/knowledge/ringcentral-video/`,
because tones are presenter-runtime behavior shared across packages. It may link
to RingCentral runtime safety routing for the style-only invariant.

## Acceptance Criteria

- The doc lists all canonical tones from `src/ai_presenter/runtime/voice.py`:
  `professional`, `conversational`, `concise`, `friendly`, `coach`, `formal`,
  `executive`, `support`, and `careful`.
- Each tone row includes label, aliases, public description, English dynamic
  rendering behavior, Chinese dynamic-text behavior, localized narration
  behavior, and Chinese SAPI rate.
- `executive` is documented as canonical, with `briefing` and `boardroom`
  aliases.
- `support` and `careful` are clearly distinguished: support is
  recovery/helpdesk style; careful is privacy/boundary style.
- Japanese and Spanish localized text only apply `concise` first-sentence
  behavior; other tones do not add English prefixes.
- The doc states tone is style-only and must not affect `entrypoint_id`,
  `can_operate`, `questionPolicy`, Q&A-first matching, interrupt creation,
  package YAML, locators, or live acceptance claims.
- Add a narrow docs-contract test so the durable knowledge doc stays aligned
  with runtime tone choices, aliases, and descriptions.

## Non-Goals

- No runtime behavior changes.
- No package YAML, aliases, Q&A, localization counts, locators, or RingCentral
  routes.
- No new tone, language, provider, SAPI voice, Piper asset, or OpenAI prompt
  behavior.
- No persistent natural-language tone-state mutation.
- No live RingCentral acceptance claim.

## Privacy / Routing Constraints

Tone must remain a phrasing and speech-style setting only. Privacy-sensitive
prompts must still route through existing Q&A-first and answer-only boundaries
regardless of selected tone or alias. `privacy`, `safety`, and `compliance`
remain aliases for `careful`; they are not policy engines.

## Suggested Verification

```powershell
rg -n "professional|executive|style-only|SAPI|questionPolicy" docs/knowledge/presenter-tone-behavior-matrix.md
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests/unit/test_voice.py::test_presenter_tone_behavior_matrix_matches_runtime_contract
git diff --check
```
