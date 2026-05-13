from pathlib import Path

import pytest

from ai_presenter.config.loader import load_profile
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


def test_profile_runner_executes_launch_steps_and_binds_window() -> None:
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))
    desktop = FakeDesktopDriver()

    handle = ProfileRunner(profile, desktop).launch_and_bind()

    assert handle.process == "RingCentralVideo"
    assert desktop.actions == [
        "focus:RingCentralDevelop",
        "tab:Video",
        "button:Start",
        "wait:RingCentralVideo:RingCentralVideoClass:30000",
    ]


def test_profile_runner_rejects_browser_profiles(tmp_path: Path) -> None:
    profile_path = tmp_path / "browser.yaml"
    profile_path.write_text(
        """
id: browser-demo
type: browser
launch:
  url: https://example.test/meeting
bind:
  title: Example Meeting
observe:
  intervalMs: 1000
  sources: [screenshot]
events: []
narration:
  style: concise_presenter
  maxSentences: 2
  minSecondsBetweenUtterances: 4
  repeatCooldownSeconds: 30
  confidenceThreshold: 0.75
  forbidSharedScreenInterpretation: true
audio:
  output: speaker
providers:
  vision: fake
  narration: fake
  speech: fake
""",
        encoding="utf-8",
    )
    profile = load_profile(profile_path)

    with pytest.raises(ValueError, match="ProfileRunner only supports desktop profiles"):
        ProfileRunner(profile, FakeDesktopDriver()).launch_and_bind()
