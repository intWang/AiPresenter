# Controller No-Op Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce unnecessary Tk status/button writes in the controller polling loop without changing automation behavior.

**Architecture:** Add small pure/controller-local helpers in `runtime/controller.py`, cover them with unit tests, and wire them into `run_controller()`.

**Tech Stack:** Python dataclasses, pytest, existing controller/view-model tests.

---

## File Structure

- Modify: `src/ai_presenter/runtime/controller.py`
  - Add status application dataclasses/helper.
  - Add idempotent button-state helper.
  - Wire helpers into `run_controller()`.
- Modify: `tests/unit/test_controller.py`
  - Add unit tests for status application and button-state helpers.
- Create: `docs/agent-handoffs/cycle-019-implementation.md`
  - Record TDD and verification.
- Create: `docs/agent-handoffs/cycle-019-review.md`
  - Record review findings.
- Create: `docs/agent-handoffs/cycle-019-summary.md`
  - Record final outcome.

No live RingCentral actions and no Tk root are required.

---

### Task 1: Status Application Tests

**Files:**
- Modify: `tests/unit/test_controller.py`

- [ ] **Step 1: Add failing imports and tests**

Add imports:

```python
from ai_presenter.runtime.controller import ControllerAppliedStatusState
from ai_presenter.runtime.controller import ControllerStatusUpdate
from ai_presenter.runtime.controller import plan_controller_status_application
```

Add tests near the existing controller status tests:

```python
def test_controller_status_application_skips_operator_refresh_when_unchanged() -> None:
    application = plan_controller_status_application(
        ControllerAppliedStatusState(status="Ready", pause_label="Pause"),
        ControllerStatusUpdate(status="Ready", pause_label="Pause"),
    )

    assert application.status_changed is False
    assert application.pause_label_changed is False
    assert application.mark_session_stopped is False
    assert application.refresh_operator_view is False
    assert application.state == ControllerAppliedStatusState(status="Ready", pause_label="Pause")


def test_controller_status_application_refreshes_when_status_or_pause_changes() -> None:
    application = plan_controller_status_application(
        ControllerAppliedStatusState(status="Running", pause_label="Pause"),
        ControllerStatusUpdate(status="Paused", pause_label="Resume"),
    )

    assert application.status_changed is True
    assert application.pause_label_changed is True
    assert application.refresh_operator_view is True
    assert application.state == ControllerAppliedStatusState(status="Paused", pause_label="Resume")


def test_controller_status_application_refreshes_for_session_stop_side_effect() -> None:
    application = plan_controller_status_application(
        ControllerAppliedStatusState(status="Ended", pause_label="Pause"),
        ControllerStatusUpdate(status="Ended", pause_label="Pause", mark_session_stopped=True),
    )

    assert application.status_changed is False
    assert application.pause_label_changed is False
    assert application.mark_session_stopped is True
    assert application.refresh_operator_view is True
```

- [ ] **Step 2: Run focused tests and verify RED**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller.py::test_controller_status_application_skips_operator_refresh_when_unchanged tests\unit\test_controller.py::test_controller_status_application_refreshes_when_status_or_pause_changes tests\unit\test_controller.py::test_controller_status_application_refreshes_for_session_stop_side_effect
```

Expected: FAIL because the helper/dataclass imports do not exist.

---

### Task 2: Status Application Implementation

**Files:**
- Modify: `src/ai_presenter/runtime/controller.py`

- [ ] **Step 1: Add dataclasses and helper**

Add near `ControllerStatusUpdate`:

```python
@dataclass(frozen=True)
class ControllerAppliedStatusState:
    status: str
    pause_label: str


@dataclass(frozen=True)
class ControllerStatusApplication:
    state: ControllerAppliedStatusState
    status_changed: bool
    pause_label_changed: bool
    mark_session_stopped: bool
    refresh_operator_view: bool


def plan_controller_status_application(
    current: ControllerAppliedStatusState,
    update: ControllerStatusUpdate,
) -> ControllerStatusApplication:
    status_changed = current.status != update.status
    pause_label_changed = current.pause_label != update.pause_label
    return ControllerStatusApplication(
        state=ControllerAppliedStatusState(
            status=update.status,
            pause_label=update.pause_label,
        ),
        status_changed=status_changed,
        pause_label_changed=pause_label_changed,
        mark_session_stopped=update.mark_session_stopped,
        refresh_operator_view=(
            status_changed or pause_label_changed or update.mark_session_stopped
        ),
    )
```

- [ ] **Step 2: Run focused tests and verify GREEN**

Run the three status application tests from Task 1.

Expected: PASS.

---

### Task 3: Button State Tests

**Files:**
- Modify: `tests/unit/test_controller.py`

- [ ] **Step 1: Add failing button helper import and tests**

Add import:

```python
from ai_presenter.runtime.controller import _apply_button_state
```

Add tests:

```python
class _FakeButton:
    def __init__(self, state: str) -> None:
        self.state = state
        self.configure_calls: list[str] = []

    def cget(self, key: str) -> str:
        assert key == "state"
        return self.state

    def configure(self, *, state: str) -> None:
        self.configure_calls.append(state)
        self.state = state


def test_apply_button_state_skips_configure_when_state_matches() -> None:
    button = _FakeButton("normal")

    changed = _apply_button_state(button, enabled=True)

    assert changed is False
    assert button.configure_calls == []


def test_apply_button_state_configures_only_on_state_change() -> None:
    button = _FakeButton("disabled")

    changed = _apply_button_state(button, enabled=True)

    assert changed is True
    assert button.configure_calls == ["normal"]
    assert button.state == "normal"
```

- [ ] **Step 2: Run focused tests and verify RED**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller.py::test_apply_button_state_skips_configure_when_state_matches tests\unit\test_controller.py::test_apply_button_state_configures_only_on_state_change
```

Expected: FAIL because `_apply_button_state` does not exist.

---

### Task 4: Button Helper And Refresh Wiring

**Files:**
- Modify: `src/ai_presenter/runtime/controller.py`

- [ ] **Step 1: Add button protocol/helper**

Add imports:

```python
from typing import Protocol
```

Add near helper functions:

```python
class _ButtonStateWidget(Protocol):
    def cget(self, key: str) -> object: ...
    def configure(self, **kwargs: object) -> None: ...


def _apply_button_state(button: _ButtonStateWidget, enabled: bool) -> bool:
    desired_state = "normal" if enabled else "disabled"
    if button.cget("state") == desired_state:
        return False
    button.configure(state=desired_state)
    return True
```

- [ ] **Step 2: Wire button helper**

Remove the nested `apply_button_state()` inside `run_controller()`.

Replace calls:

```python
apply_button_state(start_button, view_model.buttons.start_enabled)
```

with:

```python
_apply_button_state(start_button, view_model.buttons.start_enabled)
```

for all six buttons.

- [ ] **Step 3: Wire status application helper**

In `refresh_status()`, after resolving `update`, add:

```python
application = plan_controller_status_application(
    ControllerAppliedStatusState(status=status.get(), pause_label=pause_label.get()),
    update,
)
if application.mark_session_stopped:
    session.mark_stopped()
if application.status_changed:
    status.set(application.state.status)
if application.pause_label_changed:
    pause_label.set(application.state.pause_label)
if application.refresh_operator_view:
    refresh_operator_view()
root.after(500, refresh_status)
```

Remove the old unconditional `status.set`, `pause_label.set`, and `refresh_operator_view()` calls.

- [ ] **Step 4: Run focused controller tests**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller.py
```

Expected: PASS.

---

### Task 5: Implementation Handoff And Verification

**Files:**
- Create: `docs/agent-handoffs/cycle-019-implementation.md`

- [ ] **Step 1: Write implementation handoff**

Create:

```markdown
# Cycle 019 Implementation

Date: 2026-05-16

## Changes

- Added controller status no-op refresh planning helper.
- Added idempotent button-state helper.
- Wired the Tk polling loop to skip no-op status/view refreshes.

## TDD Evidence

- RED status helper tests:
- GREEN status helper tests:
- RED button helper tests:
- GREEN button helper tests:

## Verification

- Controller tests:
- Controller view-model tests:
- Full suite:
- Ruff:
- Mypy:
- Diff check:

## Notes

- No live RingCentral actions were run.
- No desktop scan threading changes were made.
- Voice readiness cache behavior is unchanged.
```

- [ ] **Step 2: Run controller tests**

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller.py tests\unit\test_controller_view_model.py
```

- [ ] **Step 3: Run full verification**

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
.\.venv\Scripts\python -m ruff check --no-cache .
.\.venv\Scripts\python -m mypy --no-incremental src tests
git diff --check -- src\ai_presenter\runtime\controller.py tests\unit\test_controller.py docs\agent-handoffs\cycle-019-implementation.md
```

Expected: all verification passes. Pytest may show the existing pywinauto STA warning.
