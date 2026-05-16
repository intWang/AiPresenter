# Controller Disabled Action Reasons Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Explain why controller Start and Submit actions are disabled by adding pure view-model reason fields and rendering them compactly in the existing Tk summary.

**Architecture:** Keep action availability logic in `controller_view_model.py`, next to the existing button enablement predicates. Preserve `ControllerButtonStates` as the stable boolean API, add `ControllerDisabledActionReasons` as additional display output, and make `controller.py` render those reasons without deriving state from Tk widgets.

**Tech Stack:** Python dataclasses, existing Tk controller, pytest, ruff, mypy.

---

## File Structure

- Modify `src/ai_presenter/runtime/controller_view_model.py`: add the disabled-reason dataclass, helper functions, and view-model field.
- Modify `src/ai_presenter/runtime/controller.py`: append action reasons to the existing `operator_summary` only when reasons exist.
- Modify `tests/unit/test_controller_view_model.py`: add focused pure tests for disabled-action reason strings and preserve existing button-state assertions.
- Create `docs/agent-handoffs/cycle-020-implementation.md`: implementation handoff with changed paths and verification evidence.

## Task 1: Add Pure Disabled-Action Reasons

**Files:**

- Modify: `tests/unit/test_controller_view_model.py`
- Modify: `src/ai_presenter/runtime/controller_view_model.py`

- [ ] **Step 1: Write failing view-model tests**

Add these tests to `tests/unit/test_controller_view_model.py`:

```python
def test_ready_material_package_has_no_start_reason_and_submit_needs_question() -> None:
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
            voice_readiness=None,
            run_status="Ready",
            is_running=False,
            is_stopping=False,
            question_text="",
            last_question_outcome="",
        )
    )

    assert view_model.buttons.start_enabled is True
    assert view_model.disabled_reasons.start == ""
    assert view_model.buttons.submit_enabled is False
    assert view_model.disabled_reasons.submit == "Type a question to enable Submit."
```

```python
def test_missing_voice_assets_explain_start_and_submit_disabled() -> None:
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
            voice=PresenterVoiceSettings(language="zh", tone="friendly"),
            voice_readiness=ControllerVoiceReadiness(
                status="FAIL",
                label="FAIL",
                detail="speech=windows-sapi-zh requires installed SAPI voice matching Huihui",
            ),
            run_status="Ready",
            is_running=False,
            is_stopping=False,
            question_text="chat",
            last_question_outcome="",
        )
    )

    assert view_model.buttons.start_enabled is False
    assert view_model.buttons.submit_enabled is False
    assert "Selected voice assets are not ready" in view_model.disabled_reasons.start
    assert "Huihui" in view_model.disabled_reasons.start
    assert "Selected voice assets are not ready" in view_model.disabled_reasons.submit
    assert "Huihui" in view_model.disabled_reasons.submit
```

```python
def test_running_app_unscanned_explains_start_and_submit_scan_required() -> None:
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
            voice=PresenterVoiceSettings(),
            voice_readiness=None,
            run_status="Selected running app needs scanning",
            is_running=False,
            is_stopping=False,
            question_text="chat",
            last_question_outcome="",
        )
    )

    assert view_model.buttons.start_enabled is False
    assert view_model.disabled_reasons.start == "Scan the selected running app first."
    assert view_model.buttons.submit_enabled is False
    assert view_model.disabled_reasons.submit == (
        "Scan the selected running app before questions."
    )
```

```python
def test_running_app_without_selection_explains_select_app_before_actions() -> None:
    view_model = build_controller_operator_view_model(
        ControllerOperatorSnapshot(
            source_mode="running_desktop_app",
            material_package_id="ringcentral-video",
            material_flow_id="meeting-control-map-demo",
            running_app_label="No running apps found",
            has_running_app_selection=False,
            has_scanned_running_app=False,
            scanned_package_id="",
            scanned_flow_id="",
            voice=PresenterVoiceSettings(),
            voice_readiness=None,
            run_status="Ready",
            is_running=False,
            is_stopping=False,
            question_text="chat",
            last_question_outcome="",
        )
    )

    assert view_model.buttons.start_enabled is False
    assert view_model.disabled_reasons.start == "Select a running app, then scan it."
    assert view_model.buttons.submit_enabled is False
    assert view_model.disabled_reasons.submit == (
        "Select and scan a running app before questions."
    )
```

```python
def test_running_state_explains_start_disabled_but_allows_submit() -> None:
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
            voice_readiness=None,
            run_status="Running",
            is_running=True,
            is_stopping=False,
            question_text="chat",
            last_question_outcome="",
        )
    )

    assert view_model.buttons.start_enabled is False
    assert view_model.disabled_reasons.start == "Demo is already running."
    assert view_model.buttons.submit_enabled is True
    assert view_model.disabled_reasons.submit == ""
```

```python
def test_ending_state_explains_start_and_submit_disabled() -> None:
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
            voice_readiness=None,
            run_status="Ending",
            is_running=True,
            is_stopping=True,
            question_text="chat",
            last_question_outcome="",
        )
    )

    assert view_model.buttons.start_enabled is False
    assert view_model.disabled_reasons.start == "Controller is ending; wait for Ended."
    assert view_model.buttons.submit_enabled is False
    assert view_model.disabled_reasons.submit == "Controller is ending; wait for Ended."
```

- [ ] **Step 2: Run the new tests and verify RED**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller_view_model.py
```

Expected: the new tests fail with an `AttributeError` or equivalent because `ControllerOperatorViewModel` has no `disabled_reasons` field yet.

- [ ] **Step 3: Implement the minimal view-model support**

In `src/ai_presenter/runtime/controller_view_model.py`, add:

```python
@dataclass(frozen=True)
class ControllerDisabledActionReasons:
    start: str = ""
    submit: str = ""
```

Add `disabled_reasons: ControllerDisabledActionReasons` to `ControllerOperatorViewModel`.

Inside `build_controller_operator_view_model()`, compute:

```python
disabled_reasons = ControllerDisabledActionReasons(
    start=_start_disabled_reason(snapshot, target_ready, voice_ready),
    submit=_submit_disabled_reason(
        snapshot,
        target_ready,
        voice_ready,
        question_text_present,
    ),
)
```

Return `disabled_reasons=disabled_reasons` in the view model.

Add helper functions:

```python
def _start_disabled_reason(
    snapshot: ControllerOperatorSnapshot,
    target_ready: bool,
    voice_ready: bool,
) -> str:
    if snapshot.is_stopping:
        return "Controller is ending; wait for Ended."
    if snapshot.is_running:
        return "Demo is already running."
    if snapshot.source_mode == "running_desktop_app":
        if not snapshot.has_running_app_selection:
            return "Select a running app, then scan it."
        if not snapshot.has_scanned_running_app:
            return "Scan the selected running app first."
    elif not target_ready:
        return "Select a material package and flow."
    if not voice_ready:
        return _voice_disabled_reason(snapshot.voice_readiness)
    return ""


def _submit_disabled_reason(
    snapshot: ControllerOperatorSnapshot,
    target_ready: bool,
    voice_ready: bool,
    question_text_present: bool,
) -> str:
    if snapshot.is_stopping:
        return "Controller is ending; wait for Ended."
    if not question_text_present:
        return "Type a question to enable Submit."
    if snapshot.source_mode == "running_desktop_app":
        if not snapshot.has_running_app_selection:
            return "Select and scan a running app before questions."
        if not snapshot.has_scanned_running_app:
            return "Scan the selected running app before questions."
    elif not target_ready:
        return "Select a material package and flow."
    if not voice_ready:
        return _voice_disabled_reason(snapshot.voice_readiness)
    return ""


def _voice_disabled_reason(readiness: ControllerVoiceReadiness | None) -> str:
    return f"Selected voice assets are not ready: {_voice_readiness_label(readiness)}"
```

- [ ] **Step 4: Run focused tests and verify GREEN**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller_view_model.py
```

Expected: all `test_controller_view_model.py` tests pass.

## Task 2: Render Reasons In The Existing Controller Summary

**Files:**

- Modify: `src/ai_presenter/runtime/controller.py`
- Modify: `tests/unit/test_controller_view_model.py` only if a pure summary helper is introduced; otherwise leave tests from Task 1 as the coverage seam.

- [ ] **Step 1: Add a tiny summary formatter or inline rendering**

In `run_controller().refresh_operator_view()`, after building `view_model`, collect action reason text:

```python
action_reasons = []
if view_model.disabled_reasons.start:
    action_reasons.append(f"Start blocked: {view_model.disabled_reasons.start}")
if view_model.disabled_reasons.submit:
    action_reasons.append(f"Submit blocked: {view_model.disabled_reasons.submit}")
actions_label = f" | Actions: {'; '.join(action_reasons)}" if action_reasons else ""
```

Append `actions_label` to the existing `operator_summary.set(...)` string:

```python
operator_summary.set(
    f"{view_model.source_label} | Target: {view_model.target_label} | "
    f"Flow: {view_model.flow_label or '-'} | Voice: {view_model.voice_label} | "
    f"Voice assets: {view_model.voice_readiness_label} | "
    f"Scan: {view_model.scan_label} | Question: {view_model.question_label}"
    f"{actions_label}"
)
```

- [ ] **Step 2: Run controller/view-model focused tests**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller.py tests\unit\test_controller_view_model.py
```

Expected: focused controller and view-model tests pass.

## Task 3: Verify And Record Handoff

**Files:**

- Create: `docs/agent-handoffs/cycle-020-implementation.md`

- [ ] **Step 1: Run lint/type/full checks**

Run:

```powershell
.\.venv\Scripts\python -m ruff check --no-cache src\ai_presenter\runtime\controller_view_model.py src\ai_presenter\runtime\controller.py tests\unit\test_controller_view_model.py tests\unit\test_controller.py
.\.venv\Scripts\python -m mypy --no-incremental src tests
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q
git diff --check -- src\ai_presenter\runtime\controller_view_model.py src\ai_presenter\runtime\controller.py tests\unit\test_controller_view_model.py tests\unit\test_controller.py docs\agent-handoffs\cycle-020-implementation.md
```

Expected:

- Ruff passes.
- Mypy passes.
- Full pytest passes.
- Diff check is clean except possible CRLF warnings already present in the workspace.

- [ ] **Step 2: Write implementation handoff**

Create `docs/agent-handoffs/cycle-020-implementation.md` with:

```markdown
# Cycle 020 Implementation Handoff

## Summary

- Added pure disabled-action reasons for controller Start and Submit.
- Rendered disabled reasons in the existing operator summary when present.
- Preserved existing button-state behavior and controller guards.

## Changed Paths

- `src/ai_presenter/runtime/controller_view_model.py`
- `src/ai_presenter/runtime/controller.py`
- `tests/unit/test_controller_view_model.py`

## TDD Evidence

- RED command and failure summary:
- GREEN command and pass summary:

## Verification

- Focused tests:
- Ruff:
- Mypy:
- Full pytest:
- Diff check:

## Notes

- No live RingCentralVideo interaction was performed.
- Passive refresh still uses cached voice readiness; Start/Submit callbacks still force fresh checks.
```

- [ ] **Step 3: Return worker status**

Return `DONE` with changed paths, test evidence, and any concerns.
