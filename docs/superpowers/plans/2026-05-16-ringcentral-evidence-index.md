# RingCentral Evidence Index Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a maintainable evidence index that connects RingCentral Video package entrypoints to observations, locator confidence, privacy policy, acceptance evidence, and next validation targets.

**Architecture:** Add a documentation-only index under `docs/knowledge/ringcentral-video/`. Keep existing source documents authoritative and reference them from the index. Verify coverage with lightweight text checks and package entrypoint enumeration.

**Tech Stack:** Markdown docs, PowerShell, Python package loader for entrypoint ID checks.

---

## File Structure

- Create `docs/knowledge/ringcentral-video/evidence-index.md`
  - Evidence levels.
  - Validation priority queue.
  - Entry point coverage table.
  - Surface evidence notes.
  - Maintenance checklist.
- Optionally modify `docs/knowledge/ringcentral-video/source-index.md`
  - Add the evidence index as a repo-local source if useful.
- Create `docs/agent-handoffs/cycle-010-implementation.md`
- Create `docs/agent-handoffs/cycle-010-review.md`
- Create `docs/agent-handoffs/cycle-010-summary.md`

## Tasks

### Task 1: Build Evidence Index

**Files:**

- Create: `docs/knowledge/ringcentral-video/evidence-index.md`

- [ ] **Step 1: Enumerate package entrypoints**

Run:

```powershell
@'
from pathlib import Path
from ai_presenter.packages.loader import load_material_package
p = load_material_package(Path("packages/ringcentral-video.yaml"))
for entrypoint in p.operation_entrypoints:
    print(entrypoint.id)
'@ | .\.venv\Scripts\python -
```

Expected: 27 entrypoint IDs.

- [ ] **Step 2: Draft the index**

Create `evidence-index.md` with:

- Evidence level legend.
- Top validation targets table.
- Entry point evidence table covering every package entrypoint ID.
- Surface-level privacy and observation references.
- Maintenance checklist for future live observations.

- [ ] **Step 3: Self-check coverage**

Run a Python check that every entrypoint ID appears in the evidence index:

```powershell
@'
from pathlib import Path
from ai_presenter.packages.loader import load_material_package
p = load_material_package(Path("packages/ringcentral-video.yaml"))
text = Path("docs/knowledge/ringcentral-video/evidence-index.md").read_text(encoding="utf-8")
missing = [entrypoint.id for entrypoint in p.operation_entrypoints if entrypoint.id not in text]
print("missing=", missing)
raise SystemExit(1 if missing else 0)
'@ | .\.venv\Scripts\python -
```

Expected: `missing= []`.

### Task 2: Doc Integrity Checks

**Files:**

- Modify: `docs/knowledge/ringcentral-video/evidence-index.md` if checks find issues.

- [ ] **Step 1: Placeholder scan**

Run:

```powershell
rg -n "TODO|TBD|PLACEHOLDER" docs\knowledge\ringcentral-video\evidence-index.md
```

Expected: no matches.

- [ ] **Step 2: Link target smoke check**

Run:

```powershell
Test-Path docs\knowledge\ringcentral-video\locator-matrix.md
Test-Path docs\knowledge\ringcentral-video\observation-log.md
Test-Path docs\knowledge\ringcentral-video\privacy-matrix.md
Test-Path docs\knowledge\ringcentral-video\acceptance-runs.md
Test-Path docs\runbooks\ringcentral-manual-acceptance.md
```

Expected: all `True`.

- [ ] **Step 3: Review scoped diff**

Run:

```powershell
git diff -- docs\knowledge\ringcentral-video\evidence-index.md
```

Expected: index content only.

### Task 3: Review And Summary

**Files:**

- Create: `docs/agent-handoffs/cycle-010-implementation.md`
- Create: `docs/agent-handoffs/cycle-010-review.md`
- Create: `docs/agent-handoffs/cycle-010-summary.md`

- [ ] **Step 1: Write implementation handoff**

Record the index structure, source docs used, and verification commands.

- [ ] **Step 2: Request read-only review**

Ask a subagent to verify entrypoint coverage, evidence/source consistency, and whether the index creates any misleading acceptance claims.

- [ ] **Step 3: Write summary**

Record review result, checks, and next live acceptance target.
