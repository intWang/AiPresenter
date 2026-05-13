from pathlib import Path

import pytest

from ai_presenter.config.loader import load_profile
from ai_presenter.config.models import DesktopAppProfile, LaunchStep
from ai_presenter.desktop.base import DesktopDriver, WindowHandle
from ai_presenter.runtime.profile_runner import ProfileRunner


class FakeDesktopDriver(DesktopDriver):
    def __init__(self) -> None:
        self.actions: list[str] = []

    def focus_window(self, process: str) -> None:
        self.actions.append(f"focus:{process}")

    def click_tab(self, target: str) -> None:
        self.actions.append(f"tab:{target}")

    def click_button(self, target: str) -> None:
        self.actions.append(f"button:{target}")

    def wait_for_window(self, process: str, window_class: str, timeout_ms: int) -> WindowHandle:
        self.actions.append(f"wait:{process}:{window_class}:{timeout_ms}")
        return WindowHandle(process, 1234, window_class, "RingCentral Video")


def load_desktop_profile() -> DesktopAppProfile:
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))
    assert isinstance(profile, DesktopAppProfile)
    return profile


def profile_with_steps(steps: list[LaunchStep]) -> DesktopAppProfile:
    profile = load_desktop_profile()
    return profile.model_copy(update={"launch": profile.launch.model_copy(update={"steps": steps})})


def test_profile_runner_executes_launch_steps_and_binds_window() -> None:
    profile = load_desktop_profile()
    desktop = FakeDesktopDriver()

    handle = ProfileRunner(profile, desktop).launch_and_bind()

    assert handle.process == "RingCentralVideo"
    assert desktop.actions == [
        "focus:RingCentralDevelop",
        "tab:Video",
        "button:Start",
        "wait:RingCentralVideo:RingCentralVideoClass:30000",
    ]


def test_profile_runner_rejects_unsupported_action_before_waiting() -> None:
    profile = profile_with_steps([LaunchStep(action="openDoor")])
    desktop = FakeDesktopDriver()

    with pytest.raises(ValueError, match="Unsupported launch action: openDoor"):
        ProfileRunner(profile, desktop).launch_and_bind()

    assert desktop.actions == []


def test_profile_runner_rejects_missing_match_process_before_waiting() -> None:
    profile = profile_with_steps([LaunchStep(action="focusWindow")])
    desktop = FakeDesktopDriver()

    with pytest.raises(ValueError, match="focusWindow requires match.process"):
        ProfileRunner(profile, desktop).launch_and_bind()

    assert desktop.actions == []


def test_profile_runner_rejects_blank_match_process_before_dispatch() -> None:
    profile = profile_with_steps([LaunchStep(action="focusWindow", match={"process": "   "})])
    desktop = FakeDesktopDriver()

    with pytest.raises(ValueError, match="focusWindow requires match.process"):
        ProfileRunner(profile, desktop).launch_and_bind()

    assert desktop.actions == []


@pytest.mark.parametrize(
    ("action", "message"),
    [
        ("clickTab", "clickTab requires target"),
        ("clickButton", "clickButton requires target"),
    ],
)
def test_profile_runner_rejects_missing_target_before_waiting(
    action: str,
    message: str,
) -> None:
    profile = profile_with_steps([LaunchStep(action=action)])
    desktop = FakeDesktopDriver()

    with pytest.raises(ValueError, match=message):
        ProfileRunner(profile, desktop).launch_and_bind()

    assert desktop.actions == []


@pytest.mark.parametrize(
    ("action", "message"),
    [
        ("clickTab", "clickTab requires target"),
        ("clickButton", "clickButton requires target"),
    ],
)
def test_profile_runner_rejects_blank_target_before_dispatch(
    action: str,
    message: str,
) -> None:
    step = LaunchStep.model_construct(action=action, target="   ", match={})
    profile = profile_with_steps([step])
    desktop = FakeDesktopDriver()

    with pytest.raises(ValueError, match=message):
        ProfileRunner(profile, desktop).launch_and_bind()

    assert desktop.actions == []


def test_profile_runner_stops_after_first_validation_failure() -> None:
    profile = profile_with_steps(
        [
            LaunchStep(action="clickButton", target="Join"),
            LaunchStep(action="focusWindow"),
        ]
    )
    desktop = FakeDesktopDriver()

    with pytest.raises(ValueError, match="focusWindow requires match.process"):
        ProfileRunner(profile, desktop).launch_and_bind()

    assert desktop.actions == ["button:Join"]
