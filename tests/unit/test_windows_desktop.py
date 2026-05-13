from types import SimpleNamespace
from typing import Any

import pytest

from ai_presenter.desktop import windows
from ai_presenter.desktop.base import WindowHandle
from ai_presenter.desktop.windows import WindowsDesktopDriver, collect_ui_text


class FakeControl:
    def __init__(
        self,
        name: str | None,
        children: list["FakeControl"] | None = None,
    ) -> None:
        self.Name = name
        self._children = children or []

    def GetChildren(self) -> list["FakeControl"]:
        return self._children


class FakeClickableControl(FakeControl):
    def __init__(
        self,
        name: str,
        control_type_name: str,
        clicked: list[str],
        children: list[FakeControl] | None = None,
    ) -> None:
        super().__init__(name, children)
        self.ControlTypeName = control_type_name
        self._clicked = clicked

    def Click(self) -> None:
        self._clicked.append(self.Name)


class FakeFocusedWindow:
    handle = 99

    def __init__(self, focus_calls: list[str] | None = None) -> None:
        self._focus_calls = focus_calls

    def set_focus(self) -> None:
        if self._focus_calls is not None:
            self._focus_calls.append("focus")


def focused_driver(monkeypatch: pytest.MonkeyPatch, root_control: FakeControl) -> WindowsDesktopDriver:
    class FakeApplication:
        def __init__(self, backend: str) -> None:
            assert backend == "uia"

        def connect(self, path: str) -> "FakeApplication":
            assert path == "RingCentralDevelop.exe"
            return self

        def top_window(self) -> FakeFocusedWindow:
            return FakeFocusedWindow()

    monkeypatch.setattr(windows, "Application", FakeApplication)
    monkeypatch.setattr(windows.uiautomation, "ControlFromHandle", lambda handle: root_control)
    driver = WindowsDesktopDriver()
    driver.focus_window("RingCentralDevelop")
    return driver


def test_collect_ui_text_walks_tree_and_strips_blanks() -> None:
    root = FakeControl(
        "  Root  ",
        [
            FakeControl("   "),
            FakeControl("\nVideo\t"),
            FakeControl("Controls", [FakeControl("  Start meeting  ")]),
        ],
    )

    assert collect_ui_text(root) == ["Root", "Video", "Controls", "Start meeting"]


def test_collect_ui_text_treats_control_without_children_method_as_leaf() -> None:
    leaf = SimpleNamespace(Name="  Join  ")

    assert collect_ui_text(leaf) == ["Join"]


def test_collect_ui_text_treats_raising_children_as_leaf() -> None:
    class RaisingControl:
        Name = "  Camera  "

        def GetChildren(self) -> list[Any]:
            raise RuntimeError("uia tree changed")

    assert collect_ui_text(RaisingControl()) == ["Camera"]


def test_capture_bounds_png_uses_bounded_region(monkeypatch: pytest.MonkeyPatch) -> None:
    grabs: list[dict[str, int]] = []

    class FakeShot:
        size = (3, 2)
        rgb = b"123456789012345678"

    class FakeMss:
        def __enter__(self) -> "FakeMss":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def grab(self, monitor: dict[str, int]) -> FakeShot:
            grabs.append(monitor)
            return FakeShot()

    class FakeImage:
        def save(self, buffer: Any, format: str) -> None:
            assert format == "PNG"
            buffer.write(b"png-bytes")

    def fake_frombytes(mode: str, size: tuple[int, int], data: bytes) -> FakeImage:
        assert mode == "RGB"
        assert size == (3, 2)
        assert data == FakeShot.rgb
        return FakeImage()

    monkeypatch.setattr(windows.mss, "mss", lambda: FakeMss())
    monkeypatch.setattr(windows.Image, "frombytes", fake_frombytes)

    assert windows._capture_bounds_png((10, 20, 25, 35)) == b"png-bytes"
    assert grabs == [{"left": 10, "top": 20, "width": 15, "height": 15}]


def test_focus_window_connects_to_process_executable_and_focuses(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, str]] = []

    class FakeWindow:
        handle = 99

        def set_focus(self) -> None:
            calls.append(("focus", ""))

    class FakeApplication:
        def __init__(self, backend: str) -> None:
            calls.append(("backend", backend))

        def connect(self, path: str) -> "FakeApplication":
            calls.append(("path", path))
            return self

        def top_window(self) -> FakeWindow:
            return FakeWindow()

    monkeypatch.setattr(windows, "Application", FakeApplication)

    WindowsDesktopDriver().focus_window("RingCentralDevelop")

    assert calls == [
        ("backend", "uia"),
        ("path", "RingCentralDevelop.exe"),
        ("focus", ""),
    ]


def test_click_tab_clicks_named_tab(monkeypatch: pytest.MonkeyPatch) -> None:
    clicked: list[str] = []
    root = FakeControl(
        "RingCentral",
        [
            FakeClickableControl("Video", "ButtonControl", clicked),
            FakeClickableControl("Video", "TabItemControl", clicked),
        ],
    )

    focused_driver(monkeypatch, root).click_tab("Video")

    assert clicked == ["Video"]


def test_click_button_raises_clear_error_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    root = FakeControl("RingCentral", [FakeClickableControl("Video", "TabItemControl", [])])

    with pytest.raises(RuntimeError, match="Button control not found: Start"):
        focused_driver(monkeypatch, root).click_button("Start")


def test_click_button_requires_focused_window() -> None:
    with pytest.raises(RuntimeError, match="before focusing a window"):
        WindowsDesktopDriver().click_button("Start")


def test_wait_for_window_uses_process_and_class(monkeypatch: pytest.MonkeyPatch) -> None:
    lookups: list[tuple[int, str]] = []

    class FakeProcess:
        info = {"pid": 4321, "name": "RingCentralVideo.exe"}

    class FakeWindow:
        def window_text(self) -> str:
            return "RingCentral Video"

    class FakeWindowSpec:
        def exists(self, timeout: float) -> bool:
            assert timeout == 0
            return True

        def wrapper_object(self) -> FakeWindow:
            return FakeWindow()

    class FakeDesktop:
        def __init__(self, backend: str) -> None:
            assert backend == "uia"

        def window(self, *, process: int, class_name: str) -> FakeWindowSpec:
            lookups.append((process, class_name))
            return FakeWindowSpec()

    monkeypatch.setattr(windows.psutil, "process_iter", lambda attrs: [FakeProcess()])
    monkeypatch.setattr(windows, "Desktop", FakeDesktop)

    handle = WindowsDesktopDriver().wait_for_window("RingCentralVideo", "VideoClass", 100)

    assert handle == WindowHandle("RingCentralVideo", 4321, "VideoClass", "RingCentral Video")
    assert lookups == [(4321, "VideoClass")]


def test_wait_for_window_raises_after_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(windows.psutil, "process_iter", lambda attrs: [])

    with pytest.raises(
        RuntimeError,
        match="Timed out after 0ms waiting for Missing.exe window class MissingClass",
    ):
        WindowsDesktopDriver().wait_for_window("Missing", "MissingClass", 0)


def test_wait_for_window_fails_fast_on_binding_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeProcess:
        info = {"pid": 4321, "name": "RingCentralVideo.exe"}

    class FailingDesktop:
        def __init__(self, backend: str) -> None:
            assert backend == "uia"

        def window(self, *, process: int, class_name: str) -> object:
            raise RuntimeError(f"backend unavailable for {process}:{class_name}")

    monkeypatch.setattr(windows.psutil, "process_iter", lambda attrs: [FakeProcess()])
    monkeypatch.setattr(windows, "Desktop", FailingDesktop)

    with pytest.raises(RuntimeError, match="backend unavailable"):
        WindowsDesktopDriver().wait_for_window("RingCentralVideo", "VideoClass", 30_000)


def test_focus_window_reports_missing_dependency(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(windows, "Application", None)

    with pytest.raises(RuntimeError, match="pywinauto"):
        WindowsDesktopDriver().focus_window("RingCentralDevelop")


def test_capture_binds_window_and_builds_observation(monkeypatch: pytest.MonkeyPatch) -> None:
    bounds_seen: list[tuple[int, int, int, int]] = []
    lookups: list[tuple[int, str]] = []

    class FakeWindow:
        handle = 99

        def rectangle(self) -> SimpleNamespace:
            return SimpleNamespace(left=5, top=10, right=105, bottom=60)

        def window_text(self) -> str:
            return "Live meeting"

        def is_active(self) -> bool:
            return True

        def is_minimized(self) -> bool:
            return False

    class FakeWindowSpec:
        def wrapper_object(self) -> FakeWindow:
            return FakeWindow()

    class FakeDesktop:
        def __init__(self, backend: str) -> None:
            assert backend == "uia"

        def window(self, *, process: int, class_name: str) -> FakeWindowSpec:
            lookups.append((process, class_name))
            return FakeWindowSpec()

    def fake_capture(bounds: tuple[int, int, int, int]) -> bytes:
        bounds_seen.append(bounds)
        return b"png"

    control = FakeControl("  Meeting  ", [FakeControl("  Mic muted  ")])

    monkeypatch.setattr(windows, "Desktop", FakeDesktop)
    monkeypatch.setattr(windows, "_capture_bounds_png", fake_capture)
    monkeypatch.setattr(windows.uiautomation, "ControlFromHandle", lambda handle: control)

    observation = WindowsDesktopDriver().capture(
        WindowHandle("RingCentralVideo", 4321, "VideoClass", "Old title")
    )

    assert lookups == [(4321, "VideoClass")]
    assert bounds_seen == [(5, 10, 105, 60)]
    assert observation.screenshot_png == b"png"
    assert observation.ui_text == ("Meeting", "Mic muted")
    assert observation.metadata.process == "RingCentralVideo"
    assert observation.metadata.pid == 4321
    assert observation.metadata.window_class == "VideoClass"
    assert observation.metadata.title == "Live meeting"
    assert observation.metadata.bounds == (5, 10, 105, 60)
    assert observation.metadata.focused is True
    assert observation.metadata.minimized is False
