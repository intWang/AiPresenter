# Cycle 112 Demand Analysis: RingCentral Video Knowledge Navigation Integrity

Date: 2026-05-16
Scope: demand analysis only. This file is the only file edited by this handoff.

## Product And Maintainer Demand

The RingCentral Video material package is now a multi-doc knowledge bundle, not a single YAML file with nearby notes. Cycle 111 added `runtime-safety-routing.md` and linked it from both navigation indexes, which is the right maintenance behavior. The problem is that the behavior is still convention-only: a future agent can add another canonical knowledge doc and forget to expose it from the source and evidence indexes.

That matters because the package's highest-risk work is not "find a file"; it is deciding whether a route is safe, accepted, observed, blocked, or only explainable. Missing navigation can hide the exact doc that preserves that boundary. The demand is therefore real but narrow: protect discoverability for canonical RingCentral Video knowledge docs without building a general documentation platform.

The current repo already has useful nearby guardrails:

- `tests/unit/test_validation_targets.py` validates that the evidence index covers every package entrypoint exactly once.
- `tests/unit/test_material_packages.py::test_ringcentral_validation_checklist_covers_package_routes` checks validation checklist coverage and basic source/evidence references.
- `docs/knowledge/ringcentral-video/evidence-index.md` already lists all non-self RingCentral Video knowledge docs as primary sources.
- `docs/knowledge/ringcentral-video/source-index.md` references the evidence index, runtime safety guide, validation checklist, and acceptance runs, but does not yet directly enumerate every matrix/log doc.

So the useful next slice is not a new script or broad link checker. It is a focused unit test that turns the existing navigation convention into a CI-visible invariant.

## Target Audience

- Future agents adding RingCentral Video knowledge docs under `docs/knowledge/ringcentral-video`.
- Maintainers reviewing package, safety, routing, evidence, or localization changes.
- QA reviewers using the indexes to decide where live evidence belongs.
- Product owners who want the durable RingCentral Video material package to remain navigable across cycles.

The guard should assume readers know repo-relative paths and entrypoint IDs, but should not assume they remember which cycle introduced each doc.

## Knowledge Docs That Must Be Discoverable

Every committed Markdown file under `docs/knowledge/ringcentral-video` should be treated as canonical package knowledge. If a note is not intended to be discoverable, it should stay in `docs/agent-handoffs` or another draft area instead of this package directory.

Current docs that must remain discoverable:

| Doc | Discoverability Reason |
| --- | --- |
| `source-index.md` | Product, repo, and verification source map for the package. |
| `evidence-index.md` | Main route/evidence navigation layer and validation priority map. |
| `acceptance-runs.md` | Dated proof log; required before live evidence levels are promoted. |
| `observation-log.md` | Read-only live observation history and UI metadata. |
| `locator-matrix.md` | Locator confidence, coordinate/UIA risk, and cleanup notes. |
| `state-matrix.md` | Meeting state labels, adapter signals, and state extraction gaps. |
| `privacy-matrix.md` | Default safety policy for private or meeting-impacting surfaces. |
| `runtime-safety-routing.md` | Q&A-first, answer-only, Notes/Transcript, Recording, and tone-as-style-only rules. |
| `validation-checklist-index.md` | Operator-ready checklist for turning evidence gaps into manual runs. |

The two navigation entry points should have complementary obligations:

- `evidence-index.md` should reference every other RingCentral Video knowledge doc because it is the primary navigation layer for current package evidence.
- `source-index.md` should reference every other RingCentral Video knowledge doc because it is the source map maintainers read before deciding whether a change is product-scope, repo-scope, evidence-scope, or safety-scope.
- Neither index needs to self-reference, as long as the paired index references it.

## Recommended Guard

Recommendation: add one focused unit test, not a standalone script.

Preferred shape for a future implementation cycle:

- Add a compact "Knowledge Package Map" or equivalent table to `docs/knowledge/ringcentral-video/source-index.md` so every existing package doc has one direct repo-relative path reference there.
- Add `test_ringcentral_knowledge_docs_are_indexed` near the existing RingCentral package docs checks, likely in `tests/unit/test_material_packages.py`.
- The test should enumerate `docs/knowledge/ringcentral-video/*.md`, read `source-index.md` and `evidence-index.md`, and assert:
  - every doc except `source-index.md` appears in `source-index.md`;
  - every doc except `evidence-index.md` appears in `evidence-index.md`;
  - the checked references use stable file names or repo-relative paths, preferably repo-relative paths in code spans.

Why a unit test:

- It fits the existing pytest-based validation style.
- It runs wherever package integrity tests already run.
- It catches the most likely regression: a canonical knowledge doc exists but is invisible from one navigation index.
- It avoids creating a script that maintainers must remember to run separately.

Do not expand the guard into a full Markdown link checker in this cycle. Exact file-reference presence is enough to protect the user-facing demand: the RingCentral Video package stays indexed and discoverable.

## Acceptance Criteria

A future one-cycle implementation satisfies this demand when:

- `docs/knowledge/ringcentral-video/source-index.md` has a concise package-doc map or equivalent references for all current knowledge docs except itself.
- `docs/knowledge/ringcentral-video/evidence-index.md` continues to reference all current knowledge docs except itself.
- A focused unit test fails if a new `docs/knowledge/ringcentral-video/*.md` file is added without being referenced from both navigation indexes, with the self-reference exceptions above.
- The test does not require production code changes and does not validate unrelated docs outside `docs/knowledge/ringcentral-video`.
- The implementation preserves the existing evidence-entrypoint guard in `tests/unit/test_validation_targets.py`; it does not duplicate or weaken that coverage.
- Verification includes the focused new pytest test, the existing RingCentral validation target tests if touched, and `git diff --check`.
- The implementation does not change package YAML, profiles, runtime behavior, live evidence levels, or test expectations unrelated to the new guard.

## Non-Goals

- Do not edit production code, package YAML, profiles, or runtime tests as part of this demand-analysis cycle.
- Do not add a general docs linter, external link checker, Markdown AST parser, or pre-commit hook.
- Do not enforce navigation rules outside `docs/knowledge/ringcentral-video`.
- Do not require the indexes to prove semantic completeness of each doc; they only need discoverability references.
- Do not promote any route from `Repo-tested` or `Observed` to `Accepted`.
- Do not add live RingCentral acceptance evidence, locator changes, privacy policy changes, or new validation targets.
- Do not turn draft handoffs into canonical knowledge docs automatically.

## Handoff Notes

- The guard is valuable because RingCentral Video safety knowledge is now distributed across source, evidence, runtime-safety, privacy, locator, state, validation, observation, and acceptance docs.
- The source-index prework is intentionally small: add a short package-doc table rather than expanding long prose sections.
- Prefer repo-relative paths such as `docs/knowledge/ringcentral-video/privacy-matrix.md` so future grep and tests are stable.
- Keep the evidence index as the operational navigation hub; keep the source index as the source taxonomy and entry map.
- If a future agent needs an unindexed scratch note, put it outside `docs/knowledge/ringcentral-video`.
- The worktree had an unrelated `.coverage` modification before this handoff; do not stage, delete, or normalize it.
