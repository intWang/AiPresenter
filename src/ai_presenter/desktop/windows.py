from __future__ import annotations

from io import BytesIO
from time import monotonic, sleep
from typing import Any
import importlib

from ai_presenter.desktop.base import WindowHandle
from ai_presenter.domain.state import RawObservation, WindowMetadata

Application: Any = importlib.import_module("pywinauto").Application
Desktop: Any = importlib.import_module("pywinauto").Desktop
uiautomation: Any = importlib.import_module("uiautomation")
psutil: Any = importlib.import_module("psutil")
mss: Any = importlib.import_module("mss")
Image: Any = importlib.import_module("PIL.Image")

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
    def focus_window(self, process: str) -> None:
        executable = _process_executable(process)
        try:
            app = Application(backend="uia").connect(path=executable)
            window = app.top_window()
            _focus_window(window)
        except Exception as exc:
            raise RuntimeError(f"Unable to focus {executable}: {exc}") from exc

    def click_tab(self, target: str) -> None:
        _click_named_control(uiautomation.TabItemControl, target, "Tab")

    def click_button(self, target: str) -> None:
        _click_named_control(uiautomation.ButtonControl, target, "Button")

    def wait_for_window(self, process: str, window_class: str, timeout_ms: int) -> WindowHandle:
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

    def capture(self, handle: WindowHandle) -> RawObservation:
        try:
            window = _bind_window(handle.pid, handle.window_class)
        except Exception as exc:
            raise RuntimeError(
                f"Unable to bind window class {handle.window_class} for pid {handle.pid}: {exc}"
            ) from exc

        bounds = _window_bounds(window)
        control = _control_from_window(window)
        ui_text = collect_ui_text(control) if control is not None else []

        return RawObservation(
            metadata=WindowMetadata(
                process=handle.process,
                pid=handle.pid,
                window_class=handle.window_class,
                title=_window_title(window, fallback=handle.title),
                bounds=bounds,
                focused=_call_bool_window_method(window, "is_active"),
                minimized=_call_bool_window_method(window, "is_minimized"),
            ),
            screenshot_png=_capture_bounds_png(bounds),
            ui_text=ui_text,
        )


def _process_executable(process: str) -> str:
    stripped_process = process.strip()
    if stripped_process.casefold().endswith(".exe"):
        return stripped_process
    return f"{stripped_process}.exe"


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


def _click_named_control(control_factory: Any, target: str, label: str) -> None:
    try:
        control = control_factory(Name=target)
        if not bool(
            control.Exists(
                _CONTROL_SEARCH_SECONDS,
                _CONTROL_SEARCH_INTERVAL_SECONDS,
                False,
            )
        ):
            raise RuntimeError(f"{label} control not found: {target}")
        control.Click()
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
    except Exception:
        return None


def _bind_window(pid: int, window_class: str) -> Any:
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
    handle = getattr(window, "handle", None)
    if not isinstance(handle, int):
        return None

    try:
        return uiautomation.ControlFromHandle(handle)
    except Exception:
        return None


def _call_bool_window_method(window: Any, method_name: str) -> bool:
    method = getattr(window, method_name, None)
    if not callable(method):
        return False

    try:
        return bool(method())
    except Exception:
        return False


def _capture_bounds_png(bounds: tuple[int, int, int, int]) -> bytes:
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
