# Cycle 112 Risk Scan: RingCentral Video Knowledge Navigation Integrity

Date: 2026-05-16
Scope: documentation-only risk/review scan. This handoff does not edit production code, tests, package YAML, or RingCentral Video knowledge docs.

## Verdict

Go, with guardrails, for a small offline docs/test slice that protects navigation integrity for `docs/knowledge/ringcentral-video`.

The guard should make stable knowledge docs discoverable and catch broken local links, missing hub references, duplicate evidence rows, or unknown entrypoint references. It should not turn the knowledge directory into a rigid schema, require every draft to be indexed, fetch external RingCentral URLs, or snapshot prose.

The safest shape is:

- Treat `source-index.md`, `evidence-index.md`, `validation-checklist-index.md`, and `runtime-safety-routing.md` as stable navigation hubs.
- Validate a small allowlist of stable hub files and local relative markdown links.
- Reuse existing package/evidence parsing where available instead of adding broad regex assertions.
- Leave drafts, scratch notes, and future exploratory docs opt-out capable.
- Keep the test deterministic, offline, and scoped to docs navigation.

## Risks By Severity

| Severity | Risk | Failure mode | Impact | Guardrail |
| --- | --- | --- | --- | --- |
| P0 | Drafts become blocking | A test scans every `*.md` file under `docs/knowledge/ringcentral-video` and fails if a new draft is not linked from an index. | Future agents avoid writing useful working notes, or they add noisy index links before facts are ready. | Validate only stable hub docs, or support an explicit draft escape hatch such as `draft-*.md`, `scratch-*.md`, or `<!-- nav: ignore -->`. |
| P0 | Brittle markdown-link parsing | A regex treats backticked file names, heading anchors, Windows separators, or markdown tables as required links and fails valid docs. | The guard becomes noisy and maintainers bypass or weaken it. | Limit parsing to explicit local markdown links and known tables; normalize paths with `pathlib`; avoid asserting incidental prose references. |
| P0 | Navigation test implies source-of-truth status | Passing link/index checks is mistaken for proof that RingCentral Video routes are accepted or safe to execute. | Reviewers may promote unvalidated routes or privacy-sensitive surfaces based on docs presence. | Test messages and docs should say navigation integrity is not live acceptance evidence. Evidence promotion still requires `acceptance-runs.md`. |
| P0 | Scope creep into runtime/package behavior | The slice edits `packages/ringcentral-video.yaml`, production code, route logic, or acceptance evidence to make navigation assertions pass. | A docs guard accidentally changes product behavior or evidence status. | Keep Cycle 112 implementation docs/test-only. No production code, package YAML, profiles, live artifacts, or generated coverage changes. |
| P1 | Over-constrained hub membership | The guard requires every stable doc to appear in every index, or requires exact section names and row order. | Harmless documentation restructuring creates failures unrelated to discoverability. | Require each stable doc to be reachable from at least one intended hub; avoid exact prose, heading-order, and table-order assertions unless a parser depends on them. |
| P1 | Broken links still slip through | Tests only assert literal filenames such as `validation-checklist-index.md` are present, but do not resolve markdown links. | Renames or moved docs can leave stale navigation that still passes string checks. | Resolve explicit local links from the linking file's directory and fail with the source file and missing target. |
| P1 | Intentional external links become flaky | The guard fetches RingCentral support URLs or fails when external URLs are unreachable. | Offline CI and local docs checks become network-dependent. | Do not fetch HTTP(S) URLs. For external links, at most assert they are syntactically non-empty. |
| P1 | Evidence and checklist roles blur | A navigation guard requires checklist rows to mirror evidence rows or vice versa. | Procedure docs begin to duplicate evidence docs, increasing stale contradictions. | Preserve roles: checklist is procedure, evidence index is navigation/evidence status, acceptance runs are dated proof. Cross-link, do not duplicate. |
| P1 | Case and path separator drift | Windows backslashes, POSIX slashes, and case sensitivity produce different pass/fail behavior across machines. | CI or another developer's environment sees different results from the same docs. | Resolve all paths via `Path`, compare normalized relative paths, and keep fixtures OS-neutral. |
| P2 | Empty or duplicate links reduce usefulness | Docs contain repeated links, placeholder links, or `[]()` that technically do not break a required-file assertion. | Navigation becomes cluttered or misleading even though the guard passes. | Add lightweight checks for empty link targets and duplicate stable hub rows only if failures are clear and low-noise. |
| P2 | Anchor checks become too clever | The guard validates every `#heading-anchor` and fails on punctuation or markdown renderer differences. | Minor heading wording changes create maintenance churn. | Skip anchor validation in the first slice, or validate anchors only for explicitly curated hub links. |
| P2 | Untracked or generated files confuse scope | The test includes temporary docs, generated exports, or untracked local notes. | Local-only work causes failures that do not reproduce. | Use repository paths intentionally, ignore known generated/scratch patterns, and make the target set explicit. |

## Candidate Assertions

Recommended first slice:

| Assertion | Why it helps | Keep it flexible by |
| --- | --- | --- |
| Stable hub files exist: `source-index.md`, `evidence-index.md`, `validation-checklist-index.md`, `runtime-safety-routing.md`, `acceptance-runs.md`, `observation-log.md`, `locator-matrix.md`, `state-matrix.md`, and `privacy-matrix.md`. | Catches accidental deletes or renames of the current knowledge package spine. | Use an allowlist of stable docs rather than all files in the directory. |
| `source-index.md` mentions the primary knowledge docs that explain source discipline, evidence, validation, safety routing, and acceptance evidence. | Keeps the source map useful as the first entry point. | Assert filenames or explicit links, not exact sentences or section order. |
| `evidence-index.md` lists the primary sources needed for evidence navigation, including `runtime-safety-routing.md`, `validation-checklist-index.md`, and `acceptance-runs.md`. | Prevents the evidence hub from losing the docs needed to interpret evidence levels. | Do not require every future note or handoff to be linked. |
| `validation-checklist-index.md` keeps pointing operators to `acceptance-runs.md` before evidence promotion. | Preserves the current proof-before-index-update workflow. | Assert the required destination and role phrase, not the whole update rule text. |
| Explicit local markdown links inside stable knowledge docs resolve to files. | Finds stale relative links after renames. | Ignore external URLs and backticked prose-only references in the first slice. |
| Evidence table entrypoints remain known package entrypoint IDs and each stable evidence row uses a supported evidence level. | Keeps the navigation table from drifting into typos. | Reuse the existing validation-target/evidence parser if available; do not parse all tables with ad hoc regex. |
| No empty markdown links in stable hub docs. | Catches unfinished navigation placeholders. | Limit to `[]()` and empty targets; do not ban placeholder text in drafts. |

Optional later assertions, only if the first slice stays quiet:

- Every stable knowledge doc is reachable from either `source-index.md` or `evidence-index.md`.
- Duplicate explicit links in the same short hub section are flagged as warnings or focused failures.
- Curated heading anchors in `source-index.md` and `evidence-index.md` resolve, if the docs start using anchors heavily.

Assertions to avoid in Cycle 112:

- Every markdown file in `docs/knowledge/ringcentral-video` must be indexed.
- Every stable doc must have backlinks from every other stable doc.
- Full markdown prose snapshots.
- Exact table row order except where an existing parser depends on a named table.
- External URL fetches.
- Live RingCentral evidence or package localization counts.

## Anti-Patterns

- Do not make docs discoverability depend on exact prose such as "runbook checkboxes are not acceptance evidence" unless that wording is the behavior being protected.
- Do not require draft, scratch, or temporary research files to appear in public indexes before they are ready.
- Do not add a broad markdown parser when the slice only needs local link resolution and a few stable file assertions.
- Do not parse backticked file names as if they were links; prose references can be useful without being navigation edges.
- Do not require every file to link back to `source-index.md`; useful leaf docs can stay leaf docs.
- Do not treat official RingCentral support links as local evidence or fetch them in unit tests.
- Do not duplicate `privacy-matrix.md`, `state-matrix.md`, `locator-matrix.md`, or `acceptance-runs.md` content inside indexes just to satisfy a guard.
- Do not promote any route to `Accepted` because an index row exists.
- Do not edit production code, package YAML, profiles, generated coverage, or live evidence files as part of a navigation guard.
- Do not bury guard failure messages behind large diffs; failures should name the source file, link target, and suggested owning hub.

## Go / No-Go

Go if Cycle 112 implements a compact, deterministic guard that:

- Touches only docs and tests approved for the small slice.
- Protects stable RingCentral Video knowledge hubs without policing all future notes.
- Resolves explicit local markdown links in stable docs.
- Preserves `source-index.md` and `evidence-index.md` as navigation layers, not source-of-truth replacements.
- Keeps `validation-checklist-index.md` tied to `acceptance-runs.md` for evidence promotion.
- Uses existing package/evidence parsing where practical.
- Produces clear failure messages that a docs maintainer can fix quickly.

No-go if the proposed guard:

- Scans all markdown files and fails intentionally unindexed drafts.
- Requires every doc to be linked from every index.
- Depends on network access, live RingCentral state, screenshots, or current external website availability.
- Snapshots full prose, exact heading order, or all table rows.
- Forces package YAML, runtime code, profile, acceptance evidence, or localization-count edits.
- Treats docs presence as live acceptance evidence.
- Creates more maintenance work than the broken-link/navigation risk justifies.

## Review Checklist

Use this checklist before approving the Cycle 112 implementation.

- [ ] Diff scope is limited to the planned docs/test slice; no production code, package YAML, profiles, `.coverage`, or live artifacts are staged.
- [ ] The guard has an explicit stable-doc allowlist or documented draft opt-out.
- [ ] Failure messages identify the source markdown file and missing target.
- [ ] Explicit local markdown links are resolved with path normalization, not raw string slash assumptions.
- [ ] External URLs are not fetched during tests.
- [ ] Backticked file references are not treated as mandatory links unless intentionally curated.
- [ ] `source-index.md` and `evidence-index.md` remain navigation layers and do not duplicate package YAML or acceptance evidence.
- [ ] `validation-checklist-index.md` still points to `acceptance-runs.md` before evidence promotion.
- [ ] Draft/scratch docs can exist without index churn.
- [ ] Tests avoid exact prose snapshots, full table snapshots, and broad heading-order assertions.
- [ ] Existing evidence-level and entrypoint-id validation is reused or kept compatible with current validation-target parsing.
- [ ] The guard is offline and fast enough for the focused unit suite.
- [ ] The review notes clearly state that navigation integrity is not RingCentral live acceptance.

## Recommended Verification For The Future Slice

For this handoff, a markdown diff check is enough because the change is advisory documentation only.

For a later Cycle 112 test/docs implementation, recommended focused verification is:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py
git diff --check -- docs\knowledge\ringcentral-video docs\agent-handoffs\cycle-112-risk-scan.md tests\unit\test_material_packages.py
```

If the implementation touches validation-target CLI parsing instead of test-local helpers, add the focused CLI tests around `validation-targets`. Do not run live RingCentral acceptance or localization reports unless the implementation changes package data, routing behavior, or evidence records.
