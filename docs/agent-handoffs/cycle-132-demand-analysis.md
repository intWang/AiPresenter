# Cycle 132 Demand Analysis: Seed Spanish Entrypoint Copy

Date: 2026-05-16
Cycle: 132
Scope: demand analysis only. This file is the only intended edit. Do not modify
source, tests, package YAML, profiles, generated artifacts, staging, commits, or
live acceptance evidence in this analysis slice.

## Question

After Cycles128-131, Spanish is OpenAI-runtime bounded, Spanish fallback answer
labels are improved, and optional `localizedTitles` / `localizedPurposes` schema
and runtime rendering exist. The RingCentral package still has zero localized
entrypoint titles and purposes: `localizedTitles.es` and
`localizedPurposes.es` remain `0/27`.

What is the best next product slice for Cycle132?

Recommendation: seed Spanish localized title and purpose copy for two safe
RingCentral Video entrypoints, with focused package/runtime/safety tests. This
turns the Cycle131 schema from unused infrastructure into visible user value
without attempting full Spanish entrypoint localization.

## Current Product State

The current stack has the right runtime boundary but no RingCentral package
content using it:

- Spanish can run only through OpenAI-backed speech profiles; local SAPI/Piper
  Spanish support remains out of scope and unproven.
- Authored Spanish Q&A answers are complete and should remain the preferred
  path for support, privacy, and state-changing questions.
- Spanish entrypoint aliases cover `26/27` RingCentral entrypoints and can route
  many "where is this control" questions.
- Cycle130 made Spanish entrypoint fallback labels less jarring by using the
  first Spanish alias when no localized title exists.
- Cycle131 added optional `localizedTitles` and `localizedPurposes`, runtime
  answer rendering, and optional report counts, but deliberately did not add
  package YAML content.

The remaining visible gap is simple: the product now knows how to render
localized entrypoint copy, but real RingCentral package answers still fall back
to aliases plus English purpose text.

## Options Compared

### 1. Seed Spanish `localizedTitles` / `localizedPurposes` For 1-2 Safe Entrypoints

This is the best next slice. It creates real user-facing value, exercises the
Cycle131 schema on the production RingCentral package, and keeps scope small
enough for careful copy and safety review.

Recommended seed entrypoints:

- `ringcentral.video.overview`
  - Passive narrative bridge.
  - `openSteps: []`, so no UI operation is implied.
  - Good first proof that Spanish fallback answers can be natural without
    touching privacy-sensitive panels.
- `ringcentral.video.top.network-quality`
  - Diagnostic surface with cleanup via Escape.
  - Useful for RingCentral understanding and troubleshooting.
  - Lower privacy/state-change risk than chat, participants, invite, share,
    recording, notes, microphone, camera, or leave.

This option should update package content plus tests in the implementation
cycle. It should not bulk-translate all 27 entrypoints.

### 2. Add Safety-Focused Tests Before Content Edits

This is valuable but less complete as a standalone product slice. Cycle131
already added structural tests proving localized title/purpose rendering,
fallback behavior, and matcher isolation. More safety tests are still needed
when real package YAML content lands, especially around Q&A precedence and
non-operable risky controls, but a tests-only cycle would leave the visible
`0/27` gap untouched.

The right move is to include safety tests in the content seed slice:

- authored Spanish Q&A still beats entrypoint fallback for privacy or risky
  prompts;
- localized title/purpose copy does not change matching;
- `can_operate` behavior remains unchanged for the seeded entrypoints and for
  representative risky controls.

### 3. Add CLI Inspection Such As `entrypoints --language`

This is useful author tooling, but it is slightly premature while the real
RingCentral package has no localized title/purpose content. Today the
localization report already exposes the zero counts, and `entrypoints` still
prints canonical English titles. A `--language` flag becomes more valuable after
at least one real package entrypoint has localized display copy to inspect.

Keep this as a follow-up once the seed exists:

- default `entrypoints` remains English;
- `entrypoints --language es` prints localized title/purpose where present and
  a clear fallback where absent;
- the command is inspection-only and does not imply runtime support or live
  acceptance.

### 4. Another Small Optimization: Update Durable Localization Docs For Entrypoint Copy

The docs now mention package-local text, Q&A, aliases, and runtime language
boundaries, but durable guidance has not yet absorbed the optional
`localizedTitles` / `localizedPurposes` distinction. This would make future
cycles safer, yet it is lower value than proving the new package field with real
content. A docs-only update should follow the seed if reviewers find confusion
around whether entrypoint title/purpose coverage is required localization.

## Recommended Cycle132 Slice

Implement a two-entrypoint Spanish content seed for RingCentral Video:

1. Add `localizedTitles.es` and `localizedPurposes.es` to:
   - `ringcentral.video.overview`
   - `ringcentral.video.top.network-quality`
2. Use concise Spanish prose that preserves literal RingCentral UI labels when
   the user must find the same label on screen.
3. Add focused tests proving the real package answers use Spanish localized
   title and purpose for those two entrypoints.
4. Add guardrail tests proving authored Spanish Q&A precedence and risky-control
   non-operability are not weakened.
5. Update only the expected optional report counts for Spanish entrypoint
   localized title/purpose coverage from `0/27` to `2/27`.

This slice is narrow but meaningful: Spanish users get two natural entrypoint
answers, package authors get a concrete pattern to copy, and the team gets a
reviewable template before touching the remaining 25 entrypoints.

## Acceptance Criteria

- `packages/ringcentral-video.yaml` includes Spanish `localizedTitles` and
  `localizedPurposes` for exactly the selected 1-2 safe entrypoints, preferably
  the two listed above.
- Spanish runtime question answers for those entrypoints render Spanish title
  and Spanish purpose, not English purpose prose.
- Existing Spanish alias fallback still works for an unseeded entrypoint.
- Localized title/purpose fields still do not affect matcher candidates,
  alias ordering, Q&A-first routing, or operation safety gating.
- Authored Spanish Q&A answers still take precedence over entrypoint fallback
  for privacy or state-changing areas such as recording, invite/share, notes,
  meeting information, microphone/camera, participants, chat, and leave.
- `localization-report --package ringcentral-video --language es` reports
  `localizedTitles.es present on 2/27 entrypoints` and
  `localizedPurposes.es present on 2/27 entrypoints` if two entrypoints are
  seeded.
- `--require-complete` behavior remains based on required demo narration and
  Q&A localization; partial entrypoint localized title/purpose coverage stays
  informative, not failing.
- English, Chinese, and Japanese localization report expectations remain
  unchanged except for any explicitly scoped optional count update.
- Verification is local and offline: focused unit tests, localization report,
  doctor/localization checks as needed, `ruff`, `mypy`, `git diff --check`, and
  `git status --short`.

## Out Of Scope

- No full 27-entrypoint Spanish translation pass.
- No Chinese or Japanese localized title/purpose content.
- No CLI `entrypoints --language` implementation in the same slice unless the
  content seed is already complete and reviewed.
- No localized title/purpose matching, duplicate diagnostics, or alias-overlap
  semantics change.
- No changes to `questionPolicy`, `openSteps`, cleanup behavior,
  `relatedEntrypointIds`, existing Q&A answers, aliases, demo narration, or
  presenter skills except where a test fixture requires read-only assertions.
- No controller UI localization, provider behavior change, local Spanish
  SAPI/Piper support, OpenAI model change, or live audio claim.
- No live RingCentral Video acceptance claim. A dated acceptance run remains a
  separate artifact with separate evidence requirements.
- No durable README/runbook/language-lifecycle update unless a later docs-owned
  cycle scopes it.
- No staging, commit, or generated artifact cleanup as part of this analysis.

## Why This Beats The Alternatives

The user asked for continuous optimization across RingCentral understanding,
UI/performance, languages/tones, skills, and docs packets. The highest-leverage
thread right now is the Spanish entrypoint copy wedge because the previous
cycles already built the runway and left a visible zero-count gap. A content
seed is small enough to verify, directly improves the spoken Q&A experience,
and avoids overclaiming full localization.

Tests-only work would be prudent but invisible. CLI-only work would help package
authors but has little to show until package content exists. Durable docs would
reduce future confusion but would still leave the product behavior unchanged.

Cycle132 should therefore make the smallest real package-content move: two safe
Spanish localized entrypoint titles and purposes, with safety tests keeping the
RingCentral boundary intact.
