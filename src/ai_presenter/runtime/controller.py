from __future__ import annotations

import threading
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from ai_presenter.config.models import AppProfile
from ai_presenter.desktop.base import VisibleWindow, WindowHandle
from ai_presenter.desktop.windows import WindowsDesktopDriver
from ai_presenter.packages.models import DemoFlow, DemoStep
from ai_presenter.runtime.catalog import ControllerAppCatalog
from ai_presenter.runtime.control import DemoControl
from ai_presenter.runtime.controller_view_model import ControllerOperatorSnapshot
from ai_presenter.runtime.controller_view_model import ControllerOperatorViewModel
from ai_presenter.runtime.controller_view_model import ControllerSourceMode
from ai_presenter.runtime.controller_view_model import ControllerVoiceReadiness
from ai_presenter.runtime.controller_view_model import build_controller_operator_view_model
from ai_presenter.runtime.controller_view_model import render_controller_operator_summary_rows
from ai_presenter.runtime.controller_view_model import render_voice_label as _render_voice_label
from ai_presenter.runtime.factory import run_existing_window_material_demo
from ai_presenter.runtime.factory import run_material_demo
from ai_presenter.runtime.questions import QuestionAnswerSource, answer_question
from ai_presenter.runtime.session import ControllerSession, MaterialPackageTarget, RunningAppTarget
from ai_presenter.runtime.session import create_question_interrupt_step
from ai_presenter.runtime.voice import PRESENTER_LANGUAGE_CHOICES
from ai_presenter.runtime.voice import PRESENTER_TONE_CHOICES
from ai_presenter.runtime.voice import PresenterVoiceSettings
from ai_presenter.runtime.voice import language_label
from ai_presenter.runtime.voice import tone_label
from ai_presenter.runtime.voice import validate_profile_voice
from ai_presenter.runtime.voice_assets import VoiceAssetAvailability
from ai_presenter.runtime.voice_assets import check_voice_asset_availability

if TYPE_CHECKING:
    from tkinter import Tk

    from ai_presenter.config.models import DesktopAppProfile
    from ai_presenter.packages.models import MaterialPackage


REPO_PACKAGE_DIR = Path(__file__).resolve().parents[3] / "packages"
NO_RUNNING_APPS_LABEL = "No running apps found"
RUNNING_APP_SCAN_REQUIRED_MESSAGE = "Scan the selected running app before asking questions."
QUESTION_FLOW_ID = "question-answer-demo"

QuestionDemonstrationStatus = Literal["text_only", "interrupting", "queued", "started"]
VoiceAssetChecker = Callable[[AppProfile, PresenterVoiceSettings], VoiceAssetAvailability | None]


@dataclass(frozen=True)
class ChatTurn:
    speaker: str
    message: str


@dataclass(frozen=True)
class QuestionSubmitResult:
    answer_text: str
    demonstration_status: QuestionDemonstrationStatus = "text_only"
    demonstration_message: str = ""
    entrypoint_id: str | None = None
    can_operate: bool = False
    answer_source: QuestionAnswerSource = "no_match"


@dataclass(frozen=True)
class ControllerStatusSnapshot:
    current_status: str
    last_error: Exception | None
    is_running: bool
    is_paused: bool
    is_stopping: bool
    is_switching_targets: bool
    session_is_running: bool


@dataclass(frozen=True)
class ControllerStatusUpdate:
    status: str
    pause_label: str
    mark_session_stopped: bool = False


@dataclass(frozen=True)
class ControllerAppliedStatusState:
    status: str
    pause_label: str


@dataclass(frozen=True)
class ControllerStatusApplication:
    state: ControllerAppliedStatusState
    status_changed: bool
    pause_label_changed: bool
    mark_session_stopped: bool
    refresh_operator_view: bool


def plan_controller_status_application(
    current: ControllerAppliedStatusState,
    update: ControllerStatusUpdate,
) -> ControllerStatusApplication:
    status_changed = current.status != update.status
    pause_label_changed = current.pause_label != update.pause_label
    return ControllerStatusApplication(
        state=ControllerAppliedStatusState(
            status=update.status,
            pause_label=update.pause_label,
        ),
        status_changed=status_changed,
        pause_label_changed=pause_label_changed,
        mark_session_stopped=update.mark_session_stopped,
        refresh_operator_view=(
            status_changed or pause_label_changed or update.mark_session_stopped
        ),
    )


def format_chat_turns(turns: Sequence[ChatTurn]) -> str:
    return "\n\n".join(f"{turn.speaker}: {turn.message}" for turn in turns)


def render_operator_summary_text(view_model: ControllerOperatorViewModel) -> str:
    return "\n".join(render_controller_operator_summary_rows(view_model))


def resolve_controller_status(snapshot: ControllerStatusSnapshot) -> ControllerStatusUpdate:
    if snapshot.last_error is not None:
        return ControllerStatusUpdate(
            status=f"Error: {_exception_message(snapshot.last_error)}",
            pause_label="Pause",
            mark_session_stopped=snapshot.session_is_running,
        )
    if snapshot.is_running:
        if snapshot.is_switching_targets:
            return ControllerStatusUpdate(status="Switching to answer", pause_label="Pause")
        if snapshot.is_stopping:
            return ControllerStatusUpdate(status="Ending", pause_label="Pause")
        if snapshot.is_paused:
            return ControllerStatusUpdate(status="Paused", pause_label="Resume")
        return ControllerStatusUpdate(status="Running", pause_label="Pause")
    if snapshot.current_status == "Ending" or snapshot.session_is_running:
        return ControllerStatusUpdate(
            status="Ended",
            pause_label="Pause",
            mark_session_stopped=True,
        )
    return ControllerStatusUpdate(status=snapshot.current_status, pause_label="Pause")


def _exception_message(exc: Exception) -> str:
    if isinstance(exc, KeyError) and exc.args:
        return str(exc.args[0])
    return str(exc)


def describe_question_error(_exc: Exception) -> str:
    return "Question error: question could not be answered safely."


def describe_question_result(result: QuestionSubmitResult) -> str:
    if result.demonstration_status == "queued" and result.entrypoint_id is not None:
        return f"Queued safe demo: {result.entrypoint_id}"
    if result.demonstration_status == "started" and result.entrypoint_id is not None:
        return f"Demonstrating: {result.entrypoint_id}"
    if result.answer_source == "presenter_meta":
        return "Answered only: presenter settings response; no demo was started"
    if result.answer_source == "qa":
        return "Answered only: matched text guidance; no demo was started"
    if result.answer_source == "no_match" or result.entrypoint_id is None:
        return "Answered only: no matching safe control"
    if result.entrypoint_id is not None and not result.can_operate:
        return f"Answered only: {result.entrypoint_id} is not safe to operate automatically"
    return f"Answered only: {result.entrypoint_id}"


def render_voice_label(voice: PresenterVoiceSettings) -> str:
    return _render_voice_label(voice)


def _check_controller_voice_readiness(
    profile: AppProfile,
    voice: PresenterVoiceSettings,
    *,
    checker: VoiceAssetChecker = check_voice_asset_availability,
) -> ControllerVoiceReadiness | None:
    try:
        validate_profile_voice(profile, voice)
    except ValueError as exc:
        return ControllerVoiceReadiness(
            status="FAIL",
            label="FAIL",
            detail=str(exc),
        )
    try:
        availability = checker(profile, voice)
    except Exception as exc:
        return ControllerVoiceReadiness(
            status="FAIL",
            label="FAIL",
            detail=f"voice asset check failed: {exc}",
        )
    if availability is None:
        return None
    return ControllerVoiceReadiness(
        status=availability.status,
        label=availability.status,
        detail=availability.detail,
    )


def _voice_readiness_failure_message(
    readiness: ControllerVoiceReadiness | None,
) -> str | None:
    if readiness is None or readiness.status == "OK":
        return None
    return readiness.detail or readiness.label


@dataclass
class _ControllerVoiceReadinessCache:
    profile: AppProfile
    checker: VoiceAssetChecker
    _cached_readiness_by_key: dict[
        tuple[str, str], ControllerVoiceReadiness | None
    ] = field(default_factory=dict, init=False)

    def get(self, voice: PresenterVoiceSettings) -> ControllerVoiceReadiness | None:
        key = self._key(voice)
        if key in self._cached_readiness_by_key:
            return self._cached_readiness_by_key[key]
        readiness = _check_controller_voice_readiness(
            self.profile,
            voice,
            checker=self.checker,
        )
        self._cached_readiness_by_key[key] = readiness
        return readiness

    def refresh(self, voice: PresenterVoiceSettings) -> ControllerVoiceReadiness | None:
        key = self._key(voice)
        readiness = _check_controller_voice_readiness(
            self.profile,
            voice,
            checker=self.checker,
        )
        self._cached_readiness_by_key[key] = readiness
        return readiness

    def _key(self, voice: PresenterVoiceSettings) -> tuple[str, str]:
        return (voice.language, voice.tone)


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
        voice: PresenterVoiceSettings | None = None,
    ) -> None:
        self._profile = profile
        self._target = _ControllerRunTarget(material_package, flow_id)
        self._control = control or DemoControl()
        self._runner = runner or run_material_demo
        self._window_runner = window_runner or run_existing_window_material_demo
        self._thread: threading.Thread | None = None
        self._last_error: Exception | None = None
        self._voice = voice or PresenterVoiceSettings()
        self._state_lock = threading.Lock()
        self._pending_target: _ControllerRunTarget | None = None
        self._pending_voice: PresenterVoiceSettings | None = None

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
        with self._state_lock:
            self._pending_target = None
            self._pending_voice = None
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
            return QuestionSubmitResult(
                answer_text=response.answer_text,
                entrypoint_id=response.entrypoint_id,
                can_operate=response.can_operate,
                answer_source=response.answer_source,
            )
        question_target = _target_with_question_flow(target, interrupt)
        if self.is_running and not self.is_stopping:
            self._control.enqueue_interrupt(interrupt)
            return QuestionSubmitResult(
                answer_text=response.answer_text,
                demonstration_status="queued",
                demonstration_message="I queued that for the next safe step.",
                entrypoint_id=response.entrypoint_id,
                can_operate=response.can_operate,
                answer_source=response.answer_source,
            )
        if self.is_running:
            return QuestionSubmitResult(
                answer_text=response.answer_text,
                demonstration_message="I answered in text because the current demo is ending.",
                entrypoint_id=response.entrypoint_id,
                can_operate=response.can_operate,
                answer_source=response.answer_source,
            )
        if self._start_target(question_target, voice):
            return QuestionSubmitResult(
                answer_text=response.answer_text,
                demonstration_status="started",
                demonstration_message="Demonstrating it now.",
                entrypoint_id=response.entrypoint_id,
                can_operate=response.can_operate,
                answer_source=response.answer_source,
            )
        return QuestionSubmitResult(
            answer_text=response.answer_text,
            demonstration_message="I answered in text because another demo is already running.",
            entrypoint_id=response.entrypoint_id,
            can_operate=response.can_operate,
            answer_source=response.answer_source,
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
    def is_stopping(self) -> bool:
        return self._control.is_stop_requested

    @property
    def is_switching_targets(self) -> bool:
        with self._state_lock:
            return self._pending_target is not None

    @property
    def last_error(self) -> Exception | None:
        return self._last_error

    def _start_target(self, target: _ControllerRunTarget, voice: PresenterVoiceSettings) -> bool:
        validate_profile_voice(self._profile, voice)
        if self._thread is not None and self._thread.is_alive():
            return False
        self._last_error = None
        self._control.reset()
        with self._state_lock:
            self._pending_target = None
            self._pending_voice = None
        self._thread = threading.Thread(
            target=self._run_demo_sequence,
            args=(target, voice),
            daemon=True,
        )
        self._thread.start()
        return True

    def _switch_to_target_after_current_step(
        self,
        target: _ControllerRunTarget,
        voice: PresenterVoiceSettings,
    ) -> None:
        with self._state_lock:
            self._pending_target = target
            self._pending_voice = voice
        self._control.request_stop()

    def _run_demo_sequence(
        self,
        target: _ControllerRunTarget,
        voice: PresenterVoiceSettings,
    ) -> None:
        current_target = target
        current_voice = voice
        while True:
            self._run_demo(current_target, current_voice)
            if self._last_error is not None:
                return
            next_run = self._pop_pending_target()
            if next_run is None:
                return
            current_target, current_voice = next_run
            self._control.reset()

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

    def _pop_pending_target(
        self,
    ) -> tuple[_ControllerRunTarget, PresenterVoiceSettings] | None:
        with self._state_lock:
            if self._pending_target is None:
                return None
            target = self._pending_target
            voice = self._pending_voice or self._voice
            self._pending_target = None
            self._pending_voice = None
            return target, voice


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
    package = target.material_package.with_demo_flow(flow)
    return _ControllerRunTarget(package, QUESTION_FLOW_ID, target.handle)


def _apply_button_state(button: Any, enabled: bool) -> bool:
    desired_state = "normal" if enabled else "disabled"
    if button.cget("state") == desired_state:
        return False
    button.configure(state=desired_state)
    return True


def _apply_operator_summary_wraplength(label: Any, width: int) -> bool:
    wraplength = max(1, int(width))
    try:
        current = int(label.cget("wraplength"))
    except (TypeError, ValueError):
        current = 0
    if current == wraplength:
        return False
    label.configure(wraplength=wraplength)
    return True


def _configure_operator_summary_label(label: Any) -> None:
    label.configure(anchor="nw", justify="left")

    def sync_wraplength(event: Any) -> None:
        _apply_operator_summary_wraplength(label, int(getattr(event, "width", 1)))

    label.bind("<Configure>", sync_wraplength)


def run_controller(
    profile: DesktopAppProfile,
    material_package: MaterialPackage,
    flow_id: str,
    *,
    voice: PresenterVoiceSettings | None = None,
    voice_asset_checker: VoiceAssetChecker = check_voice_asset_availability,
) -> None:
    import tkinter as tk

    voice_settings = voice or PresenterVoiceSettings()
    validate_profile_voice(profile, voice_settings)
    material_package.demo_flow_by_id(flow_id)
    desktop = WindowsDesktopDriver()
    session = ControllerSession()
    session.set_voice(voice_settings)
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
        voice=voice_settings,
    )
    root = tk.Tk()
    root.title("AiPresenter Controller")
    root.geometry("720x500")

    status = tk.StringVar(value="Ready")
    operator_summary = tk.StringVar(value="Target ready")
    pause_label = tk.StringVar(value="Pause")
    source = tk.StringVar(value="Material package")
    package_choice = tk.StringVar(value=material_package.app_id)
    flow_choice = tk.StringVar(value=flow_id)
    app_choice = tk.StringVar(value="")
    language = tk.StringVar(value=language_label(voice_settings.language))
    tone = tk.StringVar(value=tone_label(voice_settings.tone))
    question = tk.StringVar(value="")
    chat_turns: list[ChatTurn] = []
    last_question_outcome = ""
    language_values = dict(PRESENTER_LANGUAGE_CHOICES)
    tone_values = dict(PRESENTER_TONE_CHOICES)
    voice_readiness_cache = _ControllerVoiceReadinessCache(
        profile=profile,
        checker=voice_asset_checker,
    )

    def running_app_label(window: VisibleWindow) -> str:
        title = window.title.strip() or window.window_class or "Untitled"
        return f"{title} ({window.process}:{window.pid})"

    def selected_running_window() -> VisibleWindow | None:
        return scan_state.selected_window

    def current_voice() -> PresenterVoiceSettings:
        return PresenterVoiceSettings(
            language=language_values[language.get()],
            tone=tone_values[tone.get()],
        )

    def current_voice_readiness() -> ControllerVoiceReadiness | None:
        return voice_readiness_cache.refresh(current_voice())

    def source_mode() -> ControllerSourceMode:
        return "running_desktop_app" if source.get() == "Running desktop app" else "material_package"

    def refresh_operator_view() -> None:
        voice = current_voice()
        voice_readiness = voice_readiness_cache.get(voice)
        view_model = build_controller_operator_view_model(
            ControllerOperatorSnapshot(
                source_mode=source_mode(),
                material_package_id=material_package.app_id,
                material_flow_id=flow_id,
                running_app_label=app_choice.get(),
                has_running_app_selection=selected_running_window() is not None,
                has_scanned_running_app=scan_state.has_scanned_selection,
                scanned_package_id=scanned_package_id,
                scanned_flow_id=scanned_flow_id,
                voice=voice,
                voice_readiness=voice_readiness,
                run_status=status.get(),
                is_running=controller.is_running,
                is_stopping=controller.is_stopping,
                question_text=question.get(),
                last_question_outcome=last_question_outcome,
            )
        )
        operator_summary.set(render_operator_summary_text(view_model))
        _apply_button_state(start_button, view_model.buttons.start_enabled)
        _apply_button_state(pause_button, view_model.buttons.pause_enabled)
        _apply_button_state(end_button, view_model.buttons.end_enabled)
        _apply_button_state(refresh_button, view_model.buttons.refresh_enabled)
        _apply_button_state(scan_button, view_model.buttons.scan_enabled)
        _apply_button_state(submit_button, view_model.buttons.submit_enabled)

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
            refresh_operator_view()
            return
        package_choice.set(material_package.app_id)
        flow_choice.set(flow_id)
        if not controller.is_running:
            controller.set_target(material_package=material_package, flow_id=flow_id)
        refresh_operator_view()

    def choose_running_app(label: str) -> None:
        previously_scanned = scan_state.has_scanned_selection
        scan_state.choose(label)
        app_choice.set(label)
        if previously_scanned and not scan_state.has_scanned_selection:
            status.set("Selected running app needs scanning")
        sync_target_choice()
        refresh_operator_view()

    def refresh_running_windows() -> None:
        try:
            running_windows = list(catalog.list_running_apps())
        except Exception as exc:
            scan_state.replace_windows({})
            app_choice.set(NO_RUNNING_APPS_LABEL)
            status.set(f"App refresh error: {exc}")
            sync_target_choice()
            refresh_operator_view()
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
            refresh_operator_view()
            return

        for label in scan_state.window_by_label:
            menu.add_command(label=label, command=lambda value=label: choose_running_app(value))
        app_choice.set(scan_state.selected_label)
        if previously_scanned and not scan_state.has_scanned_selection:
            status.set("Selected running app needs scanning")
        sync_target_choice()
        refresh_operator_view()

    def scan_selected_app() -> None:
        nonlocal scanned_flow_id, scanned_package_id, scanned_handle, scanned_package
        selected = selected_running_window()
        if selected is None:
            status.set("Scan error: select a running app first")
            refresh_operator_view()
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
        refresh_operator_view()

    def start() -> None:
        try:
            voice = current_voice()
            validate_profile_voice(profile, voice)
            controller.set_voice(voice)
            if source.get() == "Running desktop app":
                if (
                    not scan_state.has_scanned_selection
                    or scanned_package is None
                    or scanned_handle is None
                    or not scanned_flow_id
                ):
                    status.set(RUNNING_APP_SCAN_REQUIRED_MESSAGE)
                    refresh_operator_view()
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
            readiness = current_voice_readiness()
            failure = _voice_readiness_failure_message(readiness)
            if failure is not None:
                status.set(f"Start error: {failure}")
                refresh_operator_view()
                return
            session.mark_running()
            controller.start()
            status.set("Running")
            pause_label.set("Pause")
        except Exception as exc:
            session.mark_stopped()
            status.set(f"Start error: {exc}")
        refresh_operator_view()

    def pause_or_resume() -> None:
        paused = controller.pause_or_resume()
        status.set("Paused" if paused else "Running")
        pause_label.set("Resume" if paused else "Pause")
        refresh_operator_view()

    def end() -> None:
        controller.end()
        session.mark_stopped()
        status.set("Ending")
        pause_label.set("Pause")
        refresh_operator_view()

    def append_chat(speaker: str, message: str) -> None:
        chat_turns.append(ChatTurn(speaker, message))
        chat_history.configure(state="normal")
        chat_history.delete("1.0", "end")
        chat_history.insert("end", format_chat_turns(chat_turns))
        chat_history.configure(state="disabled")
        chat_history.see("end")

    def submit_question() -> None:
        nonlocal last_question_outcome
        text = question.get().strip()
        if not text:
            refresh_operator_view()
            return
        append_chat("You", text)
        question.set("")
        try:
            voice = current_voice()
            controller.set_voice(voice)
            if source.get() == "Running desktop app":
                if not scan_state.has_scanned_selection:
                    append_chat("AiPresenter", RUNNING_APP_SCAN_REQUIRED_MESSAGE)
                    last_question_outcome = RUNNING_APP_SCAN_REQUIRED_MESSAGE
                    status.set(RUNNING_APP_SCAN_REQUIRED_MESSAGE)
                    refresh_operator_view()
                    return
                session.set_voice(voice)
            elif not controller.is_running:
                controller.set_target(material_package=material_package, flow_id=flow_id)
            readiness = current_voice_readiness()
            failure = _voice_readiness_failure_message(readiness)
            if failure is not None:
                append_chat("AiPresenter", f"Question error: {failure}")
                last_question_outcome = f"Question error: {failure}"
                status.set(last_question_outcome)
                refresh_operator_view()
                return
            result = controller.submit_question(text)
            append_chat("AiPresenter", result.answer_text)
            last_question_outcome = describe_question_result(result)
            status.set(last_question_outcome)
            if result.demonstration_message:
                append_chat("AiPresenter", result.demonstration_message)
            if result.demonstration_status == "started":
                session.mark_running()
        except Exception as exc:
            last_question_outcome = describe_question_error(exc)
            append_chat("AiPresenter", last_question_outcome)
        refresh_operator_view()

    def refresh_status() -> None:
        update = resolve_controller_status(
            ControllerStatusSnapshot(
                current_status=status.get(),
                last_error=controller.last_error,
                is_running=controller.is_running,
                is_paused=controller.is_paused,
                is_stopping=controller.is_stopping,
                is_switching_targets=controller.is_switching_targets,
                session_is_running=session.is_running,
            )
        )
        application = plan_controller_status_application(
            ControllerAppliedStatusState(status=status.get(), pause_label=pause_label.get()),
            update,
        )
        if application.mark_session_stopped:
            session.mark_stopped()
        if application.status_changed:
            status.set(application.state.status)
        if application.pause_label_changed:
            pause_label.set(application.state.pause_label)
        if application.refresh_operator_view:
            refresh_operator_view()
        root.after(500, refresh_status)

    frame = tk.Frame(root, padx=16, pady=16)
    frame.pack(fill="both", expand=True)
    tk.Label(frame, textvariable=status, anchor="w").pack(fill="x", pady=(0, 12))
    operator_summary_label = tk.Label(frame, textvariable=operator_summary)
    _configure_operator_summary_label(operator_summary_label)
    operator_summary_label.pack(fill="x", pady=(0, 12))

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
    refresh_button = tk.Button(
        target_frame,
        text="Refresh",
        command=refresh_running_windows,
        width=10,
    )
    refresh_button.pack(
        side="left",
        padx=(8, 0),
    )
    scan_button = tk.Button(target_frame, text="Scan", command=scan_selected_app, width=8)
    scan_button.pack(
        side="left",
        padx=(8, 0),
    )

    button_row = tk.Frame(frame)
    button_row.pack(fill="x")
    start_button = tk.Button(button_row, text="Start", command=start, width=10)
    start_button.pack(side="left", padx=(0, 8))
    pause_button = tk.Button(button_row, textvariable=pause_label, command=pause_or_resume, width=10)
    pause_button.pack(
        side="left",
        padx=(0, 8),
    )
    end_button = tk.Button(button_row, text="End", command=end, width=10)
    end_button.pack(side="left")

    voice_row = tk.Frame(frame)
    voice_row.pack(fill="x", pady=(24, 12))
    tk.OptionMenu(
        voice_row,
        language,
        *(label for label, _ in PRESENTER_LANGUAGE_CHOICES),
        command=lambda *_args: refresh_operator_view(),
    ).pack(side="left", padx=(0, 8))
    tk.OptionMenu(
        voice_row,
        tone,
        *(label for label, _ in PRESENTER_TONE_CHOICES),
        command=lambda *_args: refresh_operator_view(),
    ).pack(side="left")

    question_row = tk.Frame(frame)
    question_row.pack(fill="x", pady=(12, 8))
    question_entry = tk.Entry(question_row, textvariable=question)
    question_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
    question_entry.bind("<Return>", lambda _event: submit_question())
    question.trace_add("write", lambda *_args: refresh_operator_view())
    submit_button = tk.Button(question_row, text="Submit", command=submit_question, width=10)
    submit_button.pack(side="left")
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
