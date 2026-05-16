# Voice Profile Preflight Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Validate presenter voice/profile compatibility before CLI, controller, or material-demo runtime paths cause desktop automation side effects.

**Architecture:** Keep `validate_profile_voice()` as the compatibility source of truth, enrich its error context, and call it at outer entry points before creating desktop drivers, provider registries, Tk windows, or demo threads.

**Tech Stack:** Python, Typer, Tkinter controller, pytest, ruff, mypy.

---

## File Structure

- Modify `src/ai_presenter/runtime/voice.py`
  - Enrich `validate_profile_voice()` messages with profile id, configured speech provider, and normalized voice label.
- Modify `src/ai_presenter/cli.py`
  - Validate loaded profile plus selected voice in `demo` and `controller`.
  - Convert compatibility `ValueError` to `typer.BadParameter`.
- Modify `src/ai_presenter/runtime/factory.py`
  - Validate before desktop/provider/launcher setup in material demo entry points.
- Modify `src/ai_presenter/runtime/controller.py`
  - Validate initial voice before controller setup.
  - Validate the current UI-selected voice in Start before launching a runner thread.
- Modify tests:
  - `tests/unit/test_cli.py`
  - `tests/unit/test_runtime_factory.py`
  - `tests/unit/test_controller.py`
  - `tests/unit/test_voice.py`
- Create handoff docs under `docs/agent-handoffs/`.

## Tasks

### Task 1: Enrich Compatibility Errors

**Files:**

- Modify: `tests/unit/test_voice.py`
- Modify: `src/ai_presenter/runtime/voice.py`

- [ ] **Step 1: Write failing test**

Add a test that proves unsupported fake/Chinese output includes useful context:

```python
def test_voice_validation_error_includes_profile_provider_and_voice() -> None:
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))

    with pytest.raises(ValueError) as exc_info:
        validate_profile_voice(profile, PresenterVoiceSettings(language="zh-CN", tone="friendly"))

    message = str(exc_info.value)
    assert "ringcentral-video" in message
    assert "speech provider fake" in message
    assert "Chinese / Friendly" in message
    assert "openai or windows-sapi-zh" in message
```

- [ ] **Step 2: Verify red**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py::test_voice_validation_error_includes_profile_provider_and_voice
```

Expected: fails because current error lacks profile/provider/voice context.

- [ ] **Step 3: Implement message helper**

In `runtime.voice`, add a private helper:

```python
def _profile_voice_context(profile: AppProfile, settings: PresenterVoiceSettings) -> str:
    voice = f"{language_label(settings.language)} / {tone_label(settings.tone)}"
    return f"Profile {profile.id} with speech provider {profile.providers.speech} cannot use {voice}."
```

Prefix existing `ValueError` messages with that context while keeping the existing required-provider text.

- [ ] **Step 4: Verify green**

Run the same focused pytest command. Expected: pass.

### Task 2: CLI Compatibility Preflight

**Files:**

- Modify: `tests/unit/test_cli.py`
- Modify: `src/ai_presenter/cli.py`

- [ ] **Step 1: Write failing CLI tests**

Add tests:

```python
def test_demo_rejects_unsupported_profile_voice_before_runtime(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = False

    def fake_run_material_demo(*_args: object, **_kwargs: object) -> None:
        nonlocal called
        called = True

    monkeypatch.setattr("ai_presenter.cli.run_material_demo", fake_run_material_demo)
    result = CliRunner().invoke(
        app,
        [
            "demo",
            "--profile",
            "ringcentral-video",
            "--package",
            "ringcentral-video",
            "--flow",
            "meeting-controls-tour",
            "--language",
            "zh-CN",
            "--tone",
            "friendly",
            "--dry-run",
        ],
    )

    assert result.exit_code != 0
    assert "ringcentral-video" in result.output
    assert "speech provider fake" in result.output
    assert "Chinese / Friendly" in result.output
    assert called is False
```

```python
def test_controller_rejects_unsupported_profile_voice_before_runtime(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = False

    def fake_run_controller(*_args: object, **_kwargs: object) -> None:
        nonlocal called
        called = True

    monkeypatch.setattr("ai_presenter.cli.run_controller", fake_run_controller)
    result = CliRunner().invoke(
        app,
        [
            "controller",
            "--profile",
            "ringcentral-video",
            "--package",
            "ringcentral-video",
            "--flow",
            "meeting-control-map-demo",
            "--language",
            "zh-CN",
            "--tone",
            "friendly",
            "--dry-run",
        ],
    )

    assert result.exit_code != 0
    assert "speech provider fake" in result.output
    assert "Chinese / Friendly" in result.output
    assert called is False
```

- [ ] **Step 2: Verify red**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_demo_rejects_unsupported_profile_voice_before_runtime tests\unit\test_cli.py::test_controller_rejects_unsupported_profile_voice_before_runtime
```

Expected: tests fail because CLI dry-run currently reports success.

- [ ] **Step 3: Implement CLI helper**

Add `validate_profile_voice` import and helper:

```python
def validate_cli_voice_profile(profile: DesktopAppProfile, voice: PresenterVoiceSettings) -> None:
    try:
        validate_profile_voice(profile, voice)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc
```

Call this after the profile type check and before dry-run return/runtime invocation in `demo()` and `controller()`.

- [ ] **Step 4: Verify green**

Run the same focused CLI command. Expected: pass.

### Task 3: Runtime And Controller Early Validation

**Files:**

- Modify: `tests/unit/test_runtime_factory.py`
- Modify: `tests/unit/test_controller.py`
- Modify: `src/ai_presenter/runtime/factory.py`
- Modify: `src/ai_presenter/runtime/controller.py`

- [ ] **Step 1: Write failing runtime tests**

Add:

```python
def test_run_material_demo_validates_voice_before_desktop_driver(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))
    assert isinstance(profile, DesktopAppProfile)
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    calls: list[str] = []

    def fake_desktop_driver() -> object:
        calls.append("desktop")
        raise AssertionError("desktop should not start")

    monkeypatch.setattr(factory_module, "WindowsDesktopDriver", fake_desktop_driver)
    monkeypatch.setattr(
        factory_module,
        "create_provider_registry",
        lambda *_args, **_kwargs: calls.append("registry"),
    )

    with pytest.raises(ValueError, match="Chinese / Friendly"):
        run_material_demo(
            profile,
            package,
            "meeting-controls-tour",
            voice=PresenterVoiceSettings(language="zh-CN", tone="friendly"),
        )

    assert calls == []
```

```python
def test_existing_window_material_demo_validates_voice_before_desktop_driver(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))
    assert isinstance(profile, DesktopAppProfile)
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    handle = WindowHandle("RingCentralVideo", 1, "RingCentralVideoClass", "RingCentral Video")
    calls: list[str] = []

    monkeypatch.setattr(factory_module, "WindowsDesktopDriver", lambda: calls.append("desktop"))

    with pytest.raises(ValueError, match="speech provider fake"):
        run_existing_window_material_demo(
            profile,
            package,
            "meeting-controls-tour",
            handle=handle,
            voice=PresenterVoiceSettings(language="zh"),
        )

    assert calls == []
```

- [ ] **Step 2: Write failing controller test**

Add:

```python
def test_run_controller_validates_initial_voice_before_desktop_driver(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))
    assert isinstance(profile, DesktopAppProfile)
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    calls: list[str] = []

    monkeypatch.setattr(controller_module, "WindowsDesktopDriver", lambda: calls.append("desktop"))

    with pytest.raises(ValueError, match="Chinese / Friendly"):
        controller_module.run_controller(
            profile,
            package,
            "meeting-control-map-demo",
            voice=PresenterVoiceSettings(language="zh-CN", tone="friendly"),
        )

    assert calls == []
```

- [ ] **Step 3: Verify red**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_runtime_factory.py::test_run_material_demo_validates_voice_before_desktop_driver tests\unit\test_runtime_factory.py::test_existing_window_material_demo_validates_voice_before_desktop_driver tests\unit\test_controller.py::test_run_controller_validates_initial_voice_before_desktop_driver
```

Expected: tests fail because validation currently happens after driver setup in runtime paths and is absent before controller setup.

- [ ] **Step 4: Implement early validation**

In `factory.py`, compute `voice_settings = voice or PresenterVoiceSettings()` and call `validate_profile_voice(profile, voice_settings)` before desktop/provider setup. Pass `voice=voice_settings` into `_run_material_demo_on_handle()`.

In `controller.py`, import `validate_profile_voice`, validate `voice_settings` before creating desktop/session/catalog/Tk state, and call `validate_profile_voice(profile, voice)` in the Start handler before `controller.set_voice(voice)`.

- [ ] **Step 5: Verify green**

Run the same focused runtime/controller command. Expected: pass.

### Task 4: Documentation And Quality Gate

**Files:**

- Modify: `README.md`
- Modify: `docs/runbooks/ringcentral-manual-acceptance.md`
- Create: `docs/agent-handoffs/cycle-012-implementation.md`
- Create: `docs/agent-handoffs/cycle-012-review.md`
- Create: `docs/agent-handoffs/cycle-012-summary.md`

- [ ] **Step 1: Update docs**

Add a brief voice/profile support note:

```markdown
Voice compatibility is checked before demo launch. The fake speech profile is suitable for default English smoke tests; Chinese output requires OpenAI or the Windows SAPI Chinese route.
```

Add one runbook passing example with `ringcentral-video-bind-speaker --language zh-CN` and one failing preflight example with `ringcentral-video --language zh-CN`.

- [ ] **Step 2: Run focused verification**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py tests\unit\test_runtime_factory.py tests\unit\test_controller.py tests\unit\test_voice.py tests\unit\test_controller_session.py
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\cli.py src\ai_presenter\runtime\factory.py src\ai_presenter\runtime\controller.py src\ai_presenter\runtime\voice.py tests\unit\test_cli.py tests\unit\test_runtime_factory.py tests\unit\test_controller.py tests\unit\test_voice.py
.\.venv\Scripts\mypy --no-incremental src\ai_presenter\cli.py src\ai_presenter\runtime\factory.py src\ai_presenter\runtime\controller.py src\ai_presenter\runtime\voice.py tests\unit\test_cli.py tests\unit\test_runtime_factory.py tests\unit\test_controller.py tests\unit\test_voice.py
```

Expected: all focused checks pass.

- [ ] **Step 3: Run full verification**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
```

Expected: full tests pass with only the known pywinauto STA warning.

- [ ] **Step 4: Review and handoff**

Dispatch a review subagent for preflight ordering, error clarity, and supported-route regressions. Record implementation evidence, review result, and follow-ups in Cycle 012 handoff docs.
