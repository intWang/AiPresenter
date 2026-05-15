from __future__ import annotations

import threading
from collections.abc import Callable
from typing import TYPE_CHECKING

from ai_presenter.runtime.control import DemoControl
from ai_presenter.runtime.factory import run_material_demo
from ai_presenter.runtime.questions import answer_question
from ai_presenter.runtime.voice import PresenterTone, PresenterVoiceSettings

if TYPE_CHECKING:
    from tkinter import Tk

    from ai_presenter.config.models import DesktopAppProfile
    from ai_presenter.packages.models import MaterialPackage


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

    def sync_target_choice(*_args: object) -> None:
        if source.get() == "Running desktop app":
            package_choice.set(app_choice.get() or "No running app selected")
            flow_choice.set("")
            return
        package_choice.set(material_package.app_id)
        flow_choice.set(flow_id)

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
            controller.set_voice(
                PresenterVoiceSettings(
                    language="zh" if language.get() == "Chinese" else "en",
                    tone=tone_values[tone.get()],
                )
            )
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
    refresh_status()
    root.mainloop()


def _center_window(root: Tk) -> None:
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() - width) // 2
    y = (root.winfo_screenheight() - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")
