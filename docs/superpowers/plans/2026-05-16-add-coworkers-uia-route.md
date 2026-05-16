# Add Coworkers UIA Route Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the RingCentral Video `Add coworkers` coordinate route with the UIA button route observed in Cycle 003.

**Architecture:** Keep the route change inside the material package YAML; the existing `PackageActionExecutor` already supports `clickWindowControl`, `controlType`, and `cleanup`. Add one package regression test so future package edits cannot silently move this entrypoint back to a fragile coordinate route.

**Tech Stack:** Python, pytest, Pydantic package loader, YAML material package, Windows UI Automation route metadata.

---

### Task 1: Add Coworkers Package Route

**Files:**
- Modify: `tests/unit/test_material_packages.py`
- Modify: `packages/ringcentral-video.yaml`
- Modify: `docs/knowledge/ringcentral-video/locator-matrix.md`
- Modify: `docs/knowledge/ringcentral-video/acceptance-runs.md`
- Create: `docs/agent-handoffs/cycle-004-implementation.md`

- [ ] **Step 1: Write the failing package regression test**

Add this test near the other RingCentral package tests in `tests/unit/test_material_packages.py`:

```python
def test_ringcentral_add_coworkers_uses_observed_uia_button_route() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    entrypoint = package.entrypoint_by_id("ringcentral.video.main.add-coworkers")

    assert len(entrypoint.open_steps) == 1
    step = entrypoint.open_steps[0]
    assert step.action == "clickWindowControl"
    assert step.target == "Add coworkers"
    assert step.match["controlType"] == "button"
    assert step.match["cleanup"] == "modal"
```

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_add_coworkers_uses_observed_uia_button_route
```

Expected: failure because the current package still uses `clickWindowRelative`.

- [ ] **Step 3: Update the YAML route**

In `packages/ringcentral-video.yaml`, change `ringcentral.video.main.add-coworkers` from:

```yaml
  - action: clickWindowRelative
    target: Add coworkers
    match:
      x: '461'
      y: '462'
      cleanup: modal
```

to:

```yaml
  - action: clickWindowControl
    target: Add coworkers
    match:
      controlType: button
      cleanup: modal
```

- [ ] **Step 4: Run focused package tests and verify GREEN**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py
```

Expected: all tests in `test_material_packages.py` pass.

- [ ] **Step 5: Update RingCentral knowledge docs**

In `docs/knowledge/ringcentral-video/locator-matrix.md`, update the `ringcentral.video.main.add-coworkers` row so the locator type is `UIA Add coworkers button`, confidence remains scoped, and the verification need says to manually validate modal close on live RingCentral.

In `docs/knowledge/ringcentral-video/acceptance-runs.md`, add a Cycle 004 automated baseline note explaining that the package route was changed based on Cycle 003 UIA evidence, but no click/manual modal validation was performed in Cycle 004.

- [ ] **Step 6: Write implementation handoff**

Create `docs/agent-handoffs/cycle-004-implementation.md` with:

```markdown
# Cycle 004 Implementation Handoff

Date: 2026-05-16

## Change

Replaced `ringcentral.video.main.add-coworkers` with a UIA `Add coworkers` button route.

## Evidence Used

- Cycle 003 observed `Add coworkers` as a `ButtonControl` at `(1029, 493, 1329, 541)`.
- Existing executor support for `clickWindowControl` handles target, occurrence, control type, and cleanup.

## Tests

- RED: focused package test failed while route was still `clickWindowRelative`.
- GREEN: focused package tests passed after YAML update.

## Remaining Risk

- Route has not been clicked in a live meeting during Cycle 004.
- Modal cleanup still needs live manual validation.
```

- [ ] **Step 7: Run full verification**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
```

Expected: full test suite passes with only the known `pywinauto` STA COM threading warning.
