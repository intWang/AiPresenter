# Cycle 127 Demand Analysis: Product Docs Localization Hygiene

Date: 2026-05-17
Scope: docs audit only. This file is the only intended edit. Do not stage or commit.

Shared-worktree note: initial `git status --short` showed only `.coverage` as
modified. During final verification, concurrent uncommitted edits appeared in
`docs/knowledge/language-lifecycle.md`, `docs/knowledge/ai-presenter-maintenance.md`,
`docs/knowledge/ringcentral-video/runtime-safety-routing.md`, and
`docs/knowledge/ringcentral-video/source-index.md`; a later status check also
showed `README.md` modified and `docs/agent-handoffs/cycle-127-risk-scan.md`
untracked. This audit records the stale phrases found in committed/product-facing
docs at inspection time; re-check the current working tree before applying any
follow-up patch.

## Files Inspected

- `README.md`
- `docs/knowledge/language-lifecycle.md`
- `docs/knowledge/ai-presenter-maintenance.md`
- `docs/knowledge/ringcentral-video/source-index.md`
- `docs/knowledge/ringcentral-video/runtime-safety-routing.md`
- `docs/knowledge/ringcentral-video/evidence-index.md`
- `docs/knowledge/ringcentral-video/locator-matrix.md`
- `docs/knowledge/ringcentral-video/state-matrix.md`
- `docs/knowledge/ringcentral-video/validation-checklist-index.md`
- `docs/runbooks/ringcentral-manual-acceptance.md`
- `presenter/*.md`, `presenter/skills/*.md`
- `src/ai_presenter/presenter/*.md`, `src/ai_presenter/presenter/skills/*.md`
- Context only: `docs/agent-handoffs/cycle-124-*`, `cycle-125-*`, `cycle-126-*`

## Current Verified State

- Spanish package localization is complete: `localization-report --package ringcentral-video --language es --require-complete` exits 0 and reports `51/51` demo steps, `12/12` Q&A questions, `12/12` Q&A answers.
- Spanish remains package-only for runtime: Cycle 126 handoffs verify `demo --language es --dry-run` still rejects `Unsupported presenter language: es`, and `doctor --require-localization --localization-language es` reports localization OK with runtime language support failure.
- Spanish aliases are no longer sparse: `questionAliases.es` is present on `26/27` entrypoints with `69` aliases.
- Accent-insensitive Latin matching is implemented: Cycle 126 added shared normalization for package aliases, localized Q&A prompts, diagnostics, tokenization, and legacy alias precomputation.
- Current doctor counts: `156` package-owned aliases, `84` Q&A prompts, `11` Q&A alias substring-risk info items, `0` warnings, `0` failed.

## Stale Or Misleading Facts Found

1. `docs/knowledge/language-lifecycle.md`
   - Phrase: `As of Cycle 123, Spanish is package-local only:`
   - Phrase: ``localization-report --package ringcentral-video --language es` reports partial package coverage.`
   - Phrase: `Spanish aliases are intentionally sparse.`
   - Why stale: Spanish is still package-only, but Cycle 124 made package localization complete and Cycle 125 expanded aliases to `26/27` entrypoints and `69` aliases.

2. `docs/knowledge/ringcentral-video/runtime-safety-routing.md`
   - Phrase: `Runtime guard: English, Japanese, and Chinese Notes/Transcript action or content prompts route to an answer-only safety Q&A when they are not location lookups.`
   - Why stale/misleading: Spanish localized Q&A is now complete and Cycle 126 verifies unaccented Spanish safety prompts stay Q&A-first and non-operable. The phrase can make maintainers think Spanish is excluded from safety Q&A routing.

3. `docs/knowledge/ringcentral-video/runtime-safety-routing.md`
   - Phrase: `Package-owned aliases: 87.`
   - Phrase: `Q&A prompts: 71.`
   - Phrase: `Chinese aliases: 15/27 entrypoints, 49 aliases.`
   - Phrase: `Japanese aliases: 13/27 entrypoints, 34 aliases.`
   - Phrase: `Chinese and Japanese localization coverage: 51/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers.`
   - Why stale: doctor now reports `156` aliases and `84` Q&A prompts; localization docs should include Spanish complete package coverage and Spanish alias status. Chinese/Japanese counts may need re-verification before rewriting because this audit only verified the current Spanish report and aggregate doctor output.

4. `docs/knowledge/ringcentral-video/source-index.md`
   - Phrase: `27 entrypoints, 4 flows, 21 explainers, 12 QA items with Chinese and Japanese Q&A localization, manual controls, safety notes.`
   - Phrase: `Japanese Q&A now has localized no-match text, while legacy Python aliases remain as fallback.`
   - Phrase: `Localization: Japanese coverage is complete...`
   - Why stale/misleading: package source coverage now includes complete Spanish package localization and expanded Spanish package-owned aliases. The question-matching row also omits Cycle 126 accent-insensitive Latin matching.

5. `docs/knowledge/ai-presenter-maintenance.md`
   - Phrase: `More partial languages are added beyond Chinese, Japanese, and Spanish seeds.`
   - Why slightly stale: Spanish should no longer be described as merely a seed/partial language. This is lower-impact because the same doc correctly warns that package localization is separate from runtime support.

## User-Impact Ranking

- P0: `language-lifecycle.md` Current Spanish State. This is the highest-risk doc because it is the canonical lifecycle boundary and currently says Spanish is partial/sparse when it is complete-but-package-only.
- P1: `runtime-safety-routing.md` counts and language list. Maintainers use it as a regression checklist; stale counts can cause false reviews, and the safety-language phrase can hide Spanish Q&A-first expectations.
- P1: `source-index.md` repository-local source summary and localization implications. It is the navigation layer for RingCentral Video knowledge and currently under-represents Spanish coverage and accent-insensitive matching.
- P2: `ai-presenter-maintenance.md` localization wedge planner wording. Useful cleanup, but it does not directly misstate command behavior.
- No stale user-facing problem found in `README.md` or `docs/runbooks/ringcentral-manual-acceptance.md`; they mostly discuss runtime-supported English/Chinese demo flows and package/runtime separation.

## Recommended Docs Update Scope For This Cycle

- Update `docs/knowledge/language-lifecycle.md` only enough to say Spanish is package-local complete, aliases are expanded, `--require-complete` passes, and runtime `--language es` remains unsupported until promotion.
- Update `docs/knowledge/ringcentral-video/runtime-safety-routing.md` counts from current doctor output, add Spanish package-local safety/Q&A coverage where appropriate, and add `localization-report --language es --require-complete` to verification commands.
- Update `docs/knowledge/ringcentral-video/source-index.md` to include Spanish Q&A/demo localization, Spanish `questionAliases.es` coverage, and Cycle 126 Latin accent-insensitive matching.
- Optional small wording fix in `docs/knowledge/ai-presenter-maintenance.md` so Spanish is no longer grouped with partial seeds.

## Out Of Scope

- Do not promote Spanish to runtime presenter language or update voice/provider/controller/profile surfaces.
- Do not change package YAML, aliases, Q&A, demo flows, locators, open steps, cleanup, safety policy, or source code.
- Do not update historical cycle handoffs; they are dated records and can remain as-is.
- Do not claim RingCentral Video live acceptance for Spanish or localized RingCentral UI. Existing locator docs still note English UIA labels and limited live evidence.
- Do not stage generated artifacts such as `.coverage`; it was already modified before this audit.
