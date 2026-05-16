# RingCentral Knowledge Package Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a companion RingCentralVideo knowledge package that records sources, observations, locators, states, privacy policies, and acceptance evidence without changing runtime behavior.

**Architecture:** Keep `packages/ringcentral-video.yaml` unchanged and add documentation under `docs/knowledge/ringcentral-video/`. Use official RingCentral pages for product taxonomy and local repo artifacts for executable/verified behavior. Use handoff docs under `docs/agent-handoffs/` for cycle coordination, review, and next steps.

**Tech Stack:** Markdown documentation, existing YAML package knowledge, RingCentral support docs, pytest/ruff/mypy verification for no-regression confidence.

---

## File Structure

- Create `docs/knowledge/ringcentral-video/source-index.md`
  - Index official and local sources and map them to package areas.
- Create `docs/knowledge/ringcentral-video/observation-log.md`
  - Provide an append-only observation template and seed observations from current repo evidence.
- Create `docs/knowledge/ringcentral-video/locator-matrix.md`
  - Capture current locator routes, cleanup modes, confidence, and verification gaps.
- Create `docs/knowledge/ringcentral-video/state-matrix.md`
  - Capture adapter-known states, package-known states, and missing RingCentral states.
- Create `docs/knowledge/ringcentral-video/privacy-matrix.md`
  - Centralize privacy and safety rules.
- Create `docs/knowledge/ringcentral-video/acceptance-runs.md`
  - Record automated baseline and manual acceptance template.
- Create `docs/agent-handoffs/cycle-002-coordination.md`
  - Record cycle scope and agent assignments.
- Create `docs/agent-handoffs/cycle-002-review.md`
  - Record independent review findings.

---

### Task 1: Source And Observation Docs

**Files:**
- Create: `docs/knowledge/ringcentral-video/source-index.md`
- Create: `docs/knowledge/ringcentral-video/observation-log.md`

- [ ] **Step 1: Create source index**

Include official sources for:

- RingCentral Video introduction.
- In-meeting controls.
- Attendee controls.
- Host controls.
- Meeting settings.

Include local sources:

- `packages/ringcentral-video.yaml`
- `src/ai_presenter/adapters/ringcentral.py`
- `docs/runbooks/ringcentral-manual-acceptance.md`
- Relevant specs, plans, tests, and Cycle 000/001 handoffs.

- [ ] **Step 2: Create observation log**

Seed it with current repo-derived observations and a template for future manual observations. Do not invent a live app version/build.

### Task 2: Locator And State Matrices

**Files:**
- Create: `docs/knowledge/ringcentral-video/locator-matrix.md`
- Create: `docs/knowledge/ringcentral-video/state-matrix.md`

- [ ] **Step 1: Create locator matrix**

Group current package entrypoints by locator risk:

- Explain-only.
- UIA control target.
- UIA control target with occurrence.
- Coordinate fallback.
- Multi-step route.
- Modal/side-panel/settings cleanup.

- [ ] **Step 2: Create state matrix**

Separate:

- Adapter-detected states.
- Package/demo states.
- Runbook/manual states.
- Missing or weakly verified states.

### Task 3: Privacy And Acceptance Docs

**Files:**
- Create: `docs/knowledge/ringcentral-video/privacy-matrix.md`
- Create: `docs/knowledge/ringcentral-video/acceptance-runs.md`

- [ ] **Step 1: Create privacy matrix**

Centralize rules for shared screen, chat, participants, invite links, meeting IDs, recording, notes/transcripts, captions, host controls, security/waiting room, and leave/end.

- [ ] **Step 2: Create acceptance runs template**

Add automated command baseline and manual acceptance record fields: date, tester, app build, OS, locale, DPI, monitor setup, meeting state, role, participant count, evidence files, failures, recovery.

### Task 4: Review And Verification

**Files:**
- Create: `docs/agent-handoffs/cycle-002-coordination.md`
- Create: `docs/agent-handoffs/cycle-002-review.md`

- [ ] **Step 1: Create coordination handoff**

Record scope, sources, write targets, and verification expectations.

- [ ] **Step 2: Run verification**

Run:

```powershell
Get-ChildItem -LiteralPath docs\knowledge\ringcentral-video | Select-Object -ExpandProperty Name
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
```

Expected:

- All six knowledge docs exist.
- Full no-coverage tests pass.

- [ ] **Step 3: Request independent review**

Dispatch a subagent to review the knowledge docs against Cycle 000/001 findings and official source scope.

---

## Self-Review Checklist

- Spec coverage: all design goals map to Tasks 1-4.
- Placeholder scan: docs must use explicit "Unknown until observed" instead of empty placeholders.
- Scope check: documentation-only; no runtime behavior changes.
- Source discipline: official docs are product taxonomy; local observations/tests are automation evidence.
