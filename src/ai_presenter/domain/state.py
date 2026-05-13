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
