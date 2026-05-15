from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from ai_presenter.desktop.base import VisibleWindow, WindowHandle
from ai_presenter.desktop.windows import WindowsDesktopDriver
from ai_presenter.runtime.catalog import ControllerAppCatalog
from ai_presenter.runtime.control import DemoControl
from ai_presenter.runtime.factory import run_material_demo
from ai_presenter.runtime.questions import answer_question
from ai_presenter.runtime.session import ControllerSession, RunningAppTarget
from ai_presenter.runtime.voice import PresenterTone, PresenterVoiceSettings

if TYPE_CHECKING:
    from tkinter import Tk

    from ai_presenter.config.models import DesktopAppProfile
    from ai_presenter.packages.models import MaterialPackage


REPO_PACKAGE_DIR = Path(__file__).resolve().parents[3] / "packages"
NO_RUNNING_APPS_LABEL = "No running apps found"
RUNNING_APP_SCAN_REQUIRED_MESSAGE = "Scan the selected running app before asking questions."


@dataclass
class _RunningAppScanState:
    window_by_label: dict[str, VisibleWindow] = field(default_factory=dict)
    selected_label: str = ""
    _scanned_window_key: tuple[str, int, str] | None = None

    def replace_windows(self, window_by_label: dict[str, VisibleWindow]) -> None:
        self.window_by_label = dict(window_by_label)
        if self.selected_label not in self.window_by_label:
            self.selected_label = next(iter(self.window_by_label), NO_RUNNING_APPS_LABEL)
        self._clear_stale_scan()

    def choose(self, label: str) -> None:
        self.selected_label = label
        self._clear_stale_scan()

    def mark_selected_scanned(self) -> None:
        self._scanned_window_key = self._selected_window_key()

    @property
    def selected_window(self) -> VisibleWindow | None:
        return self.window_by_label.get(self.selected_label)

    @property
    def has_scanned_selection(self) -> bool:
        return self._selected_window_key() == self._scanned_window_key

    def _clear_stale_scan(self) -> None:
        if self._scanned_window_key is None:
            return
        available_keys = {
            self._window_key(label, window) for label, window in self.window_by_label.items()
        }
        if (
            self._scanned_window_key not in available_keys
            or self._selected_window_key() != self._scanned_window_key
        ):
            self._scanned_window_key = None

    def _selected_window_key(self) -> tuple[str, int, str] | None:
        window = self.selected_window
        if window is None:
            return None
        return self._window_key(self.selected_label, window)

    @staticmethod
    def _window_key(label: str, window: VisibleWindow) -> tuple[str, int, str]:
        return (label, window.pid, window.window_class)


class PresenterController:
    def __init__(
        self,
        *,
        profile: DesktopAppProfile,
        material_package: MaterialPackage,
        flow_id: str,
        control: DemoControl | None = None,
        runner: Callable[..., None] | None = None,
    ) -> None:
        self._profile = profile
        self._material_package = material_package
        self._flow_id = flow_id
        self._control = control or DemoControl()
        self._runner = runner or run_material_demo
        self._thread: threading.Thread | None = None
        self._last_error: Exception | None = None
        self._voice = PresenterVoiceSettings()

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._last_error = None
        self._control.reset()
        self._thread = threading.Thread(target=self._run_demo, daemon=True)
        self._thread.start()

    def pause_or_resume(self) -> bool:
        if self._control.is_paused:
            self._control.resume()
            return False
        self._control.pause()
        return True

    def end(self) -> None:
        self._control.request_stop()

    def set_voice(self, voice: PresenterVoiceSettings) -> None:
        self._voice = voice

    def submit_question(self, question: str) -> str:
        response = answer_question(
            package=self._material_package,
            question=question,
            voice=self._voice,
        )
        return response.answer_text

    def join(self, timeout: float | None = None) -> None:
        if self._thread is not None:
            self._thread.join(timeout=timeout)

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    @property
    def is_paused(self) -> bool:
        return self._control.is_paused

    @property
    def last_error(self) -> Exception | None:
        return self._last_error

    def _run_demo(self) -> None:
        try:
            self._runner(
                self._profile,
                self._material_package,
                self._flow_id,
                control=self._control,
            )
        except Exception as exc:
            self._last_error = exc


def run_controller(
    profile: DesktopAppProfile,
    material_package: MaterialPackage,
    flow_id: str,
) -> None:
    import tkinter as tk

    desktop = WindowsDesktopDriver()
    session = ControllerSession()
    catalog = ControllerAppCatalog(package_dir=REPO_PACKAGE_DIR, desktop=desktop)
    scan_state = _RunningAppScanState()
    scanned_package_id = ""
    scanned_flow_id = ""

    controller = PresenterController(
        profile=profile,
        material_package=material_package,
        flow_id=flow_id,
    )
    root = tk.Tk()
    root.title("AiPresenter Controller")
    root.geometry("640x360")

    status = tk.StringVar(value="Ready")
    pause_label = tk.StringVar(value="Pause")
    source = tk.StringVar(value="Material package")
    package_choice = tk.StringVar(value=material_package.app_id)
    flow_choice = tk.StringVar(value=flow_id)
    app_choice = tk.StringVar(value="")
    language = tk.StringVar(value="English")
    tone = tk.StringVar(value="Professional")
    question = tk.StringVar(value="")
    answer = tk.StringVar(value="")
    tone_values: dict[str, PresenterTone] = {
        "Professional": "professional",
        "Conversational": "conversational",
        "Concise": "concise",
    }

    def running_app_label(window: VisibleWindow) -> str:
        title = window.title.strip() or window.window_class or "Untitled"
        return f"{title} ({window.process}:{window.pid})"

    def selected_running_window() -> VisibleWindow | None:
        return scan_state.selected_window

    def sync_target_choice(*_args: object) -> None:
        if source.get() == "Running desktop app":
            if scan_state.has_scanned_selection:
                package_choice.set(scanned_package_id)
                flow_choice.set(scanned_flow_id)
            else:
                package_choice.set(f"{app_choice.get() or 'No running app selected'} needs scan")
                flow_choice.set("")
            return
        package_choice.set(material_package.app_id)
        flow_choice.set(flow_id)

    def choose_running_app(label: str) -> None:
        previously_scanned = scan_state.has_scanned_selection
        scan_state.choose(label)
        app_choice.set(label)
        if previously_scanned and not scan_state.has_scanned_selection:
            status.set("Selected running app needs scanning")
        sync_target_choice()

    def refresh_running_windows() -> None:
        try:
            running_windows = list(catalog.list_running_apps())
        except Exception as exc:
            scan_state.replace_windows({})
            app_choice.set(NO_RUNNING_APPS_LABEL)
            status.set(f"App refresh error: {exc}")
            sync_target_choice()
            return

        next_window_by_label: dict[str, VisibleWindow] = {}
        for index, window in enumerate(running_windows, start=1):
            label = running_app_label(window)
            if label in next_window_by_label:
                label = f"{label} #{index}"
            next_window_by_label[label] = window

        previously_scanned = scan_state.has_scanned_selection
        scan_state.replace_windows(next_window_by_label)

        menu = running_app_menu["menu"]
        menu.delete(0, "end")
        if not scan_state.window_by_label:
            app_choice.set(NO_RUNNING_APPS_LABEL)
            menu.add_command(label=app_choice.get(), command=lambda: choose_running_app(app_choice.get()))
            sync_target_choice()
            if previously_scanned:
                status.set("Selected running app needs scanning")
            return

        for label in scan_state.window_by_label:
            menu.add_command(label=label, command=lambda value=label: choose_running_app(value))
        app_choice.set(scan_state.selected_label)
        if previously_scanned and not scan_state.has_scanned_selection:
            status.set("Selected running app needs scanning")
        sync_target_choice()

    def scan_selected_app() -> None:
        nonlocal scanned_flow_id, scanned_package_id
        selected = selected_running_window()
        if selected is None:
            status.set("Scan error: select a running app first")
            return
        try:
            handle = WindowHandle(
                process=selected.process,
                pid=selected.pid,
                window_class=selected.window_class,
                title=selected.title,
            )
            controls = desktop.list_visible_controls(handle)
            package = session.scan_running_app(RunningAppTarget(window=selected), controls)
            scan_state.mark_selected_scanned()
            scanned_package_id = package.app_id
            scanned_flow_id = package.demo_flows[0].id if package.demo_flows else ""
            package_choice.set(scanned_package_id)
            flow_choice.set(scanned_flow_id)
            status.set(
                f"Scanned {package.app_name}: {len(package.operation_entrypoints)} entrypoints"
            )
        except Exception as exc:
            status.set(f"Scan error: {exc}")

    def start() -> None:
        controller.start()
        status.set("Running")
        pause_label.set("Pause")

    def pause_or_resume() -> None:
        paused = controller.pause_or_resume()
        status.set("Paused" if paused else "Running")
        pause_label.set("Resume" if paused else "Pause")

    def end() -> None:
        controller.end()
        status.set("Ending")
        pause_label.set("Pause")

    def submit_question() -> None:
        text = question.get().strip()
        if not text:
            return
        try:
            voice = PresenterVoiceSettings(
                language="zh" if language.get() == "Chinese" else "en",
                tone=tone_values[tone.get()],
            )
            controller.set_voice(voice)
            if source.get() == "Running desktop app":
                if not scan_state.has_scanned_selection:
                    answer.set(RUNNING_APP_SCAN_REQUIRED_MESSAGE)
                    status.set(RUNNING_APP_SCAN_REQUIRED_MESSAGE)
                    return
                session.set_voice(voice)
                answer.set(session.answer_question(text).answer_text)
            else:
                answer.set(controller.submit_question(text))
        except Exception as exc:
            answer.set(f"Question error: {exc}")

    def refresh_status() -> None:
        if controller.last_error is not None:
            status.set(f"Error: {controller.last_error}")
        elif controller.is_running:
            status.set("Paused" if controller.is_paused else "Running")
            pause_label.set("Resume" if controller.is_paused else "Pause")
        elif status.get() == "Ending":
            status.set("Ended")
        root.after(500, refresh_status)

    frame = tk.Frame(root, padx=16, pady=16)
    frame.pack(fill="both", expand=True)
    tk.Label(frame, textvariable=status, anchor="w").pack(fill="x", pady=(0, 12))

    target_frame = tk.LabelFrame(frame, text="Target", padx=8, pady=8)
    target_frame.pack(fill="x", pady=(0, 12))
    tk.OptionMenu(
        target_frame,
        source,
        "Material package",
        "Running desktop app",
        command=sync_target_choice,
    ).pack(side="left")
    tk.Label(target_frame, textvariable=package_choice).pack(side="left", padx=(8, 0))
    tk.Label(target_frame, textvariable=flow_choice).pack(side="left", padx=(8, 0))
    running_app_menu = tk.OptionMenu(
        target_frame,
        app_choice,
        "No running apps found",
        command=sync_target_choice,
    )
    running_app_menu.pack(side="left", padx=(8, 0))
    tk.Button(target_frame, text="Refresh", command=refresh_running_windows, width=10).pack(
        side="left",
        padx=(8, 0),
    )
    tk.Button(target_frame, text="Scan", command=scan_selected_app, width=8).pack(
        side="left",
        padx=(8, 0),
    )

    button_row = tk.Frame(frame)
    button_row.pack(fill="x")
    tk.Button(button_row, text="Start", command=start, width=10).pack(side="left", padx=(0, 8))
    tk.Button(button_row, textvariable=pause_label, command=pause_or_resume, width=10).pack(
        side="left",
        padx=(0, 8),
    )
    tk.Button(button_row, text="End", command=end, width=10).pack(side="left")

    voice_row = tk.Frame(frame)
    voice_row.pack(fill="x", pady=(24, 12))
    tk.OptionMenu(voice_row, language, "English", "Chinese").pack(side="left", padx=(0, 8))
    tk.OptionMenu(voice_row, tone, "Professional", "Conversational", "Concise").pack(side="left")

    question_row = tk.Frame(frame)
    question_row.pack(fill="x", pady=(12, 8))
    tk.Entry(question_row, textvariable=question).pack(side="left", fill="x", expand=True, padx=(0, 8))
    tk.Button(question_row, text="Submit", command=submit_question, width=10).pack(side="left")
    tk.Label(frame, textvariable=answer, anchor="w", wraplength=580, justify="left").pack(fill="x")

    _center_window(root)
    refresh_running_windows()
    refresh_status()
    root.mainloop()


def _center_window(root: Tk) -> None:
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() - width) // 2
    y = (root.winfo_screenheight() - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")
