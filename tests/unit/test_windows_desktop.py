from types import SimpleNamespace
from typing import Any

import pytest

from ai_presenter.desktop import windows
from ai_presenter.desktop.base import WindowHandle
from ai_presenter.desktop.windows import WindowsDesktopDriver, collect_ui_text
from ai_presenter.config.models import ObservationSource


class FakeControl:
    def __init__(
        self,
        name: str | None,
        control_type: str | list["FakeControl"] | None = None,
        bounds: SimpleNamespace | None = None,
        children: list["FakeControl"] | None = None,
        is_offscreen: bool | None = None,
    ) -> None:
        self.Name = name
        if isinstance(control_type, list):
            self._children = control_type
        else:
            self.ControlTypeName = control_type or ""
            if bounds is not None:
                self.BoundingRectangle = bounds
            if is_offscreen is not None:
                self.IsOffscreen = is_offscreen
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
        self._clicked.append(self.Name or "")


def set_bounds(control: FakeControl, bounds: tuple[int, int, int, int]) -> FakeControl:
    left, top, right, bottom = bounds
    setattr(
        control,
        "BoundingRectangle",
        SimpleNamespace(left=left, top=top, right=right, bottom=bottom),
    )
    return control


class FakeFocusedWindow:
    handle = 99

    def __init__(self, focus_calls: list[str] | None = None) -> None:
        self._focus_calls = focus_calls

    def set_focus(self) -> None:
        if self._focus_calls is not None:
            self._focus_calls.append("focus")


class FakeWindow:
    def __init__(
        self,
        *,
        title: str,
        class_name: str,
        pid: int,
        rectangle: SimpleNamespace,
        visible: bool,
        minimized: bool,
    ) -> None:
        self._title = title
        self._class_name = class_name
        self._pid = pid
        self._rectangle = rectangle
        self._visible = visible
        self._minimized = minimized

    def window_text(self) -> str:
        return self._title

    def class_name(self) -> str:
        return self._class_name

    def process_id(self) -> int:
        return self._pid

    def rectangle(self) -> SimpleNamespace:
        return self._rectangle

    def is_visible(self) -> bool:
        return self._visible

    def is_minimized(self) -> bool:
        return self._minimized


class FakeDesktop:
    def __init__(self, root_windows: list[FakeWindow]) -> None:
        self._root_windows = root_windows

    def windows(self) -> list[FakeWindow]:
        return self._root_windows


class FakeBoundWindow:
    def __init__(self, handle: WindowHandle) -> None:
        self.handle = handle


class FakePsutil:
    def __init__(self, processes_by_name: dict[str, list[int]]) -> None:
        self._process_names_by_pid = {
            pid: name for name, pids in processes_by_name.items() for pid in pids
        }

    def Process(self, pid: int) -> Any:
        process_name = self._process_names_by_pid[pid]
        return SimpleNamespace(name=lambda: process_name)


class StaleNameControl:
    @property
    def Name(self) -> str:
        raise RuntimeError("stale name")

    @property
    def BoundingRectangle(self) -> SimpleNamespace:
        return SimpleNamespace(left=20, top=20, right=120, bottom=50)

    def GetChildren(self) -> list[FakeControl]:
        return []


class StaleTypeControl:
    Name = "Stale Type"

    @property
    def ControlTypeName(self) -> str:
        raise RuntimeError("stale type")

    @property
    def BoundingRectangle(self) -> SimpleNamespace:
        return SimpleNamespace(left=20, top=60, right=120, bottom=90)

    def GetChildren(self) -> list[FakeControl]:
        return []


class StaleChildrenControl:
    Name = "Stale Children"
    ControlTypeName = "Button"
    BoundingRectangle = SimpleNamespace(left=20, top=100, right=120, bottom=130)

    def GetChildren(self) -> list[FakeControl]:
        raise RuntimeError("stale children")


class StaleOffscreenControl:
    Name = "Stale Offscreen"
    ControlTypeName = "Button"
    BoundingRectangle = SimpleNamespace(left=20, top=140, right=120, bottom=170)

    @property
    def IsOffscreen(self) -> bool:
        raise RuntimeError("stale visibility")

    def GetChildren(self) -> list[FakeControl]:
        return []


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


def test_find_descendant_controls_orders_matches_left_to_right() -> None:
    clicked: list[str] = []
    audio_more = set_bounds(
        FakeClickableControl("More", "ButtonControl", clicked),
        (603, 962, 623, 981),
    )
    video_more = set_bounds(
        FakeClickableControl("More", "ButtonControl", clicked),
        (678, 962, 698, 981),
    )
    toolbar_more = set_bounds(
        FakeClickableControl("More", "ButtonControl", clicked),
        (1226, 958, 1302, 1030),
    )
    root = FakeControl("Root", [toolbar_more, audio_more, video_more])

    matches = windows._find_descendant_controls(
        root,
        target="More",
        type_markers=("button",),
    )

    assert matches == [audio_more, video_more, toolbar_more]


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


def test_focus_window_skips_matching_processes_without_top_windows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, int | str | None]] = []

    class FakeProcessWithoutWindow:
        info = {"pid": 1111, "name": "RingCentralDevelop.exe"}

    class FakeProcessWithWindow:
        info = {"pid": 2222, "name": "RingCentralDevelop.exe"}

    class FakeWindow:
        handle = 99

        def set_focus(self) -> None:
            calls.append(("focus", "window"))

    class FakeConnectedApplication:
        def __init__(self, pid: int | None = None) -> None:
            self._pid = pid

        def top_window(self) -> FakeWindow:
            calls.append(("top_window", self._pid))
            if self._pid is None or self._pid == 1111:
                raise RuntimeError("No windows for that process could be found")
            return FakeWindow()

    class FakeApplication:
        def __init__(self, backend: str) -> None:
            calls.append(("backend", backend))

        def connect(self, **kwargs: int | str) -> FakeConnectedApplication:
            if "path" in kwargs:
                calls.append(("path", str(kwargs["path"])))
                return FakeConnectedApplication()
            process = kwargs["process"]
            assert isinstance(process, int)
            calls.append(("process", process))
            return FakeConnectedApplication(process)

    monkeypatch.setattr(
        windows.psutil,
        "process_iter",
        lambda attrs: [FakeProcessWithoutWindow(), FakeProcessWithWindow()],
    )
    monkeypatch.setattr(windows, "Application", FakeApplication)

    WindowsDesktopDriver().focus_window("RingCentralDevelop")

    assert calls == [
        ("backend", "uia"),
        ("path", "RingCentralDevelop.exe"),
        ("top_window", None),
        ("backend", "uia"),
        ("process", 1111),
        ("top_window", 1111),
        ("backend", "uia"),
        ("process", 2222),
        ("top_window", 2222),
        ("focus", "window"),
    ]


def test_failed_refocus_clears_previous_focused_window(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = FakeControl("RingCentral", [FakeClickableControl("Start", "ButtonControl", [])])
    driver = focused_driver(monkeypatch, root)

    class FailingApplication:
        def __init__(self, backend: str) -> None:
            assert backend == "uia"

        def connect(self, path: str) -> "FailingApplication":
            raise RuntimeError(f"missing {path}")

    monkeypatch.setattr(windows, "Application", FailingApplication)

    with pytest.raises(RuntimeError, match="missing Missing.exe"):
        driver.focus_window("Missing")

    with pytest.raises(RuntimeError, match="before focusing a window"):
        driver.click_button("Start")


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


def test_read_focused_window_text_uses_focused_control_tree(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = FakeControl("RingCentral", [FakeControl("Video"), FakeControl("Start")])

    assert focused_driver(monkeypatch, root).read_focused_window_text() == (
        "RingCentral",
        "Video",
        "Start",
    )


def test_read_focused_window_text_requires_focused_window() -> None:
    with pytest.raises(RuntimeError, match="before focusing a window"):
        WindowsDesktopDriver().read_focused_window_text()


def test_list_visible_windows_returns_metadata_and_filters_noise(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = FakeWindow(
        title="Demo App",
        class_name="DemoWindow",
        pid=42,
        rectangle=SimpleNamespace(left=10, top=20, right=410, bottom=320),
        visible=True,
        minimized=False,
    )
    hidden = FakeWindow(
        title="Hidden App",
        class_name="HiddenWindow",
        pid=43,
        rectangle=SimpleNamespace(left=10, top=20, right=410, bottom=320),
        visible=False,
        minimized=False,
    )
    minimized = FakeWindow(
        title="Minimized App",
        class_name="MinimizedWindow",
        pid=44,
        rectangle=SimpleNamespace(left=10, top=20, right=410, bottom=320),
        visible=True,
        minimized=True,
    )
    blank_title = FakeWindow(
        title="   ",
        class_name="BlankTitleWindow",
        pid=45,
        rectangle=SimpleNamespace(left=10, top=20, right=410, bottom=320),
        visible=True,
        minimized=False,
    )
    blank_class = FakeWindow(
        title="Blank Class App",
        class_name="",
        pid=46,
        rectangle=SimpleNamespace(left=10, top=20, right=410, bottom=320),
        visible=True,
        minimized=False,
    )
    invalid_bounds = FakeWindow(
        title="Invalid App",
        class_name="InvalidWindow",
        pid=47,
        rectangle=SimpleNamespace(left=10, top=20, right=10, bottom=320),
        visible=True,
        minimized=False,
    )
    monkeypatch.setattr(
        windows,
        "Desktop",
        lambda backend: FakeDesktop(
            [hidden, minimized, blank_title, blank_class, invalid_bounds, root]
        ),
    )
    monkeypatch.setattr(windows, "psutil", FakePsutil({"Demo.exe": [42]}))

    discovered = WindowsDesktopDriver().list_visible_windows()

    assert len(discovered) == 1
    assert discovered[0].process == "Demo"
    assert discovered[0].pid == 42
    assert discovered[0].window_class == "DemoWindow"
    assert discovered[0].title == "Demo App"
    assert discovered[0].bounds == (10, 20, 410, 320)


def test_list_visible_windows_returns_empty_when_enumeration_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FailingDesktop:
        def __init__(self, backend: str) -> None:
            assert backend == "uia"

        def windows(self) -> list[FakeWindow]:
            raise RuntimeError("desktop changed")

    monkeypatch.setattr(windows, "Desktop", FailingDesktop)

    assert WindowsDesktopDriver().list_visible_windows() == ()


def test_list_visible_controls_returns_named_controls(monkeypatch: pytest.MonkeyPatch) -> None:
    handle = WindowHandle("Demo", 42, "DemoWindow", "Demo App")
    root_control = FakeControl(
        name="root",
        control_type="Window",
        bounds=SimpleNamespace(left=0, top=0, right=500, bottom=500),
        children=[
            FakeControl(
                "Settings",
                "Button",
                SimpleNamespace(left=10, top=10, right=100, bottom=40),
            ),
            FakeControl(
                "Delete",
                "Button",
                SimpleNamespace(left=10, top=50, right=100, bottom=80),
            ),
        ],
    )
    monkeypatch.setattr(windows, "_bind_window", lambda pid, window_class: FakeBoundWindow(handle))
    monkeypatch.setattr(windows, "_control_from_window", lambda window: root_control)

    controls = WindowsDesktopDriver().list_visible_controls(handle)

    assert [control.name for control in controls] == ["Settings", "Delete"]
    assert controls[0].control_type == "Button"


def test_list_visible_controls_returns_empty_for_missing_root(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    handle = WindowHandle("Demo", 42, "DemoWindow", "Demo App")
    monkeypatch.setattr(windows, "_bind_window", lambda pid, window_class: FakeBoundWindow(handle))
    monkeypatch.setattr(windows, "_control_from_window", lambda window: None)

    assert WindowsDesktopDriver().list_visible_controls(handle) == ()


def test_list_visible_controls_returns_empty_for_stale_binding(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    handle = WindowHandle("Demo", 42, "DemoWindow", "Demo App")
    monkeypatch.setattr(
        windows,
        "_bind_window",
        lambda pid, window_class: (_ for _ in ()).throw(RuntimeError("window closed")),
    )

    assert WindowsDesktopDriver().list_visible_controls(handle) == ()


def test_list_visible_controls_returns_empty_for_stale_root(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    handle = WindowHandle("Demo", 42, "DemoWindow", "Demo App")
    monkeypatch.setattr(windows, "_bind_window", lambda pid, window_class: FakeBoundWindow(handle))
    monkeypatch.setattr(
        windows,
        "_control_from_window",
        lambda window: (_ for _ in ()).throw(RuntimeError("uia unavailable")),
    )

    assert WindowsDesktopDriver().list_visible_controls(handle) == ()


def test_list_visible_controls_filters_offscreen_controls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    handle = WindowHandle("Demo", 42, "DemoWindow", "Demo App")
    root_control = FakeControl(
        name="root",
        control_type="Window",
        bounds=SimpleNamespace(left=0, top=0, right=500, bottom=500),
        children=[
            FakeControl(
                "Hidden",
                "Button",
                SimpleNamespace(left=10, top=10, right=100, bottom=40),
                is_offscreen=True,
            ),
            FakeControl(
                "Shown",
                "Button",
                SimpleNamespace(left=10, top=50, right=100, bottom=80),
                is_offscreen=False,
            ),
        ],
    )
    monkeypatch.setattr(windows, "_bind_window", lambda pid, window_class: FakeBoundWindow(handle))
    monkeypatch.setattr(windows, "_control_from_window", lambda window: root_control)

    controls = WindowsDesktopDriver().list_visible_controls(handle)

    assert [control.name for control in controls] == ["Shown"]


def test_list_visible_controls_skips_stale_controls_and_continues(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    handle = WindowHandle("Demo", 42, "DemoWindow", "Demo App")
    root_control = FakeControl(
        name="root",
        control_type="Window",
        bounds=SimpleNamespace(left=0, top=0, right=500, bottom=500),
        children=[
            StaleNameControl(),
            StaleTypeControl(),
            StaleChildrenControl(),
            StaleOffscreenControl(),
            FakeControl(
                "Settings",
                "Button",
                SimpleNamespace(left=10, top=10, right=100, bottom=40),
            ),
        ],
    )
    monkeypatch.setattr(windows, "_bind_window", lambda pid, window_class: FakeBoundWindow(handle))
    monkeypatch.setattr(windows, "_control_from_window", lambda window: root_control)

    controls = WindowsDesktopDriver().list_visible_controls(handle)

    assert [control.name for control in controls] == ["Settings"]


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


def test_wait_for_window_reports_missing_pywinauto_dependency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(windows, "Desktop", None)

    with pytest.raises(RuntimeError, match="pywinauto"):
        WindowsDesktopDriver().wait_for_window("RingCentralVideo", "VideoClass", 30_000)


def test_wait_for_window_reports_missing_psutil_dependency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(windows, "psutil", None)

    with pytest.raises(RuntimeError, match="psutil"):
        WindowsDesktopDriver().wait_for_window("RingCentralVideo", "VideoClass", 30_000)


def test_focus_window_reports_missing_dependency(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(windows, "Application", None)

    with pytest.raises(RuntimeError, match="pywinauto"):
        WindowsDesktopDriver().focus_window("RingCentralDevelop")


def test_press_key_maps_escape_to_pywinauto_escape_code(monkeypatch: pytest.MonkeyPatch) -> None:
    sent_keys: list[str] = []

    class FakeKeyboard:
        @staticmethod
        def send_keys(keys: str) -> None:
            sent_keys.append(keys)

    monkeypatch.setattr(windows, "keyboard", FakeKeyboard)

    WindowsDesktopDriver().press_key("Escape")

    assert sent_keys == ["{ESC}"]


def test_capture_reports_missing_pywinauto_dependency(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(windows, "Desktop", None)

    with pytest.raises(RuntimeError, match="pywinauto"):
        WindowsDesktopDriver().capture(WindowHandle("RingCentralVideo", 4321, "VideoClass", "Old"))


@pytest.mark.parametrize(
    ("dependency", "package"),
    [("mss", "mss"), ("Image", "Pillow")],
)
def test_capture_bounds_png_reports_missing_dependencies(
    monkeypatch: pytest.MonkeyPatch,
    dependency: str,
    package: str,
) -> None:
    monkeypatch.setattr(windows, dependency, None)

    with pytest.raises(RuntimeError, match=package):
        windows._capture_bounds_png((0, 0, 10, 10))


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


def test_capture_respects_requested_observation_sources(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    capture_calls: list[tuple[int, int, int, int]] = []
    control_calls: list[int] = []

    class FakeWindow:
        handle = 99

        def rectangle(self) -> SimpleNamespace:
            return SimpleNamespace(left=5, top=10, right=105, bottom=60)

        def window_text(self) -> str:
            return "Live meeting"

    class FakeWindowSpec:
        def wrapper_object(self) -> FakeWindow:
            return FakeWindow()

    class FakeDesktop:
        def __init__(self, backend: str) -> None:
            assert backend == "uia"

        def window(self, *, process: int, class_name: str) -> FakeWindowSpec:
            return FakeWindowSpec()

    def fake_capture(bounds: tuple[int, int, int, int]) -> bytes:
        capture_calls.append(bounds)
        return b"png"

    def fake_control_from_handle(handle: int) -> FakeControl:
        control_calls.append(handle)
        return FakeControl("Meeting")

    monkeypatch.setattr(windows, "Desktop", FakeDesktop)
    monkeypatch.setattr(windows, "_capture_bounds_png", fake_capture)
    monkeypatch.setattr(windows.uiautomation, "ControlFromHandle", fake_control_from_handle)

    observation = WindowsDesktopDriver().capture(
        WindowHandle("RingCentralVideo", 4321, "VideoClass", "Old title"),
        [ObservationSource.WINDOW_METADATA],
    )

    assert observation.screenshot_png is None
    assert observation.ui_text == ()
    assert observation.metadata.title == "Live meeting"
    assert observation.metadata.bounds == (5, 10, 105, 60)
    assert capture_calls == []
    assert control_calls == []
