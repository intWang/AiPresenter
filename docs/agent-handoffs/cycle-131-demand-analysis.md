# Cycle 131 Demand Analysis: Entrypoint Title/Purpose Localization

Date: 2026-05-16
Cycle: 131
Scope: demand analysis only. This file is the only intended edit. Do not
modify source, tests, package YAML, durable docs, profiles, generated artifacts,
staging, commits, or live acceptance evidence in this analysis slice.

## Question

Cycle130 improved Spanish entrypoint answer labels by using the first
`questionAliases.es` value as the answer prefix for Spanish voices. The
remaining issue is that entrypoint answer purpose text still comes from
`OperationEntrypoint.purpose`, which is English-only.

Should the next product slice add localized entrypoint title/purpose schema, or
keep leaning on alias-label fallback?

Recommendation: define a small content-model localization slice next, but do
not implement it as broad package YAML churn. The product need is now beyond an
alias-label fallback: Spanish users can ask for controls in Spanish, and the
system can label the matched control in Spanish, but the explanatory sentence is
still English. That mixed output is acceptable as an explicitly documented
temporary fallback, not as the steady-state Spanish Q&A contract.

## Current Product State

Current Spanish behavior has three different quality levels:

- Authored package Q&A answers are localized and can return natural Spanish
  `localizedAnswers.es`.
- Entrypoint alias questions can route correctly and now show a Spanish label
  when a useful `questionAliases.es` value exists.
- Entrypoint purpose prose remains English because `OperationEntrypoint` only
  models `title`, `area`, and `purpose`; there are no localized title or purpose
  fields.

That means an answer such as:

```text
panel de participantes: Open participant list and meeting people controls.
```

is better than the previous English title prefix, but it is still visibly mixed
language. For live Spanish acceptance, this is the kind of answer a user will
notice immediately because it occurs on common "where is this control" prompts,
not only obscure fallback paths.

## Alias Fallback Versus Localized Schema

### Keep Alias-Label Fallback Only

This is low-risk and already implemented for Spanish. It avoids schema changes,
package migration, diagnostics churn, and broad content review. It also keeps
aliases doing what they already do: help match user phrasing.

The downside is that aliases are not a content model. They are matcher hints,
often terse noun phrases, and their ordering now affects visible answer copy.
They do not provide a localized purpose sentence, cannot distinguish display
title from alternate user phrasing, and can encourage content authors to stuff
answer prose into a field meant for routing.

This option is acceptable only as a temporary fallback boundary:

- use aliases to improve labels when no localized title exists;
- keep English purpose text documented as a residual gap;
- do not claim fully localized entrypoint Q&A.

### Add Localized Entrypoint Title/Purpose Fields

This better matches the user/product need. Entrypoints are now a user-facing Q&A
surface, not just an internal operation map. Once a runtime language is
accepted, common entrypoint answers need localized display copy just like demo
narration and authored Q&A answers.

A conservative schema could add optional fields on `OperationEntrypoint`, for
example:

```yaml
localizedTitles:
  es: panel de participantes
localizedPurposes:
  es: Abre la lista de participantes y los controles de personas de la reunion.
```

Runtime answer rendering would prefer localized title and purpose for
`voice.language`, then fall back to the Cycle130 alias label, then fall back to
the canonical English title/purpose. This preserves compatibility while giving
package authors the right place for user-facing localized copy.

The risk is scope. There are 27 RingCentral entrypoints, multiple languages,
diagnostic/report semantics, model validation, CLI output, and tests that could
balloon quickly. The next cycle should therefore prove the schema and runtime
contract on a small Spanish subset, not translate the whole package.

## Recommended Next Scope

Run a narrow entrypoint-localization schema cycle:

1. Add optional localized entrypoint title and purpose fields to the package
   model and loader contract.
2. Update entrypoint answer rendering to use localized title/purpose for the
   active voice language when both are present.
3. Preserve Cycle130 alias-label fallback for Spanish when localized fields are
   missing.
4. Add a tiny package fixture or a very small RingCentral subset to prove the
   behavior. Prefer one safe executable control and one answer-only/passive
   control over bulk-editing all 27 RingCentral entrypoints.
5. Keep localization completeness reporting unchanged unless the cycle
   explicitly designs new optional reporting for entrypoint title/purpose
   coverage.
6. Document the residual boundary: Spanish entrypoint answers are only fully
   localized for entrypoints that have localized title and purpose fields.

The product line should be: "entrypoint answer localization now has a schema and
fallback contract." It should not be: "RingCentral Video Spanish acceptance is
complete."

## Acceptance Criteria For The Next Cycle

- `OperationEntrypoint` accepts optional localized title and purpose maps without
  breaking existing packages.
- Runtime entrypoint answers prefer localized title and localized purpose for
  the active voice language when present.
- If localized title/purpose are missing, Spanish still falls back to the
  Cycle130 alias-label behavior, then to canonical English title/purpose.
- Tests cover at least one Spanish entrypoint answer with both localized title
  and localized purpose, proving the answer no longer contains English purpose
  prose.
- Tests cover a Spanish entrypoint with no localized purpose, proving the
  fallback remains intentional and stable.
- English, Chinese, and Japanese existing entrypoint answer behavior is not
  weakened or silently reinterpreted.
- Authored `localizedAnswers.es` Q&A behavior remains the preferred path for
  safety/support questions and remains answer-only where policy requires it.
- `questionAliases` remains a matcher field; tests should not require aliases to
  carry long display sentences.
- Package diagnostics and localization reports either remain unchanged or add
  explicitly optional entrypoint-copy reporting that cannot make a partially
  localized package look complete.
- Verification stays local and offline: unit tests, static checks, and
  `git diff --check` are enough for this slice.

## Out Of Scope

- No broad `packages/ringcentral-video.yaml` translation pass across all
  entrypoints.
- No package YAML reordering, alias expansion, demo narration rewrites,
  Q&A rewrites, locator edits, or safety policy edits.
- No durable README/runbook/spec updates unless a later implementation cycle
  explicitly scopes a concise documentation note.
- No live RingCentral Video Spanish acceptance claim.
- No live OpenAI synthesis or audio quality claim.
- No local Spanish SAPI support, Windows voice discovery, Piper model selection,
  Piper downloads, or local asset-readiness changes.
- No controller or CLI chrome localization beyond the answer text path under
  test.
- No machine translation pipeline, glossary system, bulk migration tool, or
  multi-language completion mandate.

## Demand Rationale

The user need is not merely "make the first word Spanish." It is "when I ask in
Spanish where a control is, the presenter should answer in Spanish enough to be
credible." Cycle130 moved the label from embarrassing to acceptable. Cycle131
should now decide whether entrypoints are first-class localized content.

They should be, but carefully. Entrypoints already power routing, answer text,
and demo interrupts, so they sit at the boundary between product knowledge and
automation. Localized title/purpose fields give authors a clean place to write
human-facing copy without overloading aliases or changing operation safety.

The smallest valuable next step is schema plus runtime selection plus focused
tests. Full RingCentral YAML coverage, live acceptance, and local Spanish voice
support are separate cycles with different evidence requirements.
