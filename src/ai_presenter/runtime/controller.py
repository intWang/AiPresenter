from __future__ import annotations

import threading
from typing import TYPE_CHECKING

from ai_presenter.runtime.control import DemoControl
from ai_presenter.runtime.factory import run_material_demo

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
    ) -> None:
        self._profile = profile
        self._material_package = material_package
        self._flow_id = flow_id
        self._control = control or DemoControl()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
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

    def _run_demo(self) -> None:
        run_material_demo(
            self._profile,
            self._material_package,
            self._flow_id,
            control=self._control,
        )


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
    root.geometry("360x140")

    status = tk.StringVar(value="Ready")
    pause_label = tk.StringVar(value="Pause")

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

    frame = tk.Frame(root, padx=16, pady=16)
    frame.pack(fill="both", expand=True)
    tk.Label(frame, textvariable=status, anchor="w").pack(fill="x", pady=(0, 12))

    button_row = tk.Frame(frame)
    button_row.pack(fill="x")
    tk.Button(button_row, text="Start", command=start, width=10).pack(side="left", padx=(0, 8))
    tk.Button(button_row, textvariable=pause_label, command=pause_or_resume, width=10).pack(
        side="left",
        padx=(0, 8),
    )
    tk.Button(button_row, text="End", command=end, width=10).pack(side="left")

    _center_window(root)
    root.mainloop()


def _center_window(root: Tk) -> None:
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() - width) // 2
    y = (root.winfo_screenheight() - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")
