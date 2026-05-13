from ai_presenter.config.models import AppProfile, DesktopAppProfile
from ai_presenter.desktop.base import DesktopDriver, WindowHandle


class ProfileRunner:
    def __init__(self, profile: AppProfile, desktop: DesktopDriver) -> None:
        self._profile = profile
        self._desktop = desktop

    def launch_and_bind(self) -> WindowHandle:
        if not isinstance(self._profile, DesktopAppProfile):
            raise ValueError("ProfileRunner only supports desktop profiles")

        profile = self._profile
        for step in profile.launch.steps:
            if step.action == "focusWindow":
                process = step.match.get("process")
                if not isinstance(process, str):
                    raise ValueError("focusWindow requires match.process")
                self._desktop.focus_window(process)
            elif step.action == "clickTab":
                if step.target is None:
                    raise ValueError("clickTab requires target")
                self._desktop.click_tab(step.target)
            elif step.action == "clickButton":
                if step.target is None:
                    raise ValueError("clickButton requires target")
                self._desktop.click_button(step.target)
            else:
                raise ValueError(f"Unsupported launch action: {step.action}")

        return self._desktop.wait_for_window(
            profile.bind.process,
            profile.bind.window_class,
            profile.bind.timeout_ms,
        )
