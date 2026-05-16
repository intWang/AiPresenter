# RingCentral Validation Checklist Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an operator-ready RingCentral Video validation checklist index and tests that keep it aligned with package entrypoints.

**Architecture:** Keep runtime behavior unchanged. Add a procedural knowledge document under `docs/knowledge/ringcentral-video/`, cross-link it from the existing evidence/source/runbook docs, and add package-doc coverage tests using stable IDs.

**Tech Stack:** Python, pytest, markdown docs, existing `ai_presenter.packages.loader.load_material_package`.

---

## File Structure

- Modify: `tests/unit/test_material_packages.py`
  - Add tests that load `packages/ringcentral-video.yaml` and read RingCentral knowledge docs.
- Create: `docs/knowledge/ringcentral-video/validation-checklist-index.md`
  - Operator-facing procedure for route validation, cleanup, privacy, and post-run updates.
- Modify: `docs/knowledge/ringcentral-video/evidence-index.md`
  - Add the checklist as a primary source and maintenance target.
- Modify: `docs/knowledge/ringcentral-video/source-index.md`
  - Register the checklist as repository-local procedure.
- Modify: `docs/runbooks/ringcentral-manual-acceptance.md`
  - Point operators to the checklist before live route validation.
- Create: `docs/agent-handoffs/cycle-017-implementation.md`
  - Record TDD and verification evidence for this cycle.
- Create: `docs/agent-handoffs/cycle-017-review.md`
  - Record review findings after implementation.
- Create: `docs/agent-handoffs/cycle-017-summary.md`
  - Record final outcome and next cycle suggestions.

No commit is required in this continuous optimization session unless the user explicitly asks.

---

### Task 1: Add Failing Package/Docs Coverage Test

**Files:**
- Modify: `tests/unit/test_material_packages.py`

- [ ] **Step 1: Add the failing test**

Add this test near the existing RingCentral package tests:

```python
def test_ringcentral_validation_checklist_covers_package_routes() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    knowledge_dir = Path("docs/knowledge/ringcentral-video")

    checklist_text = (knowledge_dir / "validation-checklist-index.md").read_text(
        encoding="utf-8"
    )
    evidence_text = (knowledge_dir / "evidence-index.md").read_text(encoding="utf-8")
    source_text = (knowledge_dir / "source-index.md").read_text(encoding="utf-8")

    missing_entrypoints = [
        entrypoint.id
        for entrypoint in package.operation_entrypoints
        if entrypoint.id not in checklist_text
    ]
    missing_flows = [
        flow.id for flow in package.demo_flows if flow.id not in evidence_text
    ]

    assert missing_entrypoints == []
    assert missing_flows == []
    assert "validation-checklist-index.md" in evidence_text
    assert "validation-checklist-index.md" in source_text
    assert "acceptance-runs.md" in checklist_text
    assert "Do Not Execute Yet" in checklist_text
    assert "ringcentral.video.main.add-coworkers" in checklist_text
    assert "ringcentral.video.more.recording" in checklist_text
    assert "ringcentral.video.toolbar.leave" in checklist_text
    assert "runbook checkboxes are not acceptance evidence" in checklist_text
```

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_validation_checklist_covers_package_routes
```

Expected: FAIL because `docs/knowledge/ringcentral-video/validation-checklist-index.md` does not exist yet or is not linked.

---

### Task 2: Create Validation Checklist Index

**Files:**
- Create: `docs/knowledge/ringcentral-video/validation-checklist-index.md`

- [ ] **Step 1: Create the checklist document**

Use this structure and include all listed IDs:

```markdown
# RingCentral Video Validation Checklist Index

Date: 2026-05-16

## Purpose

This checklist turns known RingCentral Video evidence gaps into safe manual validation work. It is procedure, not proof. Dated proof belongs in `acceptance-runs.md`; runbook checkboxes are not acceptance evidence.

## Update Rule

1. Append a dated run to `acceptance-runs.md`.
2. Record build, locale, DPI, window bounds, role, scenario, participant count, action, cleanup, pass/fail, failures, recovery, privacy notes, and locator updates.
3. Update `locator-matrix.md`, `state-matrix.md`, `privacy-matrix.md`, and `evidence-index.md` only after the run is recorded.
4. Do not promote a route to `Accepted` from automated tests, dry runs, `doctor`, or read-only UIA observation alone.

## Priority Checklist

| Priority | Route Or Group | Entrypoints | Current State | Validate | Cleanup | Privacy Boundary | Record Result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P0 | Add coworkers modal | `ringcentral.video.main.add-coworkers` | Observed UIA button, package route repo-tested, no live click acceptance | In a disposable empty-room meeting, click Add coworkers, confirm Invite/Add coworkers dialog opens, then close it | Modal close by X or Cancel; confirm toolbar is usable again | Do not read or store invite links, emails, names, or suggestions | `acceptance-runs.md`, then `evidence-index.md` and `locator-matrix.md` |
| P0 | Controller queued Chat question | `ringcentral.video.toolbar.chat`, `meeting-control-map-demo` | Unit-tested, not manually accepted | Start the map demo, ask `chat`, confirm queued safe demo and original flow continuity | Toggle or close Chat panel | Do not read chat message text | `acceptance-runs.md`, then controller/runbook notes |
| P1 | App shell launch | `ringcentral.develop.video.tab`, `ringcentral.develop.video.start` | Repo-tested only | Focus RingCentralDevelop, open Video tab, click Start, bind RingCentralVideo window | Leave meeting only if the disposable session requires it | Do not expose account or meeting identifiers | `acceptance-runs.md` |
| P1 | Top-bar coordinate routes | `ringcentral.video.top.meeting-info`, `ringcentral.video.top.network-quality`, `ringcentral.video.top.views`, `ringcentral.video.top.report-issue` | Repo-tested, coordinate drift risk | Open each route at recorded bounds/DPI and confirm expected panel/dialog/menu | Escape for popovers/menus; modal X for Report issue | Do not read meeting IDs, links, dial-in details, account data, or report contents | `acceptance-runs.md`, then `locator-matrix.md` |
| P1 | Common toolbar panels and pickers | `ringcentral.video.toolbar.invite`, `ringcentral.video.toolbar.participants`, `ringcentral.video.toolbar.chat`, `ringcentral.video.toolbar.share` | Observed labels, cleanup unaccepted | Open each surface and verify it can close without state changes | Modal, toggle, or Escape according to route | Do not read names, roles, chat text, invite links, suggestions, or shared content | `acceptance-runs.md`, then `privacy-matrix.md` if policy changes |
| P1 | More occurrence routes | `ringcentral.video.toolbar.audio-menu`, `ringcentral.video.toolbar.video-menu`, `ringcentral.video.toolbar.more` | Observed only in empty-room en-US 100% DPI state | Recapture More order in empty-room, one-participant, two-plus participant, narrow, and fullscreen variants | Escape after each menu | Do not infer hidden recording/settings state | `observation-log.md`, `acceptance-runs.md`, then `locator-matrix.md` |
| P1 | Notes and transcript | `ringcentral.video.more.notes` | Repo-tested, route variant unresolved | Open Notes from the current build route and identify direct vs nested label | Side-panel close or toggle; do not start notes | Do not read notes, transcript, or recording prompts beyond sanitized labels | `acceptance-runs.md`, then `state-matrix.md` |
| P2 | Media controls | `ringcentral.video.toolbar.audio`, `ringcentral.video.toolbar.video` | Observed labels, variant states missing | Capture Mute/Unmute and Start video/Stop video variants in a disposable meeting | Restore original mic/camera state | Avoid exposing room video or private audio device details | `acceptance-runs.md`, then `state-matrix.md` |
| P2 | Reactions and raise hand | `ringcentral.video.toolbar.react`, `ringcentral.video.toolbar.raise-hand` | Observed labels, side effects unaccepted | Open reactions without sending; raise and lower hand in disposable meeting | Escape reactions; lower hand after toggle | Reactions and hand state are visible meeting signals | `acceptance-runs.md` |
| P2 | Settings and background | `ringcentral.video.settings.video`, `ringcentral.video.settings.background`, `ringcentral.video.settings.background.blur`, `ringcentral.video.more.background`, `ringcentral.video.more.settings` | Repo-tested, close behavior unaccepted | Open each settings route, confirm panel, optionally select Blur only in demo-safe context | Settings close by X; verify return to meeting | Do not expose device names, room imagery, custom assets, or account preferences | `acceptance-runs.md`, then `locator-matrix.md` |
| P3 | Overview and explain-only context | `ringcentral.video.overview` | Backlog/explain-only | Confirm narration context still matches current meeting canvas | No UI cleanup | Do not infer participant identities or private state | `acceptance-runs.md` if manually reviewed |
```

Then add:

```markdown
## Do Not Execute Yet

| Route | Entrypoint | Reason |
| --- | --- | --- |
| Recording | `ringcentral.video.more.recording` | Recording changes meeting state and may require participant consent. Keep explain-only until confirmation and role policy exist. |
| Leave or end meeting | `ringcentral.video.toolbar.leave` | Leaving or ending a meeting is destructive. Keep explain-only until a tested confirmation workflow exists. |

## Evidence Upgrade Rules

- `Accepted` requires a dated manual/live record in `acceptance-runs.md`.
- `Observed` can come from sanitized UIA/window metadata, but does not prove click or cleanup.
- `Repo-tested` means package shape or runtime code was tested locally, not that RingCentral accepted the route live.
- `Blocked` means privacy, role, confirmation, locator, or side-effect risk prevents execution.

## Post-Run Documentation Checklist

- Update `acceptance-runs.md` first.
- Update `locator-matrix.md` when locator confidence or cleanup changes.
- Update `state-matrix.md` when UI labels or state extraction changes.
- Update `privacy-matrix.md` before expanding any sensitive route.
- Update `evidence-index.md` last so it reflects recorded evidence instead of intention.
```

- [ ] **Step 2: Run focused test**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_validation_checklist_covers_package_routes
```

Expected: still FAIL until cross-links are added to `evidence-index.md` and `source-index.md`.

---

### Task 3: Cross-Link Evidence, Source, And Runbook Docs

**Files:**
- Modify: `docs/knowledge/ringcentral-video/evidence-index.md`
- Modify: `docs/knowledge/ringcentral-video/source-index.md`
- Modify: `docs/runbooks/ringcentral-manual-acceptance.md`

- [ ] **Step 1: Update evidence index primary sources**

Add `docs/knowledge/ringcentral-video/validation-checklist-index.md` to the Primary sources list.

Add this maintenance bullet:

```markdown
- [ ] When planning a manual route run, start from `validation-checklist-index.md` and record the dated result in `acceptance-runs.md` before changing evidence levels.
```

- [ ] **Step 2: Update source index repository-local sources**

Add this row under Repository-Local Sources:

```markdown
| `docs/knowledge/ringcentral-video/validation-checklist-index.md` | Manual validation procedure | Operator-ready checklist for turning evidence gaps into privacy-safe manual runs; proof still belongs in `acceptance-runs.md`. |
```

- [ ] **Step 3: Update manual acceptance runbook**

Add this bullet near the Smoke Checklist introduction:

```markdown
- Before live route validation, open `docs/knowledge/ringcentral-video/validation-checklist-index.md` and choose the smallest target route group. Record any pass/fail evidence in `acceptance-runs.md`; runbook checkboxes are not acceptance evidence.
```

- [ ] **Step 4: Run focused test and verify GREEN**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_validation_checklist_covers_package_routes
```

Expected: PASS.

---

### Task 4: Record Implementation Evidence And Verify

**Files:**
- Create: `docs/agent-handoffs/cycle-017-implementation.md`

- [ ] **Step 1: Write implementation handoff**

Include:

```markdown
# Cycle 017 Implementation

Date: 2026-05-16

## Changes

- Added `docs/knowledge/ringcentral-video/validation-checklist-index.md`.
- Linked the checklist from evidence/source/runbook docs.
- Added a package/docs coverage test for RingCentral validation checklist drift.

## TDD Evidence

- RED: focused checklist test failed before the checklist existed or was linked.
- GREEN: focused checklist test passed after the checklist and links were added.

## Verification

- Focused package test:
- Full package test:
- Full suite:
- Diff check:

## Notes

- No live RingCentral clicks were performed.
- No route was promoted to Accepted.
- Runtime behavior and package YAML were unchanged.
```

- [ ] **Step 2: Run package tests**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py
```

Expected: PASS.

- [ ] **Step 3: Run full tests**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
```

Expected: PASS with the existing pywinauto STA warning only.

- [ ] **Step 4: Run diff check**

Run:

```powershell
git diff --check -- docs\knowledge\ringcentral-video\validation-checklist-index.md docs\knowledge\ringcentral-video\evidence-index.md docs\knowledge\ringcentral-video\source-index.md docs\runbooks\ringcentral-manual-acceptance.md tests\unit\test_material_packages.py docs\agent-handoffs\cycle-017-implementation.md
```

Expected: exit code 0.
