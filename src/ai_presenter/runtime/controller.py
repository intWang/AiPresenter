from __future__ import annotations

import threading
from collections.abc import Callable
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
    running_windows: list[VisibleWindow] = []
    window_by_label: dict[str, VisibleWindow] = {}

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
        return window_by_label.get(app_choice.get())

    def sync_target_choice(*_args: object) -> None:
        if source.get() == "Running desktop app":
            package_choice.set(app_choice.get() or "No running app selected")
            flow_choice.set("")
            return
        package_choice.set(material_package.app_id)
        flow_choice.set(flow_id)

    def choose_running_app(label: str) -> None:
        app_choice.set(label)
        sync_target_choice()

    def refresh_running_windows() -> None:
        nonlocal running_windows, window_by_label
        try:
            running_windows = list(catalog.list_running_apps())
        except Exception as exc:
            running_windows = []
            window_by_label = {}
            app_choice.set("No running apps found")
            status.set(f"App refresh error: {exc}")
            sync_target_choice()
            return

        next_window_by_label: dict[str, VisibleWindow] = {}
        for index, window in enumerate(running_windows, start=1):
            label = running_app_label(window)
            if label in next_window_by_label:
                label = f"{label} #{index}"
            next_window_by_label[label] = window
        window_by_label = next_window_by_label

        menu = running_app_menu["menu"]
        menu.delete(0, "end")
        if not window_by_label:
            app_choice.set("No running apps found")
            menu.add_command(label=app_choice.get(), command=lambda: choose_running_app(app_choice.get()))
            sync_target_choice()
            return

        for label in window_by_label:
            menu.add_command(label=label, command=lambda value=label: choose_running_app(value))
        if app_choice.get() not in window_by_label:
            app_choice.set(next(iter(window_by_label)))
        sync_target_choice()

    def scan_selected_app() -> None:
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
            package_choice.set(package.app_id)
            flow_choice.set(package.demo_flows[0].id if package.demo_flows else "")
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
