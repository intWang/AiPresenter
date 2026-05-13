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
