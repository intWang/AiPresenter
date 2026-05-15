from dataclasses import dataclass
from collections.abc import Iterable
from typing import Protocol

from ai_presenter.config.models import ObservationSource
from ai_presenter.domain.state import RawObservation


@dataclass(frozen=True)
class WindowHandle:
    process: str
    pid: int
    window_class: str
    title: str


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


class DesktopDriver(Protocol):
    def focus_window(self, process: str) -> None:
        ...

    def click_tab(self, target: str) -> None:
        ...

    def click_button(self, target: str) -> None:
        ...

    def wait_for_window(self, process: str, window_class: str, timeout_ms: int) -> WindowHandle:
        ...

    def read_focused_window_text(self) -> tuple[str, ...]:
        ...

    def list_visible_windows(self) -> tuple[VisibleWindow, ...]:
        ...

    def list_visible_controls(self, handle: WindowHandle) -> tuple[VisibleControl, ...]:
        ...

    def click_window_relative(self, handle: WindowHandle, x: int, y: int) -> None:
        ...

    def click_window_control(
        self,
        handle: WindowHandle,
        target: str,
        *,
        occurrence: int = 1,
        control_type: str | None = None,
    ) -> None:
        ...

    def window_bounds(self, handle: WindowHandle) -> tuple[int, int, int, int]:
        ...

    def press_key(self, key: str) -> None:
        ...


class ObservationDriver(Protocol):
    def capture(
        self,
        handle: WindowHandle,
        sources: Iterable[ObservationSource] | None = None,
    ) -> RawObservation:
        ...
