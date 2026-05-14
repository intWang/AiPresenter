# RingCentral Meeting Control Map Demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add and run a new RingCentral Video demo flow that teaches Meeting controls as a coherent map: status, people, media, interaction, advanced tools, and closeout.

**Architecture:** Keep the demo as data in `packages/ringcentral-video.yaml` using existing operation entrypoints and synchronized narration placements. Tests assert the new flow exists, uses English narration, avoids destructive clicks, and keeps open/toggle actions synchronized during narration.

**Tech Stack:** Python, PyYAML material package models, pytest, existing AiPresenter demo CLI.

---

### Task 1: Material Package Test

**Files:**
- Modify: `tests/unit/test_material_packages.py`

- [ ] **Step 1: Write the failing test**

Add assertions that `meeting-control-map-demo` exists, starts with overview, ends with a summary, includes the required feature areas, and uses `during` placement for visible open/toggle actions.

- [ ] **Step 2: Run the test to verify it fails**

Run: `.venv\Scripts\python.exe -m pytest tests\unit\test_material_packages.py::test_loads_ringcentral_video_app_material_package -q --no-cov`

Expected: FAIL because `meeting-control-map-demo` does not exist yet.

### Task 2: Add Demo Flow

**Files:**
- Modify: `packages/ringcentral-video.yaml`

- [ ] **Step 1: Add `meeting-control-map-demo`**

Add a flow with the approved structure:

1. Meeting overview.
2. Top status: meeting info, network quality, view layout, report issue.
3. People and communication: add coworkers, participants, chat.
4. Media readiness: microphone, audio menu, camera, camera menu, share.
5. Lightweight interaction: reactions, raise hand.
6. Advanced tools: more, recording, notes, background, settings, leave.
7. Closing summary.

- [ ] **Step 2: Run the focused test to verify it passes**

Run: `.venv\Scripts\python.exe -m pytest tests\unit\test_material_packages.py::test_loads_ringcentral_video_app_material_package -q --no-cov`

Expected: PASS.

### Task 3: Verification And Demo

**Files:**
- No code changes expected.

- [ ] **Step 1: Dry-run the new flow**

Run: `.venv\Scripts\ai-presenter.exe demo --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --dry-run`

Expected: loads profile, package, and flow.

- [ ] **Step 2: Run full tests**

Run: `.venv\Scripts\python.exe -m pytest -q --no-cov`

Expected: all tests pass.

- [ ] **Step 3: Demonstrate**

If a visible `RingCentralVideoClass` meeting window exists, run:

`.venv\Scripts\ai-presenter.exe demo --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --debug`

If no visible meeting window exists, start or ask the user to open a meeting window first, then rerun the command.
