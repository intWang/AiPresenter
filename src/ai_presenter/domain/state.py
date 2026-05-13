from dataclasses import dataclass, field
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any
from typing import Mapping
from typing import Sequence


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
    ui_text: Sequence[str] = field(default_factory=tuple)
    captured_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        object.__setattr__(self, "ui_text", tuple(self.ui_text))


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
    payload: Mapping[str, Any]
    confidence: float
    occurred_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))
