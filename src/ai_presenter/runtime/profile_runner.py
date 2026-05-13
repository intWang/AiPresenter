import logging

from ai_presenter.config.models import DesktopAppProfile
from ai_presenter.desktop.base import DesktopDriver, WindowHandle

logger = logging.getLogger("ai_presenter.runtime.profile_runner")


class ProfileRunner:
    def __init__(self, profile: DesktopAppProfile, desktop: DesktopDriver) -> None:
        self._profile = profile
        self._desktop = desktop

    def launch_and_bind(self) -> WindowHandle:
        logger.info("profile_launch_started profile=%s", self._profile.id)
        for step in self._profile.launch.steps:
            logger.info("launch_step_started action=%s target=%s", step.action, step.target)
            if step.action == "focusWindow":
                process = step.match.get("process")
                if not isinstance(process, str) or not process.strip():
                    raise ValueError("focusWindow requires match.process")
                self._desktop.focus_window(process.strip())
            elif step.action == "clickTab":
                if step.target is None or not step.target.strip():
                    raise ValueError("clickTab requires target")
                self._desktop.click_tab(step.target.strip())
            elif step.action == "clickButton":
                if step.target is None or not step.target.strip():
                    raise ValueError("clickButton requires target")
                self._desktop.click_button(step.target.strip())
            else:
                raise ValueError(f"Unsupported launch action: {step.action}")
            logger.info("launch_step_completed action=%s", step.action)

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
