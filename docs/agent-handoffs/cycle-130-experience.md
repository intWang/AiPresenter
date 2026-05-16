# Cycle 130 Experience Handoff: Spanish Entrypoint Copy Boundary

Date: 2026-05-16
Cycle: 130
Scope: experience handoff only. This file is the only intended edit for this
handoff. Do not modify source, tests, durable docs, package YAML, profiles,
generated artifacts, staging, commits, or live acceptance evidence from this
slice.

## Summary

Cycle130 worked best after it narrowed the localization fix to one honest
runtime-copy improvement: Spanish entrypoint answers can use an existing
Spanish package alias as the answer label, but the purpose text remains English
because `OperationEntrypoint` has no localized purpose field.

That distinction matters. The useful result is not "Spanish entrypoints are
localized." It is "Spanish entrypoint fallback answers no longer begin with an
English title when a package-authored Spanish alias already exists."

The current in-flight diff reflects that boundary:

- `_render_entrypoint_answer()` now prefixes answers with
  `_entrypoint_answer_label(entrypoint, voice)`.
- `_entrypoint_answer_label()` is scoped to `voice.language == "es"` and uses
  the first nonblank `questionAliases.es` value.
- English, Chinese, and Japanese entrypoint labels continue to use
  `entrypoint.title`.
- Package YAML was preserved.
- Purpose copy remains English until a schema/content cycle adds localized
  entrypoint title and purpose fields, or equivalent authored Q&A content.
- Live Spanish RingCentral acceptance remains unclaimed.

`.coverage` is dirty in the worktree and should remain treated as generated
output unless the cycle owner explicitly asks otherwise.

## Lessons For Future Cycles

### Avoid Broad Non-English Behavior Changes

The first implementation direction tried to use localized aliases for
non-English voices generally. That was too broad for the evidence and the
request. Cycle130 is about Spanish output quality after Spanish became an
OpenAI-backed runtime language; it is not a multilingual entrypoint rendering
redesign.

Future localization fixes should preserve existing behavior for English,
Chinese, Japanese, and any other language unless the cycle explicitly scopes and
tests that language. A small Spanish-specific branch is acceptable here because
the package already owns Spanish aliases and the tests prove that exact path.

### Use Spanish Aliases As Label-Only Fallback

Existing `questionAliases.es` strings are good labels for Spanish entrypoint
fallback answers. They are already curated package content, they route the
Spanish prompts, and using the first nonblank alias avoids package YAML churn.

Keep the alias use label-only. Do not treat aliases as full translations of
entrypoint purpose, safety policy, UI labels, or operator instructions. An
answer such as:

```text
panel de participantes: Open participant list and meeting people controls.
```

is a partial improvement with a known English residual, not complete Spanish
copy.

### Purpose Remains English Until Schema And Content Work

`OperationEntrypoint` currently has `title`, `area`, and `purpose`, but no
localized title or purpose fields. Runtime code cannot truthfully produce fully
localized entrypoint explanations without either new schema/content or authored
Spanish Q&A entries for the relevant prompts.

Do not paper over this with broad runtime translation, fuzzy wording, or
machine-like generic Spanish. The next real step for full entrypoint
localization is a content-model cycle that designs localized entrypoint
title/purpose fields, updates loader/status tests, reviews package YAML, and
documents how literal RingCentral UI labels should be handled.

### Preserve The Package YAML Boundary

Cycle130 deliberately did not edit `packages/ringcentral-video.yaml`. That
boundary was valuable. The package is product knowledge, not a scratchpad for a
runtime-copy fix.

Any future YAML localization change should be treated as a reviewed content
change. Review alias ordering, `questionPolicy`, `openSteps`, risky controls,
localized questions, localized answers, and related entrypoint IDs. Do not hide
routing or safety changes inside "copy polish."

### Preserve The Live Acceptance Boundary

Unit tests, dry runs, and static checks can prove routing, answer selection,
provider compatibility, and non-live controller behavior. They do not prove
live Spanish audio, real OpenAI synthesis, or RingCentral UI acceptance.

The safe Cycle130 claim is narrow:

- Spanish OpenAI Q&A routing can use package-authored Spanish alias labels for
  entrypoint fallback answers.
- Spanish package Q&A answers remain the stronger fully localized answer path.
- Spanish local SAPI/Piper remains unsupported.
- Live Spanish RingCentral acceptance remains unproven without a dated run that
  records profile, provider, flow, audio behavior, question prompt, answer text,
  RingCentral UI state, and result.

## Recommended Next Cycle

Run a schema/content planning cycle before attempting full Spanish entrypoint
copy. The cycle should decide whether to add localized entrypoint title/purpose
fields or instead add authored Spanish Q&A for high-value "where is this
control" prompts.

Keep that next cycle separate from live acceptance. After the content boundary
is resolved and tested, run a dedicated live Spanish acceptance cycle with real
OpenAI credentials and RingCentral evidence. Until then, keep describing this
work as label polish and runtime-copy quality, not full localization.
