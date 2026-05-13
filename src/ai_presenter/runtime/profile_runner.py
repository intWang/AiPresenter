import logging
from dataclasses import dataclass

from ai_presenter.config.models import DesktopAppProfile
from ai_presenter.config.models import LaunchStep
from ai_presenter.desktop.base import DesktopDriver, WindowHandle

logger = logging.getLogger("ai_presenter.runtime.profile_runner")


@dataclass(frozen=True)
class LaunchCommand:
    action: str
    target: str


class ProfileRunner:
    def __init__(self, profile: DesktopAppProfile, desktop: DesktopDriver) -> None:
        self._profile = profile
        self._desktop = desktop

    def launch_and_bind(self) -> WindowHandle:
        launch_commands = self._validate_launch_plan()
        logger.info("profile_launch_started profile=%s", self._profile.id)
        for command in launch_commands:
            logger.info("launch_step_started action=%s target=%s", command.action, command.target)
            if command.action == "focusWindow":
                self._desktop.focus_window(command.target)
                if self._profile.launch.require_already_logged_in:
                    self._ensure_logged_in()
            elif command.action == "clickTab":
                self._desktop.click_tab(command.target)
            elif command.action == "clickButton":
                self._desktop.click_button(command.target)
            else:
                raise ValueError(f"Unsupported launch action: {command.action}")
            logger.info("launch_step_completed action=%s", command.action)

        handle = self._desktop.wait_for_window(
            self._profile.bind.process,
            self._profile.bind.window_class,
            self._profile.bind.timeout_ms,
        )
        logger.info(
            "window_bound process=%s pid=%s class=%s",
            handle.process,
            handle.pid,
            handle.window_class,
        )
        return handle

    def _validate_launch_plan(self) -> list[LaunchCommand]:
        app_process = self._profile.launch.app_process.strip()
        commands: list[LaunchCommand] = []
        saw_app_focus = False

        for step in self._profile.launch.steps:
            command = self._validate_launch_step(step)
            if command.action == "focusWindow":
                if _process_key(command.target) != _process_key(app_process):
                    raise ValueError("focusWindow match.process must match launch.appProcess")
                saw_app_focus = True
            commands.append(command)

        if self._profile.launch.require_already_logged_in and not saw_app_focus:
            raise ValueError("requireAlreadyLoggedIn requires focusWindow for launch.appProcess")

        return commands

    def _validate_launch_step(self, step: LaunchStep) -> LaunchCommand:
        if step.action == "focusWindow":
            process = step.match.get("process")
            if not isinstance(process, str) or not process.strip():
                raise ValueError("focusWindow requires match.process")
            return LaunchCommand(step.action, process.strip())

        if step.action == "clickTab":
            if step.target is None or not step.target.strip():
                raise ValueError("clickTab requires target")
            return LaunchCommand(step.action, step.target.strip())

        if step.action == "clickButton":
            if step.target is None or not step.target.strip():
                raise ValueError("clickButton requires target")
            return LaunchCommand(step.action, step.target.strip())

        raise ValueError(f"Unsupported launch action: {step.action}")

    def _ensure_logged_in(self) -> None:
        text = self._desktop.read_focused_window_text()
        if _contains_logged_out_marker(text):
            raise RuntimeError(
                "launch requires an already logged-in app, but the focused window appears signed out"
            )


def _process_key(process: str) -> str:
    normalized = process.strip().casefold()
    if normalized.endswith(".exe"):
        return normalized[:-4]
    return normalized


def _contains_logged_out_marker(text: tuple[str, ...]) -> bool:
    markers = ("sign in", "signin", "log in", "login")
    return any(marker in item.casefold() for item in text for marker in markers)
