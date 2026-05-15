from __future__ import annotations

import threading
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from ai_presenter.desktop.base import VisibleWindow, WindowHandle
from ai_presenter.desktop.windows import WindowsDesktopDriver
from ai_presenter.packages.models import DemoFlow, DemoStep
from ai_presenter.runtime.catalog import ControllerAppCatalog
from ai_presenter.runtime.control import DemoControl
from ai_presenter.runtime.factory import run_existing_window_material_demo
from ai_presenter.runtime.factory import run_material_demo
from ai_presenter.runtime.questions import answer_question
from ai_presenter.runtime.session import ControllerSession, MaterialPackageTarget, RunningAppTarget
from ai_presenter.runtime.session import create_question_interrupt_step
from ai_presenter.runtime.voice import PresenterTone, PresenterVoiceSettings

if TYPE_CHECKING:
    from tkinter import Tk

    from ai_presenter.config.models import DesktopAppProfile
    from ai_presenter.packages.models import MaterialPackage


REPO_PACKAGE_DIR = Path(__file__).resolve().parents[3] / "packages"
NO_RUNNING_APPS_LABEL = "No running apps found"
RUNNING_APP_SCAN_REQUIRED_MESSAGE = "Scan the selected running app before asking questions."
QUESTION_FLOW_ID = "question-answer-demo"

QuestionDemonstrationStatus = Literal["text_only", "queued", "started"]


@dataclass(frozen=True)
class ChatTurn:
    speaker: str
    message: str


@dataclass(frozen=True)
class QuestionSubmitResult:
    answer_text: str
    demonstration_status: QuestionDemonstrationStatus = "text_only"
    demonstration_message: str = ""


def format_chat_turns(turns: Sequence[ChatTurn]) -> str:
    return "\n\n".join(f"{turn.speaker}: {turn.message}" for turn in turns)


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
        selected_key = self._selected_window_key()
        return (
            selected_key is not None
            and self._scanned_window_key is not None
            and selected_key == self._scanned_window_key
        )

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


@dataclass(frozen=True)
class _ControllerRunTarget:
    material_package: MaterialPackage
    flow_id: str
    handle: WindowHandle | None = None


class PresenterController:
    def __init__(
        self,
        *,
        profile: DesktopAppProfile,
        material_package: MaterialPackage,
        flow_id: str,
        control: DemoControl | None = None,
        runner: Callable[..., None] | None = None,
        window_runner: Callable[..., None] | None = None,
    ) -> None:
        self._profile = profile
        self._target = _ControllerRunTarget(material_package, flow_id)
        self._control = control or DemoControl()
        self._runner = runner or run_material_demo
        self._window_runner = window_runner or run_existing_window_material_demo
        self._thread: threading.Thread | None = None
        self._last_error: Exception | None = None
        self._voice = PresenterVoiceSettings()
        self._state_lock = threading.Lock()

    def start(self) -> None:
        with self._state_lock:
            target = self._target
            voice = self._voice
        self._start_target(target, voice)

    def pause_or_resume(self) -> bool:
        if self._control.is_paused:
            self._control.resume()
            return False
        self._control.pause()
        return True

    def end(self) -> None:
        self._control.request_stop()

    def set_voice(self, voice: PresenterVoiceSettings) -> None:
        with self._state_lock:
            self._voice = voice

    def set_target(
        self,
        *,
        material_package: MaterialPackage,
        flow_id: str,
        handle: WindowHandle | None = None,
    ) -> None:
        if self.is_running:
            raise RuntimeError("Cannot change target while a demo is running.")
        with self._state_lock:
            self._target = _ControllerRunTarget(material_package, flow_id, handle)

    def submit_question(self, question: str) -> QuestionSubmitResult:
        with self._state_lock:
            target = self._target
            voice = self._voice
        response = answer_question(
            package=target.material_package,
            question=question,
            voice=voice,
        )
        interrupt = create_question_interrupt_step(target.material_package, response)
        if interrupt is None:
            return QuestionSubmitResult(answer_text=response.answer_text)
        if self.is_running:
            self._control.enqueue_interrupt(interrupt)
            return QuestionSubmitResult(
                answer_text=response.answer_text,
                demonstration_status="queued",
                demonstration_message="I will show that right after the current step.",
            )
        question_target = _target_with_question_flow(target, interrupt)
        if self._start_target(question_target, voice):
            return QuestionSubmitResult(
                answer_text=response.answer_text,
                demonstration_status="started",
                demonstration_message="Demonstrating it now.",
            )
        self._control.enqueue_interrupt(interrupt)
        return QuestionSubmitResult(
            answer_text=response.answer_text,
            demonstration_status="queued",
            demonstration_message="I will show that right after the current step.",
        )

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

    def _start_target(self, target: _ControllerRunTarget, voice: PresenterVoiceSettings) -> bool:
        if self._thread is not None and self._thread.is_alive():
            return False
        self._last_error = None
        self._control.reset()
        self._thread = threading.Thread(target=self._run_demo, args=(target, voice), daemon=True)
        self._thread.start()
        return True

    def _run_demo(self, target: _ControllerRunTarget, voice: PresenterVoiceSettings) -> None:
        try:
            if target.handle is None:
                self._runner(
                    self._profile,
                    target.material_package,
                    target.flow_id,
                    control=self._control,
                    voice=voice,
                )
            else:
                self._window_runner(
                    self._profile,
                    target.material_package,
                    target.flow_id,
                    handle=target.handle,
                    control=self._control,
                    voice=voice,
                )
        except Exception as exc:
            self._last_error = exc


def _target_with_question_flow(
    target: _ControllerRunTarget,
    step: DemoStep,
) -> _ControllerRunTarget:
    flow = DemoFlow(
        id=QUESTION_FLOW_ID,
        title="Question answer",
        goal="Answer the user's question with a focused UI demonstration.",
        steps=[step],
    )
    package = target.material_package.model_copy(
        update={"demo_flows": [*target.material_package.demo_flows, flow]},
    )
    return _ControllerRunTarget(package, QUESTION_FLOW_ID, target.handle)


def run_controller(
    profile: DesktopAppProfile,
    material_package: MaterialPackage,
    flow_id: str,
) -> None:
    import tkinter as tk

    desktop = WindowsDesktopDriver()
    session = ControllerSession()
    session.select_target(
        MaterialPackageTarget(profile=profile, package=material_package, flow_id=flow_id)
    )
    catalog = ControllerAppCatalog(package_dir=REPO_PACKAGE_DIR, desktop=desktop)
    scan_state = _RunningAppScanState()
    scanned_package_id = ""
    scanned_flow_id = ""
    scanned_package: MaterialPackage | None = None
    scanned_handle: WindowHandle | None = None

    controller = PresenterController(
        profile=profile,
        material_package=material_package,
        flow_id=flow_id,
    )
    root = tk.Tk()
    root.title("AiPresenter Controller")
    root.geometry("720x500")

    status = tk.StringVar(value="Ready")
    pause_label = tk.StringVar(value="Pause")
    source = tk.StringVar(value="Material package")
    package_choice = tk.StringVar(value=material_package.app_id)
    flow_choice = tk.StringVar(value=flow_id)
    app_choice = tk.StringVar(value="")
    language = tk.StringVar(value="English")
    tone = tk.StringVar(value="Professional")
    question = tk.StringVar(value="")
    chat_turns: list[ChatTurn] = []
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

    def current_voice() -> PresenterVoiceSettings:
        return PresenterVoiceSettings(
            language="zh" if language.get() == "Chinese" else "en",
            tone=tone_values[tone.get()],
        )

    def handle_from_window(window: VisibleWindow) -> WindowHandle:
        return WindowHandle(
            process=window.process,
            pid=window.pid,
            window_class=window.window_class,
            title=window.title,
        )

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
        if not controller.is_running:
            controller.set_target(material_package=material_package, flow_id=flow_id)

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
        nonlocal scanned_flow_id, scanned_package_id, scanned_handle, scanned_package
        selected = selected_running_window()
        if selected is None:
            status.set("Scan error: select a running app first")
            return
        try:
            handle = handle_from_window(selected)
            controls = desktop.list_visible_controls(handle)
            package = session.scan_running_app(RunningAppTarget(window=selected), controls)
            scan_state.mark_selected_scanned()
            scanned_package = package
            scanned_handle = handle
            scanned_package_id = package.app_id
            scanned_flow_id = package.demo_flows[0].id if package.demo_flows else ""
            controller.set_target(
                material_package=package,
                flow_id=scanned_flow_id,
                handle=handle,
            )
            package_choice.set(scanned_package_id)
            flow_choice.set(scanned_flow_id)
            status.set(
                f"Scanned {package.app_name}: {len(package.operation_entrypoints)} entrypoints"
            )
        except Exception as exc:
            status.set(f"Scan error: {exc}")

    def start() -> None:
        try:
            voice = current_voice()
            controller.set_voice(voice)
            if source.get() == "Running desktop app":
                if (
                    not scan_state.has_scanned_selection
                    or scanned_package is None
                    or scanned_handle is None
                    or not scanned_flow_id
                ):
                    status.set(RUNNING_APP_SCAN_REQUIRED_MESSAGE)
                    return
                controller.set_target(
                    material_package=scanned_package,
                    flow_id=scanned_flow_id,
                    handle=scanned_handle,
                )
            else:
                session.set_voice(voice)
                session.select_target(
                    MaterialPackageTarget(
                        profile=profile,
                        package=material_package,
                        flow_id=flow_id,
                    )
                )
                controller.set_target(material_package=material_package, flow_id=flow_id)
            session.mark_running()
            controller.start()
            status.set("Running")
            pause_label.set("Pause")
        except Exception as exc:
            session.mark_stopped()
            status.set(f"Start error: {exc}")

    def pause_or_resume() -> None:
        paused = controller.pause_or_resume()
        status.set("Paused" if paused else "Running")
        pause_label.set("Resume" if paused else "Pause")

    def end() -> None:
        controller.end()
        session.mark_stopped()
        status.set("Ending")
        pause_label.set("Pause")

    def append_chat(speaker: str, message: str) -> None:
        chat_turns.append(ChatTurn(speaker, message))
        chat_history.configure(state="normal")
        chat_history.delete("1.0", "end")
        chat_history.insert("end", format_chat_turns(chat_turns))
        chat_history.configure(state="disabled")
        chat_history.see("end")

    def submit_question() -> None:
        text = question.get().strip()
        if not text:
            return
        append_chat("You", text)
        question.set("")
        try:
            voice = current_voice()
            controller.set_voice(voice)
            if source.get() == "Running desktop app":
                if not scan_state.has_scanned_selection:
                    append_chat("AiPresenter", RUNNING_APP_SCAN_REQUIRED_MESSAGE)
                    status.set(RUNNING_APP_SCAN_REQUIRED_MESSAGE)
                    return
                session.set_voice(voice)
            elif not controller.is_running:
                controller.set_target(material_package=material_package, flow_id=flow_id)
            result = controller.submit_question(text)
            append_chat("AiPresenter", result.answer_text)
            if result.demonstration_message:
                append_chat("AiPresenter", result.demonstration_message)
            if result.demonstration_status == "started":
                session.mark_running()
                status.set("Demonstrating answer")
            elif result.demonstration_status == "queued":
                status.set("Question queued")
        except Exception as exc:
            append_chat("AiPresenter", f"Question error: {exc}")

    def refresh_status() -> None:
        if controller.last_error is not None:
            session.mark_stopped()
            status.set(f"Error: {controller.last_error}")
        elif controller.is_running:
            status.set("Paused" if controller.is_paused else "Running")
            pause_label.set("Resume" if controller.is_paused else "Pause")
        elif status.get() == "Ending":
            session.mark_stopped()
            status.set("Ended")
        elif session.is_running:
            session.mark_stopped()
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
    question_entry = tk.Entry(question_row, textvariable=question)
    question_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
    question_entry.bind("<Return>", lambda _event: submit_question())
    tk.Button(question_row, text="Submit", command=submit_question, width=10).pack(side="left")
    chat_history = tk.Text(frame, height=8, wrap="word", state="disabled")
    chat_history.pack(fill="both", expand=True)

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
