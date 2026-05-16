# Demo Flow Lookup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add safe indexed demo-flow lookup with consistent unknown-flow errors and no stale indexes for controller-generated question flows.

**Architecture:** Build a package-owned demo-flow index beside the existing entrypoint index, keep the runtime wrapper for compatibility, and replace controller synthetic-flow `model_copy` with an explicit full-validation helper.

**Tech Stack:** Python, Pydantic, pytest, ruff, mypy.

---

## File Structure

- Modify `src/ai_presenter/packages/models.py`
  - Add `_demo_flows_by_id`, `demo_flows_by_id`, `demo_flow_by_id()`, and `with_demo_flow()`.
  - Reject duplicate demo flow IDs.
- Modify `src/ai_presenter/runtime/package_demo.py`
  - Delegate `demo_flow_by_id()` wrapper to `MaterialPackage.demo_flow_by_id()`.
- Modify `src/ai_presenter/runtime/diagnostics.py`
  - Surface the unified unknown-flow message.
- Modify `src/ai_presenter/runtime/controller.py`
  - Use `target.material_package.with_demo_flow(flow)` for question-answer flow.
- Modify tests:
  - `tests/unit/test_material_packages.py`
  - `tests/unit/test_package_demo.py`
  - `tests/unit/test_cli.py`
  - `tests/unit/test_diagnostics.py`
  - `tests/unit/test_controller.py`
- Update README/runbook and create Cycle 014 handoff docs.

## Tasks

### Task 1: Package Flow Index

**Files:**

- Modify: `tests/unit/test_material_packages.py`
- Modify: `src/ai_presenter/packages/models.py`

- [ ] **Step 1: Write failing package tests**

Add:

```python
def test_material_package_exposes_read_only_demo_flow_index() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    index = package.demo_flows_by_id

    assert isinstance(index, MappingProxyType)
    assert index["meeting-control-map-demo"] is package.demo_flow_by_id("meeting-control-map-demo")
    assert set(index) == {flow.id for flow in package.demo_flows}


def test_demo_flow_by_id_preserves_unknown_id_error() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    with pytest.raises(
        KeyError,
        match="Unknown demo flow: missing-flow. Available flows:",
    ):
        package.demo_flow_by_id("missing-flow")
```

Add duplicate-flow validation:

```python
def test_rejects_duplicate_demo_flow_ids(tmp_path: Path) -> None:
    package_path = tmp_path / "duplicate-flows.yaml"
    package_path.write_text(
        """
appId: demo
appName: Demo
version: 1
profileIds: [demo-profile]
operationEntrypoints:
  - id: demo.panel
    title: Panel
    area: Main
    purpose: Explain panel
    openSteps: []
demoFlows:
  - id: same-flow
    title: First
    goal: First
    steps: []
  - id: same-flow
    title: Second
    goal: Second
    steps: []
manualControls: []
""",
        encoding="utf-8",
    )

    with pytest.raises(ValidationError, match="duplicate demo flow id: same-flow"):
        load_material_package(package_path)
```

- [ ] **Step 2: Verify red**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_material_package_exposes_read_only_demo_flow_index tests\unit\test_material_packages.py::test_demo_flow_by_id_preserves_unknown_id_error tests\unit\test_material_packages.py::test_rejects_duplicate_demo_flow_ids
```

Expected: fail because the index/method/duplicate validation do not exist.

- [ ] **Step 3: Implement index and lookup**

In `MaterialPackage`, add:

```python
_demo_flows_by_id: dict[str, DemoFlow] = PrivateAttr(default_factory=dict)

@property
def demo_flows_by_id(self) -> Mapping[str, DemoFlow]:
    return MappingProxyType(self._demo_flows_by_id)

def demo_flow_by_id(self, flow_id: str) -> DemoFlow:
    try:
        return self._demo_flows_by_id[flow_id]
    except KeyError:
        available = ", ".join(flow.id for flow in self.demo_flows) or "none"
        raise KeyError(f"Unknown demo flow: {flow_id}. Available flows: {available}") from None
```

During validation, build `demo_flows_by_id`, reject duplicates, and assign the private attr after validating flow step references.

- [ ] **Step 4: Verify green**

Run the same package tests. Expected: pass.

### Task 2: Safe Synthetic Flow Rebuild

**Files:**

- Modify: `tests/unit/test_material_packages.py`
- Modify: `tests/unit/test_controller.py`
- Modify: `src/ai_presenter/packages/models.py`
- Modify: `src/ai_presenter/runtime/controller.py`

- [ ] **Step 1: Write failing safe-copy tests**

Add:

```python
def test_with_demo_flow_rebuilds_runtime_indexes_for_appended_flow() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flows[0].model_copy(update={"id": "copy-flow"})

    copied = package.with_demo_flow(flow)

    assert copied.demo_flow_by_id("copy-flow").id == "copy-flow"
    assert "copy-flow" in copied.demo_flows_by_id
    assert "copy-flow" not in package.demo_flows_by_id
```

Update or add controller regression:

```python
def test_presenter_controller_starts_safe_question_demo_with_indexed_flow_lookup() -> None:
    profile, package = _controller_inputs()
    calls: list[str] = []

    def runner(
        _profile: DesktopAppProfile,
        captured_package: MaterialPackage,
        captured_flow_id: str,
        *,
        control: DemoControl,
        voice: PresenterVoiceSettings | None = None,
    ) -> None:
        calls.append(captured_package.demo_flow_by_id(captured_flow_id).id)

    controller = PresenterController(
        profile=profile,
        material_package=package,
        flow_id="meeting-control-map-demo",
        runner=runner,
    )

    result = controller.submit_question("chat")
    controller.join(timeout=1)

    assert result.demonstration_status == "started"
    assert calls == ["question-answer-demo"]
```

- [ ] **Step 2: Verify red**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_with_demo_flow_rebuilds_runtime_indexes_for_appended_flow tests\unit\test_controller.py::test_presenter_controller_starts_safe_question_demo_with_indexed_flow_lookup
```

Expected: first test fails because `with_demo_flow()` does not exist. The controller test should fail once flow lookup is index-backed unless controller stops using raw `model_copy`.

- [ ] **Step 3: Implement helper and controller usage**

Add:

```python
def with_demo_flow(self, flow: DemoFlow) -> "MaterialPackage":
    data = self.model_dump(by_alias=True)
    data["demoFlows"] = [*data.get("demoFlows", []), flow.model_dump(by_alias=True)]
    return MaterialPackage.model_validate(data)
```

Update `_target_with_question_flow()` to call `target.material_package.with_demo_flow(flow)`.

- [ ] **Step 4: Verify green**

Run the same focused tests. Expected: pass.

### Task 3: Runtime Wrapper, Diagnostics, And CLI Consistency

**Files:**

- Modify: `tests/unit/test_package_demo.py`
- Modify: `tests/unit/test_cli.py`
- Modify: `tests/unit/test_diagnostics.py`
- Modify: `src/ai_presenter/runtime/package_demo.py`
- Modify: `src/ai_presenter/runtime/diagnostics.py`

- [ ] **Step 1: Write failing consistency tests**

Add a package_demo wrapper test:

```python
def test_demo_flow_by_id_delegates_to_package_lookup() -> None:
    package = make_package().model_copy(
        update={
            "demo_flows": [
                {
                    "id": "demo-flow",
                    "title": "Demo",
                    "goal": "Demo",
                    "steps": [],
                }
            ]
        }
    )

    with pytest.raises(KeyError, match="Unknown demo flow: missing. Available flows:"):
        package_demo_module.demo_flow_by_id(package, "missing")
```

Add CLI controller missing-flow coverage:

```python
def test_controller_reports_available_flows_when_flow_is_missing() -> None:
    result = CliRunner().invoke(
        app,
        [
            "controller",
            "--profile",
            "ringcentral-video-bind-speaker",
            "--package",
            "ringcentral-video",
            "--flow",
            "missing-flow",
            "--dry-run",
        ],
    )

    assert result.exit_code != 0
    assert "Unknown demo flow: missing-flow" in result.output
    assert "Available flows:" in result.output
```

Add diagnostics coverage:

```python
def test_doctor_uses_unified_missing_flow_message(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(diagnostics, "_iter_process_executable_paths", lambda process_name: [])

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--profile",
            "ringcentral-video-bind-speaker",
            "--package",
            "ringcentral-video",
            "--flow",
            "missing-flow",
        ],
    )

    assert result.exit_code == 1
    assert "[FAIL] demo flow: Unknown demo flow: missing-flow. Available flows:" in result.stdout
```

- [ ] **Step 2: Verify red**

Run the new tests. Expected: diagnostics test fails with the older message; wrapper test may fail until wrapper delegates to package method.

- [ ] **Step 3: Implement consistency**

Update `runtime.package_demo.demo_flow_by_id()`:

```python
def demo_flow_by_id(package: MaterialPackage, flow_id: str) -> DemoFlow:
    return package.demo_flow_by_id(flow_id)
```

Update diagnostics missing-flow handling to use `str(exc.args[0])`.

- [ ] **Step 4: Verify green**

Run the new consistency tests. Expected: pass.

### Task 4: Flow Preflight And Quality Gate

**Files:**

- Modify: `tests/unit/test_runtime_factory.py`
- Modify: `src/ai_presenter/runtime/factory.py`
- Modify: `README.md`
- Modify: `docs/runbooks/ringcentral-manual-acceptance.md`
- Create: `docs/agent-handoffs/cycle-014-implementation.md`
- Create: `docs/agent-handoffs/cycle-014-review.md`
- Create: `docs/agent-handoffs/cycle-014-summary.md`

- [ ] **Step 1: Write failing runtime preflight test**

Add:

```python
def test_run_material_demo_validates_flow_before_desktop_driver(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))
    assert isinstance(profile, DesktopAppProfile)
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    calls: list[str] = []

    monkeypatch.setattr(factory_module, "WindowsDesktopDriver", lambda: calls.append("desktop"))

    with pytest.raises(KeyError, match="Unknown demo flow: missing-flow"):
        run_material_demo(profile, package, "missing-flow")

    assert calls == []
```

- [ ] **Step 2: Verify red**

Run the new runtime test. Expected: fails because driver setup happens before flow lookup.

- [ ] **Step 3: Implement flow preflight**

In `run_material_demo()` and `run_existing_window_material_demo()`, call `material_package.demo_flow_by_id(flow_id)` after voice validation and before desktop/provider setup. The inner `_run_material_demo_on_handle()` can still look up the flow defensively.

Update docs with a short note to run `flows --package ...` before scripted demos and one missing-flow dry-run acceptance step.

- [ ] **Step 4: Run focused verification**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_package_demo.py tests\unit\test_cli.py tests\unit\test_diagnostics.py tests\unit\test_controller.py tests\unit\test_runtime_factory.py
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\packages\models.py src\ai_presenter\runtime\package_demo.py src\ai_presenter\runtime\diagnostics.py src\ai_presenter\runtime\controller.py src\ai_presenter\runtime\factory.py tests\unit\test_material_packages.py tests\unit\test_package_demo.py tests\unit\test_cli.py tests\unit\test_diagnostics.py tests\unit\test_controller.py tests\unit\test_runtime_factory.py
.\.venv\Scripts\mypy --no-incremental src\ai_presenter\packages\models.py src\ai_presenter\runtime\package_demo.py src\ai_presenter\runtime\diagnostics.py src\ai_presenter\runtime\controller.py src\ai_presenter\runtime\factory.py tests\unit\test_material_packages.py tests\unit\test_package_demo.py tests\unit\test_cli.py tests\unit\test_diagnostics.py tests\unit\test_controller.py tests\unit\test_runtime_factory.py
```

Expected: all focused checks pass.

- [ ] **Step 5: Run full verification and review**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
```

Expected: full tests pass with only the known pywinauto STA warning. Dispatch review and write handoff docs.
