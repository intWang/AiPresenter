from __future__ import annotations

import importlib
from collections.abc import Iterable
from io import BytesIO
from time import monotonic, sleep
from typing import Any

from ai_presenter.config.models import ObservationSource
from ai_presenter.desktop.base import VisibleControl, VisibleWindow, WindowHandle
from ai_presenter.domain.state import RawObservation, WindowMetadata

_pywinauto: Any = None
try:
    _pywinauto = importlib.import_module("pywinauto")
except ImportError:
    pass

Application: Any = getattr(_pywinauto, "Application", None)
Desktop: Any = getattr(_pywinauto, "Desktop", None)
uiautomation: Any = None
psutil: Any = None
mss: Any = None
Image: Any = None
keyboard: Any = None
mouse: Any = None

try:
    uiautomation = importlib.import_module("uiautomation")
except ImportError:
    pass

try:
    psutil = importlib.import_module("psutil")
except ImportError:
    pass

try:
    mss = importlib.import_module("mss")
except ImportError:
    pass

try:
    Image = importlib.import_module("PIL.Image")
except ImportError:
    pass

try:
    keyboard = importlib.import_module("pywinauto.keyboard")
except ImportError:
    pass

try:
    mouse = importlib.import_module("pywinauto.mouse")
except ImportError:
    pass

_CONTROL_SEARCH_SECONDS = 5.0
_CONTROL_SEARCH_INTERVAL_SECONDS = 0.25
_WINDOW_POLL_INTERVAL_SECONDS = 0.1


def collect_ui_text(control: Any) -> list[str]:
    text: list[str] = []

    def walk(node: Any) -> None:
        name = getattr(node, "Name", None)
        if isinstance(name, str):
            stripped_name = name.strip()
            if stripped_name:
                text.append(stripped_name)

        get_children = getattr(node, "GetChildren", None)
        if not callable(get_children):
            return

        try:
            children = get_children()
        except Exception:
            return

        for child in children or []:
            walk(child)

    walk(control)
    return text


class WindowsDesktopDriver:
    def __init__(self) -> None:
        self._focused_window: Any | None = None

    def focus_window(self, process: str) -> None:
        _require_dependency(Application, "pywinauto")
        self._focused_window = None
        executable = _process_executable(process)
        failures: list[str] = []
        try:
            app = Application(backend="uia").connect(path=executable)
            window = app.top_window()
            _focus_window(window)
            self._focused_window = window
            return
        except Exception as exc:
            failures.append(str(exc))

        if psutil is not None:
            for pid in _matching_process_ids(process):
                try:
                    app = Application(backend="uia").connect(process=pid)
                    window = app.top_window()
                    _focus_window(window)
                    self._focused_window = window
                    return
                except Exception as exc:
                    failures.append(f"pid {pid}: {exc}")

        detail = "; ".join(failures) if failures else "no matching process"
        raise RuntimeError(f"Unable to focus {executable}: {detail}")

    def click_tab(self, target: str) -> None:
        _click_named_control(self._focused_window, target, "Tab", ("tab", "tabitem"))

    def click_button(self, target: str) -> None:
        _click_named_control(self._focused_window, target, "Button", ("button",))

    def read_focused_window_text(self) -> tuple[str, ...]:
        if self._focused_window is None:
            raise RuntimeError("Cannot read focused window text before focusing a window")

        root_control = _control_from_window(self._focused_window)
        if root_control is None:
            return ()
        return tuple(collect_ui_text(root_control))

    def list_visible_windows(self) -> tuple[VisibleWindow, ...]:
        _require_dependency(Desktop, "pywinauto")
        visible_windows: list[VisibleWindow] = []
        for window in Desktop(backend="uia").windows():
            try:
                if not _window_is_visible(window) or _call_bool_window_method(
                    window, "is_minimized"
                ):
                    continue
                bounds = _window_bounds(window)
                pid = int(getattr(window, "process_id")())
                process = _process_name_from_pid(pid)
                title = _window_title(window)
                window_class = _window_class(window)
            except Exception:
                continue
            if title.strip() and window_class.strip():
                visible_windows.append(VisibleWindow(process, pid, window_class, title, bounds))
        return tuple(visible_windows)

    def list_visible_controls(self, handle: WindowHandle) -> tuple[VisibleControl, ...]:
        window = _bind_window(handle.pid, handle.window_class)
        root_control = _control_from_window(window)
        if root_control is None:
            return ()
        return tuple(_collect_visible_controls(root_control))

    def click_window_relative(self, handle: WindowHandle, x: int, y: int) -> None:
        _require_dependency(mouse, "pywinauto")
        try:
            window = _bind_window(handle.pid, handle.window_class)
            _focus_window(window)
            left, top, _, _ = _window_bounds(window)
            mouse.click(button="left", coords=(left + x, top + y))
        except Exception as exc:
            raise RuntimeError(
                f"Unable to click relative point ({x}, {y}) in "
                f"{handle.window_class} for pid {handle.pid}: {exc}"
            ) from exc

    def click_window_control(
        self,
        handle: WindowHandle,
        target: str,
        *,
        occurrence: int = 1,
        control_type: str | None = None,
    ) -> None:
        if occurrence < 1:
            raise RuntimeError("Control occurrence must be at least 1")
        try:
            window = _bind_window(handle.pid, handle.window_class)
            _focus_window(window)
            root_control = _control_from_window(window)
            if root_control is None:
                raise RuntimeError("window does not expose UI Automation controls")

            markers = _normalize_type_markers(control_type)
            controls = _find_descendant_controls(
                root_control,
                target=target,
                type_markers=markers,
            )
            if len(controls) < occurrence:
                raise RuntimeError(
                    f"found {len(controls)} visible controls named {target}, "
                    f"need occurrence {occurrence}"
                )
            _click_control(controls[occurrence - 1])
        except Exception as exc:
            raise RuntimeError(
                f"Unable to click window control {target!r} occurrence {occurrence} in "
                f"{handle.window_class} for pid {handle.pid}: {exc}"
            ) from exc

    def window_bounds(self, handle: WindowHandle) -> tuple[int, int, int, int]:
        try:
            return _window_bounds(_bind_window(handle.pid, handle.window_class))
        except Exception as exc:
            raise RuntimeError(
                f"Unable to read bounds for {handle.window_class} pid {handle.pid}: {exc}"
            ) from exc

    def press_key(self, key: str) -> None:
        _require_dependency(keyboard, "pywinauto")
        normalized = key.strip()
        if not normalized:
            raise RuntimeError("Key cannot be blank")
        normalized = _pywinauto_key_name(normalized)
        try:
            keyboard.send_keys(f"{{{normalized}}}")
        except Exception as exc:
            raise RuntimeError(f"Unable to press key {normalized}: {exc}") from exc

    def wait_for_window(self, process: str, window_class: str, timeout_ms: int) -> WindowHandle:
        _require_dependency(Desktop, "pywinauto")
        _require_dependency(psutil, "psutil")
        deadline = monotonic() + max(timeout_ms, 0) / 1000

        while True:
            for pid in _matching_process_ids(process):
                window = _find_window(pid, window_class)
                if window is not None:
                    return WindowHandle(
                        process=process,
                        pid=pid,
                        window_class=window_class,
                        title=_window_title(window),
                    )

            if monotonic() >= deadline:
                executable = _process_executable(process)
                raise RuntimeError(
                    f"Timed out after {timeout_ms}ms waiting for "
                    f"{executable} window class {window_class}"
                )

            sleep(min(_WINDOW_POLL_INTERVAL_SECONDS, max(deadline - monotonic(), 0)))

    def capture(
        self,
        handle: WindowHandle,
        sources: Iterable[ObservationSource] | None = None,
    ) -> RawObservation:
        requested_sources = _normalize_observation_sources(sources)
        try:
            window = _bind_window(handle.pid, handle.window_class)
        except Exception as exc:
            raise RuntimeError(
                f"Unable to bind window class {handle.window_class} for pid {handle.pid}: {exc}"
            ) from exc

        needs_bounds = (
            ObservationSource.SCREENSHOT in requested_sources
            or ObservationSource.WINDOW_METADATA in requested_sources
        )
        bounds = _window_bounds(window) if needs_bounds else (0, 0, 0, 0)

        ui_text: list[str] = []
        if ObservationSource.WINDOWS_UI_AUTOMATION in requested_sources:
            control = _control_from_window(window)
            ui_text = collect_ui_text(control) if control is not None else []

        title = handle.title
        focused = False
        minimized = False
        if ObservationSource.WINDOW_METADATA in requested_sources:
            title = _window_title(window, fallback=handle.title)
            focused = _call_bool_window_method(window, "is_active")
            minimized = _call_bool_window_method(window, "is_minimized")

        return RawObservation(
            metadata=WindowMetadata(
                process=handle.process,
                pid=handle.pid,
                window_class=handle.window_class,
                title=title,
                bounds=bounds,
                focused=focused,
                minimized=minimized,
            ),
            screenshot_png=(
                _capture_bounds_png(bounds)
                if ObservationSource.SCREENSHOT in requested_sources
                else None
            ),
            ui_text=ui_text,
        )


def _process_executable(process: str) -> str:
    stripped_process = process.strip()
    if stripped_process.casefold().endswith(".exe"):
        return stripped_process
    return f"{stripped_process}.exe"


def _normalize_observation_sources(
    sources: Iterable[ObservationSource] | None,
) -> frozenset[ObservationSource]:
    if sources is None:
        return frozenset(ObservationSource)
    return frozenset(ObservationSource(source) for source in sources)


def _focus_window(window: Any) -> None:
    set_focus = getattr(window, "set_focus", None)
    if callable(set_focus):
        set_focus()
        return

    set_focus = getattr(window, "SetFocus", None)
    if callable(set_focus):
        set_focus()
        return

    raise RuntimeError("window does not expose a focus method")


def _click_named_control(
    focused_window: Any | None,
    target: str,
    label: str,
    type_markers: tuple[str, ...],
) -> None:
    if focused_window is None:
        raise RuntimeError(f"Cannot click {label.lower()} control before focusing a window")

    root_control = _control_from_window(focused_window)
    if root_control is None:
        raise RuntimeError(f"Focused window does not expose UI Automation controls for {label}")

    try:
        control = _find_descendant_control(
            root_control,
            target=target,
            type_markers=type_markers,
        )
        if control is None:
            raise RuntimeError(f"{label} control not found: {target}")
        _click_control(control)
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError(f"Unable to click {label.lower()} control {target}: {exc}") from exc


def _matching_process_ids(process: str) -> list[int]:
    executable = _process_executable(process).casefold()
    matching_pids: list[int] = []

    for candidate in psutil.process_iter(["pid", "name"]):
        try:
            info = getattr(candidate, "info", {})
            pid_value = info.get("pid") if isinstance(info, dict) else None
            name_value = info.get("name") if isinstance(info, dict) else None

            if not isinstance(name_value, str):
                name = getattr(candidate, "name", None)
                name_value = name() if callable(name) else None

            if not isinstance(pid_value, int):
                pid = getattr(candidate, "pid", None)
                pid_value = pid if isinstance(pid, int) else None

            if isinstance(name_value, str) and name_value.casefold() == executable:
                if isinstance(pid_value, int):
                    matching_pids.append(pid_value)
        except Exception:
            continue

    return matching_pids


def _find_window(pid: int, window_class: str) -> Any | None:
    try:
        window_spec = Desktop(backend="uia").window(process=pid, class_name=window_class)
        exists = getattr(window_spec, "exists", None)
        if callable(exists) and not bool(exists(timeout=0)):
            return None
        return _window_from_spec(window_spec)
    except Exception as exc:
        raise RuntimeError(
            f"Unable to query window class {window_class} for pid {pid}: {exc}"
        ) from exc


def _bind_window(pid: int, window_class: str) -> Any:
    _require_dependency(Desktop, "pywinauto")
    window_spec = Desktop(backend="uia").window(process=pid, class_name=window_class)
    return _window_from_spec(window_spec)


def _window_from_spec(window_spec: Any) -> Any:
    wrapper_object = getattr(window_spec, "wrapper_object", None)
    if callable(wrapper_object):
        return wrapper_object()
    return window_spec


def _window_title(window: Any, fallback: str = "") -> str:
    window_text = getattr(window, "window_text", None)
    if callable(window_text):
        try:
            title = window_text()
        except Exception:
            return fallback
        if isinstance(title, str):
            return title
    return fallback


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


def _window_bounds(window: Any) -> tuple[int, int, int, int]:
    rectangle = getattr(window, "rectangle", None)
    if not callable(rectangle):
        raise RuntimeError("window does not expose bounds")

    try:
        rect = rectangle()
        bounds = (int(rect.left), int(rect.top), int(rect.right), int(rect.bottom))
    except Exception as exc:
        raise RuntimeError(f"Unable to read window bounds: {exc}") from exc

    left, top, right, bottom = bounds
    if right <= left or bottom <= top:
        raise RuntimeError(f"Window bounds are empty: {bounds}")
    return bounds


def _control_from_window(window: Any) -> Any | None:
    _require_dependency(uiautomation, "uiautomation")
    handle = getattr(window, "handle", None)
    if not isinstance(handle, int):
        return None

    try:
        return uiautomation.ControlFromHandle(handle)
    except Exception:
        return None


def _find_descendant_control(
    root: Any,
    *,
    target: str,
    type_markers: tuple[str, ...],
) -> Any | None:
    normalized_target = target.strip()
    if not normalized_target:
        raise RuntimeError("Control target cannot be blank")

    stack = [root]
    while stack:
        node = stack.pop()
        if _control_name(node) == normalized_target and _matches_control_type(node, type_markers):
            return node

        get_children = getattr(node, "GetChildren", None)
        if not callable(get_children):
            continue
        try:
            children = get_children()
        except Exception:
            continue
        stack.extend(reversed(list(children or [])))
    return None


def _find_descendant_controls(
    root: Any,
    *,
    target: str,
    type_markers: tuple[str, ...],
) -> list[Any]:
    normalized_target = target.strip()
    if not normalized_target:
        raise RuntimeError("Control target cannot be blank")

    matches: list[tuple[tuple[int, int, int, int], Any]] = []
    stack = [root]
    while stack:
        node = stack.pop()
        bounds = _control_bounds(node)
        if (
            _control_name(node) == normalized_target
            and _matches_control_type(node, type_markers)
            and bounds is not None
        ):
            matches.append((bounds, node))

        get_children = getattr(node, "GetChildren", None)
        if not callable(get_children):
            continue
        try:
            children = get_children()
        except Exception:
            continue
        stack.extend(reversed(list(children or [])))

    matches.sort(key=lambda item: (item[0][0], item[0][1], item[0][2], item[0][3]))
    return [control for _, control in matches]


def _collect_visible_controls(root: Any) -> list[VisibleControl]:
    controls: list[VisibleControl] = []
    stack = list(reversed(_control_children(root)))
    while stack:
        node = stack.pop()
        name = _control_name(node)
        bounds = _control_bounds(node)
        control_type = _control_type_name(node)
        if name and bounds is not None:
            controls.append(VisibleControl(name=name, control_type=control_type, bounds=bounds))
        stack.extend(reversed(_control_children(node)))
    return controls


def _control_children(control: Any) -> list[Any]:
    get_children = getattr(control, "GetChildren", None)
    if not callable(get_children):
        return []
    try:
        return list(get_children() or [])
    except Exception:
        return []


def _control_name(control: Any) -> str:
    name = getattr(control, "Name", "")
    return name.strip() if isinstance(name, str) else ""


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


def _normalize_type_markers(control_type: str | None) -> tuple[str, ...]:
    if control_type is None:
        return ()
    return tuple(
        marker.strip().casefold()
        for marker in control_type.split(",")
        if marker.strip()
    )


def _matches_control_type(control: Any, type_markers: tuple[str, ...]) -> bool:
    if not type_markers:
        return True
    raw_markers = [
        getattr(control, "ControlTypeName", ""),
        getattr(control, "LocalizedControlType", ""),
        control.__class__.__name__,
    ]
    normalized = [marker.casefold() for marker in raw_markers if isinstance(marker, str)]
    if not normalized:
        return True
    return any(type_marker in marker for marker in normalized for type_marker in type_markers)


def _control_bounds(control: Any) -> tuple[int, int, int, int] | None:
    try:
        rect = control.BoundingRectangle
        bounds = (int(rect.left), int(rect.top), int(rect.right), int(rect.bottom))
    except Exception:
        return None

    left, top, right, bottom = bounds
    if right <= left or bottom <= top:
        return None
    return bounds


def _click_control(control: Any) -> None:
    click = getattr(control, "Click", None)
    if callable(click):
        click()
        return

    click = getattr(control, "ClickSimulation", None)
    if callable(click):
        click()
        return

    raise RuntimeError("control does not expose a click method")


def _call_bool_window_method(window: Any, method_name: str) -> bool:
    method = getattr(window, method_name, None)
    if not callable(method):
        return False

    try:
        return bool(method())
    except Exception:
        return False


def _pywinauto_key_name(key: str) -> str:
    aliases = {
        "escape": "ESC",
        "esc": "ESC",
        "enter": "ENTER",
        "return": "ENTER",
    }
    return aliases.get(key.casefold(), key)


def _capture_bounds_png(bounds: tuple[int, int, int, int]) -> bytes:
    _require_dependency(mss, "mss")
    _require_dependency(Image, "Pillow")
    left, top, right, bottom = bounds
    width = right - left
    height = bottom - top
    if width <= 0 or height <= 0:
        raise RuntimeError(f"Cannot capture empty bounds: {bounds}")

    monitor = {"left": left, "top": top, "width": width, "height": height}
    try:
        with mss.mss() as screen:
            shot = screen.grab(monitor)

        image = Image.frombytes("RGB", shot.size, shot.rgb)
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()
    except Exception as exc:
        raise RuntimeError(f"Unable to capture window screenshot: {exc}") from exc


def _require_dependency(dependency: Any | None, package_name: str) -> None:
    if dependency is None:
        raise RuntimeError(f"Windows desktop dependency is not available: {package_name}")
