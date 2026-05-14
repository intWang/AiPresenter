# Adaptive Demo Controller Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make RingCentral Video demos adjust to the live meeting state and add a minimal local Start/Pause/End controller for AiPresenter.

**Architecture:** Keep package scripts as the primary source of truth, but add a small runtime adjustment layer that captures the RingCentralVideo window before each demo step and can skip or rewrite a step based on extracted `MeetingState`. Add a generic `DemoControl` object consumed at step boundaries by the synchronized timeline runner, then expose it through a Tkinter controller command.

**Tech Stack:** Python, pytest, Tkinter from the standard library, existing AiPresenter package demo runtime.

---

### Task 1: Adaptive RingCentral Demo Step Adjustment

**Files:**
- Create: `src/ai_presenter/runtime/adaptive_demo.py`
- Test: `tests/unit/test_adaptive_demo.py`
- Modify: `src/ai_presenter/runtime/factory.py`

- [ ] **Step 1: Write failing tests**

Cover:

- `participant_count >= 2` skips the empty-room Add coworkers step.
- `participant_count >= 2` rewrites Invite narration to describe adding more people to an active meeting.
- Unrelated steps stay unchanged.

- [ ] **Step 2: Implement minimal adjustment function**

Add `adjust_ringcentral_demo_step(step, state)` returning `DemoStep | None`.

- [ ] **Step 3: Capture and adjust before each step**

In `run_material_demo`, call `desktop.capture(handle, profile.observe.sources)`, `create_adapter(profile).extract_state(observation)`, then adjust the step before running it.

### Task 2: Step-Boundary Demo Control

**Files:**
- Create: `src/ai_presenter/runtime/control.py`
- Test: `tests/unit/test_demo_control.py`
- Modify: `src/ai_presenter/runtime/sync.py`

- [ ] **Step 1: Write failing tests**

Cover:

- Pause blocks before a step and resumes when unpaused.
- End skips remaining work at step boundary.

- [ ] **Step 2: Implement `DemoControl`**

Use `threading.Event` to model pause/resume and stop.

- [ ] **Step 3: Wire into `SynchronizedTimelineRunner`**

Check the control before each step. Do not interrupt audio mid-sentence in this first version.

### Task 3: Tkinter Controller Command

**Files:**
- Create: `src/ai_presenter/runtime/controller.py`
- Test: `tests/unit/test_cli.py`
- Modify: `src/ai_presenter/cli.py`

- [ ] **Step 1: Add CLI test**

Use monkeypatching to assert `ai-presenter controller --profile ... --package ... --flow ... --dry-run` loads inputs without opening the UI.

- [ ] **Step 2: Implement controller launcher**

Add a Tkinter window with Start, Pause/Resume, and End buttons. Start runs the demo on a background thread with a shared `DemoControl`.

### Task 4: Verification

Run:

`.venv\Scripts\python.exe -m pytest tests\unit\test_adaptive_demo.py tests\unit\test_demo_control.py tests\unit\test_cli.py -q --no-cov`

Then:

`.venv\Scripts\python.exe -m pytest -q --no-cov`

Then:

`.venv\Scripts\ai-presenter.exe controller --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --dry-run`
