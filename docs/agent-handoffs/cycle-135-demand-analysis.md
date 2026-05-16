# Cycle 135 Demand Analysis: Guard Optional Entrypoint Metadata Counts

Date: 2026-05-16
Cycle: 135
Scope: demand analysis only. This file is the only intended edit. Do not
modify source, tests, package YAML, README, durable docs, profiles, generated
artifacts, staging, commits, or live acceptance evidence in this analysis
slice.

## Question

After Cycle131 added optional `localizedTitles` / `localizedPurposes` schema and
runtime rendering, Cycle132 seeded two Spanish RingCentral Video entries,
Cycle133 added `entrypoints --language` inspection, and Cycle134 documented the
language lifecycle, what is the best narrow Cycle135 slice?

Recommendation: add focused tests/tooling that prevents optional entrypoint
display metadata count drift between the RingCentral package, CLI/report
fixtures, and durable documentation. Do this before adding more Spanish
localized title/purpose content.

## Current Product State

The Spanish entrypoint localization wedge is now real but intentionally partial:

- Required Spanish package localization is complete for demo narration and Q&A:
  `51/51` demo steps, `12/12` localized questions, and `12/12` localized
  answers.
- Spanish `questionAliases.es` covers `26/27` RingCentral Video entrypoints
  with `69` aliases.
- Optional Spanish entrypoint display metadata covers only
  `localizedTitles.es` on `2/27` entrypoints and `localizedPurposes.es` on
  `2/27` entrypoints.
- The two seeded entries are `ringcentral.video.overview` and
  `ringcentral.video.top.network-quality`.
- `entrypoints --language es` can inspect localized versus fallback display
  copy.
- Durable docs now mention the `2/27` state and explicitly warn that dated
  counts can drift when future package content changes.

That last point is the live risk. The repo has several places that can mention
or assert the same optional metadata counts: package tests, CLI tests,
`localization-report`, README snippets, language lifecycle docs, RingCentral
source index docs, and cycle handoffs. More Spanish copy will immediately
require count updates, so the next highest-value slice is a small guardrail that
makes count drift harder to miss.

## Options Compared

### 1. Add 1-2 More Spanish `localizedTitles` / `localizedPurposes` Entries

This is valuable and should remain the likely follow-up. A good future content
slice could add one or two low-risk, explanatory surfaces such as view/layout or
report/help-style controls, still avoiding privacy-sensitive and state-changing
areas until a fresh risk scan scopes them.

However, adding more copy now would move counts from `2/27` to `3/27` or
`4/27` across several files and tests. Cycle134 already identified count drift
as residual risk. Continuing content before adding a drift check increases the
chance that docs, tests, and report examples disagree.

### 2. Add Tests/Tooling To Prevent Docs/Count Drift

This is the best Cycle135 slice. It is narrow, local, and directly protects the
work from Cycles131-134.

A conservative implementation should add a small test or helper that derives
optional localized entrypoint metadata counts from the real RingCentral package
and asserts that the durable documentation count mentions match the derived
Spanish state. It should focus on `localizedTitles.es` and
`localizedPurposes.es`, not on every localization count in the repository.

The goal is not to make docs brittle for every historical handoff. The goal is
to catch current durable-doc drift in the places future authors are expected to
trust, especially:

- `docs/knowledge/language-lifecycle.md`
- `docs/knowledge/ringcentral-video/source-index.md`

This slice would give future Spanish content agents a clear failure when they
add metadata but forget to update the durable counts.

### 3. Add A Concise README Inspection Example

This is useful but lower leverage. README already has command examples for
`entrypoints`, localization reports, voices, doctor, demo, and controller
usage. Adding:

```powershell
.\.venv\Scripts\ai-presenter entrypoints --package ringcentral-video --language es
```

would make the inspection path easier to discover, but it does not prevent
stale counts or overclaims. It is a fine optional add-on after a guardrail test
exists, but should not be the whole cycle.

### 4. Another Small High-Value Improvement

The best adjacent improvement is a tiny author checklist for the next Spanish
content slice: when adding `localizedTitles` / `localizedPurposes`, rerun
`localization-report`, run `entrypoints --language es`, and update durable
counts together. Cycle134 already put most of this in docs; enforcing the count
check is more valuable than adding another prose reminder.

I do not recommend CLI output polish or controller/runtime language work for
Cycle135. No concrete CLI friction has been recorded, and Spanish runtime
readiness remains OpenAI-backed and live-acceptance bounded.

## Recommended Cycle135 Slice

Implement a count-drift guard for optional RingCentral Video entrypoint display
metadata:

1. Add a focused test or small verification helper that derives the current
   Spanish `localizedTitles` and `localizedPurposes` counts from the real
   `ringcentral-video` package.
2. Assert that durable docs with current-state claims contain matching
   `localizedTitles.es` and `localizedPurposes.es` `2/27` mentions.
3. Keep the guard scoped to current durable docs, not historical cycle handoffs.
4. Preserve `localization-report --require-complete` semantics: optional
   entrypoint title/purpose coverage remains informational and must not become
   a completeness gate.
5. Do not add new Spanish package content in this slice.

This is small but high leverage: it reduces maintenance friction before the
next content agent moves beyond the two-entrypoint pilot.

## Acceptance Criteria

- A focused test or script derives Spanish optional entrypoint display metadata
  counts from the loaded RingCentral Video package.
- The guard verifies that current durable docs mentioning Spanish optional
  entrypoint display state match the derived `localizedTitles.es` and
  `localizedPurposes.es` counts.
- The guard covers `docs/knowledge/language-lifecycle.md` and
  `docs/knowledge/ringcentral-video/source-index.md`.
- Historical handoffs under `docs/agent-handoffs/` are not treated as
  authoritative current-state docs.
- The current expected state remains `2/27` titles and `2/27` purposes until a
  separate package-content cycle changes it.
- `localization-report --package ringcentral-video --language es` continues to
  report optional title/purpose counts without making them part of
  `--require-complete`.
- `entrypoints --language es` behavior and output contract are unchanged.
- No package YAML, localized Spanish copy, matcher behavior, Q&A precedence,
  operation safety gating, runtime provider checks, controller UI, voice
  support, or live acceptance evidence changes are included.
- Verification for the implementation cycle includes the new focused guard,
  relevant existing CLI/package tests if touched, `ruff` for touched Python
  files, `git diff --check`, and `git status --short`.

## Out Of Scope

- No new Spanish `localizedTitles` or `localizedPurposes` package entries.
- No full Spanish `27/27` entrypoint localization target.
- No Chinese, Japanese, German, or other localized entrypoint display copy.
- No README edit unless the implementation owner explicitly chooses it as a
  tiny add-on after the guard passes.
- No broad doc-count audit across all historical handoffs, generated reports,
  or stale cycle notes.
- No CLI formatting changes, source-marker renames, compact mode, or behavior
  changes to `entrypoints --language`.
- No changes to runtime answer rendering, matcher candidates, alias ordering,
  duplicate diagnostics, Q&A precedence, safety gating, controller UI, profiles,
  provider routing, or voice asset validation.
- No local Spanish SAPI/Piper support, OpenAI provider/model change, or live
  RingCentral Video acceptance claim.
- No staging, commit, generated artifact cleanup, or `.coverage` handling.

## Why This Beats The Alternatives

Cycles131-134 built the localized entrypoint copy path, seeded it, exposed it,
and documented it. The next failure mode is not lack of one more Spanish phrase;
it is silently stale count claims as soon as the content surface grows.

A small count-drift guard makes future content cycles safer and faster. Once it
exists, the repo can resume adding low-risk Spanish entrypoint display copy with
less chance of leaving README, durable docs, tests, and reports out of sync.
