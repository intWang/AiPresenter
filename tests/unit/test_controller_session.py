from pathlib import Path

import pytest

from ai_presenter.config.loader import load_profile
from ai_presenter.config.models import DesktopAppProfile
from ai_presenter.desktop.base import VisibleControl, VisibleWindow
from ai_presenter.packages.loader import load_material_package
from ai_presenter.runtime.session import ControllerSession
from ai_presenter.runtime.session import MaterialPackageTarget
from ai_presenter.runtime.session import RunningAppTarget
from ai_presenter.runtime.voice import PresenterVoiceSettings


def load_desktop_profile() -> DesktopAppProfile:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))
    assert isinstance(profile, DesktopAppProfile)
    return profile


def test_session_blocks_target_change_while_running() -> None:
    session = ControllerSession()
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    target = MaterialPackageTarget(
        profile=load_desktop_profile(),
        package=package,
        flow_id="meeting-control-map-demo",
    )
    session.select_target(target)
    session.mark_running_for_test()

    with pytest.raises(RuntimeError, match="running"):
        session.select_target(target)


def test_session_scans_running_app_into_temporary_package() -> None:
    window = VisibleWindow("Demo", 10, "DemoWindow", "Demo App", (0, 0, 800, 600))
    controls = (VisibleControl("Settings", "Button", (10, 10, 120, 40)),)
    session = ControllerSession()

    package = session.scan_running_app(RunningAppTarget(window=window), controls)

    assert package.app_id == "temp.demo.10"
    assert package.demo_flows[0].id == "temp-demo"


def test_session_answers_question_with_active_voice_settings() -> None:
    session = ControllerSession()
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    target = MaterialPackageTarget(
        profile=load_desktop_profile(),
        package=package,
        flow_id="meeting-control-map-demo",
    )
    session.select_target(target)
    session.set_voice(PresenterVoiceSettings(language="zh", tone="conversational"))

    response = session.answer_question("chat")

    assert "聊天" in response.answer_text
