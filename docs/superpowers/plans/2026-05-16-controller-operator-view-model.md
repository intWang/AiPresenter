# Controller Operator View-Model Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a pure controller operator view-model and wire a compact status/buttons slice into the Tk controller.

**Architecture:** Create `src/ai_presenter/runtime/controller_view_model.py` with immutable dataclasses and one pure builder function. Keep Tk-specific work in `run_controller()` and call the view-model from `refresh_status()` and question/source callbacks.

**Tech Stack:** Python dataclasses, pytest, existing Tk controller, existing `PresenterVoiceSettings`.

---

### Task 1: Pure Controller View-Model

**Files:**
- Create: `src/ai_presenter/runtime/controller_view_model.py`
- Create: `tests/unit/test_controller_view_model.py`
- Modify: `src/ai_presenter/runtime/controller.py`
- Modify: `docs/runbooks/ringcentral-manual-acceptance.md`
- Create: `docs/agent-handoffs/cycle-005-implementation.md`

- [ ] **Step 1: Write failing view-model tests**

Create `tests/unit/test_controller_view_model.py`:

```python
from ai_presenter.runtime.controller_view_model import ControllerOperatorSnapshot
from ai_presenter.runtime.controller_view_model import ControllerSourceMode
from ai_presenter.runtime.controller_view_model import build_controller_operator_view_model
from ai_presenter.runtime.voice import PresenterVoiceSettings


def test_material_package_view_model_is_ready_and_startable() -> None:
    view_model = build_controller_operator_view_model(
        ControllerOperatorSnapshot(
            source_mode="material_package",
            material_package_id="ringcentral-video",
            material_flow_id="meeting-control-map-demo",
            running_app_label="",
            has_running_app_selection=False,
            has_scanned_running_app=False,
            scanned_package_id="",
            scanned_flow_id="",
            voice=PresenterVoiceSettings(),
            run_status="Ready",
            is_running=False,
            is_stopping=False,
            question_text="",
            last_question_outcome="",
        )
    )

    assert view_model.source_label == "Material package"
    assert view_model.target_label == "ringcentral-video"
    assert view_model.flow_label == "meeting-control-map-demo"
    assert view_model.voice_label == "English / Professional"
    assert view_model.scan_label == "Package target ready"
    assert view_model.question_label == "No question yet"
    assert view_model.buttons.start_enabled is True
    assert view_model.buttons.pause_enabled is False
    assert view_model.buttons.end_enabled is False
    assert view_model.buttons.refresh_enabled is True
    assert view_model.buttons.scan_enabled is False
    assert view_model.buttons.submit_enabled is False


def test_running_app_requires_scan_before_start_or_submit() -> None:
    view_model = build_controller_operator_view_model(
        ControllerOperatorSnapshot(
            source_mode="running_desktop_app",
            material_package_id="ringcentral-video",
            material_flow_id="meeting-control-map-demo",
            running_app_label="Demo App (Demo:10)",
            has_running_app_selection=True,
            has_scanned_running_app=False,
            scanned_package_id="",
            scanned_flow_id="",
            voice=PresenterVoiceSettings(language="zh", tone="concise"),
            run_status="Selected running app needs scanning",
            is_running=False,
            is_stopping=False,
            question_text="chat",
            last_question_outcome="",
        )
    )

    assert view_model.source_label == "Running desktop app"
    assert view_model.target_label == "Demo App (Demo:10) needs scan"
    assert view_model.flow_label == ""
    assert view_model.voice_label == "Chinese / Concise"
    assert view_model.scan_label == "Scan required"
    assert view_model.question_label == "Scan required before questions"
    assert view_model.buttons.start_enabled is False
    assert view_model.buttons.scan_enabled is True
    assert view_model.buttons.submit_enabled is False


def test_running_app_scanned_selection_is_ready() -> None:
    view_model = build_controller_operator_view_model(
        ControllerOperatorSnapshot(
            source_mode="running_desktop_app",
            material_package_id="ringcentral-video",
            material_flow_id="meeting-control-map-demo",
            running_app_label="Demo App (Demo:10)",
            has_running_app_selection=True,
            has_scanned_running_app=True,
            scanned_package_id="temp.demo.10",
            scanned_flow_id="temp-demo",
            voice=PresenterVoiceSettings(tone="conversational"),
            run_status="Ready",
            is_running=False,
            is_stopping=False,
            question_text="chat",
            last_question_outcome="Queued safe demo: temp.demo.chat",
        )
    )

    assert view_model.target_label == "temp.demo.10"
    assert view_model.flow_label == "temp-demo"
    assert view_model.scan_label == "Scanned temp.demo.10"
    assert view_model.question_label == "Queued safe demo: temp.demo.chat"
    assert view_model.buttons.start_enabled is True
    assert view_model.buttons.scan_enabled is True
    assert view_model.buttons.submit_enabled is True


def test_running_state_disables_target_churn_and_enables_controls() -> None:
    view_model = build_controller_operator_view_model(
        ControllerOperatorSnapshot(
            source_mode="material_package",
            material_package_id="ringcentral-video",
            material_flow_id="meeting-control-map-demo",
            running_app_label="",
            has_running_app_selection=False,
            has_scanned_running_app=False,
            scanned_package_id="",
            scanned_flow_id="",
            voice=PresenterVoiceSettings(),
            run_status="Running",
            is_running=True,
            is_stopping=False,
            question_text="chat",
            last_question_outcome="",
        )
    )

    assert view_model.buttons.start_enabled is False
    assert view_model.buttons.pause_enabled is True
    assert view_model.buttons.end_enabled is True
    assert view_model.buttons.refresh_enabled is False
    assert view_model.buttons.scan_enabled is False
    assert view_model.buttons.submit_enabled is True


def test_ending_state_keeps_end_visible_but_blocks_new_actions() -> None:
    view_model = build_controller_operator_view_model(
        ControllerOperatorSnapshot(
            source_mode="material_package",
            material_package_id="ringcentral-video",
            material_flow_id="meeting-control-map-demo",
            running_app_label="",
            has_running_app_selection=False,
            has_scanned_running_app=False,
            scanned_package_id="",
            scanned_flow_id="",
            voice=PresenterVoiceSettings(),
            run_status="Ending",
            is_running=True,
            is_stopping=True,
            question_text="chat",
            last_question_outcome="",
        )
    )

    assert view_model.buttons.start_enabled is False
    assert view_model.buttons.pause_enabled is False
    assert view_model.buttons.end_enabled is True
    assert view_model.buttons.refresh_enabled is False
    assert view_model.buttons.scan_enabled is False
    assert view_model.buttons.submit_enabled is False
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller_view_model.py
```

Expected: import failure because `controller_view_model.py` does not exist yet.

- [ ] **Step 3: Implement the pure module**

Create `src/ai_presenter/runtime/controller_view_model.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ai_presenter.runtime.voice import PresenterVoiceSettings

ControllerSourceMode = Literal["material_package", "running_desktop_app"]

_LANGUAGE_LABELS = {"en": "English", "zh": "Chinese"}
_TONE_LABELS = {
    "professional": "Professional",
    "conversational": "Conversational",
    "concise": "Concise",
}


@dataclass(frozen=True)
class ControllerOperatorSnapshot:
    source_mode: ControllerSourceMode
    material_package_id: str
    material_flow_id: str
    running_app_label: str
    has_running_app_selection: bool
    has_scanned_running_app: bool
    scanned_package_id: str
    scanned_flow_id: str
    voice: PresenterVoiceSettings
    run_status: str
    is_running: bool
    is_stopping: bool
    question_text: str
    last_question_outcome: str


@dataclass(frozen=True)
class ControllerButtonStates:
    start_enabled: bool
    pause_enabled: bool
    end_enabled: bool
    refresh_enabled: bool
    scan_enabled: bool
    submit_enabled: bool


@dataclass(frozen=True)
class ControllerOperatorViewModel:
    source_label: str
    target_label: str
    flow_label: str
    voice_label: str
    scan_label: str
    run_label: str
    question_label: str
    buttons: ControllerButtonStates


def build_controller_operator_view_model(
    snapshot: ControllerOperatorSnapshot,
) -> ControllerOperatorViewModel:
    target_ready = _target_ready(snapshot)
    question_text_present = bool(snapshot.question_text.strip())
    can_start_new_action = not snapshot.is_running and not snapshot.is_stopping

    return ControllerOperatorViewModel(
        source_label=_source_label(snapshot.source_mode),
        target_label=_target_label(snapshot),
        flow_label=_flow_label(snapshot),
        voice_label=render_voice_label(snapshot.voice),
        scan_label=_scan_label(snapshot),
        run_label=snapshot.run_status,
        question_label=_question_label(snapshot),
        buttons=ControllerButtonStates(
            start_enabled=can_start_new_action and target_ready,
            pause_enabled=snapshot.is_running and not snapshot.is_stopping,
            end_enabled=snapshot.is_running or snapshot.is_stopping,
            refresh_enabled=not snapshot.is_running and not snapshot.is_stopping,
            scan_enabled=(
                snapshot.source_mode == "running_desktop_app"
                and snapshot.has_running_app_selection
                and can_start_new_action
            ),
            submit_enabled=(
                question_text_present
                and target_ready
                and not snapshot.is_stopping
            ),
        ),
    )


def render_voice_label(voice: PresenterVoiceSettings) -> str:
    return f"{_LANGUAGE_LABELS[voice.language]} / {_TONE_LABELS[voice.tone]}"


def _source_label(source_mode: ControllerSourceMode) -> str:
    if source_mode == "running_desktop_app":
        return "Running desktop app"
    return "Material package"


def _target_ready(snapshot: ControllerOperatorSnapshot) -> bool:
    if snapshot.source_mode == "material_package":
        return bool(snapshot.material_package_id and snapshot.material_flow_id)
    return snapshot.has_running_app_selection and snapshot.has_scanned_running_app


def _target_label(snapshot: ControllerOperatorSnapshot) -> str:
    if snapshot.source_mode == "material_package":
        return snapshot.material_package_id
    if snapshot.has_scanned_running_app and snapshot.scanned_package_id:
        return snapshot.scanned_package_id
    label = snapshot.running_app_label or "No running app selected"
    return f"{label} needs scan" if snapshot.has_running_app_selection else label


def _flow_label(snapshot: ControllerOperatorSnapshot) -> str:
    if snapshot.source_mode == "material_package":
        return snapshot.material_flow_id
    return snapshot.scanned_flow_id if snapshot.has_scanned_running_app else ""


def _scan_label(snapshot: ControllerOperatorSnapshot) -> str:
    if snapshot.source_mode == "material_package":
        return "Package target ready"
    if not snapshot.has_running_app_selection:
        return "No running app selected"
    if snapshot.has_scanned_running_app and snapshot.scanned_package_id:
        return f"Scanned {snapshot.scanned_package_id}"
    return "Scan required"


def _question_label(snapshot: ControllerOperatorSnapshot) -> str:
    if snapshot.last_question_outcome:
        return snapshot.last_question_outcome
    if (
        snapshot.source_mode == "running_desktop_app"
        and snapshot.question_text.strip()
        and not _target_ready(snapshot)
    ):
        return "Scan required before questions"
    return "No question yet"
```

- [ ] **Step 4: Run focused view-model tests and verify GREEN**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller_view_model.py
```

Expected: all tests pass.

- [ ] **Step 5: Wire the Tk controller minimally**

In `src/ai_presenter/runtime/controller.py`:

1. Import from the new module:

```python
from ai_presenter.runtime.controller_view_model import ControllerOperatorSnapshot
from ai_presenter.runtime.controller_view_model import build_controller_operator_view_model
from ai_presenter.runtime.controller_view_model import render_voice_label
```

2. Remove the local `_LANGUAGE_LABELS`, `_TONE_LABELS`, and `render_voice_label()` definitions from `controller.py`.

3. Add a new `operator_summary = tk.StringVar(value="Target ready")` and `last_question_outcome = ""` local variable in `run_controller()`.

4. Store button widgets in locals:

```python
refresh_button = tk.Button(...)
scan_button = tk.Button(...)
start_button = tk.Button(...)
pause_button = tk.Button(...)
end_button = tk.Button(...)
submit_button = tk.Button(...)
```

5. Add a compact label below the status label:

```python
tk.Label(frame, textvariable=operator_summary, anchor="w").pack(fill="x", pady=(0, 12))
```

6. Add helper functions inside `run_controller()`:

```python
def source_mode() -> str:
    return "running_desktop_app" if source.get() == "Running desktop app" else "material_package"


def apply_button_state(button: tk.Button, enabled: bool) -> None:
    button.configure(state="normal" if enabled else "disabled")


def refresh_operator_view() -> None:
    view_model = build_controller_operator_view_model(
        ControllerOperatorSnapshot(
            source_mode=source_mode(),
            material_package_id=material_package.app_id,
            material_flow_id=flow_id,
            running_app_label=app_choice.get(),
            has_running_app_selection=selected_running_window() is not None,
            has_scanned_running_app=scan_state.has_scanned_selection,
            scanned_package_id=scanned_package_id,
            scanned_flow_id=scanned_flow_id,
            voice=current_voice(),
            run_status=status.get(),
            is_running=controller.is_running,
            is_stopping=controller.is_stopping,
            question_text=question.get(),
            last_question_outcome=last_question_outcome,
        )
    )
    operator_summary.set(
        f"{view_model.source_label} | Target: {view_model.target_label} | "
        f"Flow: {view_model.flow_label or '-'} | Voice: {view_model.voice_label} | "
        f"Scan: {view_model.scan_label} | Question: {view_model.question_label}"
    )
    apply_button_state(start_button, view_model.buttons.start_enabled)
    apply_button_state(pause_button, view_model.buttons.pause_enabled)
    apply_button_state(end_button, view_model.buttons.end_enabled)
    apply_button_state(refresh_button, view_model.buttons.refresh_enabled)
    apply_button_state(scan_button, view_model.buttons.scan_enabled)
    apply_button_state(submit_button, view_model.buttons.submit_enabled)
```

7. Call `refresh_operator_view()` at the end of `sync_target_choice()`, `choose_running_app()`, `refresh_running_windows()`, `scan_selected_app()`, `start()`, `pause_or_resume()`, `end()`, `submit_question()`, and `refresh_status()`. Avoid calling it before button variables are created; initial UI refresh still happens after widget creation.

8. In `submit_question()`, declare `nonlocal last_question_outcome` and set it after `result = controller.submit_question(text)`:

```python
last_question_outcome = describe_question_result(result)
status.set(last_question_outcome)
```

9. After creating `question_entry`, refresh the view as the user types:

```python
question.trace_add("write", lambda *_args: refresh_operator_view())
```

- [ ] **Step 6: Run focused controller tests**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller.py tests\unit\test_controller_view_model.py
```

Expected: all focused tests pass.

- [ ] **Step 7: Update manual acceptance runbook**

In `docs/runbooks/ringcentral-manual-acceptance.md`, add Cycle 005 checks for:

- Operator summary shows source, target, flow, voice, scan state, and question outcome.
- Start is disabled while running.
- Refresh/Scan are disabled while running.
- Running-app question submit is disabled or blocked before scan.
- Pause/End enablement matches running/ending state.

- [ ] **Step 8: Write implementation handoff**

Create `docs/agent-handoffs/cycle-005-implementation.md` with:

```markdown
# Cycle 005 Implementation Handoff

Date: 2026-05-16

## Change

Added a pure controller operator view-model and wired a compact operator summary/button state slice into the Tk controller.

## Tests

- RED: view-model tests failed because the module did not exist.
- GREEN: view-model tests passed after implementation.
- Focused controller tests passed.

## Remaining Risk

- Tk visual behavior still needs manual acceptance.
- Current/next demo step display remains out of scope.
```

- [ ] **Step 9: Run full verification**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
```

Expected: full test suite passes with only the known `pywinauto` STA COM threading warning.
