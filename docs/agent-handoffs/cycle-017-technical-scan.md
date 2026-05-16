# Cycle 017 Technical Scan

Date: 2026-05-16
Role: technical-scan worker
Write scope: this file only

## Scope

Scanned the current RingCentral Video package, knowledge docs, prior Cycle 003/004/010 handoffs, manual acceptance runbook, and package/CLI tests. No production code or tests were edited.

Workspace note: the scanned files already have other-agent changes in the worktree, including `packages/ringcentral-video.yaml`, `docs/runbooks/ringcentral-manual-acceptance.md`, `tests/unit/test_material_packages.py`, `tests/unit/test_cli.py`, and untracked `docs/knowledge/`. Treat these as current working context, not as a clean baseline.

## Current Docs/Package Architecture

- `packages/ringcentral-video.yaml` is the executable/package knowledge source: 27 operation entrypoints, 4 demo flows, 51 flow steps, 21 explainers, 3 QA entries, 3 manual controls, 5 supported profile ids, and 19 package-owned question aliases.
- `src/ai_presenter/packages/models.py` accepts only the current schema: entrypoints, open steps, presenter notes, question aliases, flows, explainers, QA, and manual controls. Extra YAML fields are forbidden, so route/evidence metadata needs model work before it can live in the package.
- `docs/knowledge/ringcentral-video/` is the evidence companion set:
  - `source-index.md` separates official product docs from local repo/live evidence.
  - `observation-log.md` records append-only observations.
  - `acceptance-runs.md` records dated automated/manual evidence; runbook checklist items are not evidence until recorded here.
  - `locator-matrix.md`, `state-matrix.md`, and `privacy-matrix.md` split locator confidence, state confidence, and safety policy.
  - `evidence-index.md` is now the navigation layer connecting entrypoints, flows, risks, runbook checks, and evidence records.
- `docs/runbooks/ringcentral-manual-acceptance.md` is procedure, not proof. It drives smoke/audio/controller acceptance, but passing evidence belongs in `acceptance-runs.md` and then gets linked from `evidence-index.md`.
- `tests/unit/test_material_packages.py` protects package shape, IDs, executable-step validity, explainer coverage, localized text, and specific RingCentral routes such as `Add coworkers`.
- `tests/unit/test_cli.py` protects package/profile/flow resolution, flow listing, dry-run behavior, voice preflight, and doctor checks. It does not currently inspect evidence docs.

## Likely Change Paths

- `docs/knowledge/ringcentral-video/evidence-index.md`: add or normalize structured route/evidence rows, stable evidence IDs, route metadata columns, and missing-evidence status.
- `docs/knowledge/ringcentral-video/locator-matrix.md`: keep locator confidence and cleanup details synchronized with any route metadata.
- `docs/knowledge/ringcentral-video/acceptance-runs.md`: append dated manual/live runs before upgrading route status from observed/repo-tested to accepted.
- `docs/knowledge/ringcentral-video/observation-log.md`: append sanitized UIA/window observations for route variants before changing confidence.
- `docs/knowledge/ringcentral-video/source-index.md`: fix/keep wording that runbooks are procedure only, not current evidence.
- `docs/runbooks/ringcentral-manual-acceptance.md`: optional stable checklist IDs would make runbook mapping less brittle.
- `packages/ringcentral-video.yaml`: only after schema support, add optional route/evidence metadata such as evidence IDs, locator confidence, operation mode, confirmation requirement, or privacy surface.
- `src/ai_presenter/packages/models.py`: required if metadata moves into YAML; keep fields optional and non-operational at first.
- `tests/unit/test_material_packages.py`: best first test home for package metadata coverage and doc-link existence.
- `tests/unit/test_cli.py`: only change if CLI/doctor/entrypoints output starts exposing evidence freshness or route metadata.

## Tests Recommendation

Add tests, but in layers.

1. Doc-only layer: add a focused test or script that loads `packages/ringcentral-video.yaml`, reads `docs/knowledge/ringcentral-video/evidence-index.md`, and asserts every package entrypoint and flow appears in the appropriate table. This catches stale docs without changing runtime behavior.
2. Package metadata layer: if optional metadata is added to `OperationEntrypoint`, add model tests proving backward compatibility, `model_dump(by_alias=True)` shape, and that existing packages without metadata still load.
3. Safety/evidence policy layer: add assertions that high-risk IDs such as `ringcentral.video.more.recording` and `ringcentral.video.toolbar.leave` remain explain-only/blocked unless a confirmation workflow exists.
4. CLI layer: defer until evidence metadata has a user-facing command or doctor output. Do not force `test_cli.py` to know about docs unless CLI behavior changes.

Do not add tests that imply live acceptance from dry runs, `doctor`, or UIA read-only observations. That was the main discipline established in Cycles 003 and 010.

## Edge Cases/Risks

- `extra="forbid"` means package metadata cannot be added casually; schema and tests must land in the same slice.
- Evidence line numbers are brittle. Use stable IDs: entrypoint IDs, flow IDs, evidence IDs, and runbook check IDs.
- The evidence index already uses `Entry Point Evidence Table`, while earlier scan language proposed `Entrypoint Coverage`; tests should check actual headings or parse tables deliberately.
- `More` occurrence routes are scoped only to one empty-room, English, 100% DPI observation; do not generalize to participant-heavy, localized, narrow, or fullscreen states.
- Coordinate top-bar routes remain high drift risk.
- `Add coworkers` is implemented as a UIA route but still lacks live modal open/close acceptance.
- Manual checklist items can be mistaken for proof. Keep `acceptance-runs.md` as the dated proof source.
- Route metadata must not change automation permission by itself. Runtime behavior should continue to require existing safe operations until a separate, testable confirmation policy exists.
- Sensitive surfaces include meeting info, invite links, participant names, chat text, shared content, notes/transcript, recording, settings, and leave/end controls.

## Proposed File List

First safe implementation slice:

- `docs/knowledge/ringcentral-video/evidence-index.md`
- `docs/knowledge/ringcentral-video/source-index.md`
- `docs/runbooks/ringcentral-manual-acceptance.md`
- `tests/unit/test_material_packages.py`

Second slice, only if route metadata belongs in YAML:

- `src/ai_presenter/packages/models.py`
- `packages/ringcentral-video.yaml`
- `tests/unit/test_material_packages.py`

Defer unless surfaced in commands:

- `tests/unit/test_cli.py`
- `src/ai_presenter/runtime/diagnostics.py`
- `src/ai_presenter/cli.py`

## Safe Implementation Path

1. Start with docs discoverability: ensure the evidence index has stable rows for all 27 entrypoints and 4 flows, and ensure `source-index.md` calls the runbook a checklist, not evidence.
2. Add a non-live coverage test that cross-checks package IDs against the evidence index and runbook IDs if stable IDs are introduced.
3. If package-local route metadata is still desired, add optional schema fields that are explicitly descriptive: evidence IDs, locator confidence, privacy surface, operation mode, and confirmation requirement.
4. Keep runtime automation behavior unchanged in that metadata slice. Use metadata only for docs, diagnostics, or reporting until there is a separate tested confirmation flow.
5. Only promote any route to accepted after a dated manual/live record is added to `acceptance-runs.md` and linked back from `evidence-index.md`.
