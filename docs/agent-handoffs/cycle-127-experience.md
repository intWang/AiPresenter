# Cycle 127 Experience: Durable Localization Knowledge Refresh

Date: 2026-05-17

## Summary

Cycle 127 was a docs-only knowledge refresh after Spanish package
localization, Spanish alias expansion, and Latin-diacritic matching. The main
lesson is that durable docs need to describe the current generated package
state without turning package-local readiness into a runtime language claim.
Historical handoffs should remain dated records; durable knowledge pages are
the places where future cycles should land the current operating truth.

## Generated Counts Are Contract Clues, Not Trivia

Future cycles should treat generated counts as cheap drift detectors. After the
Spanish package work and normalization update, the current RingCentral Video
signals were:

- `156` package-owned aliases from doctor output.
- `84` Q&A prompts from doctor output.
- Spanish localization report: `51/51` demo steps, `12/12` Q&A questions,
  `12/12` Q&A answers.
- Spanish aliases: `questionAliases.es` on `26/27` entrypoints with `69`
  aliases.
- Chinese aliases: `15/27` entrypoints with `49` aliases.
- Japanese aliases: `13/27` entrypoints with `34` aliases.

When these numbers change, update durable docs and nearby verification notes
together. Do not hand-edit the numbers from memory, and do not use old cycle
handoffs as the source of truth after package generators or diagnostics have
moved on.

## Package-Only Language Wording Matters

Spanish is package-local complete and query-ready, but it is not a runtime
presenter language. Keep that distinction crisp:

- OK: Spanish package localization is complete.
- OK: Spanish package aliases and Q&A prompts are usable for package-local
  matching and diagnostics.
- OK: `doctor --require-localization --localization-language es` can validate
  package localization while still reporting runtime support boundaries.
- Not OK: Spanish is supported by `--language es`.
- Not OK: Spanish voice, provider, presenter controller, profile, or live demo
  acceptance exists unless a later runtime-promotion cycle proves it.

The shortest safe phrase is "Spanish is package-only." It prevents accidental
promotion while still acknowledging that the package content is no longer
partial or sparse.

## Normalization Boundaries

Cycle 126 made Latin-diacritic matching a shared behavior for package aliases,
localized Q&A prompts, diagnostics, tokenization, and legacy alias
precomputation. Cycle 127 documentation should preserve that boundary:

- Normalize only comparison keys, not authored package text.
- Preserve `strip()` and `casefold()` behavior.
- Fold Latin letters and combining marks for matching.
- Do not add unaccented alias duplicates to YAML just to satisfy lookup.
- Do not imply translation, stemming, synonym expansion, edit distance,
  semantic search, ASCII-only cleanup, CJK romanization, or runtime language
  promotion.

The durable lesson is that normalization is part of the package matching
contract. Runtime routes and diagnostics must share the same key so doctor
output can catch the same collisions and overlaps that users can hit at
runtime.

## Durable Docs Versus Historical Handoffs

Older handoffs are allowed to be wrong in hindsight because they are dated
records. Do not rewrite historical cycle files just to remove stale phrases
such as partial Spanish coverage, sparse Spanish aliases, or old alias/Q&A
counts.

Durable docs are different. README and `docs/knowledge/*` pages should reflect
the current maintained behavior because future agents use them as navigation
and regression-checklist material. If a durable page says Spanish is partial or
omits Latin-diacritic matching, it can send the next cycle toward unnecessary
YAML churn or an accidental runtime promotion.

For docs refreshes, update durable knowledge pages and add a new handoff that
explains what changed. Leave old cycle handoffs alone unless the user
explicitly asks for archival cleanup.

## Verification And Staging Discipline

For this kind of docs-only refresh, verification should prove that the docs
match generated behavior, not that unrelated local artifacts are clean.
Recommended checks:

```powershell
rg -n "Cycle 123|partial package coverage|intentionally sparse|Package-owned aliases: 87|Q&A prompts: 71|3 QA items" docs\knowledge README.md
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language zh --require-complete
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja --require-complete
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --localization-language es
.\.venv\Scripts\ai-presenter demo --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
git diff --check -- README.md docs\knowledge\ai-presenter-maintenance.md docs\knowledge\language-lifecycle.md docs\knowledge\ringcentral-video\runtime-safety-routing.md docs\knowledge\ringcentral-video\source-index.md docs\knowledge\ringcentral-video\observation-log.md
git status --short
```

Expected boundary: doctor stays at `0 warnings, 0 failed`; Spanish, Chinese,
and Japanese package localization reports pass where required; Spanish
`demo --language es --dry-run` still fails with `Unsupported presenter
language: es`.

In shared worktrees, check status before and after editing. Do not stage
generated files such as `.coverage`, and do not stage or commit unless the user
asks. If concurrent edits appear in durable docs, record what you observed and
work around them instead of reverting or overwriting them.
