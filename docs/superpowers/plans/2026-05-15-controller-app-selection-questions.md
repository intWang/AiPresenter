# Controller App Selection And Questions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a controller that can select prepared material packages or already-running desktop apps, generate temporary packages for unprepared apps, answer text questions, demonstrate safe matched controls, and switch spoken output between English/Chinese plus tone presets.

**Architecture:** Keep Tk UI thin. Add testable runtime units for voice settings, app/window catalog, temporary package generation, question matching/answering, and controller sessions. Reuse `MaterialPackage`, `PackageActionExecutor`, `SynchronizedTimelineRunner`, and `DemoControl` wherever possible so prepared and temporary packages run through the same machinery.

**Tech Stack:** Python 3.11, Typer, Tkinter, Pydantic models, pywinauto/uiautomation desktop capture, pytest, ruff, mypy.

---

## File Structure

- Create `src/ai_presenter/runtime/voice.py`
  - Defines `PresenterLanguage`, `PresenterTone`, `PresenterVoiceSettings`, rendering helpers, and profile compatibility checks.
- Create `tests/unit/test_voice.py`
  - Unit tests for language/tone rendering and provider compatibility.
- Create `src/ai_presenter/runtime/catalog.py`
  - Lists material-package options and running desktop app/window options.
- Create `tests/unit/test_catalog.py`
  - Unit tests with fake package paths and fake desktop windows.
- Modify `src/ai_presenter/desktop/base.py`
  - Add `VisibleWindow` and `VisibleControl` dataclasses plus optional discovery protocol methods.
- Modify `src/ai_presenter/desktop/windows.py`
  - Implement visible-window listing and visible-control extraction.
- Modify `tests/unit/test_windows_desktop.py`
  - Unit tests for visible-window/control discovery with fakes.
- Create `src/ai_presenter/runtime/temporary_package.py`
  - Builds in-memory `MaterialPackage` instances from scanned app windows and classifies safe/risky controls.
- Create `tests/unit/test_temporary_package.py`
  - Tests temporary package generation, safety policy, generated flow, explainers, and validation.
- Create `src/ai_presenter/runtime/questions.py`
  - Defines `QuestionRequest`, `QuestionResponse`, deterministic matcher, answer renderer, and interrupt-step creation.
- Create `tests/unit/test_questions.py`
  - Tests QA, explainer, entrypoint, temporary package matching, language, tone, safe/risky handling.
- Create `src/ai_presenter/runtime/session.py`
  - Owns selected controller target, active package/flow, `DemoControl`, thread lifecycle, question handling, and target-change blocking.
- Create `tests/unit/test_controller_session.py`
  - Tests material target lifecycle, running-app scan lifecycle, question submission, voice settings, and target-change blocking.
- Modify `src/ai_presenter/runtime/controller.py`
  - Replace direct fixed-target Tk logic with catalog/session-driven UI: target source selector, package/window selectors, Scan, Start/Pause/End, language/tone selectors, question input, answer/status.
- Modify `tests/unit/test_controller.py`
  - Keep non-Tk controller/session tests; avoid brittle Tk widget assertions.
- Modify `src/ai_presenter/runtime/factory.py`
  - Extract reusable material-demo runtime helpers where needed for question interrupts.
- Modify `tests/unit/test_runtime_factory.py`
  - Preserve existing RCV behavior and add coverage for extracted runtime helpers.
- Modify `README.md`
  - Document controller target selection, voice settings, and text questions.
- Modify `docs/runbooks/ringcentral-manual-acceptance.md`
  - Add manual acceptance steps for app selection, questions, language, and tone.

---

### Task 1: Voice Settings Core

**Files:**
- Create: `src/ai_presenter/runtime/voice.py`
- Create: `tests/unit/test_voice.py`

- [ ] **Step 1: Write failing tests for language/tone models**

Add `tests/unit/test_voice.py`:

```python
from pathlib import Path

import pytest

from ai_presenter.config.loader import load_profile
from ai_presenter.runtime.voice import PresenterVoiceSettings
from ai_presenter.runtime.voice import render_voice_instruction
from ai_presenter.runtime.voice import validate_profile_voice


def test_default_voice_settings_are_english_professional() -> None:
    settings = PresenterVoiceSettings()

    assert settings.language == "en"
    assert settings.tone == "professional"


def test_voice_instruction_renders_chinese_conversational_style() -> None:
    settings = PresenterVoiceSettings(language="zh", tone="conversational")

    instruction = render_voice_instruction(settings)

    assert "Chinese" in instruction
    assert "natural" in instruction
    assert "conversational" in instruction


def test_voice_validation_allows_chinese_windows_sapi_profile() -> None:
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))
    profile.providers.speech = "windows-sapi-zh"

    validate_profile_voice(profile, PresenterVoiceSettings(language="zh"))


def test_voice_validation_rejects_chinese_with_english_only_sapi_profile() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))

    with pytest.raises(ValueError, match="Chinese.*windows-sapi-zh"):
        validate_profile_voice(profile, PresenterVoiceSettings(language="zh"))
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.\.venv\Scripts\python.exe -m pytest tests\unit\test_voice.py -q --no-cov`

Expected: FAIL because `ai_presenter.runtime.voice` does not exist.

- [ ] **Step 3: Implement minimal voice module**

Create `src/ai_presenter/runtime/voice.py`:

```python
from dataclasses import dataclass
from typing import Literal

from ai_presenter.config.models import AppProfile

PresenterLanguage = Literal["en", "zh"]
PresenterTone = Literal["professional", "conversational", "concise"]

_TONE_DESCRIPTIONS: dict[PresenterTone, str] = {
    "professional": "professional, structured, and product-specialist",
    "conversational": "natural, conversational, warm, and easy to follow",
    "concise": "concise, brisk, and transition-focused",
}


@dataclass(frozen=True)
class PresenterVoiceSettings:
    language: PresenterLanguage = "en"
    tone: PresenterTone = "professional"


def render_voice_instruction(settings: PresenterVoiceSettings) -> str:
    language = "Chinese" if settings.language == "zh" else "English"
    tone = _TONE_DESCRIPTIONS[settings.tone]
    return f"Speak in {language}. Use a {tone} tone."


def validate_profile_voice(profile: AppProfile, settings: PresenterVoiceSettings) -> None:
    speech = profile.providers.speech
    if settings.language == "zh" and speech not in {"openai", "windows-sapi-zh"}:
        raise ValueError("Chinese voice output requires speech provider openai or windows-sapi-zh.")
    if settings.language == "en" and speech == "windows-sapi-zh":
        raise ValueError("English voice output requires speech provider openai, fake, windows-sapi, or windows-sapi-en.")
```

- [ ] **Step 4: Run focused tests**

Run: `.\.venv\Scripts\python.exe -m pytest tests\unit\test_voice.py -q --no-cov`

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add src/ai_presenter/runtime/voice.py tests/unit/test_voice.py
git commit -m "feat: add presenter voice settings"
```

---

### Task 2: Desktop Discovery Models And Windows Driver Support

**Files:**
- Modify: `src/ai_presenter/desktop/base.py`
- Modify: `src/ai_presenter/desktop/windows.py`
- Modify: `tests/unit/test_windows_desktop.py`

- [ ] **Step 1: Write failing tests for visible windows and controls**

Add tests to `tests/unit/test_windows_desktop.py`:

```python
def test_list_visible_windows_returns_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    root = FakeWindow(
        title="Demo App",
        class_name="DemoWindow",
        pid=42,
        rectangle=SimpleNamespace(left=10, top=20, right=410, bottom=320),
        visible=True,
        minimized=False,
    )
    monkeypatch.setattr(windows, "Desktop", lambda backend: FakeDesktop([root]))
    monkeypatch.setattr(windows, "psutil", FakePsutil({"Demo.exe": [42]}))

    discovered = WindowsDesktopDriver().list_visible_windows()

    assert discovered[0].process == "Demo"
    assert discovered[0].pid == 42
    assert discovered[0].window_class == "DemoWindow"
    assert discovered[0].title == "Demo App"


def test_list_visible_controls_returns_named_controls(monkeypatch: pytest.MonkeyPatch) -> None:
    handle = WindowHandle("Demo", 42, "DemoWindow", "Demo App")
    root_control = FakeControl(
        name="root",
        control_type="Window",
        bounds=SimpleNamespace(left=0, top=0, right=500, bottom=500),
        children=[
            FakeControl("Settings", "Button", SimpleNamespace(left=10, top=10, right=100, bottom=40)),
            FakeControl("Delete", "Button", SimpleNamespace(left=10, top=50, right=100, bottom=80)),
        ],
    )
    monkeypatch.setattr(windows, "_bind_window", lambda pid, window_class: FakeBoundWindow(handle))
    monkeypatch.setattr(windows, "_control_from_window", lambda window: root_control)

    controls = WindowsDesktopDriver().list_visible_controls(handle)

    assert [control.name for control in controls] == ["Settings", "Delete"]
    assert controls[0].control_type == "Button"
```

- [ ] **Step 2: Run focused tests to verify failure**

Run: `.\.venv\Scripts\python.exe -m pytest tests\unit\test_windows_desktop.py -q --no-cov`

Expected: FAIL because `list_visible_windows` and `list_visible_controls` are not defined.

- [ ] **Step 3: Add discovery dataclasses and protocol methods**

Modify `src/ai_presenter/desktop/base.py`:

```python
@dataclass(frozen=True)
class VisibleWindow:
    process: str
    pid: int
    window_class: str
    title: str
    bounds: tuple[int, int, int, int]


@dataclass(frozen=True)
class VisibleControl:
    name: str
    control_type: str
    bounds: tuple[int, int, int, int]
```

Add methods to `DesktopDriver` protocol:

```python
    def list_visible_windows(self) -> tuple[VisibleWindow, ...]:
        ...

    def list_visible_controls(self, handle: WindowHandle) -> tuple[VisibleControl, ...]:
        ...
```

- [ ] **Step 4: Implement Windows driver discovery**

In `src/ai_presenter/desktop/windows.py`, add:

```python
from ai_presenter.desktop.base import VisibleControl, VisibleWindow


def _window_class(window: Any) -> str:
    class_name = getattr(window, "class_name", None)
    if callable(class_name):
        value = class_name()
        return value if isinstance(value, str) else ""
    return ""


def _window_is_visible(window: Any) -> bool:
    visible = getattr(window, "is_visible", None)
    if callable(visible):
        try:
            return bool(visible())
        except Exception:
            return False
    return True
```

Add methods on `WindowsDesktopDriver`:

```python
    def list_visible_windows(self) -> tuple[VisibleWindow, ...]:
        _require_dependency(Desktop, "pywinauto")
        windows: list[VisibleWindow] = []
        for window in Desktop(backend="uia").windows():
            try:
                if not _window_is_visible(window) or _call_bool_window_method(window, "is_minimized"):
                    continue
                bounds = _window_bounds(window)
                pid = int(getattr(window, "process_id")())
                process = _process_name_from_pid(pid)
                title = _window_title(window)
                window_class = _window_class(window)
            except Exception:
                continue
            if title.strip() and window_class.strip():
                windows.append(VisibleWindow(process, pid, window_class, title, bounds))
        return tuple(windows)

    def list_visible_controls(self, handle: WindowHandle) -> tuple[VisibleControl, ...]:
        window = _bind_window(handle.pid, handle.window_class)
        root_control = _control_from_window(window)
        if root_control is None:
            return ()
        return tuple(_collect_visible_controls(root_control))
```

Add helpers:

```python
def _collect_visible_controls(root: Any) -> list[VisibleControl]:
    controls: list[VisibleControl] = []
    stack = [root]
    while stack:
        node = stack.pop()
        name = _control_name(node)
        bounds = _control_bounds(node)
        control_type = _control_type_name(node)
        if name and bounds is not None:
            controls.append(VisibleControl(name=name, control_type=control_type, bounds=bounds))
        get_children = getattr(node, "GetChildren", None)
        if callable(get_children):
            try:
                stack.extend(reversed(list(get_children() or [])))
            except Exception:
                pass
    return controls


def _control_type_name(control: Any) -> str:
    for attr in ("ControlTypeName", "LocalizedControlType"):
        value = getattr(control, attr, "")
        if isinstance(value, str) and value.strip():
            return value.strip()
    return control.__class__.__name__


def _process_name_from_pid(pid: int) -> str:
    if psutil is None:
        return str(pid)
    try:
        name = psutil.Process(pid).name()
    except Exception:
        return str(pid)
    return name[:-4] if name.casefold().endswith(".exe") else name
```

- [ ] **Step 5: Run focused tests**

Run: `.\.venv\Scripts\python.exe -m pytest tests\unit\test_windows_desktop.py -q --no-cov`

Expected: PASS after adding the concrete `FakeDesktop`, `FakeWindow`, `FakeBoundWindow`,
`FakePsutil`, and three-argument `FakeControl` helpers used in the tests above.

- [ ] **Step 6: Commit**

```powershell
git add src/ai_presenter/desktop/base.py src/ai_presenter/desktop/windows.py tests/unit/test_windows_desktop.py
git commit -m "feat: discover visible desktop apps and controls"
```

---

### Task 3: Controller App Catalog

**Files:**
- Create: `src/ai_presenter/runtime/catalog.py`
- Create: `tests/unit/test_catalog.py`

- [ ] **Step 1: Write failing catalog tests**

Create `tests/unit/test_catalog.py`:

```python
from pathlib import Path

from ai_presenter.desktop.base import VisibleWindow
from ai_presenter.runtime.catalog import ControllerAppCatalog


class FakeDesktop:
    def list_visible_windows(self) -> tuple[VisibleWindow, ...]:
        return (
            VisibleWindow("Demo", 10, "DemoWindow", "Demo App", (0, 0, 800, 600)),
        )


def test_catalog_lists_material_packages() -> None:
    catalog = ControllerAppCatalog(
        package_dir=Path("packages"),
        desktop=FakeDesktop(),
    )

    packages = catalog.list_material_packages()

    assert packages[0].package_id == "ringcentral-video"
    assert packages[0].path.name == "ringcentral-video.yaml"


def test_catalog_lists_running_desktop_apps() -> None:
    catalog = ControllerAppCatalog(package_dir=Path("packages"), desktop=FakeDesktop())

    windows = catalog.list_running_apps()

    assert windows[0].process == "Demo"
    assert windows[0].title == "Demo App"
```

- [ ] **Step 2: Run tests to verify failure**

Run: `.\.venv\Scripts\python.exe -m pytest tests\unit\test_catalog.py -q --no-cov`

Expected: FAIL because `runtime.catalog` does not exist.

- [ ] **Step 3: Implement catalog**

Create `src/ai_presenter/runtime/catalog.py`:

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from ai_presenter.desktop.base import VisibleWindow


class WindowCatalogDriver(Protocol):
    def list_visible_windows(self) -> tuple[VisibleWindow, ...]:
        ...


@dataclass(frozen=True)
class MaterialPackageOption:
    package_id: str
    path: Path


class ControllerAppCatalog:
    def __init__(self, *, package_dir: Path, desktop: WindowCatalogDriver) -> None:
        self._package_dir = package_dir
        self._desktop = desktop

    def list_material_packages(self) -> tuple[MaterialPackageOption, ...]:
        options = [
            MaterialPackageOption(package_id=path.stem, path=path)
            for path in sorted(self._package_dir.glob("*.yaml"))
            if path.is_file()
        ]
        return tuple(options)

    def list_running_apps(self) -> tuple[VisibleWindow, ...]:
        return self._desktop.list_visible_windows()
```

- [ ] **Step 4: Run focused tests**

Run: `.\.venv\Scripts\python.exe -m pytest tests\unit\test_catalog.py -q --no-cov`

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add src/ai_presenter/runtime/catalog.py tests/unit/test_catalog.py
git commit -m "feat: add controller app catalog"
```

---

### Task 4: Temporary Package Generation

**Files:**
- Create: `src/ai_presenter/runtime/temporary_package.py`
- Create: `tests/unit/test_temporary_package.py`

- [ ] **Step 1: Write failing tests for safety and generated package**

Create `tests/unit/test_temporary_package.py`:

```python
from ai_presenter.desktop.base import VisibleControl, VisibleWindow
from ai_presenter.runtime.temporary_package import build_temporary_package
from ai_presenter.runtime.temporary_package import classify_control_safety


def test_classifies_destructive_controls_as_risky() -> None:
    assert classify_control_safety("Delete", "Button").is_safe is False
    assert classify_control_safety("Send", "Button").is_safe is False


def test_classifies_settings_control_as_safe() -> None:
    assert classify_control_safety("Settings", "Button").is_safe is True


def test_builds_valid_temporary_package_from_visible_controls() -> None:
    window = VisibleWindow("Demo", 10, "DemoWindow", "Demo App", (0, 0, 800, 600))
    controls = (
        VisibleControl("Settings", "Button", (10, 10, 120, 40)),
        VisibleControl("Delete", "Button", (10, 60, 120, 90)),
    )

    package = build_temporary_package(window=window, controls=controls)

    assert package.app_id == "temp.demo.10"
    assert package.app_name == "Demo App"
    assert package.demo_flows[0].id == "temp-demo"
    settings = package.entrypoint_by_id("temp.demo.10.settings")
    delete = package.entrypoint_by_id("temp.demo.10.delete")
    assert settings.open_steps[0].action == "clickWindowControl"
    assert delete.open_steps == []
    assert "risky" in " ".join(delete.presenter_notes).casefold()
```

- [ ] **Step 2: Run tests to verify failure**

Run: `.\.venv\Scripts\python.exe -m pytest tests\unit\test_temporary_package.py -q --no-cov`

Expected: FAIL because `temporary_package` does not exist.

- [ ] **Step 3: Implement temporary package builder**

Create `src/ai_presenter/runtime/temporary_package.py`:

```python
import re
from dataclasses import dataclass

from ai_presenter.desktop.base import VisibleControl, VisibleWindow
from ai_presenter.packages.models import MaterialPackage

_RISKY_WORDS = {
    "delete", "remove", "leave", "end", "send", "submit", "pay",
    "purchase", "transfer", "record", "share", "invite",
}
_SAFE_WORDS = {"settings", "preferences", "view", "menu", "help", "info", "details"}


@dataclass(frozen=True)
class ControlSafety:
    is_safe: bool
    reason: str


def classify_control_safety(name: str, control_type: str) -> ControlSafety:
    normalized = name.casefold()
    for word in _RISKY_WORDS:
        if word in normalized:
            return ControlSafety(False, f"risky label contains {word}")
    if control_type.casefold() in {"tab", "tabitem", "menuitem"}:
        return ControlSafety(True, f"safe control type {control_type}")
    for word in _SAFE_WORDS:
        if word in normalized:
            return ControlSafety(True, f"safe label contains {word}")
    return ControlSafety(False, "unknown safety defaults to explain-only")


def build_temporary_package(
    *,
    window: VisibleWindow,
    controls: tuple[VisibleControl, ...],
) -> MaterialPackage:
    app_id = f"temp.{_slug(window.process)}.{window.pid}"
    entrypoints = []
    steps = [
        {
            "id": "overview",
            "title": "App overview",
            "action": {"entrypointId": f"{app_id}.overview", "operation": "explain"},
            "narration": {
                "text": f"This is {window.title}. I will introduce visible controls and avoid risky actions.",
                "placement": "before",
            },
        }
    ]
    entrypoints.append(
        {
            "id": f"{app_id}.overview",
            "title": "App overview",
            "area": window.title,
            "purpose": f"Introduce the visible surface of {window.title}.",
            "openSteps": [],
            "presenterNotes": ["Generated from a running desktop window."],
        }
    )
    explainers = {
        "overview": {
            "shortScript": f"{window.title} is a running desktop app selected for a quick generated demo.",
            "details": ["This package was generated in memory from visible UI controls."],
            "relatedEntrypointIds": [f"{app_id}.overview"],
        }
    }

    for control in controls:
        control_id = f"{app_id}.{_slug(control.name)}"
        safety = classify_control_safety(control.name, control.control_type)
        open_steps = []
        operation = "open" if safety.is_safe else "explain"
        if safety.is_safe:
            open_steps.append(
                {
                    "action": "clickWindowControl",
                    "target": control.name,
                    "match": {"controlType": control.control_type, "cleanup": "escape"},
                }
            )
        entrypoints.append(
            {
                "id": control_id,
                "title": control.name,
                "area": window.title,
                "purpose": f"Explain the {control.name} control in {window.title}.",
                "openSteps": open_steps,
                "presenterNotes": [safety.reason, f"controlType={control.control_type}"],
            }
        )
        steps.append(
            {
                "id": _slug(control.name),
                "title": control.name,
                "action": {"entrypointId": control_id, "operation": operation},
                "narration": {
                    "text": f"{control.name} is visible in this app. {safety.reason}.",
                    "placement": "during" if safety.is_safe else "before",
                    "actionOffsetMs": 300,
                },
            }
        )
        explainers[_slug(control.name)] = {
            "shortScript": f"{control.name} is a visible {control.control_type} control.",
            "details": [safety.reason],
            "relatedEntrypointIds": [control_id],
        }

    return MaterialPackage.model_validate(
        {
            "appId": app_id,
            "appName": window.title or window.process,
            "version": 1,
            "profileIds": [f"{app_id}.profile"],
            "operationEntrypoints": entrypoints,
            "demoFlows": [
                {
                    "id": "temp-demo",
                    "title": f"{window.title} generated demo",
                    "goal": "Introduce visible controls safely.",
                    "steps": steps,
                }
            ],
            "explainers": explainers,
            "qa": [],
            "manualControls": [],
        }
    )


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return slug or "item"
```

- [ ] **Step 4: Run focused tests**

Run: `.\.venv\Scripts\python.exe -m pytest tests\unit\test_temporary_package.py -q --no-cov`

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add src/ai_presenter/runtime/temporary_package.py tests/unit/test_temporary_package.py
git commit -m "feat: generate temporary app packages"
```

---

### Task 5: Deterministic Question Matching And Answer Rendering

**Files:**
- Create: `src/ai_presenter/runtime/questions.py`
- Create: `tests/unit/test_questions.py`

- [ ] **Step 1: Write failing question tests**

Create `tests/unit/test_questions.py`:

```python
from pathlib import Path

from ai_presenter.packages.loader import load_material_package
from ai_presenter.runtime.questions import answer_question
from ai_presenter.runtime.voice import PresenterVoiceSettings


def test_answers_package_qa_match_in_english() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="How do I protect my real background?",
        voice=PresenterVoiceSettings(language="en", tone="professional"),
    )

    assert response.answer_text.startswith("Open Settings")
    assert response.entrypoint_id == "ringcentral.video.settings.background"


def test_answers_entrypoint_match_in_chinese() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="chat",
        voice=PresenterVoiceSettings(language="zh", tone="conversational"),
    )

    assert "聊天" in response.answer_text
    assert response.entrypoint_id == "ringcentral.video.toolbar.chat"


def test_risky_entrypoint_answer_is_not_operable() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="leave meeting",
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id == "ringcentral.video.toolbar.leave"
    assert response.can_operate is False
```

- [ ] **Step 2: Run tests to verify failure**

Run: `.\.venv\Scripts\python.exe -m pytest tests\unit\test_questions.py -q --no-cov`

Expected: FAIL because `runtime.questions` does not exist.

- [ ] **Step 3: Implement question module**

Create `src/ai_presenter/runtime/questions.py`:

```python
from dataclasses import dataclass

from ai_presenter.packages.models import MaterialPackage, OperationEntrypoint
from ai_presenter.runtime.voice import PresenterVoiceSettings

_RISKY_ENTRYPOINT_WORDS = {"leave", "recording", "record", "share", "delete", "send", "pay"}


@dataclass(frozen=True)
class QuestionResponse:
    answer_text: str
    entrypoint_id: str | None = None
    can_operate: bool = False


def answer_question(
    *,
    package: MaterialPackage,
    question: str,
    voice: PresenterVoiceSettings,
) -> QuestionResponse:
    normalized = question.casefold().strip()
    qa_match = _match_qa(package, normalized)
    if qa_match is not None:
        entrypoint_id = qa_match.related_entrypoint_ids[0] if qa_match.related_entrypoint_ids else None
        return QuestionResponse(
            answer_text=_render_text(qa_match.answer, voice),
            entrypoint_id=entrypoint_id,
            can_operate=_can_operate(package, entrypoint_id),
        )

    entrypoint = _match_entrypoint(package, normalized)
    if entrypoint is None:
        return QuestionResponse(
            answer_text=_render_text("I could not find a matching control in the active app context.", voice)
        )
    return QuestionResponse(
        answer_text=_render_entrypoint_answer(entrypoint, voice),
        entrypoint_id=entrypoint.id,
        can_operate=_can_operate(package, entrypoint.id),
    )


def _match_qa(package: MaterialPackage, normalized_question: str):
    for item in package.qa:
        if normalized_question and normalized_question in item.question.casefold():
            return item
        if item.question.casefold() in normalized_question:
            return item
    return None


def _match_entrypoint(package: MaterialPackage, normalized_question: str) -> OperationEntrypoint | None:
    best: OperationEntrypoint | None = None
    for entrypoint in package.operation_entrypoints:
        haystack = " ".join([entrypoint.id, entrypoint.title, entrypoint.area, entrypoint.purpose]).casefold()
        if normalized_question and normalized_question in haystack:
            return entrypoint
        for token in normalized_question.split():
            if len(token) >= 3 and token in haystack:
                best = entrypoint
    return best


def _render_entrypoint_answer(entrypoint: OperationEntrypoint, voice: PresenterVoiceSettings) -> str:
    base = f"{entrypoint.title}: {entrypoint.purpose}"
    return _render_text(base, voice)


def _render_text(text: str, voice: PresenterVoiceSettings) -> str:
    if voice.language == "zh":
        return _render_chinese(text, voice)
    if voice.tone == "conversational":
        return f"Sure. {text}"
    if voice.tone == "concise":
        return text.split(".")[0].strip() + "."
    return text


def _render_chinese(text: str, voice: PresenterVoiceSettings) -> str:
    replacements = {
        "Chat": "聊天",
        "chat": "聊天",
        "Invite": "邀请",
        "Settings": "设置",
        "Leave": "离开会议",
        "Background": "背景",
    }
    rendered = text
    for source, target in replacements.items():
        rendered = rendered.replace(source, target)
    prefix = "我来说明一下。" if voice.tone == "conversational" else ""
    return f"{prefix}{rendered}"


def _can_operate(package: MaterialPackage, entrypoint_id: str | None) -> bool:
    if entrypoint_id is None:
        return False
    entrypoint = package.entrypoint_by_id(entrypoint_id)
    if not entrypoint.open_steps:
        return False
    lowered = " ".join([entrypoint.id, entrypoint.title, entrypoint.purpose]).casefold()
    return not any(word in lowered for word in _RISKY_ENTRYPOINT_WORDS)
```

- [ ] **Step 4: Run focused tests**

Run: `.\.venv\Scripts\python.exe -m pytest tests\unit\test_questions.py -q --no-cov`

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add src/ai_presenter/runtime/questions.py tests/unit/test_questions.py
git commit -m "feat: answer package questions deterministically"
```

---

### Task 6: Extract Interrupt-Friendly Material Demo Runtime

**Files:**
- Create: `src/ai_presenter/runtime/material_runtime.py`
- Modify: `src/ai_presenter/runtime/factory.py`
- Create: `tests/unit/test_material_runtime.py`
- Modify: `tests/unit/test_runtime_factory.py`

- [ ] **Step 1: Write failing runtime tests**

Create `tests/unit/test_material_runtime.py`:

```python
from ai_presenter.packages.models import DemoStep, DemoStepAction, DemoStepNarration
from ai_presenter.runtime.material_runtime import MaterialDemoRuntime


class FakeTimeline:
    def __init__(self) -> None:
        self.steps: list[str] = []

    def run_step(self, step: DemoStep):
        self.steps.append(step.id)
        return type("Result", (), {"stopped": False})()


def make_step(step_id: str, entrypoint_id: str = "entry") -> DemoStep:
    return DemoStep(
        id=step_id,
        title=step_id,
        action=DemoStepAction(entrypointId=entrypoint_id, operation="explain"),
        narration=DemoStepNarration(text=step_id, placement="before"),
    )


def test_runtime_runs_flow_steps_in_order() -> None:
    timeline = FakeTimeline()
    runtime = MaterialDemoRuntime(
        flow_steps=[make_step("one"), make_step("two")],
        timeline=timeline,
        state_adjuster=lambda step: step,
    )

    runtime.run_to_completion()

    assert timeline.steps == ["one", "two"]


def test_runtime_can_run_interrupt_step_without_advancing_flow() -> None:
    timeline = FakeTimeline()
    runtime = MaterialDemoRuntime(
        flow_steps=[make_step("one"), make_step("two")],
        timeline=timeline,
        state_adjuster=lambda step: step,
    )

    runtime.run_interrupt(make_step("interrupt"))
    runtime.run_next()

    assert timeline.steps == ["interrupt", "one"]
```

- [ ] **Step 2: Run tests to verify failure**

Run: `.\.venv\Scripts\python.exe -m pytest tests\unit\test_material_runtime.py -q --no-cov`

Expected: FAIL because `material_runtime` does not exist.

- [ ] **Step 3: Implement runtime wrapper**

Create `src/ai_presenter/runtime/material_runtime.py`:

```python
from collections.abc import Callable, Sequence
from typing import Protocol

from ai_presenter.packages.models import DemoStep


class TimelineLike(Protocol):
    def run_step(self, step: DemoStep):
        ...


class MaterialDemoRuntime:
    def __init__(
        self,
        *,
        flow_steps: Sequence[DemoStep],
        timeline: TimelineLike,
        state_adjuster: Callable[[DemoStep], DemoStep | None],
    ) -> None:
        self._flow_steps = tuple(flow_steps)
        self._timeline = timeline
        self._state_adjuster = state_adjuster
        self._next_index = 0

    @property
    def is_complete(self) -> bool:
        return self._next_index >= len(self._flow_steps)

    def run_next(self) -> bool:
        if self.is_complete:
            return False
        step = self._flow_steps[self._next_index]
        self._next_index += 1
        adjusted = self._state_adjuster(step)
        if adjusted is None:
            return True
        result = self._timeline.run_step(adjusted)
        return not getattr(result, "stopped", False)

    def run_to_completion(self) -> None:
        while self.run_next():
            if self.is_complete:
                break

    def run_interrupt(self, step: DemoStep) -> None:
        self._timeline.run_step(step)
```

- [ ] **Step 4: Refactor factory to use runtime wrapper**

Modify `src/ai_presenter/runtime/factory.py` inside `run_material_demo` after timeline runner construction:

```python
    runtime = MaterialDemoRuntime(
        flow_steps=flow.steps,
        timeline=runner,
        state_adjuster=lambda step: _adjust_demo_step(profile, desktop, adapter, handle, step),
    )
    runtime.run_to_completion()
```

Add helper:

```python
def _adjust_demo_step(
    profile: DesktopAppProfile,
    desktop: WindowsDesktopDriver,
    adapter: AppAdapter,
    handle: WindowHandle,
    step: DemoStep,
) -> DemoStep | None:
    state = _capture_demo_state(profile, desktop, adapter, handle)
    return adjust_ringcentral_demo_step(step, state)
```

Import `DemoStep` and `MaterialDemoRuntime`.

- [ ] **Step 5: Run focused tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit\test_material_runtime.py tests\unit\test_runtime_factory.py -q --no-cov
```

Expected: PASS.

- [ ] **Step 6: Commit**

```powershell
git add src/ai_presenter/runtime/material_runtime.py src/ai_presenter/runtime/factory.py tests/unit/test_material_runtime.py tests/unit/test_runtime_factory.py
git commit -m "refactor: add interrupt-friendly material runtime"
```

---

### Task 7: Controller Session Model

**Files:**
- Create: `src/ai_presenter/runtime/session.py`
- Create: `tests/unit/test_controller_session.py`
- Modify: `src/ai_presenter/runtime/controller.py`

- [ ] **Step 1: Write failing session tests**

Create `tests/unit/test_controller_session.py`:

```python
from pathlib import Path

import pytest

from ai_presenter.config.loader import load_profile
from ai_presenter.config.models import DesktopAppProfile
from ai_presenter.desktop.base import VisibleControl, VisibleWindow
from ai_presenter.packages.loader import load_material_package
from ai_presenter.runtime.session import ControllerSession
from ai_presenter.runtime.session import MaterialPackageTarget
from ai_presenter.runtime.session import RunningAppTarget
from ai_presenter.runtime.voice import PresenterVoiceSettings


def load_desktop_profile() -> DesktopAppProfile:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))
    assert isinstance(profile, DesktopAppProfile)
    return profile


def test_session_blocks_target_change_while_running() -> None:
    session = ControllerSession()
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    target = MaterialPackageTarget(
        profile=load_desktop_profile(),
        package=package,
        flow_id="meeting-control-map-demo",
    )
    session.select_target(target)
    session.mark_running_for_test()

    with pytest.raises(RuntimeError, match="running"):
        session.select_target(target)


def test_session_scans_running_app_into_temporary_package() -> None:
    window = VisibleWindow("Demo", 10, "DemoWindow", "Demo App", (0, 0, 800, 600))
    controls = (VisibleControl("Settings", "Button", (10, 10, 120, 40)),)
    session = ControllerSession()

    package = session.scan_running_app(RunningAppTarget(window=window), controls)

    assert package.app_id == "temp.demo.10"
    assert package.demo_flows[0].id == "temp-demo"


def test_session_answers_question_with_active_voice_settings() -> None:
    session = ControllerSession()
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    target = MaterialPackageTarget(
        profile=load_desktop_profile(),
        package=package,
        flow_id="meeting-control-map-demo",
    )
    session.select_target(target)
    session.set_voice(PresenterVoiceSettings(language="zh", tone="conversational"))

    response = session.answer_question("chat")

    assert "聊天" in response.answer_text
```

- [ ] **Step 2: Run tests to verify failure**

Run: `.\.venv\Scripts\python.exe -m pytest tests\unit\test_controller_session.py -q --no-cov`

Expected: FAIL because `runtime.session` does not exist.

- [ ] **Step 3: Implement session model**

Create `src/ai_presenter/runtime/session.py`:

```python
from dataclasses import dataclass

from ai_presenter.config.models import DesktopAppProfile
from ai_presenter.desktop.base import VisibleControl, VisibleWindow
from ai_presenter.packages.models import MaterialPackage
from ai_presenter.runtime.questions import QuestionResponse, answer_question
from ai_presenter.runtime.temporary_package import build_temporary_package
from ai_presenter.runtime.voice import PresenterVoiceSettings, validate_profile_voice


@dataclass(frozen=True)
class MaterialPackageTarget:
    profile: DesktopAppProfile
    package: MaterialPackage
    flow_id: str


@dataclass(frozen=True)
class RunningAppTarget:
    window: VisibleWindow


ControllerTarget = MaterialPackageTarget | RunningAppTarget


class ControllerSession:
    def __init__(self) -> None:
        self._target: ControllerTarget | None = None
        self._active_package: MaterialPackage | None = None
        self._voice = PresenterVoiceSettings()
        self._running = False

    def select_target(self, target: ControllerTarget) -> None:
        if self._running:
            raise RuntimeError("Cannot change target while a demo is running.")
        self._target = target
        if isinstance(target, MaterialPackageTarget):
            validate_profile_voice(target.profile, self._voice)
            self._active_package = target.package

    def scan_running_app(
        self,
        target: RunningAppTarget,
        controls: tuple[VisibleControl, ...],
    ) -> MaterialPackage:
        if self._running:
            raise RuntimeError("Cannot scan while a demo is running.")
        package = build_temporary_package(window=target.window, controls=controls)
        self._target = target
        self._active_package = package
        return package

    def set_voice(self, voice: PresenterVoiceSettings) -> None:
        self._voice = voice
        if isinstance(self._target, MaterialPackageTarget):
            validate_profile_voice(self._target.profile, voice)

    def answer_question(self, question: str) -> QuestionResponse:
        if self._active_package is None:
            return QuestionResponse("Select or scan an app first.")
        return answer_question(
            package=self._active_package,
            question=question,
            voice=self._voice,
        )

    def mark_running_for_test(self) -> None:
        self._running = True
```

- [ ] **Step 4: Run focused tests**

Run: `.\.venv\Scripts\python.exe -m pytest tests\unit\test_controller_session.py -q --no-cov`

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add src/ai_presenter/runtime/session.py tests/unit/test_controller_session.py
git commit -m "feat: add controller session model"
```

---

### Task 8: Wire Question Interrupts Into Session Runtime

**Files:**
- Modify: `src/ai_presenter/runtime/session.py`
- Modify: `src/ai_presenter/runtime/questions.py`
- Create/Modify: `tests/unit/test_controller_session.py`

- [ ] **Step 1: Write failing interrupt tests**

Append to `tests/unit/test_controller_session.py`:

```python
def test_session_creates_interrupt_step_for_safe_answer() -> None:
    session = ControllerSession()
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    target = MaterialPackageTarget(
        profile=load_desktop_profile(),
        package=package,
        flow_id="meeting-control-map-demo",
    )
    session.select_target(target)

    response = session.answer_question("chat")
    interrupt = session.create_interrupt_step(response)

    assert interrupt is not None
    assert interrupt.action.entrypoint_id == "ringcentral.video.toolbar.chat"
    assert interrupt.narration.text == response.answer_text


def test_session_does_not_create_interrupt_for_risky_answer() -> None:
    session = ControllerSession()
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    session.select_target(
        MaterialPackageTarget(
            profile=load_desktop_profile(),
            package=package,
            flow_id="meeting-control-map-demo",
        )
    )

    response = session.answer_question("leave meeting")

    assert session.create_interrupt_step(response) is None
```

- [ ] **Step 2: Run tests to verify failure**

Run: `.\.venv\Scripts\python.exe -m pytest tests\unit\test_controller_session.py -q --no-cov`

Expected: FAIL because `create_interrupt_step` is missing.

- [ ] **Step 3: Implement interrupt-step creation**

In `src/ai_presenter/runtime/session.py`, import package models:

```python
from ai_presenter.packages.models import DemoStep, DemoStepAction, DemoStepNarration
```

Add method:

```python
    def create_interrupt_step(self, response: QuestionResponse) -> DemoStep | None:
        if self._active_package is None or response.entrypoint_id is None or not response.can_operate:
            return None
        entrypoint = self._active_package.entrypoint_by_id(response.entrypoint_id)
        if not entrypoint.open_steps:
            return None
        return DemoStep(
            id=f"question-{entrypoint.id}",
            title=f"Question: {entrypoint.title}",
            action=DemoStepAction(entrypointId=entrypoint.id, operation="open"),
            narration=DemoStepNarration(
                text=response.answer_text,
                placement="during",
                actionOffsetMs=300,
            ),
        )
```

- [ ] **Step 4: Run focused tests**

Run: `.\.venv\Scripts\python.exe -m pytest tests\unit\test_controller_session.py -q --no-cov`

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add src/ai_presenter/runtime/session.py tests/unit/test_controller_session.py
git commit -m "feat: create question interrupt steps"
```

---

### Task 9: Controller UI Wiring

**Files:**
- Modify: `src/ai_presenter/runtime/controller.py`
- Modify: `tests/unit/test_controller.py`
- Modify: `README.md`

- [ ] **Step 1: Write controller-level non-Tk tests**

Add to `tests/unit/test_controller.py`:

```python
def test_controller_session_answers_question_text() -> None:
    profile, package = _controller_inputs()
    controller = PresenterController(
        profile=profile,
        material_package=package,
        flow_id="meeting-control-map-demo",
    )

    answer = controller.submit_question("chat")

    assert "Chat" in answer or "chat" in answer
```

- [ ] **Step 2: Run test to verify failure**

Run: `.\.venv\Scripts\python.exe -m pytest tests\unit\test_controller.py -q --no-cov`

Expected: FAIL because `PresenterController.submit_question` is not defined.

- [ ] **Step 3: Add compatibility question method to existing controller**

In `src/ai_presenter/runtime/controller.py`, import:

```python
from ai_presenter.runtime.questions import answer_question
from ai_presenter.runtime.voice import PresenterVoiceSettings
```

Add to `PresenterController`:

```python
    def submit_question(self, question: str) -> str:
        response = answer_question(
            package=self._material_package,
            question=question,
            voice=PresenterVoiceSettings(),
        )
        return response.answer_text
```

This preserves the current constructor while the full session UI is wired.

- [ ] **Step 4: Expand Tk UI**

Modify `run_controller`:

- Grow window to `640x360`.
- Add language dropdown with values `English`, `Chinese`.
- Add tone dropdown with values `Professional`, `Conversational`, `Concise`.
- Add question entry and Submit button.
- Add answer/status label.

Use this Tk code pattern inside `run_controller`:

```python
    language = tk.StringVar(value="English")
    tone = tk.StringVar(value="Professional")
    question = tk.StringVar(value="")
    answer = tk.StringVar(value="")

    def submit_question() -> None:
        text = question.get().strip()
        if not text:
            return
        try:
            answer.set(controller.submit_question(text))
        except Exception as exc:
            answer.set(f"Question error: {exc}")

    voice_row = tk.Frame(frame)
    voice_row.pack(fill="x", pady=(0, 12))
    tk.OptionMenu(voice_row, language, "English", "Chinese").pack(side="left", padx=(0, 8))
    tk.OptionMenu(voice_row, tone, "Professional", "Conversational", "Concise").pack(side="left")

    question_row = tk.Frame(frame)
    question_row.pack(fill="x", pady=(12, 8))
    tk.Entry(question_row, textvariable=question).pack(side="left", fill="x", expand=True, padx=(0, 8))
    tk.Button(question_row, text="Submit", command=submit_question, width=10).pack(side="left")
    tk.Label(frame, textvariable=answer, anchor="w", wraplength=580, justify="left").pack(fill="x")
```

- [ ] **Step 5: Run focused tests**

Run: `.\.venv\Scripts\python.exe -m pytest tests\unit\test_controller.py -q --no-cov`

Expected: PASS.

- [ ] **Step 6: Update README**

Add under controller docs:

```markdown
The controller includes language and tone selectors plus a text question box. Text questions are
answered from the active material package. Safe matched controls can later be demonstrated as
interrupt steps; risky controls are answer-only.
```

- [ ] **Step 7: Commit**

```powershell
git add src/ai_presenter/runtime/controller.py tests/unit/test_controller.py README.md
git commit -m "feat: add controller question and voice controls"
```

---

### Task 10: Full Controller Target Selection UI

**Files:**
- Modify: `src/ai_presenter/runtime/controller.py`
- Modify: `src/ai_presenter/cli.py`
- Modify: `tests/unit/test_cli.py`
- Modify: `README.md`

- [ ] **Step 1: Write CLI/controller dry-run test**

Add to `tests/unit/test_cli.py`:

```python
def test_controller_dry_run_reports_selectable_mode() -> None:
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
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "Controller dry run complete." in result.stdout
```

This test likely already passes; keep it as a guard while changing controller internals.

- [ ] **Step 2: Refactor `run_controller` layout**

Keep existing arguments as the initial selected material package. Add UI sections:

```python
    source = tk.StringVar(value="Material package")
    package_choice = tk.StringVar(value=material_package.app_id)
    flow_choice = tk.StringVar(value=flow_id)
    app_choice = tk.StringVar(value="")
```

Add target row:

```python
    target_frame = tk.LabelFrame(frame, text="Target", padx=8, pady=8)
    target_frame.pack(fill="x", pady=(0, 12))
    tk.OptionMenu(target_frame, source, "Material package", "Running desktop app").pack(side="left")
    tk.Label(target_frame, textvariable=package_choice).pack(side="left", padx=(8, 0))
    tk.Label(target_frame, textvariable=flow_choice).pack(side="left", padx=(8, 0))
```

First implementation may show running app choices after Task 11 wires catalog into UI.

- [ ] **Step 3: Run tests**

Run: `.\.venv\Scripts\python.exe -m pytest tests\unit\test_cli.py tests\unit\test_controller.py -q --no-cov`

Expected: PASS.

- [ ] **Step 4: Commit**

```powershell
git add src/ai_presenter/runtime/controller.py src/ai_presenter/cli.py tests/unit/test_cli.py README.md
git commit -m "feat: add controller target selector shell"
```

---

### Task 11: Running App Scan UI Integration

**Files:**
- Modify: `src/ai_presenter/runtime/controller.py`
- Modify: `src/ai_presenter/runtime/session.py`
- Modify: `tests/unit/test_controller_session.py`
- Modify: `README.md`

- [ ] **Step 1: Write session scan integration test**

Add to `tests/unit/test_controller_session.py`:

```python
def test_session_answer_after_running_app_scan() -> None:
    session = ControllerSession()
    window = VisibleWindow("Demo", 10, "DemoWindow", "Demo App", (0, 0, 800, 600))
    controls = (VisibleControl("Settings", "Button", (10, 10, 120, 40)),)

    session.scan_running_app(RunningAppTarget(window=window), controls)
    response = session.answer_question("settings")

    assert response.entrypoint_id == "temp.demo.10.settings"
    assert response.can_operate is True
```

- [ ] **Step 2: Run focused tests**

Run: `.\.venv\Scripts\python.exe -m pytest tests\unit\test_controller_session.py -q --no-cov`

Expected: PASS if previous session implementation is complete.

- [ ] **Step 3: Wire Scan button in Tk UI**

In `run_controller`, instantiate:

```python
from ai_presenter.desktop.windows import WindowsDesktopDriver
from ai_presenter.runtime.catalog import ControllerAppCatalog
from ai_presenter.runtime.session import ControllerSession, RunningAppTarget

desktop = WindowsDesktopDriver()
session = ControllerSession()
catalog = ControllerAppCatalog(package_dir=REPO_PACKAGE_DIR, desktop=desktop)
running_windows = list(catalog.list_running_apps())
```

Add scan callback:

```python
    def scan_selected_app() -> None:
        try:
            selected = running_windows[0]
            handle = WindowHandle(
                process=selected.process,
                pid=selected.pid,
                window_class=selected.window_class,
                title=selected.title,
            )
            controls = desktop.list_visible_controls(handle)
            package = session.scan_running_app(RunningAppTarget(selected), controls)
            status.set(f"Scanned {package.app_name}: {len(package.operation_entrypoints)} entrypoints")
        except Exception as exc:
            status.set(f"Scan error: {exc}")
```

Use a simple first-version `OptionMenu` for `running_windows`, mapping display text to index.

- [ ] **Step 4: Run smoke commands**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit\test_controller_session.py tests\unit\test_controller.py -q --no-cov
.\.venv\Scripts\ai-presenter.exe controller --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --dry-run
```

Expected: PASS and controller dry-run complete.

- [ ] **Step 5: Commit**

```powershell
git add src/ai_presenter/runtime/controller.py src/ai_presenter/runtime/session.py tests/unit/test_controller_session.py README.md
git commit -m "feat: scan running apps from controller"
```

---

### Task 12: Final Verification And Manual Acceptance Docs

**Files:**
- Modify: `README.md`
- Modify: `docs/runbooks/ringcentral-manual-acceptance.md`

- [ ] **Step 1: Update manual acceptance runbook**

Add checklist items:

```markdown
- [ ] Open controller and verify the Target section shows Material package mode.
- [ ] Start `meeting-control-map-demo`, Pause, Resume, and End.
- [ ] Ask `What does Invite do?` and verify the answer area updates.
- [ ] Switch language to Chinese and ask `chat`; verify Chinese answer text.
- [ ] Switch tone to Conversational and verify the answer is warmer but still accurate.
- [ ] Switch to Running desktop app mode, refresh windows, select a harmless app, and scan.
- [ ] Verify generated package status reports entrypoints.
- [ ] Ask about a safe visible control and verify answer plus safe action.
- [ ] Ask about a risky visible control and verify no click happens.
```

- [ ] **Step 2: Run full automated verification**

Run:

```powershell
.\.venv\Scripts\python.exe -m ruff check src tests
.\.venv\Scripts\python.exe -m mypy src tests
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
.\.venv\Scripts\ai-presenter.exe controller --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --dry-run
```

Expected:

- ruff: `All checks passed!`
- mypy: `Success: no issues found`
- pytest: all tests pass
- doctor: `0 failed`
- controller dry-run: `Controller dry run complete.`

- [ ] **Step 3: Remove temporary coverage artifact**

Run:

```powershell
Remove-Item -LiteralPath .coverage -Force -ErrorAction SilentlyContinue
git status --short
```

Expected: no `.coverage` file.

- [ ] **Step 4: Commit docs and final polish**

```powershell
git add README.md docs/runbooks/ringcentral-manual-acceptance.md
git commit -m "docs: add controller app selection acceptance steps"
```

- [ ] **Step 5: Push branch**

```powershell
git push
```

Expected: remote branch `codex/ai-presenter-mvp` updates successfully.

---

## Self-Review

Spec coverage:

- App selection is covered by Tasks 3, 7, 10, and 11.
- Existing material packages are preserved by Tasks 6, 7, and 10.
- Running desktop app discovery is covered by Tasks 2, 3, 4, 7, and 11.
- Temporary package generation is covered by Task 4.
- Text question entry and answering are covered by Tasks 5, 7, 8, and 9.
- Safe operable question interrupts are covered by Tasks 6 and 8.
- English/Chinese language and tone switching are covered by Tasks 1, 5, 7, and 9.
- Docs and manual acceptance are covered by Task 12.

Placeholder scan:

- The plan contains no `TBD`, `TODO`, or open-ended "add tests" steps.
- Every implementation task includes a concrete focused test command and commit command.

Type consistency:

- `PresenterVoiceSettings`, `QuestionResponse`, `ControllerSession`, `MaterialPackageTarget`,
  `RunningAppTarget`, `VisibleWindow`, and `VisibleControl` are introduced before later tasks use them.
- Controller UI uses session/catalog units introduced in earlier tasks.
