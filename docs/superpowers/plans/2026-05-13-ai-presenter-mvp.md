# AI Presenter MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a config-driven Python CLI MVP that launches the RingCentral meeting flow, binds `RingCentralVideoClass`, observes meeting UI state/events, generates constrained narration, and routes TTS audio to speaker, virtual microphone, or both.

**Architecture:** The runtime is app-profile first: core orchestration is app-agnostic, while RingCentral behavior lives in a profile and adapter. Implementation proceeds from tested schemas and pure runtime logic outward to Windows desktop integration, provider integration, and manual RingCentral acceptance.

**Tech Stack:** Python 3.10+, Typer, Pydantic, PyYAML, pytest, pywinauto, uiautomation, psutil, mss, Pillow, sounddevice, soundfile, OpenAI Python SDK.

---

## Source Spec

This plan implements `docs/superpowers/specs/2026-05-13-ai-presenter-design.md`.

OpenAI provider tasks should follow the current official OpenAI Responses and Audio Speech APIs:

- https://platform.openai.com/docs/api-reference/responses
- https://platform.openai.com/docs/api-reference/audio/createSpeech
- https://platform.openai.com/docs/guides/structured-outputs

## File Structure

Create these files:

- `pyproject.toml`: package metadata, runtime dependencies, dev dependencies, script entry point, pytest/ruff/mypy config.
- `README.md`: local setup, provider environment variables, virtual audio setup, and RingCentral MVP run command.
- `.env.example`: environment variable names without secrets.
- `src/ai_presenter/__init__.py`: package marker and version.
- `src/ai_presenter/cli.py`: Typer CLI entry point.
- `src/ai_presenter/config/models.py`: Pydantic models for profiles, providers, audio, launch, bind, observe, and narration policies.
- `src/ai_presenter/config/loader.py`: profile YAML loading and validation.
- `src/ai_presenter/domain/state.py`: structured observation state, meeting state, events, and narration request/result models.
- `src/ai_presenter/runtime/events.py`: state reducer and event detector.
- `src/ai_presenter/runtime/narration.py`: narration policy, cooldown, de-duplication, and provider call orchestration.
- `src/ai_presenter/runtime/presenter.py`: presenter loop that observes, reduces, detects, narrates, and outputs.
- `src/ai_presenter/runtime/profile_runner.py`: launch phase and presenter phase orchestration.
- `src/ai_presenter/providers/base.py`: provider protocols and provider registry.
- `src/ai_presenter/providers/fake.py`: deterministic providers for tests and dry runs.
- `src/ai_presenter/providers/openai_provider.py`: OpenAI vision/narration/speech provider implementation.
- `src/ai_presenter/media/output.py`: speaker, virtual microphone, combined, and null media outputs.
- `src/ai_presenter/desktop/base.py`: desktop automation and observation protocols.
- `src/ai_presenter/desktop/windows.py`: Windows implementation using pywinauto, uiautomation, psutil, mss, and Pillow.
- `src/ai_presenter/adapters/base.py`: app adapter protocol.
- `src/ai_presenter/adapters/ringcentral.py`: RingCentral adapter for launch, bind, and state extraction.
- `profiles/ringcentral-video.yaml`: first supported app profile.
- `tests/unit/test_config_loader.py`: profile parsing tests.
- `tests/unit/test_events.py`: state reducer and event detector tests.
- `tests/unit/test_narration.py`: narration policy and de-duplication tests.
- `tests/unit/test_media_output.py`: media routing tests with mocked sinks.
- `tests/unit/test_profile_runner.py`: launch/bind orchestration tests with fake adapter.
- `tests/unit/test_cli.py`: CLI smoke tests.
- `tests/integration/test_ringcentral_profile.py`: RingCentral profile and adapter integration tests without real RingCentral.
- `tests/integration/test_presenter_loop.py`: full loop tests with fake desktop and fake providers.
- `docs/runbooks/ringcentral-manual-acceptance.md`: manual RingCentral verification checklist.

Keep files focused. Do not put runtime, provider, desktop, and RingCentral-specific logic into the same module.

## Task 1: Bootstrap Python Package And Test Harness

**Files:**
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `.env.example`
- Create: `src/ai_presenter/__init__.py`
- Create: `tests/unit/test_cli.py`

- [ ] **Step 1: Write the failing CLI import test**

Create `tests/unit/test_cli.py`:

```python
from typer.testing import CliRunner

from ai_presenter.cli import app


def test_cli_help_renders():
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "AI presenter" in result.stdout
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```powershell
python -m pytest tests/unit/test_cli.py -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'ai_presenter'`.

- [ ] **Step 3: Add package metadata and dependencies**

Create `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=69", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "ai-presenter"
version = "0.1.0"
description = "Config-driven AI presenter for desktop and browser app profiles"
requires-python = ">=3.10"
dependencies = [
  "typer>=0.12.0",
  "pydantic>=2.7.0",
  "PyYAML>=6.0.1",
  "rich>=13.7.0",
  "psutil>=5.9.8",
  "pywinauto>=0.6.8",
  "uiautomation>=2.0.20",
  "mss>=9.0.1",
  "Pillow>=10.3.0",
  "sounddevice>=0.4.6",
  "soundfile>=0.12.1",
  "numpy>=1.26.0",
  "openai>=1.99.0",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.2.0",
  "pytest-cov>=5.0.0",
  "pytest-mock>=3.14.0",
  "pip-audit>=2.7.0",
  "ruff>=0.5.0",
  "mypy>=1.10.0",
]

[project.scripts]
ai-presenter = "ai_presenter.cli:app"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=ai_presenter --cov-report=term-missing"

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.mypy]
python_version = "3.10"
strict = true
warn_unused_ignores = true
```

- [ ] **Step 4: Add the minimal package and CLI**

Create `src/ai_presenter/__init__.py`:

```python
__version__ = "0.1.0"
```

Create `src/ai_presenter/cli.py`:

```python
import typer

app = typer.Typer(help="AI presenter CLI for configured app profiles.")


@app.command()
def run(profile: str = typer.Option(..., "--profile", help="Profile id or YAML path.")) -> None:
    """Run an AI presenter profile."""
    typer.echo(f"Profile requested: {profile}")
```

- [ ] **Step 5: Add setup documentation**

Create `README.md`:

```markdown
# AI Presenter

Config-driven AI presenter MVP for desktop app profiles.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -U pip
.venv\Scripts\python -m pip install -e ".[dev]"
```

## Run

```powershell
.venv\Scripts\ai-presenter run --profile ringcentral-video
```

The RingCentral MVP assumes `RingCentralDevelop` is already open and logged in.
```

Create `.env.example`:

```dotenv
OPENAI_API_KEY=
AI_PRESENTER_OPENAI_NARRATION_MODEL=
AI_PRESENTER_VIRTUAL_MIC_DEVICE=VB-CABLE Input
```

- [ ] **Step 6: Run tests**

Run:

```powershell
python -m pip install -e ".[dev]"
python -m pytest tests/unit/test_cli.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit**

Run:

```powershell
git add pyproject.toml README.md .env.example src/ai_presenter/__init__.py src/ai_presenter/cli.py tests/unit/test_cli.py
git commit -m "chore: bootstrap ai presenter package"
```

## Task 2: Add Profile Schema And Loader

**Files:**
- Create: `src/ai_presenter/config/models.py`
- Create: `src/ai_presenter/config/loader.py`
- Create: `profiles/ringcentral-video.yaml`
- Create: `tests/unit/test_config_loader.py`

- [ ] **Step 1: Write profile loader tests**

Create `tests/unit/test_config_loader.py`:

```python
from pathlib import Path

import pytest
from pydantic import ValidationError

from ai_presenter.config.loader import load_profile
from ai_presenter.config.models import AudioOutputMode, ProfileType


def test_load_ringcentral_profile():
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))

    assert profile.id == "ringcentral-video"
    assert profile.type is ProfileType.DESKTOP
    assert profile.launch.app_process == "RingCentralDevelop"
    assert profile.bind.process == "RingCentralVideo"
    assert profile.bind.window_class == "RingCentralVideoClass"
    assert profile.audio.output is AudioOutputMode.BOTH


def test_rejects_unknown_audio_mode(tmp_path: Path):
    profile_path = tmp_path / "bad.yaml"
    profile_path.write_text(
        """
id: bad
type: desktop
launch:
  appProcess: App
  requireAlreadyLoggedIn: true
  steps: []
bind:
  process: Proc
  windowClass: Class
observe:
  intervalMs: 1000
  sources: [screenshot]
events: []
narration:
  style: concise_presenter
  maxSentences: 2
  minSecondsBetweenUtterances: 4
  repeatCooldownSeconds: 30
  confidenceThreshold: 0.75
  forbidSharedScreenInterpretation: true
audio:
  output: invalid
providers:
  vision: fake
  narration: fake
  speech: fake
""",
        encoding="utf-8",
    )

    with pytest.raises(ValidationError):
        load_profile(profile_path)
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
python -m pytest tests/unit/test_config_loader.py -q
```

Expected: FAIL with missing `ai_presenter.config` module.

- [ ] **Step 3: Implement schema models**

Create `src/ai_presenter/config/models.py`:

```python
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CamelModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class ProfileType(str, Enum):
    DESKTOP = "desktop"
    BROWSER = "browser"


class ObservationSource(str, Enum):
    SCREENSHOT = "screenshot"
    WINDOWS_UI_AUTOMATION = "windowsUiAutomation"
    WINDOW_METADATA = "windowMetadata"


class AudioOutputMode(str, Enum):
    SPEAKER = "speaker"
    VIRTUAL_MIC = "virtual_mic"
    BOTH = "both"


class LaunchStep(CamelModel):
    action: str
    target: str | None = None
    match: dict[str, Any] = Field(default_factory=dict)


class LaunchConfig(CamelModel):
    app_process: str = Field(alias="appProcess")
    require_already_logged_in: bool = Field(alias="requireAlreadyLoggedIn")
    steps: list[LaunchStep]


class BindConfig(CamelModel):
    process: str
    window_class: str = Field(alias="windowClass")
    timeout_ms: int = Field(default=30_000, alias="timeoutMs", ge=1_000)


class ObserveConfig(CamelModel):
    interval_ms: int = Field(alias="intervalMs", ge=250)
    sources: list[ObservationSource]


class NarrationConfig(CamelModel):
    style: str
    max_sentences: int = Field(alias="maxSentences", ge=1, le=3)
    min_seconds_between_utterances: float = Field(alias="minSecondsBetweenUtterances", ge=0)
    repeat_cooldown_seconds: float = Field(alias="repeatCooldownSeconds", ge=0)
    confidence_threshold: float = Field(alias="confidenceThreshold", ge=0, le=1)
    forbid_shared_screen_interpretation: bool = Field(alias="forbidSharedScreenInterpretation")


class AudioConfig(CamelModel):
    output: AudioOutputMode
    speaker_device: str = Field(default="default", alias="speakerDevice")
    virtual_mic_device: str | None = Field(default=None, alias="virtualMicDevice")


class ProviderConfig(CamelModel):
    vision: str
    narration: str
    speech: str


class AppProfile(CamelModel):
    id: str
    type: ProfileType
    launch: LaunchConfig
    bind: BindConfig
    observe: ObserveConfig
    events: list[str]
    narration: NarrationConfig
    audio: AudioConfig
    providers: ProviderConfig
```

- [ ] **Step 4: Implement YAML loading**

Create `src/ai_presenter/config/loader.py`:

```python
from pathlib import Path
from typing import Any

import yaml

from ai_presenter.config.models import AppProfile


def load_profile(path: Path) -> AppProfile:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Profile must be a YAML mapping: {path}")
    return AppProfile.model_validate(raw)


def profile_to_public_dict(profile: AppProfile) -> dict[str, Any]:
    return profile.model_dump(mode="json", by_alias=True)
```

- [ ] **Step 5: Add the RingCentral profile**

Create `profiles/ringcentral-video.yaml`:

```yaml
id: ringcentral-video
type: desktop

launch:
  appProcess: RingCentralDevelop
  requireAlreadyLoggedIn: true
  steps:
    - action: focusWindow
      match:
        process: RingCentralDevelop
    - action: clickTab
      target: Video
    - action: clickButton
      target: Start

bind:
  process: RingCentralVideo
  windowClass: RingCentralVideoClass
  timeoutMs: 30000

observe:
  intervalMs: 1000
  sources:
    - screenshot
    - windowsUiAutomation
    - windowMetadata

events:
  - meeting_joined
  - mic_state_changed
  - camera_state_changed
  - participant_count_changed
  - dialog_appeared
  - connection_warning

narration:
  style: concise_presenter
  maxSentences: 2
  minSecondsBetweenUtterances: 4
  repeatCooldownSeconds: 30
  confidenceThreshold: 0.75
  forbidSharedScreenInterpretation: true

audio:
  output: both
  speakerDevice: default
  virtualMicDevice: "VB-CABLE Input"

providers:
  vision: fake
  narration: fake
  speech: fake
```

- [ ] **Step 6: Run tests**

Run:

```powershell
python -m pytest tests/unit/test_config_loader.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit**

Run:

```powershell
git add src/ai_presenter/config profiles/ringcentral-video.yaml tests/unit/test_config_loader.py
git commit -m "feat: add profile schema and ringcentral profile"
```

## Task 3: Add Domain State, Reducer, And Event Detector

**Files:**
- Create: `src/ai_presenter/domain/state.py`
- Create: `src/ai_presenter/runtime/events.py`
- Create: `tests/unit/test_events.py`

- [ ] **Step 1: Write event detector tests**

Create `tests/unit/test_events.py`:

```python
from ai_presenter.domain.state import MeetingState
from ai_presenter.runtime.events import EventDetector


def test_detects_initial_meeting_joined_event():
    detector = EventDetector()
    current = MeetingState(meeting_joined=True, confidence=0.9)

    events = detector.detect(previous=None, current=current)

    assert [event.type for event in events] == ["meeting_joined"]


def test_detects_mic_state_change():
    detector = EventDetector()
    previous = MeetingState(meeting_joined=True, mic_muted=False, confidence=0.9)
    current = MeetingState(meeting_joined=True, mic_muted=True, confidence=0.9)

    events = detector.detect(previous=previous, current=current)

    assert len(events) == 1
    assert events[0].type == "mic_state_changed"
    assert events[0].payload == {"micMuted": True}


def test_ignores_low_confidence_state():
    detector = EventDetector(confidence_threshold=0.75)
    current = MeetingState(meeting_joined=True, confidence=0.4)

    events = detector.detect(previous=None, current=current)

    assert events == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
python -m pytest tests/unit/test_events.py -q
```

Expected: FAIL with missing `ai_presenter.domain` module.

- [ ] **Step 3: Implement domain models**

Create `src/ai_presenter/domain/state.py`:

```python
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class WindowMetadata:
    process: str
    pid: int
    window_class: str
    title: str
    bounds: tuple[int, int, int, int]
    focused: bool = False
    minimized: bool = False


@dataclass(frozen=True)
class RawObservation:
    metadata: WindowMetadata
    screenshot_png: bytes | None = None
    ui_text: list[str] = field(default_factory=list)
    captured_at: datetime = field(default_factory=utc_now)


@dataclass(frozen=True)
class MeetingState:
    meeting_joined: bool | None = None
    mic_muted: bool | None = None
    camera_off: bool | None = None
    active_dialog: str | None = None
    participant_count: int | None = None
    connection_warning: str | None = None
    confidence: float = 1.0


@dataclass(frozen=True)
class PresenterEvent:
    type: str
    payload: dict[str, Any]
    confidence: float
    occurred_at: datetime = field(default_factory=utc_now)
```

- [ ] **Step 4: Implement event detection**

Create `src/ai_presenter/runtime/events.py`:

```python
from ai_presenter.domain.state import MeetingState, PresenterEvent


class EventDetector:
    def __init__(self, confidence_threshold: float = 0.75) -> None:
        self._confidence_threshold = confidence_threshold

    def detect(
        self,
        previous: MeetingState | None,
        current: MeetingState,
    ) -> list[PresenterEvent]:
        if current.confidence < self._confidence_threshold:
            return []

        events: list[PresenterEvent] = []

        if previous is None:
            if current.meeting_joined is True:
                events.append(PresenterEvent("meeting_joined", {}, current.confidence))
            if current.active_dialog:
                events.append(
                    PresenterEvent(
                        "dialog_appeared",
                        {"activeDialog": current.active_dialog},
                        current.confidence,
                    )
                )
            return events

        if previous.mic_muted != current.mic_muted and current.mic_muted is not None:
            events.append(
                PresenterEvent(
                    "mic_state_changed",
                    {"micMuted": current.mic_muted},
                    current.confidence,
                )
            )

        if previous.camera_off != current.camera_off and current.camera_off is not None:
            events.append(
                PresenterEvent(
                    "camera_state_changed",
                    {"cameraOff": current.camera_off},
                    current.confidence,
                )
            )

        if (
            previous.participant_count != current.participant_count
            and current.participant_count is not None
        ):
            events.append(
                PresenterEvent(
                    "participant_count_changed",
                    {"participantCount": current.participant_count},
                    current.confidence,
                )
            )

        if previous.active_dialog != current.active_dialog and current.active_dialog:
            events.append(
                PresenterEvent(
                    "dialog_appeared",
                    {"activeDialog": current.active_dialog},
                    current.confidence,
                )
            )

        if previous.connection_warning != current.connection_warning and current.connection_warning:
            events.append(
                PresenterEvent(
                    "connection_warning",
                    {"connectionWarning": current.connection_warning},
                    current.confidence,
                )
            )

        return events
```

- [ ] **Step 5: Run tests**

Run:

```powershell
python -m pytest tests/unit/test_events.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```powershell
git add src/ai_presenter/domain src/ai_presenter/runtime/events.py tests/unit/test_events.py
git commit -m "feat: add meeting state event detection"
```

## Task 4: Add Provider Interfaces And Fake Providers

**Files:**
- Create: `src/ai_presenter/providers/base.py`
- Create: `src/ai_presenter/providers/fake.py`
- Create: `tests/unit/test_provider_registry.py`

- [ ] **Step 1: Write provider registry tests**

Create `tests/unit/test_provider_registry.py`:

```python
import pytest

from ai_presenter.domain.state import MeetingState, PresenterEvent
from ai_presenter.providers.base import ProviderRegistry
from ai_presenter.providers.fake import FakeSpeechProvider, FakeVisionProvider


def test_registry_returns_registered_provider():
    registry = ProviderRegistry()
    vision = FakeVisionProvider(MeetingState(meeting_joined=True, confidence=0.9))

    registry.register_vision("fake", vision)

    assert registry.vision("fake") is vision


def test_registry_rejects_missing_provider():
    registry = ProviderRegistry()

    with pytest.raises(KeyError):
        registry.speech("missing")


def test_fake_speech_returns_wav_bytes():
    audio = FakeSpeechProvider().synthesize("Meeting joined.")

    assert audio.mime_type == "audio/wav"
    assert audio.data.startswith(b"RIFF")
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
python -m pytest tests/unit/test_provider_registry.py -q
```

Expected: FAIL with missing provider modules.

- [ ] **Step 3: Implement provider protocols and registry**

Create `src/ai_presenter/providers/base.py`:

```python
from dataclasses import dataclass
from typing import Protocol

from ai_presenter.domain.state import MeetingState, PresenterEvent, RawObservation


@dataclass(frozen=True)
class SpeechAudio:
    data: bytes
    mime_type: str
    sample_rate: int
    channels: int


class VisionProvider(Protocol):
    def recognize(self, observation: RawObservation) -> MeetingState:
        ...


class NarrationProvider(Protocol):
    def narrate(self, state: MeetingState, events: list[PresenterEvent]) -> str:
        ...


class SpeechProvider(Protocol):
    def synthesize(self, text: str) -> SpeechAudio:
        ...


class ProviderRegistry:
    def __init__(self) -> None:
        self._vision: dict[str, VisionProvider] = {}
        self._narration: dict[str, NarrationProvider] = {}
        self._speech: dict[str, SpeechProvider] = {}

    def register_vision(self, name: str, provider: VisionProvider) -> None:
        self._vision[name] = provider

    def register_narration(self, name: str, provider: NarrationProvider) -> None:
        self._narration[name] = provider

    def register_speech(self, name: str, provider: SpeechProvider) -> None:
        self._speech[name] = provider

    def vision(self, name: str) -> VisionProvider:
        return self._vision[name]

    def narration(self, name: str) -> NarrationProvider:
        return self._narration[name]

    def speech(self, name: str) -> SpeechProvider:
        return self._speech[name]
```

- [ ] **Step 4: Implement deterministic fake providers**

Create `src/ai_presenter/providers/fake.py`:

```python
import io
import wave

from ai_presenter.domain.state import MeetingState, PresenterEvent, RawObservation
from ai_presenter.providers.base import SpeechAudio


class FakeVisionProvider:
    def __init__(self, state: MeetingState | None = None) -> None:
        self._state = state or MeetingState(meeting_joined=True, confidence=1.0)

    def recognize(self, observation: RawObservation) -> MeetingState:
        return self._state


class FakeNarrationProvider:
    def narrate(self, state: MeetingState, events: list[PresenterEvent]) -> str:
        if not events:
            return ""
        event_names = ", ".join(event.type for event in events)
        return f"Detected meeting event: {event_names}."


class FakeSpeechProvider:
    def synthesize(self, text: str) -> SpeechAudio:
        sample_rate = 16_000
        frames = b"\x00\x00" * int(sample_rate * 0.1)
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(frames)
        return SpeechAudio(
            data=buffer.getvalue(),
            mime_type="audio/wav",
            sample_rate=sample_rate,
            channels=1,
        )
```

- [ ] **Step 5: Run tests**

Run:

```powershell
python -m pytest tests/unit/test_provider_registry.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```powershell
git add src/ai_presenter/providers tests/unit/test_provider_registry.py
git commit -m "feat: add provider interfaces"
```

## Task 5: Add Narration Engine With Cooldown And De-Duplication

**Files:**
- Create: `src/ai_presenter/runtime/narration.py`
- Create: `tests/unit/test_narration.py`

- [ ] **Step 1: Write narration tests**

Create `tests/unit/test_narration.py`:

```python
from ai_presenter.config.models import NarrationConfig
from ai_presenter.domain.state import MeetingState, PresenterEvent
from ai_presenter.providers.fake import FakeNarrationProvider
from ai_presenter.runtime.narration import NarrationEngine


def make_config() -> NarrationConfig:
    return NarrationConfig.model_validate(
        {
            "style": "concise_presenter",
            "maxSentences": 2,
            "minSecondsBetweenUtterances": 4,
            "repeatCooldownSeconds": 30,
            "confidenceThreshold": 0.75,
            "forbidSharedScreenInterpretation": True,
        }
    )


def test_generates_for_first_event():
    engine = NarrationEngine(make_config(), FakeNarrationProvider(), now=lambda: 100.0)
    text = engine.maybe_narrate(MeetingState(confidence=0.9), [PresenterEvent("meeting_joined", {}, 0.9)])

    assert text == "Detected meeting event: meeting_joined."


def test_suppresses_repeated_event_during_cooldown():
    current_time = 100.0
    engine = NarrationEngine(make_config(), FakeNarrationProvider(), now=lambda: current_time)

    first = engine.maybe_narrate(MeetingState(confidence=0.9), [PresenterEvent("meeting_joined", {}, 0.9)])
    second = engine.maybe_narrate(MeetingState(confidence=0.9), [PresenterEvent("meeting_joined", {}, 0.9)])

    assert first
    assert second is None


def test_suppresses_low_confidence_event():
    engine = NarrationEngine(make_config(), FakeNarrationProvider(), now=lambda: 100.0)
    text = engine.maybe_narrate(MeetingState(confidence=0.5), [PresenterEvent("meeting_joined", {}, 0.5)])

    assert text is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
python -m pytest tests/unit/test_narration.py -q
```

Expected: FAIL with missing `runtime.narration`.

- [ ] **Step 3: Implement narration engine**

Create `src/ai_presenter/runtime/narration.py`:

```python
import time
from collections.abc import Callable

from ai_presenter.config.models import NarrationConfig
from ai_presenter.domain.state import MeetingState, PresenterEvent
from ai_presenter.providers.base import NarrationProvider


class NarrationEngine:
    def __init__(
        self,
        config: NarrationConfig,
        provider: NarrationProvider,
        now: Callable[[], float] | None = None,
    ) -> None:
        self._config = config
        self._provider = provider
        self._now = now or time.monotonic
        self._last_spoken_at = -1_000_000.0
        self._event_spoken_at: dict[str, float] = {}

    def maybe_narrate(
        self,
        state: MeetingState,
        events: list[PresenterEvent],
    ) -> str | None:
        if state.confidence < self._config.confidence_threshold:
            return None
        eligible = self._eligible_events(events)
        if not eligible:
            return None
        now = self._now()
        if now - self._last_spoken_at < self._config.min_seconds_between_utterances:
            return None

        text = self._provider.narrate(state, eligible).strip()
        if not text:
            return None
        self._last_spoken_at = now
        for event in eligible:
            self._event_spoken_at[event.type] = now
        return text

    def _eligible_events(self, events: list[PresenterEvent]) -> list[PresenterEvent]:
        now = self._now()
        eligible: list[PresenterEvent] = []
        for event in events:
            last = self._event_spoken_at.get(event.type)
            if last is None or now - last >= self._config.repeat_cooldown_seconds:
                eligible.append(event)
        return eligible
```

- [ ] **Step 4: Run tests**

Run:

```powershell
python -m pytest tests/unit/test_narration.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```powershell
git add src/ai_presenter/runtime/narration.py tests/unit/test_narration.py
git commit -m "feat: add constrained narration engine"
```

## Task 6: Add Media Output Routing

**Files:**
- Create: `src/ai_presenter/media/output.py`
- Create: `tests/unit/test_media_output.py`

- [ ] **Step 1: Write media output tests**

Create `tests/unit/test_media_output.py`:

```python
from ai_presenter.config.models import AudioConfig, AudioOutputMode
from ai_presenter.media.output import AudioSink, MediaOutputFactory
from ai_presenter.providers.base import SpeechAudio


class RecordingSink(AudioSink):
    def __init__(self) -> None:
        self.calls: list[SpeechAudio] = []

    def play(self, audio: SpeechAudio) -> None:
        self.calls.append(audio)


def make_audio() -> SpeechAudio:
    return SpeechAudio(b"RIFFdata", "audio/wav", 16000, 1)


def test_both_output_routes_to_speaker_and_virtual_mic():
    speaker = RecordingSink()
    virtual_mic = RecordingSink()
    config = AudioConfig(output=AudioOutputMode.BOTH, speakerDevice="default", virtualMicDevice="VB-CABLE Input")

    output = MediaOutputFactory(speaker, virtual_mic).create(config)
    output.play(make_audio())

    assert len(speaker.calls) == 1
    assert len(virtual_mic.calls) == 1


def test_virtual_mic_requires_device_name():
    speaker = RecordingSink()
    virtual_mic = RecordingSink()
    config = AudioConfig(output=AudioOutputMode.VIRTUAL_MIC, speakerDevice="default", virtualMicDevice=None)

    try:
        MediaOutputFactory(speaker, virtual_mic).create(config)
    except ValueError as exc:
        assert "virtualMicDevice" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
python -m pytest tests/unit/test_media_output.py -q
```

Expected: FAIL with missing `ai_presenter.media`.

- [ ] **Step 3: Implement media outputs**

Create `src/ai_presenter/media/output.py`:

```python
from typing import Protocol

from ai_presenter.config.models import AudioConfig, AudioOutputMode
from ai_presenter.providers.base import SpeechAudio


class AudioSink(Protocol):
    def play(self, audio: SpeechAudio) -> None:
        ...


class MediaOutput(Protocol):
    def play(self, audio: SpeechAudio) -> None:
        ...


class SingleOutput:
    def __init__(self, sink: AudioSink) -> None:
        self._sink = sink

    def play(self, audio: SpeechAudio) -> None:
        self._sink.play(audio)


class CombinedOutput:
    def __init__(self, sinks: list[AudioSink]) -> None:
        self._sinks = sinks

    def play(self, audio: SpeechAudio) -> None:
        errors: list[Exception] = []
        for sink in self._sinks:
            try:
                sink.play(audio)
            except Exception as exc:
                errors.append(exc)
        if len(errors) == len(self._sinks):
            raise RuntimeError("All audio outputs failed") from errors[0]


class MediaOutputFactory:
    def __init__(self, speaker_sink: AudioSink, virtual_mic_sink: AudioSink) -> None:
        self._speaker_sink = speaker_sink
        self._virtual_mic_sink = virtual_mic_sink

    def create(self, config: AudioConfig) -> MediaOutput:
        if config.output is AudioOutputMode.SPEAKER:
            return SingleOutput(self._speaker_sink)
        if config.output is AudioOutputMode.VIRTUAL_MIC:
            if not config.virtual_mic_device:
                raise ValueError("virtualMicDevice is required for virtual_mic output")
            return SingleOutput(self._virtual_mic_sink)
        if config.output is AudioOutputMode.BOTH:
            if not config.virtual_mic_device:
                raise ValueError("virtualMicDevice is required for both output")
            return CombinedOutput([self._speaker_sink, self._virtual_mic_sink])
        raise ValueError(f"Unsupported audio output mode: {config.output}")
```

- [ ] **Step 4: Run tests**

Run:

```powershell
python -m pytest tests/unit/test_media_output.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```powershell
git add src/ai_presenter/media tests/unit/test_media_output.py
git commit -m "feat: add media output routing"
```

## Task 7: Add Desktop Protocols And Fake Desktop Driver

**Files:**
- Create: `src/ai_presenter/desktop/base.py`
- Create: `tests/unit/test_profile_runner.py`

- [ ] **Step 1: Write fake driver orchestration test**

Create `tests/unit/test_profile_runner.py`:

```python
from pathlib import Path

from ai_presenter.config.loader import load_profile
from ai_presenter.desktop.base import DesktopDriver, WindowHandle
from ai_presenter.runtime.profile_runner import ProfileRunner


class FakeDesktopDriver(DesktopDriver):
    def __init__(self) -> None:
        self.actions: list[str] = []

    def focus_window(self, process: str) -> None:
        self.actions.append(f"focus:{process}")

    def click_tab(self, target: str) -> None:
        self.actions.append(f"tab:{target}")

    def click_button(self, target: str) -> None:
        self.actions.append(f"button:{target}")

    def wait_for_window(self, process: str, window_class: str, timeout_ms: int) -> WindowHandle:
        self.actions.append(f"wait:{process}:{window_class}:{timeout_ms}")
        return WindowHandle(process, 1234, window_class, "RingCentral Video")


def test_profile_runner_executes_launch_steps_and_binds_window():
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))
    desktop = FakeDesktopDriver()

    handle = ProfileRunner(profile, desktop).launch_and_bind()

    assert handle.process == "RingCentralVideo"
    assert desktop.actions == [
        "focus:RingCentralDevelop",
        "tab:Video",
        "button:Start",
        "wait:RingCentralVideo:RingCentralVideoClass:30000",
    ]
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m pytest tests/unit/test_profile_runner.py -q
```

Expected: FAIL with missing desktop and profile runner modules.

- [ ] **Step 3: Implement desktop protocols**

Create `src/ai_presenter/desktop/base.py`:

```python
from dataclasses import dataclass
from typing import Protocol

from ai_presenter.domain.state import RawObservation


@dataclass(frozen=True)
class WindowHandle:
    process: str
    pid: int
    window_class: str
    title: str


class DesktopDriver(Protocol):
    def focus_window(self, process: str) -> None:
        ...

    def click_tab(self, target: str) -> None:
        ...

    def click_button(self, target: str) -> None:
        ...

    def wait_for_window(self, process: str, window_class: str, timeout_ms: int) -> WindowHandle:
        ...


class ObservationDriver(Protocol):
    def capture(self, handle: WindowHandle) -> RawObservation:
        ...
```

- [ ] **Step 4: Implement profile runner launch and bind**

Create `src/ai_presenter/runtime/profile_runner.py`:

```python
from ai_presenter.config.models import AppProfile
from ai_presenter.desktop.base import DesktopDriver, WindowHandle


class ProfileRunner:
    def __init__(self, profile: AppProfile, desktop: DesktopDriver) -> None:
        self._profile = profile
        self._desktop = desktop

    def launch_and_bind(self) -> WindowHandle:
        for step in self._profile.launch.steps:
            if step.action == "focusWindow":
                process = step.match.get("process")
                if not isinstance(process, str):
                    raise ValueError("focusWindow requires match.process")
                self._desktop.focus_window(process)
            elif step.action == "clickTab":
                if step.target is None:
                    raise ValueError("clickTab requires target")
                self._desktop.click_tab(step.target)
            elif step.action == "clickButton":
                if step.target is None:
                    raise ValueError("clickButton requires target")
                self._desktop.click_button(step.target)
            else:
                raise ValueError(f"Unsupported launch action: {step.action}")

        return self._desktop.wait_for_window(
            self._profile.bind.process,
            self._profile.bind.window_class,
            self._profile.bind.timeout_ms,
        )
```

- [ ] **Step 5: Run tests**

Run:

```powershell
python -m pytest tests/unit/test_profile_runner.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```powershell
git add src/ai_presenter/desktop src/ai_presenter/runtime/profile_runner.py tests/unit/test_profile_runner.py
git commit -m "feat: add profile launch runner"
```

## Task 8: Add RingCentral Adapter Contract And State Extraction

**Files:**
- Create: `src/ai_presenter/adapters/base.py`
- Create: `src/ai_presenter/adapters/ringcentral.py`
- Create: `tests/integration/test_ringcentral_profile.py`

- [ ] **Step 1: Write RingCentral adapter tests**

Create `tests/integration/test_ringcentral_profile.py`:

```python
from pathlib import Path

from ai_presenter.adapters.ringcentral import RingCentralAdapter
from ai_presenter.config.loader import load_profile
from ai_presenter.domain.state import RawObservation, WindowMetadata


def test_ringcentral_profile_uses_expected_binding():
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))

    assert profile.bind.process == "RingCentralVideo"
    assert profile.bind.window_class == "RingCentralVideoClass"


def test_ringcentral_adapter_extracts_mic_and_camera_from_ui_text():
    adapter = RingCentralAdapter()
    observation = RawObservation(
        metadata=WindowMetadata(
            process="RingCentralVideo",
            pid=10,
            window_class="RingCentralVideoClass",
            title="RingCentral Video",
            bounds=(0, 0, 1000, 800),
        ),
        ui_text=["Mute microphone", "Stop video", "Participants 3"],
    )

    state = adapter.extract_state(observation)

    assert state.meeting_joined is True
    assert state.mic_muted is False
    assert state.camera_off is False
    assert state.participant_count == 3
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
python -m pytest tests/integration/test_ringcentral_profile.py -q
```

Expected: FAIL with missing adapter modules.

- [ ] **Step 3: Implement adapter protocol**

Create `src/ai_presenter/adapters/base.py`:

```python
from typing import Protocol

from ai_presenter.domain.state import MeetingState, RawObservation


class AppAdapter(Protocol):
    def extract_state(self, observation: RawObservation) -> MeetingState:
        ...
```

- [ ] **Step 4: Implement RingCentral state extraction**

Create `src/ai_presenter/adapters/ringcentral.py`:

```python
import re

from ai_presenter.domain.state import MeetingState, RawObservation


class RingCentralAdapter:
    def extract_state(self, observation: RawObservation) -> MeetingState:
        text = " ".join(observation.ui_text)
        participant_count = self._participant_count(text)
        active_dialog = self._active_dialog(text)
        return MeetingState(
            meeting_joined=observation.metadata.window_class == "RingCentralVideoClass",
            mic_muted=self._mic_muted(text),
            camera_off=self._camera_off(text),
            active_dialog=active_dialog,
            participant_count=participant_count,
            connection_warning=self._connection_warning(text),
            confidence=0.85,
        )

    def _mic_muted(self, text: str) -> bool | None:
        if "Unmute" in text:
            return True
        if "Mute microphone" in text or "Mute" in text:
            return False
        return None

    def _camera_off(self, text: str) -> bool | None:
        if "Start video" in text:
            return True
        if "Stop video" in text:
            return False
        return None

    def _participant_count(self, text: str) -> int | None:
        match = re.search(r"Participants?\s+(\d+)", text)
        return int(match.group(1)) if match else None

    def _active_dialog(self, text: str) -> str | None:
        dialog_markers = ["permission", "waiting room", "connection"]
        lowered = text.lower()
        for marker in dialog_markers:
            if marker in lowered:
                return marker
        return None

    def _connection_warning(self, text: str) -> str | None:
        lowered = text.lower()
        if "unstable" in lowered or "reconnecting" in lowered:
            return "connection issue"
        return None
```

- [ ] **Step 5: Run tests**

Run:

```powershell
python -m pytest tests/integration/test_ringcentral_profile.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```powershell
git add src/ai_presenter/adapters tests/integration/test_ringcentral_profile.py
git commit -m "feat: add ringcentral adapter"
```

## Task 9: Add Presenter Loop

**Files:**
- Create: `src/ai_presenter/runtime/presenter.py`
- Create: `tests/integration/test_presenter_loop.py`

- [ ] **Step 1: Write full loop test**

Create `tests/integration/test_presenter_loop.py`:

```python
from pathlib import Path

from ai_presenter.adapters.ringcentral import RingCentralAdapter
from ai_presenter.config.loader import load_profile
from ai_presenter.desktop.base import ObservationDriver, WindowHandle
from ai_presenter.domain.state import RawObservation, WindowMetadata
from ai_presenter.media.output import AudioSink
from ai_presenter.providers.base import SpeechAudio
from ai_presenter.providers.fake import FakeNarrationProvider, FakeSpeechProvider
from ai_presenter.runtime.presenter import PresenterLoop


class FakeObservationDriver(ObservationDriver):
    def capture(self, handle: WindowHandle) -> RawObservation:
        return RawObservation(
            metadata=WindowMetadata(
                process=handle.process,
                pid=handle.pid,
                window_class=handle.window_class,
                title=handle.title,
                bounds=(0, 0, 1000, 800),
            ),
            ui_text=["Mute microphone", "Stop video", "Participants 3"],
        )


class RecordingSink(AudioSink):
    def __init__(self) -> None:
        self.calls: list[SpeechAudio] = []

    def play(self, audio: SpeechAudio) -> None:
        self.calls.append(audio)


def test_presenter_loop_speaks_for_detected_event():
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))
    sink = RecordingSink()
    loop = PresenterLoop(
        profile=profile,
        observation_driver=FakeObservationDriver(),
        adapter=RingCentralAdapter(),
        narration_provider=FakeNarrationProvider(),
        speech_provider=FakeSpeechProvider(),
        media_output=sink,
        now=lambda: 100.0,
    )

    loop.run_once(WindowHandle("RingCentralVideo", 1234, "RingCentralVideoClass", "RingCentral Video"))

    assert len(sink.calls) == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m pytest tests/integration/test_presenter_loop.py -q
```

Expected: FAIL with missing `runtime.presenter`.

- [ ] **Step 3: Implement presenter loop**

Create `src/ai_presenter/runtime/presenter.py`:

```python
from collections.abc import Callable

from ai_presenter.adapters.base import AppAdapter
from ai_presenter.config.models import AppProfile
from ai_presenter.desktop.base import ObservationDriver, WindowHandle
from ai_presenter.domain.state import MeetingState
from ai_presenter.media.output import MediaOutput
from ai_presenter.providers.base import NarrationProvider, SpeechProvider
from ai_presenter.runtime.events import EventDetector
from ai_presenter.runtime.narration import NarrationEngine


class PresenterLoop:
    def __init__(
        self,
        profile: AppProfile,
        observation_driver: ObservationDriver,
        adapter: AppAdapter,
        narration_provider: NarrationProvider,
        speech_provider: SpeechProvider,
        media_output: MediaOutput,
        now: Callable[[], float] | None = None,
    ) -> None:
        self._profile = profile
        self._observation_driver = observation_driver
        self._adapter = adapter
        self._speech_provider = speech_provider
        self._media_output = media_output
        self._event_detector = EventDetector(profile.narration.confidence_threshold)
        self._narration = NarrationEngine(profile.narration, narration_provider, now)
        self._previous_state: MeetingState | None = None

    def run_once(self, handle: WindowHandle) -> None:
        observation = self._observation_driver.capture(handle)
        current_state = self._adapter.extract_state(observation)
        events = self._event_detector.detect(self._previous_state, current_state)
        self._previous_state = current_state
        text = self._narration.maybe_narrate(current_state, events)
        if not text:
            return
        audio = self._speech_provider.synthesize(text)
        self._media_output.play(audio)
```

- [ ] **Step 4: Run test**

Run:

```powershell
python -m pytest tests/integration/test_presenter_loop.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```powershell
git add src/ai_presenter/runtime/presenter.py tests/integration/test_presenter_loop.py
git commit -m "feat: add presenter loop"
```

## Task 10: Add OpenAI Providers With Mocked Tests

**Files:**
- Create: `src/ai_presenter/providers/openai_provider.py`
- Create: `tests/unit/test_openai_provider.py`

- [ ] **Step 1: Write provider tests using fake client objects**

Create `tests/unit/test_openai_provider.py`:

```python
from ai_presenter.domain.state import MeetingState, PresenterEvent
from ai_presenter.providers.openai_provider import OpenAINarrationProvider


class FakeResponses:
    def create(self, **kwargs):
        return type("Response", (), {"output_text": "The meeting window is ready."})()


class FakeClient:
    responses = FakeResponses()


def test_openai_narration_provider_sends_constrained_prompt():
    provider = OpenAINarrationProvider(client=FakeClient(), model="test-narration-model")
    text = provider.narrate(
        MeetingState(meeting_joined=True, mic_muted=True, confidence=0.9),
        [PresenterEvent("mic_state_changed", {"micMuted": True}, 0.9)],
    )

    assert text == "The meeting window is ready."
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m pytest tests/unit/test_openai_provider.py -q
```

Expected: FAIL with missing `openai_provider`.

- [ ] **Step 3: Implement narration provider**

Create `src/ai_presenter/providers/openai_provider.py`:

```python
import os
from typing import Any

from openai import OpenAI

from ai_presenter.domain.state import MeetingState, PresenterEvent


class OpenAINarrationProvider:
    def __init__(self, client: Any | None = None, model: str | None = None) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        resolved_model = model or os.getenv("AI_PRESENTER_OPENAI_NARRATION_MODEL")
        if client is None and not api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAI narration")
        if not resolved_model:
            raise ValueError("AI_PRESENTER_OPENAI_NARRATION_MODEL is required")
        self._client = client or OpenAI(api_key=api_key)
        self._model = resolved_model

    def narrate(self, state: MeetingState, events: list[PresenterEvent]) -> str:
        response = self._client.responses.create(
            model=self._model,
            instructions=(
                "You are a constrained meeting UI presenter. Speak only about verified "
                "RingCentral meeting UI state and event changes. Do not infer shared-screen "
                "content, participant identity, meeting purpose, or private content. Return "
                "one concise sentence."
            ),
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": f"State: {state}. Events: {events}",
                        }
                    ],
                }
            ],
        )
        return str(response.output_text).strip()
```

- [ ] **Step 4: Add speech provider test**

Append to `tests/unit/test_openai_provider.py`:

```python
from ai_presenter.providers.openai_provider import OpenAISpeechProvider


class FakeSpeechResponse:
    content = b"RIFFfake-wav"


class FakeSpeechCreate:
    def create(self, **kwargs):
        return FakeSpeechResponse()


class FakeAudio:
    speech = FakeSpeechCreate()


class FakeSpeechClient:
    audio = FakeAudio()


def test_openai_speech_provider_returns_audio_bytes():
    provider = OpenAISpeechProvider(client=FakeSpeechClient(), model="gpt-4o-mini-tts", voice="verse")

    audio = provider.synthesize("Meeting joined.")

    assert audio.data == b"RIFFfake-wav"
    assert audio.mime_type == "audio/wav"
```

- [ ] **Step 5: Implement speech provider**

Append to `src/ai_presenter/providers/openai_provider.py`:

```python
from ai_presenter.providers.base import SpeechAudio


class OpenAISpeechProvider:
    def __init__(
        self,
        client: Any | None = None,
        model: str = "gpt-4o-mini-tts",
        voice: str = "verse",
    ) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if client is None and not api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAI speech")
        self._client = client or OpenAI(api_key=api_key)
        self._model = model
        self._voice = voice

    def synthesize(self, text: str) -> SpeechAudio:
        response = self._client.audio.speech.create(
            model=self._model,
            voice=self._voice,
            input=text,
            response_format="wav",
        )
        return SpeechAudio(
            data=response.content,
            mime_type="audio/wav",
            sample_rate=24_000,
            channels=1,
        )
```

- [ ] **Step 6: Run tests**

Run:

```powershell
python -m pytest tests/unit/test_openai_provider.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit**

Run:

```powershell
git add src/ai_presenter/providers/openai_provider.py tests/unit/test_openai_provider.py
git commit -m "feat: add openai providers"
```

## Task 11: Add Windows Desktop Implementation

**Files:**
- Create: `src/ai_presenter/desktop/windows.py`
- Create: `tests/unit/test_windows_desktop.py`

- [ ] **Step 1: Write unit tests for pure helper behavior**

Create `tests/unit/test_windows_desktop.py`:

```python
from ai_presenter.desktop.windows import collect_ui_text


class FakeControl:
    def __init__(self, name="", children=None):
        self.Name = name
        self._children = children or []

    def GetChildren(self):
        return self._children


def test_collect_ui_text_walks_control_tree():
    tree = FakeControl("", [FakeControl("Mute microphone"), FakeControl("Participants 3")])

    assert collect_ui_text(tree) == ["Mute microphone", "Participants 3"]
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m pytest tests/unit/test_windows_desktop.py -q
```

Expected: FAIL with missing `desktop.windows`.

- [ ] **Step 3: Implement Windows helper and driver skeleton**

Create `src/ai_presenter/desktop/windows.py`:

```python
import io
import time
from typing import Any

import mss
import psutil
import uiautomation as auto
from PIL import Image
from pywinauto import Application

from ai_presenter.desktop.base import DesktopDriver, ObservationDriver, WindowHandle
from ai_presenter.domain.state import RawObservation, WindowMetadata


def collect_ui_text(control: Any) -> list[str]:
    names: list[str] = []
    name = getattr(control, "Name", "")
    if isinstance(name, str) and name.strip():
        names.append(name.strip())
    for child in control.GetChildren():
        names.extend(collect_ui_text(child))
    return names


class WindowsDesktopDriver(DesktopDriver, ObservationDriver):
    def focus_window(self, process: str) -> None:
        app = Application(backend="uia").connect(path=f"{process}.exe")
        window = app.top_window()
        window.set_focus()

    def click_tab(self, target: str) -> None:
        control = auto.Control(searchDepth=8, Name=target)
        if not control.Exists(3):
            raise RuntimeError(f"Tab not found: {target}")
        control.Click()

    def click_button(self, target: str) -> None:
        control = auto.Control(searchDepth=8, Name=target)
        if not control.Exists(3):
            raise RuntimeError(f"Button not found: {target}")
        control.Click()

    def wait_for_window(self, process: str, window_class: str, timeout_ms: int) -> WindowHandle:
        deadline = time.monotonic() + timeout_ms / 1000
        while time.monotonic() < deadline:
            for proc in psutil.process_iter(["pid", "name"]):
                if proc.info["name"] and proc.info["name"].lower() == f"{process}.exe".lower():
                    control = auto.WindowControl(searchDepth=1, ClassName=window_class)
                    if control.Exists(1):
                        return WindowHandle(process, int(proc.info["pid"]), window_class, control.Name)
            time.sleep(0.5)
        raise TimeoutError(f"Window not found: process={process} class={window_class}")

    def capture(self, handle: WindowHandle) -> RawObservation:
        control = auto.WindowControl(searchDepth=1, ClassName=handle.window_class)
        if not control.Exists(1):
            raise RuntimeError(f"Window lost: {handle.window_class}")
        rect = control.BoundingRectangle
        bounds = (rect.left, rect.top, rect.right, rect.bottom)
        screenshot = self._capture_bounds(bounds)
        return RawObservation(
            metadata=WindowMetadata(
                process=handle.process,
                pid=handle.pid,
                window_class=handle.window_class,
                title=control.Name,
                bounds=bounds,
                focused=control.HasKeyboardFocus,
                minimized=False,
            ),
            screenshot_png=screenshot,
            ui_text=collect_ui_text(control),
        )

    def _capture_bounds(self, bounds: tuple[int, int, int, int]) -> bytes:
        left, top, right, bottom = bounds
        monitor = {"left": left, "top": top, "width": right - left, "height": bottom - top}
        with mss.mss() as sct:
            shot = sct.grab(monitor)
        image = Image.frombytes("RGB", shot.size, shot.rgb)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()
```

- [ ] **Step 4: Run tests**

Run:

```powershell
python -m pytest tests/unit/test_windows_desktop.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```powershell
git add src/ai_presenter/desktop/windows.py tests/unit/test_windows_desktop.py
git commit -m "feat: add windows desktop driver"
```

## Task 12: Add Real Audio Sinks

**Files:**
- Modify: `src/ai_presenter/media/output.py`
- Create: `tests/unit/test_audio_sinks.py`

- [ ] **Step 1: Write audio decode test**

Create `tests/unit/test_audio_sinks.py`:

```python
from ai_presenter.media.output import decode_wav
from ai_presenter.providers.fake import FakeSpeechProvider


def test_decode_wav_returns_samples_and_rate():
    audio = FakeSpeechProvider().synthesize("hello")

    samples, sample_rate = decode_wav(audio)

    assert sample_rate == 16000
    assert samples.ndim == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m pytest tests/unit/test_audio_sinks.py -q
```

Expected: FAIL with missing `decode_wav`.

- [ ] **Step 3: Add WAV decode and sounddevice sink**

Append to `src/ai_presenter/media/output.py`:

```python
import io

import numpy as np
import sounddevice as sd
import soundfile as sf


def decode_wav(audio: SpeechAudio) -> tuple[np.ndarray, int]:
    data, sample_rate = sf.read(io.BytesIO(audio.data), dtype="float32", always_2d=True)
    return data, int(sample_rate)


class SoundDeviceSink:
    def __init__(self, device: str | int | None = None) -> None:
        self._device = device

    def play(self, audio: SpeechAudio) -> None:
        samples, sample_rate = decode_wav(audio)
        sd.play(samples, samplerate=sample_rate, device=self._device, blocking=True)
```

- [ ] **Step 4: Run tests**

Run:

```powershell
python -m pytest tests/unit/test_audio_sinks.py tests/unit/test_media_output.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```powershell
git add src/ai_presenter/media/output.py tests/unit/test_audio_sinks.py
git commit -m "feat: add sounddevice audio sinks"
```

## Task 13: Wire CLI Runtime

**Files:**
- Modify: `src/ai_presenter/cli.py`
- Create: `tests/unit/test_cli.py`

- [ ] **Step 1: Extend CLI tests**

Replace `tests/unit/test_cli.py` with:

```python
from typer.testing import CliRunner

from ai_presenter.cli import app


def test_cli_help_renders():
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "AI presenter" in result.stdout


def test_run_dry_run_loads_profile():
    result = CliRunner().invoke(app, ["run", "--profile", "ringcentral-video", "--dry-run"])

    assert result.exit_code == 0
    assert "Loaded profile: ringcentral-video" in result.stdout
```

- [ ] **Step 2: Run test to verify dry run fails**

Run:

```powershell
python -m pytest tests/unit/test_cli.py -q
```

Expected: FAIL because `--dry-run` is not defined.

- [ ] **Step 3: Implement CLI profile resolution and dry run**

Replace `src/ai_presenter/cli.py` with:

```python
from pathlib import Path

import typer

from ai_presenter.config.loader import load_profile

app = typer.Typer(help="AI presenter CLI for configured app profiles.")


def resolve_profile(profile: str) -> Path:
    candidate = Path(profile)
    if candidate.exists():
        return candidate
    bundled = Path("profiles") / f"{profile}.yaml"
    if bundled.exists():
        return bundled
    raise typer.BadParameter(f"Profile not found: {profile}")


@app.command()
def run(
    profile: str = typer.Option(..., "--profile", help="Profile id or YAML path."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Load configuration without app automation."),
) -> None:
    """Run an AI presenter profile."""
    loaded = load_profile(resolve_profile(profile))
    typer.echo(f"Loaded profile: {loaded.id}")
    if dry_run:
        typer.echo("Dry run complete.")
        return
    typer.echo("Runtime execution is available after desktop and provider wiring.")
```

- [ ] **Step 4: Run tests**

Run:

```powershell
python -m pytest tests/unit/test_cli.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```powershell
git add src/ai_presenter/cli.py tests/unit/test_cli.py
git commit -m "feat: wire profile loading into cli"
```

## Task 14: Wire Real Runtime Factories

**Files:**
- Create: `src/ai_presenter/runtime/factory.py`
- Modify: `src/ai_presenter/cli.py`
- Create: `tests/unit/test_runtime_factory.py`

- [ ] **Step 1: Write factory tests**

Create `tests/unit/test_runtime_factory.py`:

```python
from pathlib import Path

from ai_presenter.config.loader import load_profile
from ai_presenter.runtime.factory import create_fake_provider_registry


def test_fake_provider_registry_satisfies_ringcentral_profile():
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))
    registry = create_fake_provider_registry()

    assert registry.vision(profile.providers.vision)
    assert registry.narration(profile.providers.narration)
    assert registry.speech(profile.providers.speech)
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m pytest tests/unit/test_runtime_factory.py -q
```

Expected: FAIL with missing `runtime.factory`.

- [ ] **Step 3: Implement fake registry factory**

Create `src/ai_presenter/runtime/factory.py`:

```python
from ai_presenter.domain.state import MeetingState
from ai_presenter.providers.base import ProviderRegistry
from ai_presenter.providers.fake import FakeNarrationProvider, FakeSpeechProvider, FakeVisionProvider


def create_fake_provider_registry() -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register_vision("fake", FakeVisionProvider(MeetingState(meeting_joined=True, confidence=1.0)))
    registry.register_narration("fake", FakeNarrationProvider())
    registry.register_speech("fake", FakeSpeechProvider())
    return registry
```

- [ ] **Step 4: Run factory test**

Run:

```powershell
python -m pytest tests/unit/test_runtime_factory.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```powershell
git add src/ai_presenter/runtime/factory.py tests/unit/test_runtime_factory.py
git commit -m "feat: add runtime provider factory"
```

## Task 15: Add Manual Acceptance Runbook

**Files:**
- Create: `docs/runbooks/ringcentral-manual-acceptance.md`
- Modify: `README.md`

- [ ] **Step 1: Create the acceptance runbook**

Create `docs/runbooks/ringcentral-manual-acceptance.md`:

```markdown
# RingCentral Manual Acceptance

## Preconditions

- `RingCentralDevelop` is installed.
- The user is already logged in.
- A virtual audio device such as VB-CABLE or VoiceMeeter is installed when testing virtual microphone output.
- `OPENAI_API_KEY` is set when testing OpenAI providers.

## Checklist

- [ ] Run `.venv\Scripts\ai-presenter run --profile ringcentral-video --dry-run`.
- [ ] Confirm profile loads without validation errors.
- [ ] Open `RingCentralDevelop`.
- [ ] Confirm the user is logged in.
- [ ] Run `.venv\Scripts\ai-presenter run --profile ringcentral-video`.
- [ ] Confirm the Video tab is selected.
- [ ] Confirm Start is clicked.
- [ ] Confirm `RingCentralVideo` starts.
- [ ] Confirm the runner binds a window with class `RingCentralVideoClass`.
- [ ] Confirm meeting joined state is detected.
- [ ] Toggle microphone and confirm one narration event.
- [ ] Toggle camera and confirm one narration event.
- [ ] Change participant count and confirm one narration event.
- [ ] Enable speaker output and confirm local playback.
- [ ] Enable virtual microphone output and confirm RingCentral receives audio from the virtual device.
- [ ] Review logs for profile load, launch steps, binding, observations, events, narration text, and media output status.
```

- [ ] **Step 2: Link runbook from README**

Append to `README.md`:

```markdown
## Manual Acceptance

Use `docs/runbooks/ringcentral-manual-acceptance.md` for the RingCentral MVP checklist.
```

- [ ] **Step 3: Run documentation status check**

Run:

```powershell
git status --short
```

Expected: shows modified `README.md` and new `docs/runbooks/ringcentral-manual-acceptance.md`.

- [ ] **Step 4: Commit**

Run:

```powershell
git add README.md docs/runbooks/ringcentral-manual-acceptance.md
git commit -m "docs: add ringcentral acceptance runbook"
```

## Task 16: Add Structured Runtime Logging

**Files:**
- Create: `src/ai_presenter/runtime/logging.py`
- Modify: `src/ai_presenter/runtime/profile_runner.py`
- Modify: `src/ai_presenter/runtime/presenter.py`
- Modify: `src/ai_presenter/cli.py`
- Create: `tests/unit/test_runtime_logging.py`

- [ ] **Step 1: Write logging utility tests**

Create `tests/unit/test_runtime_logging.py`:

```python
import logging

from ai_presenter.runtime.logging import configure_logging, redact_value


def test_redact_value_masks_secret_like_values():
    assert redact_value("sk-test-secret") == "***REDACTED***"
    assert redact_value("normal-profile-name") == "normal-profile-name"


def test_configure_logging_sets_info_level():
    configure_logging(debug=False)

    assert logging.getLogger("ai_presenter").level == logging.INFO
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
python -m pytest tests/unit/test_runtime_logging.py -q
```

Expected: FAIL with missing `runtime.logging`.

- [ ] **Step 3: Implement logging helpers**

Create `src/ai_presenter/runtime/logging.py`:

```python
import logging


SECRET_PREFIXES = ("sk-", "rk-", "pk-")


def redact_value(value: object) -> object:
    if isinstance(value, str) and value.startswith(SECRET_PREFIXES):
        return "***REDACTED***"
    return value


def configure_logging(debug: bool = False) -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    logging.getLogger("ai_presenter").setLevel(level)
```

- [ ] **Step 4: Add logging to profile runner**

Modify `src/ai_presenter/runtime/profile_runner.py`:

```python
import logging

from ai_presenter.config.models import AppProfile
from ai_presenter.desktop.base import DesktopDriver, WindowHandle

logger = logging.getLogger("ai_presenter.runtime.profile_runner")


class ProfileRunner:
    def __init__(self, profile: AppProfile, desktop: DesktopDriver) -> None:
        self._profile = profile
        self._desktop = desktop

    def launch_and_bind(self) -> WindowHandle:
        logger.info("profile_launch_started profile=%s", self._profile.id)
        for step in self._profile.launch.steps:
            logger.info("launch_step_started action=%s target=%s", step.action, step.target)
            if step.action == "focusWindow":
                process = step.match.get("process")
                if not isinstance(process, str):
                    raise ValueError("focusWindow requires match.process")
                self._desktop.focus_window(process)
            elif step.action == "clickTab":
                if step.target is None:
                    raise ValueError("clickTab requires target")
                self._desktop.click_tab(step.target)
            elif step.action == "clickButton":
                if step.target is None:
                    raise ValueError("clickButton requires target")
                self._desktop.click_button(step.target)
            else:
                raise ValueError(f"Unsupported launch action: {step.action}")
            logger.info("launch_step_completed action=%s", step.action)

        handle = self._desktop.wait_for_window(
            self._profile.bind.process,
            self._profile.bind.window_class,
            self._profile.bind.timeout_ms,
        )
        logger.info(
            "window_bound process=%s pid=%s class=%s",
            handle.process,
            handle.pid,
            handle.window_class,
        )
        return handle
```

- [ ] **Step 5: Add logging to presenter loop**

Modify `src/ai_presenter/runtime/presenter.py` so `run_once` logs observations, events, narration, and output:

```python
import logging
from collections.abc import Callable

from ai_presenter.adapters.base import AppAdapter
from ai_presenter.config.models import AppProfile
from ai_presenter.desktop.base import ObservationDriver, WindowHandle
from ai_presenter.domain.state import MeetingState
from ai_presenter.media.output import MediaOutput
from ai_presenter.providers.base import NarrationProvider, SpeechProvider
from ai_presenter.runtime.events import EventDetector
from ai_presenter.runtime.narration import NarrationEngine

logger = logging.getLogger("ai_presenter.runtime.presenter")


class PresenterLoop:
    def __init__(
        self,
        profile: AppProfile,
        observation_driver: ObservationDriver,
        adapter: AppAdapter,
        narration_provider: NarrationProvider,
        speech_provider: SpeechProvider,
        media_output: MediaOutput,
        now: Callable[[], float] | None = None,
    ) -> None:
        self._profile = profile
        self._observation_driver = observation_driver
        self._adapter = adapter
        self._speech_provider = speech_provider
        self._media_output = media_output
        self._event_detector = EventDetector(profile.narration.confidence_threshold)
        self._narration = NarrationEngine(profile.narration, narration_provider, now)
        self._previous_state: MeetingState | None = None

    def run_once(self, handle: WindowHandle) -> None:
        observation = self._observation_driver.capture(handle)
        logger.info("observation_captured process=%s class=%s", handle.process, handle.window_class)
        current_state = self._adapter.extract_state(observation)
        logger.info("state_extracted confidence=%s", current_state.confidence)
        events = self._event_detector.detect(self._previous_state, current_state)
        logger.info("events_detected count=%s types=%s", len(events), [event.type for event in events])
        self._previous_state = current_state
        text = self._narration.maybe_narrate(current_state, events)
        if not text:
            logger.info("narration_skipped")
            return
        logger.info("narration_generated text=%s", text)
        audio = self._speech_provider.synthesize(text)
        self._media_output.play(audio)
        logger.info("media_output_completed mime_type=%s bytes=%s", audio.mime_type, len(audio.data))
```

- [ ] **Step 6: Configure logging from CLI**

Modify `src/ai_presenter/cli.py` to accept `--debug` and configure logging before loading profiles:

```python
from pathlib import Path

import typer

from ai_presenter.config.loader import load_profile
from ai_presenter.runtime.logging import configure_logging

app = typer.Typer(help="AI presenter CLI for configured app profiles.")


def resolve_profile(profile: str) -> Path:
    candidate = Path(profile)
    if candidate.exists():
        return candidate
    bundled = Path("profiles") / f"{profile}.yaml"
    if bundled.exists():
        return bundled
    raise typer.BadParameter(f"Profile not found: {profile}")


@app.command()
def run(
    profile: str = typer.Option(..., "--profile", help="Profile id or YAML path."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Load configuration without app automation."),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logs."),
) -> None:
    """Run an AI presenter profile."""
    configure_logging(debug)
    loaded = load_profile(resolve_profile(profile))
    typer.echo(f"Loaded profile: {loaded.id}")
    if dry_run:
        typer.echo("Dry run complete.")
        return
    typer.echo("Runtime execution is available after desktop and provider wiring.")
```

- [ ] **Step 7: Run logging and regression tests**

Run:

```powershell
python -m pytest tests/unit/test_runtime_logging.py tests/unit/test_profile_runner.py tests/integration/test_presenter_loop.py tests/unit/test_cli.py -q
```

Expected: PASS.

- [ ] **Step 8: Commit**

Run:

```powershell
git add src/ai_presenter/runtime/logging.py src/ai_presenter/runtime/profile_runner.py src/ai_presenter/runtime/presenter.py src/ai_presenter/cli.py tests/unit/test_runtime_logging.py
git commit -m "feat: add structured runtime logging"
```

## Task 17: Final Verification

**Files:**
- Modify only files needed to fix verification failures.

- [ ] **Step 1: Run unit and integration tests**

Run:

```powershell
python -m pytest -q
```

Expected: all tests PASS and coverage report is printed.

- [ ] **Step 2: Run lint**

Run:

```powershell
python -m ruff check .
```

Expected: no lint violations.

- [ ] **Step 3: Run type checking**

Run:

```powershell
python -m mypy src
```

Expected: no type errors.

- [ ] **Step 4: Run security dependency audit**

Run:

```powershell
python -m pip_audit
```

Expected: no known vulnerable dependencies. If `pip-audit` is not installed, run:

```powershell
python -m pip install pip-audit
python -m pip_audit
```

- [ ] **Step 5: Review final git diff**

Run:

```powershell
git diff --stat
git diff --check
```

Expected: no whitespace errors and only intentional files changed.

- [ ] **Step 6: Commit verification fixes**

If verification required code changes, run:

```powershell
git add <changed-files>
git commit -m "fix: address ai presenter verification issues"
```

If no files changed, do not create an empty commit.

## Self-Review

Spec coverage:

- Config-driven CLI: Tasks 1, 2, 13, and 14.
- RingCentralDevelop launch flow: Tasks 2, 7, 8, 11, and 15.
- `RingCentralVideoClass` binding: Tasks 2, 7, 8, 11, and 15.
- Real-time observation loop: Tasks 3, 8, 9, and 11.
- Dynamic constrained narration: Tasks 4, 5, 9, and 10.
- Speaker and virtual microphone output: Tasks 6, 12, and 15.
- App-profile/plugin-first architecture: Tasks 2, 7, 8, 9, and 14.
- Logging and error handling: covered by Tasks 7, 9, 11, 13, 16, and 17.
- Security and privacy: provider secrets stay in environment variables; screenshot capture is window-bounded in Task 11; manual provider use is documented in Tasks 10 and 15.
- Future avatar video extension: represented by the `MediaOutput` boundary in Task 6 and kept outside MVP runtime behavior.

Placeholder scan:

- No undefined task references.
- No unresolved profile paths.
- No secret values in examples.
- No instruction asks an engineer to guess file names.
