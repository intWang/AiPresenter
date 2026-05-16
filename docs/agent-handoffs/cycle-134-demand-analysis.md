# Cycle 134 Demand Analysis: Durable Localization Authoring Docs

Date: 2026-05-16
Cycle: 134
Scope: demand analysis only. This file is the only intended edit. Do not
modify source, tests, package YAML, profiles, durable docs, generated artifacts,
staging, commits, or live acceptance evidence in this analysis slice.

## Question

After Cycle131 added optional `localizedTitles` / `localizedPurposes` schema
and runtime rendering, Cycle132 seeded Spanish localized entrypoint display
copy for `ringcentral.video.overview` and
`ringcentral.video.top.network-quality`, and Cycle133 added read-only
`entrypoints --language` inspection, what should Cycle134 optimize next?

Recommendation: update durable localization authoring documentation for
localized entrypoint display copy and package-local inspection. This should be
a narrow docs-owned slice centered on `docs/knowledge/language-lifecycle.md`,
with at most a small README pointer/example if the implementation cycle wants
one. It should not add more Spanish package content, redesign CLI output, or
claim live RingCentral Video acceptance.

## Current Product State

The localization wedge now has three pieces in place:

- Schema/runtime support for localized entrypoint titles and purposes.
- Two safe Spanish RingCentral Video entrypoints using that copy:
  `ringcentral.video.overview` and
  `ringcentral.video.top.network-quality`.
- A read-only CLI inspection path:
  `ai-presenter entrypoints --package ringcentral-video --language es`.

The remaining gap is durable authoring guidance. The current language lifecycle
doc explains package-local text, localized Q&A, aliases, runtime voice support,
and live acceptance boundaries, but it still frames package seed examples around
`localizedText`, `localizedQuestions`, `localizedAnswers`, and
`questionAliases`. It does not yet teach future package authors when to use
`localizedTitles` / `localizedPurposes`, how to inspect them, how to interpret
localized versus fallback markers, or why partial entrypoint display coverage is
informational rather than a `--require-complete` failure.

That documentation gap matters now because Cycle133 intentionally made partial
state visible. Without durable guidance, future agents may read the new CLI
surface as runtime language support, a completeness target, or permission to
bulk-translate sensitive RingCentral controls.

## Options Compared

### 1. Update Durable Localization Authoring Docs

This is the best Cycle134 slice.

The implementation should document the current behavior, not invent new
behavior:

- `localizedTitles.<lang>` and `localizedPurposes.<lang>` are package-local
  display metadata for entrypoint answers and inspection.
- They do not affect matcher candidates, alias ordering, Q&A precedence,
  operation safety gating, controller language choices, provider routing, or
  voice asset availability.
- `entrypoints --language <lang>` is an inspection command using raw package
  language keys. It may show package-local languages that are not runtime voice
  choices.
- Localized inspection output should be interpreted per field: `localized`
  means nonblank package copy was present; `fallback` means canonical English
  title or purpose was shown.
- Spanish RingCentral Video entrypoint display copy remains partial:
  `2/27` titles and `2/27` purposes after Cycle132/Cycle133 unless a later
  content cycle changes package YAML.
- `localization-report --require-complete` remains scoped to required demo
  narration and Q&A completeness; localized entrypoint title/purpose counts are
  useful diagnostics, not a completeness gate.

This directly supports the user's continuous optimization request and fits the
RingCentralVideo knowledge/docs packet direction without changing active
runtime behavior.

### 2. Continue Spanish Localized Entrypoint Content

More Spanish display copy is valuable, but it should wait one cycle. The repo
now has only two authored examples and a new inspection surface; authors need a
stable authoring rule before the content surface grows.

If this option is chosen later, it should select one or two low-risk,
explanatory, non-state-changing entrypoints and carry a fresh risk scan. It
should avoid privacy-sensitive or state-changing surfaces such as participants,
chat, invite/link, share, recording, notes/transcript, microphone, camera, and
leave unless the cycle explicitly owns the safety copy and tests.

### 3. Improve CLI UI

The new CLI output can probably be polished over time, but Cycle133 test review
passed and no concrete user friction is recorded yet. Changing labels, compact
modes, or verbosity immediately after shipping would be speculative and could
destabilize the author-facing contract before it is documented.

The right CLI optimization now is documentation: explain the existing
`Language: <key>`, `localized`, and `fallback` output semantics.

### 4. Add Or Rearrange RingCentral Video Knowledge Packets

The RingCentral Video durable knowledge directory is already broad:
`source-index`, `evidence-index`, `locator-matrix`, `privacy-matrix`,
`state-matrix`, `runtime-safety-routing`, `validation-checklist-index`,
`observation-log`, and `acceptance-runs`.

Adding another RingCentral-specific packet for this slice would duplicate
repo-wide language lifecycle guidance. The better move is to update the
language lifecycle doc and link or mention RingCentral Video only as the current
example package. RingCentral-specific evidence docs should change only when the
cycle records new dated locator, privacy, state, or acceptance evidence.

## Recommended Cycle134 Slice

Implement a docs-only localization authoring update:

1. Update `docs/knowledge/language-lifecycle.md` with a short durable section
   for entrypoint display localization.
2. Add `localizedTitles` / `localizedPurposes` to the package seed gate
   examples, while preserving the package-local versus runtime voice boundary.
3. Document `entrypoints --language <lang>` as package-local inspection, not
   runtime language selection.
4. Explain `localized` and `fallback` source markers and the current Spanish
   RingCentral Video state of partial `2/27` entrypoint title/purpose coverage.
5. Clarify that localized entrypoint display copy is not part of
   `--require-complete` and does not change matcher, Q&A precedence, or safety
   behavior.
6. Optionally add one README command example under the existing entrypoints
   section:
   `ai-presenter entrypoints --package ringcentral-video --language es`.

This is narrow, useful, and low risk. It makes Cycles131-133 durable for future
authors before the repo adds more package content.

## Acceptance Criteria

- `docs/knowledge/language-lifecycle.md` documents
  `localizedTitles.<lang>` and `localizedPurposes.<lang>` as package-local
  entrypoint display metadata.
- The lifecycle doc explains that `entrypoints --language <lang>` accepts raw
  package-local language keys and does not perform runtime voice normalization,
  provider selection, or speech asset checks.
- The lifecycle doc explains localized/fallback source markers in the CLI
  inspection output.
- The lifecycle doc states that partial localized entrypoint title/purpose
  coverage is informative and does not make
  `localization-report --require-complete` fail.
- The lifecycle doc preserves the boundary between Spanish OpenAI-backed
  runtime support, local SAPI/Piper non-support, and unproven live
  RingCentral Video acceptance.
- The doc names the current Spanish RingCentral Video example entries without
  implying full `27/27` localized entrypoint coverage.
- If README is touched, it only adds a small inspection example or pointer and
  does not become the canonical authoring guide.
- Verification for the implementation cycle is docs-appropriate:
  path/content checks with `rg`, `git diff --check`, and `git status --short`.
- No source, tests, package YAML, profiles, generated artifacts, staging, or
  commits are required for this docs slice.

## Out Of Scope

- No new Spanish `localizedTitles` or `localizedPurposes` package content.
- No full Spanish entrypoint localization target.
- No Chinese, Japanese, German, or other new localized entrypoint copy.
- No CLI behavior changes, compact/verbose modes, source-marker renames, or
  output compatibility changes.
- No changes to runtime answer rendering, matcher candidates, alias handling,
  Q&A precedence, safety gating, controller UI, profiles, provider routing, or
  voice asset validation.
- No local Spanish SAPI/Piper support work and no OpenAI model/provider change.
- No live RingCentral Video acceptance claim or acceptance-run record.
- No new RingCentral evidence packet unless a separate cycle records dated
  evidence that belongs in `docs/knowledge/ringcentral-video/`.
- No staging, commit, generated artifact cleanup, or `.coverage` handling.

## Why This Beats The Alternatives

Cycle132 made localized entrypoint display copy real. Cycle133 made the partial
state inspectable. Cycle134 should make the authoring contract durable before
more agents add content or tune output. That is the smallest optimization that
reduces future confusion across languages, CLI inspection, runtime voice
claims, and RingCentral Video documentation.

More Spanish content can follow once the rules are written down. CLI UI polish
can follow once real users report friction. RingCentral evidence packets should
follow new evidence, not a localization metadata doc gap.
