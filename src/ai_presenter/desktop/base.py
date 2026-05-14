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

    def click_window_relative(self, handle: WindowHandle, x: int, y: int) -> None:
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
