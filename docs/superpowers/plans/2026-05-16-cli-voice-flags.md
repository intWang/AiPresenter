# CLI Voice Flags Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expose presenter language and tone selection through `demo` and `controller` CLI commands.

**Architecture:** Add a small CLI helper that builds `PresenterVoiceSettings` from free-form options and renders the shared voice label. Wire the normalized voice into `run_material_demo()` and `run_controller()`, then let the controller initialize its Tk selectors from the same canonical voice.

**Tech Stack:** Python, Typer, Tkinter, pytest, ruff, mypy.

---

## File Structure

- Modify `src/ai_presenter/cli.py`
  - Add `--language` and `--tone` options to `demo` and `controller`.
  - Add a helper to normalize CLI voice values and convert `ValueError` to `typer.BadParameter`.
  - Echo the normalized `Loaded voice` label.
  - Pass voice into the runtime entry points.
- Modify `src/ai_presenter/runtime/controller.py`
  - Accept an optional initial voice in `PresenterController`.
  - Accept an optional keyword-only voice in `run_controller()`.
  - Initialize session/controller/Tk menu labels from the initial voice.
- Modify `tests/unit/test_cli.py`
  - Cover dry-run output, invalid values, and monkeypatched runner calls.
- Modify `tests/unit/test_controller.py`
  - Cover initial `PresenterController` voice forwarding.
- Create/modify `docs/agent-handoffs/cycle-011-*.md`
  - Record demand analysis, technical scan, implementation notes, review, and summary.

## Tasks

### Task 1: CLI Voice Parsing And Demo Wiring

**Files:**

- Modify: `tests/unit/test_cli.py`
- Modify: `src/ai_presenter/cli.py`

- [ ] **Step 1: Write failing tests**

Add tests that invoke `demo` with `--language zh-CN --tone friendly` and monkeypatch `ai_presenter.cli.run_material_demo` to capture the `voice` keyword:

```python
def test_demo_passes_language_and_tone_to_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[PresenterVoiceSettings] = []

    def fake_run_material_demo(*_args: object, voice: PresenterVoiceSettings | None = None) -> None:
        assert voice is not None
        calls.append(voice)

    monkeypatch.setattr("ai_presenter.cli.run_material_demo", fake_run_material_demo)

    result = CliRunner().invoke(
        app,
        [
            "demo",
            "--profile",
            "ringcentral-video-bind-speaker",
            "--package",
            "ringcentral-video",
            "--flow",
            "meeting-control-map-demo",
            "--language",
            "zh-CN",
            "--tone",
            "friendly",
        ],
    )

    assert result.exit_code == 0
    assert "Loaded voice: Chinese / Friendly" in result.stdout
    assert calls == [PresenterVoiceSettings(language="zh", tone="friendly")]
```

Add a dry-run alias test:

```python
def test_demo_dry_run_reports_normalized_voice_aliases() -> None:
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
            "English",
            "--tone",
            "warm",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "Loaded voice: English / Friendly" in result.stdout
```

- [ ] **Step 2: Verify red**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_demo_passes_language_and_tone_to_runtime tests\unit\test_cli.py::test_demo_dry_run_reports_normalized_voice_aliases
```

Expected: tests fail because the options do not exist.

- [ ] **Step 3: Implement demo CLI voice helper**

Add imports:

```python
from ai_presenter.runtime.controller_view_model import render_voice_label
from ai_presenter.runtime.voice import PresenterVoiceSettings
```

Add:

```python
def resolve_voice_settings(language: str, tone: str) -> PresenterVoiceSettings:
    try:
        return PresenterVoiceSettings(language=language, tone=tone)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc
```

Add `language` and `tone` options to `demo()`, build `voice_settings`, echo the label, and pass `voice=voice_settings` to `run_material_demo`.

- [ ] **Step 4: Verify green**

Run the same focused pytest command. Expected: both tests pass.

### Task 2: Controller CLI Voice Wiring

**Files:**

- Modify: `tests/unit/test_cli.py`
- Modify: `src/ai_presenter/cli.py`

- [ ] **Step 1: Write failing tests**

Add:

```python
def test_controller_passes_language_and_tone_to_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[PresenterVoiceSettings] = []

    def fake_run_controller(*_args: object, voice: PresenterVoiceSettings | None = None) -> None:
        assert voice is not None
        calls.append(voice)

    monkeypatch.setattr("ai_presenter.cli.run_controller", fake_run_controller)

    result = CliRunner().invoke(
        app,
        [
            "controller",
            "--profile",
            "ringcentral-video-bind-speaker",
            "--package",
            "ringcentral-video",
            "--flow",
            "meeting-control-map-demo",
            "--language",
            "English",
            "--tone",
            "mentor",
        ],
    )

    assert result.exit_code == 0
    assert "Loaded voice: English / Coach" in result.stdout
    assert calls == [PresenterVoiceSettings(language="en", tone="coach")]
```

Add invalid value coverage:

```python
def test_demo_rejects_unknown_language_before_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
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
            "es",
            "--dry-run",
        ],
    )

    assert result.exit_code != 0
    assert "Unsupported presenter language: es" in result.output
    assert called is False
```

```python
def test_controller_rejects_unknown_tone_before_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
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
            "ringcentral-video-bind-speaker",
            "--package",
            "ringcentral-video",
            "--flow",
            "meeting-control-map-demo",
            "--tone",
            "shouty",
            "--dry-run",
        ],
    )

    assert result.exit_code != 0
    assert "Unsupported presenter tone: shouty" in result.output
    assert called is False
```

- [ ] **Step 2: Verify red**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_controller_passes_language_and_tone_to_runtime tests\unit\test_cli.py::test_demo_rejects_unknown_language_before_runtime tests\unit\test_cli.py::test_controller_rejects_unknown_tone_before_runtime
```

Expected: tests fail because controller options/runtime wiring do not exist.

- [ ] **Step 3: Implement controller CLI wiring**

Add the same `language` and `tone` options to `controller()`, echo `Loaded voice`, and call:

```python
run_controller(loaded_profile, loaded_package, loaded_flow.id, voice=voice_settings)
```

- [ ] **Step 4: Verify green**

Run the same focused pytest command. Expected: all three tests pass.

### Task 3: Controller Initial Voice

**Files:**

- Modify: `tests/unit/test_controller.py`
- Modify: `src/ai_presenter/runtime/controller.py`

- [ ] **Step 1: Write failing controller test**

Add:

```python
def test_presenter_controller_forwards_initial_voice_without_setter() -> None:
    profile, package = _controller_inputs()
    calls: list[PresenterVoiceSettings] = []

    def runner(*_args: object, voice: PresenterVoiceSettings | None = None, **_kwargs: object) -> None:
        assert voice is not None
        calls.append(voice)

    controller = PresenterController(
        profile=profile,
        material_package=package,
        flow_id="meeting-control-map-demo",
        runner=runner,
        voice=PresenterVoiceSettings(language="zh-CN", tone="friendly"),
    )

    controller.start()
    controller.join(timeout=1)

    assert calls == [PresenterVoiceSettings(language="zh", tone="friendly")]
```

- [ ] **Step 2: Verify red**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller.py::test_presenter_controller_forwards_initial_voice_without_setter
```

Expected: fails because `PresenterController.__init__` does not accept `voice`.

- [ ] **Step 3: Implement controller initial voice**

Update `PresenterController.__init__` with `voice: PresenterVoiceSettings | None = None` and initialize:

```python
self._voice = voice or PresenterVoiceSettings()
```

Update `run_controller()` with keyword-only `voice: PresenterVoiceSettings | None = None`, create `voice_settings`, call `session.set_voice(voice_settings)`, construct `PresenterController(..., voice=voice_settings)`, and initialize Tk `StringVar`s using `language_label(voice_settings.language)` and `tone_label(voice_settings.tone)`.

- [ ] **Step 4: Verify green**

Run the focused controller test. Expected: pass.

### Task 4: Documentation And Quality Gate

**Files:**

- Modify: `README.md`
- Modify: `docs/runbooks/ringcentral-manual-acceptance.md`
- Create: `docs/agent-handoffs/cycle-011-implementation.md`
- Create: `docs/agent-handoffs/cycle-011-review.md`
- Create: `docs/agent-handoffs/cycle-011-summary.md`

- [ ] **Step 1: Update docs**

Add one CLI example that shows `--language zh-CN --tone friendly` for `demo`, and one that shows `--language English --tone coach` for `controller`. Note that regional aliases normalize to English/Chinese output families.

- [ ] **Step 2: Run focused verification**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py tests\unit\test_controller.py tests\unit\test_voice.py
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\cli.py src\ai_presenter\runtime\controller.py tests\unit\test_cli.py tests\unit\test_controller.py
.\.venv\Scripts\mypy --no-incremental src\ai_presenter\cli.py src\ai_presenter\runtime\controller.py tests\unit\test_cli.py tests\unit\test_controller.py
```

Expected: all focused checks pass.

- [ ] **Step 3: Run full verification**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
```

Expected: full tests pass with only known pywinauto environmental warnings.

- [ ] **Step 4: Review and handoff**

Dispatch a review subagent for CLI behavior, controller initialization, and regression risk. Record implementation evidence, review result, and remaining follow-ups in Cycle 011 handoff docs.
