# Controller Voice Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Show selected voice asset readiness in the controller and block Start/Submit when local assets are missing.

**Architecture:** Extend the pure controller view model with a small readiness DTO, then wire the Tk controller through an injectable voice asset checker. Keep SAPI/Piper discovery in `runtime.voice_assets`; controller code only adapts results into UI state.

**Tech Stack:** Python, Tkinter wiring, pytest, ruff, mypy.

---

## File Structure

- Modify `src/ai_presenter/runtime/controller_view_model.py`
  - Add `ControllerVoiceReadiness` and readiness labels/button guards.
- Modify `tests/unit/test_controller_view_model.py`
  - Add pure tests for OK, FAIL, and not-applicable voice readiness.
- Modify `src/ai_presenter/runtime/controller.py`
  - Add an injectable checker type, readiness adapter helper, summary label wiring, and Start/Submit guards.
- Modify `tests/unit/test_controller.py`
  - Add tests for readiness adapter and guarded Start behavior with fake checker results.
- Modify `docs/runbooks/ringcentral-manual-acceptance.md`
  - Add one checklist item for controller voice readiness summary.
- Create `docs/agent-handoffs/cycle-016-implementation.md`
  - Record red/green and verification evidence.

## Tasks

### Task 1: Pure View Model Readiness

**Files:**

- Modify: `tests/unit/test_controller_view_model.py`
- Modify: `src/ai_presenter/runtime/controller_view_model.py`

- [ ] **Step 1: Write failing view-model tests**

Add tests:

```python
from ai_presenter.runtime.controller_view_model import ControllerVoiceReadiness


def test_material_package_missing_voice_assets_blocks_start_and_submit() -> None:
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

    assert "Huihui" in view_model.voice_readiness_label
    assert view_model.buttons.start_enabled is False
    assert view_model.buttons.submit_enabled is False


def test_material_package_ready_voice_assets_preserve_start_behavior() -> None:
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
                status="OK",
                label="OK",
                detail="speech=windows-sapi-zh found installed SAPI voice matching Huihui",
            ),
            run_status="Ready",
            is_running=False,
            is_stopping=False,
            question_text="chat",
            last_question_outcome="",
        )
    )

    assert view_model.voice_readiness_label == "OK"
    assert view_model.buttons.start_enabled is True
    assert view_model.buttons.submit_enabled is True


def test_not_applicable_voice_readiness_preserves_existing_start_behavior() -> None:
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
            question_text="chat",
            last_question_outcome="",
        )
    )

    assert view_model.voice_readiness_label == "Not required"
    assert view_model.buttons.start_enabled is True
    assert view_model.buttons.submit_enabled is True
```

- [ ] **Step 2: Verify view-model tests fail**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller_view_model.py::test_material_package_missing_voice_assets_blocks_start_and_submit tests\unit\test_controller_view_model.py::test_material_package_ready_voice_assets_preserve_start_behavior tests\unit\test_controller_view_model.py::test_not_applicable_voice_readiness_preserves_existing_start_behavior
```

Expected: fail because readiness fields/classes do not exist.

- [ ] **Step 3: Implement view-model readiness**

Add:

```python
ControllerVoiceReadinessStatus = Literal["OK", "FAIL"]


@dataclass(frozen=True)
class ControllerVoiceReadiness:
    status: ControllerVoiceReadinessStatus
    label: str
    detail: str = ""
```

Add `voice_readiness: ControllerVoiceReadiness | None = None` to `ControllerOperatorSnapshot`.
Add `voice_readiness_label: str` to `ControllerOperatorViewModel`.

In `build_controller_operator_view_model()`:

```python
voice_ready = _voice_ready(snapshot.voice_readiness)
...
voice_readiness_label=_voice_readiness_label(snapshot.voice_readiness)
...
start_enabled=can_start_new_action and target_ready and voice_ready
...
submit_enabled=question_text_present and target_ready and voice_ready and not snapshot.is_stopping
```

Implement:

```python
def _voice_ready(readiness: ControllerVoiceReadiness | None) -> bool:
    return readiness is None or readiness.status == "OK"


def _voice_readiness_label(readiness: ControllerVoiceReadiness | None) -> str:
    if readiness is None:
        return "Not required"
    if readiness.status == "OK":
        return readiness.label or "OK"
    detail = readiness.detail.strip()
    return f"{readiness.label}: {detail}" if detail else readiness.label
```

- [ ] **Step 4: Update existing view-model tests**

Because `ControllerOperatorSnapshot` gained a field, update existing tests to pass
`voice_readiness=None` unless they are specifically testing readiness.

- [ ] **Step 5: Verify view-model tests pass**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller_view_model.py
```

Expected: pass.

### Task 2: Controller Readiness Adapter And Guards

**Files:**

- Modify: `tests/unit/test_controller.py`
- Modify: `src/ai_presenter/runtime/controller.py`

- [ ] **Step 1: Write failing controller helper tests**

Add tests importing `ControllerVoiceReadiness`, `VoiceAssetAvailability`, and helper functions from
`controller.py`.

```python
from ai_presenter.runtime.controller import _check_controller_voice_readiness
from ai_presenter.runtime.controller import _voice_readiness_failure_message
from ai_presenter.runtime.voice_assets import VoiceAssetAvailability


def test_controller_voice_readiness_adapts_available_assets() -> None:
    profile, _package = _controller_inputs()

    readiness = _check_controller_voice_readiness(
        profile,
        PresenterVoiceSettings(language="zh"),
        checker=lambda *_args: VoiceAssetAvailability(
            status="OK",
            route="windows-sapi-zh",
            detail="speech=windows-sapi-zh found installed SAPI voice matching Huihui",
        ),
    )

    assert readiness is not None
    assert readiness.status == "OK"
    assert readiness.label == "OK"


def test_controller_voice_readiness_converts_checker_exception_to_failure() -> None:
    profile, _package = _controller_inputs()

    def checker(*_args: object) -> object:
        raise RuntimeError("SAPI unavailable")

    readiness = _check_controller_voice_readiness(
        profile,
        PresenterVoiceSettings(language="zh"),
        checker=checker,
    )

    assert readiness is not None
    assert readiness.status == "FAIL"
    assert "SAPI unavailable" in readiness.detail
    assert "SAPI unavailable" in _voice_readiness_failure_message(readiness)
```

- [ ] **Step 2: Verify controller helper tests fail**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller.py::test_controller_voice_readiness_adapts_available_assets tests\unit\test_controller.py::test_controller_voice_readiness_converts_checker_exception_to_failure
```

Expected: fail because helpers do not exist.

- [ ] **Step 3: Implement controller adapter helpers**

In `controller.py`, import `ControllerVoiceReadiness`,
`check_voice_asset_availability`, and `VoiceAssetAvailability`.

Add:

```python
VoiceAssetChecker = Callable[[DesktopAppProfile, PresenterVoiceSettings], VoiceAssetAvailability | None]


def _check_controller_voice_readiness(
    profile: DesktopAppProfile,
    voice: PresenterVoiceSettings,
    *,
    checker: VoiceAssetChecker = check_voice_asset_availability,
) -> ControllerVoiceReadiness | None:
    try:
        availability = checker(profile, voice)
    except Exception as exc:
        return ControllerVoiceReadiness(
            status="FAIL",
            label="FAIL",
            detail=f"voice asset check failed: {exc}",
        )
    if availability is None:
        return None
    return ControllerVoiceReadiness(
        status=availability.status,
        label=availability.status,
        detail=availability.detail,
    )


def _voice_readiness_failure_message(readiness: ControllerVoiceReadiness | None) -> str | None:
    if readiness is None or readiness.status == "OK":
        return None
    return readiness.detail or readiness.label
```

- [ ] **Step 4: Wire Tk controller summary and button state**

Change `run_controller()` signature:

```python
voice_asset_checker: VoiceAssetChecker = check_voice_asset_availability,
```

Inside `refresh_operator_view()`, compute:

```python
voice = current_voice()
voice_readiness = _check_controller_voice_readiness(
    profile,
    voice,
    checker=voice_asset_checker,
)
```

Pass `voice=voice` and `voice_readiness=voice_readiness` into `ControllerOperatorSnapshot`.
Update summary:

```python
f"Voice: {view_model.voice_label} | Voice assets: {view_model.voice_readiness_label} | "
```

Add a small helper in the closure:

```python
def current_voice_readiness() -> ControllerVoiceReadiness | None:
    return _check_controller_voice_readiness(
        profile,
        current_voice(),
        checker=voice_asset_checker,
    )
```

Before `controller.start()` in `start()`, check:

```python
readiness = current_voice_readiness()
failure = _voice_readiness_failure_message(readiness)
if failure is not None:
    status.set(f"Start error: {failure}")
    refresh_operator_view()
    return
```

Before `controller.submit_question(text)` in `submit_question()`, after scan checks:

```python
readiness = current_voice_readiness()
failure = _voice_readiness_failure_message(readiness)
if failure is not None:
    append_chat("AiPresenter", f"Question error: {failure}")
    last_question_outcome = f"Question error: {failure}"
    status.set(last_question_outcome)
    refresh_operator_view()
    return
```

- [ ] **Step 5: Verify controller tests pass**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller.py
```

Expected: pass.

### Task 3: Docs And Quality Gate

**Files:**

- Modify: `docs/runbooks/ringcentral-manual-acceptance.md`
- Create: `docs/agent-handoffs/cycle-016-implementation.md`

- [ ] **Step 1: Update manual acceptance checklist**

Add a controller item:

```markdown
- [ ] Open the controller with a local voice profile and confirm the operator summary includes
  `Voice assets: OK` before pressing Start. If assets are missing, confirm Start stays disabled
  and the summary names the missing SAPI or Piper requirement.
```

- [ ] **Step 2: Run focused verification**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller_view_model.py tests\unit\test_controller.py
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\runtime\controller_view_model.py src\ai_presenter\runtime\controller.py tests\unit\test_controller_view_model.py tests\unit\test_controller.py
.\.venv\Scripts\mypy --no-incremental src\ai_presenter\runtime\controller_view_model.py src\ai_presenter\runtime\controller.py tests\unit\test_controller_view_model.py tests\unit\test_controller.py
```

Expected: all focused checks pass.

- [ ] **Step 3: Run full verification**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
```

Expected: full suite passes with only the known pywinauto STA warning.

- [ ] **Step 4: Record implementation handoff**

Create `docs/agent-handoffs/cycle-016-implementation.md` with scope, red/green evidence,
verification results, and any residual risk.
