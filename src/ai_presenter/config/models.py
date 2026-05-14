from enum import Enum
from pathlib import Path
from typing import Annotated, Any, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


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

    @field_validator("action", mode="before")
    @classmethod
    def normalize_action(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        normalized = value.strip()
        if not normalized:
            raise ValueError("launch action cannot be blank")
        return normalized

    @field_validator("target", mode="before")
    @classmethod
    def normalize_target(cls, value: object) -> object:
        if value is None or not isinstance(value, str):
            return value
        normalized = value.strip()
        if not normalized:
            raise ValueError("launch target cannot be blank")
        return normalized


class LaunchConfig(CamelModel):
    app_process: str = Field(alias="appProcess")
    require_already_logged_in: bool = Field(alias="requireAlreadyLoggedIn")
    steps: list[LaunchStep]


class BrowserLaunchConfig(CamelModel):
    url: str
    steps: list[LaunchStep] = Field(default_factory=list)


class BindConfig(CamelModel):
    process: str
    window_class: str = Field(alias="windowClass")
    timeout_ms: int = Field(default=30_000, alias="timeoutMs", ge=1_000)


class BrowserBindConfig(CamelModel):
    url_pattern: str | None = Field(default=None, alias="urlPattern")
    title: str | None = None
    timeout_ms: int = Field(default=30_000, alias="timeoutMs", ge=1_000)

    @model_validator(mode="after")
    def require_bind_target(self) -> "BrowserBindConfig":
        has_url_pattern = self.url_pattern is not None and bool(self.url_pattern.strip())
        has_title = self.title is not None and bool(self.title.strip())
        if not has_url_pattern and not has_title:
            raise ValueError("Browser bind requires urlPattern or title")
        return self


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
    soul_path: Path | None = Field(default=None, alias="soulPath")
    memory_path: Path | None = Field(default=None, alias="memoryPath")
    skill_paths: list[Path] = Field(default_factory=list, alias="skillPaths")


class AudioConfig(CamelModel):
    output: AudioOutputMode
    speaker_device: str = Field(default="default", alias="speakerDevice")
    virtual_mic_device: str | None = Field(default=None, alias="virtualMicDevice")

    @model_validator(mode="after")
    def require_virtual_mic_device_for_virtual_mic_output(self) -> "AudioConfig":
        if self.output in {AudioOutputMode.VIRTUAL_MIC, AudioOutputMode.BOTH} and (
            self.virtual_mic_device is None or not self.virtual_mic_device.strip()
        ):
            raise ValueError("virtualMicDevice is required for virtual mic audio output")
        return self


class ProviderConfig(CamelModel):
    vision: str
    narration: str
    speech: str

    @field_validator("vision", "narration", "speech", mode="before")
    @classmethod
    def normalize_provider_name(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        normalized = value.strip()
        if not normalized:
            raise ValueError("provider name cannot be blank")
        return normalized


class SharedProfileConfig(CamelModel):
    id: str
    observe: ObserveConfig
    events: list[str]
    narration: NarrationConfig
    audio: AudioConfig
    providers: ProviderConfig


class DesktopAppProfile(SharedProfileConfig):
    type: Literal[ProfileType.DESKTOP]
    launch: LaunchConfig
    bind: BindConfig


class BrowserAppProfile(SharedProfileConfig):
    type: Literal[ProfileType.BROWSER]
    launch: BrowserLaunchConfig
    bind: BrowserBindConfig


AppProfile: TypeAlias = Annotated[
    DesktopAppProfile | BrowserAppProfile,
    Field(discriminator="type"),
]
