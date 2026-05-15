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


def load_desktop_profile(*, speech: str | None = None) -> DesktopAppProfile:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))
    assert isinstance(profile, DesktopAppProfile)
    if speech is not None:
        profile.providers.speech = speech
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
        profile=load_desktop_profile(speech="windows-sapi-zh"),
        package=package,
        flow_id="meeting-control-map-demo",
    )
    session.set_voice(PresenterVoiceSettings(language="zh", tone="conversational"))
    session.select_target(target)

    response = session.answer_question("chat")

    assert "聊天" in response.answer_text


def test_session_rejects_incompatible_voice_without_changing_current_voice() -> None:
    session = ControllerSession()
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    target = MaterialPackageTarget(
        profile=load_desktop_profile(),
        package=package,
        flow_id="meeting-control-map-demo",
    )
    session.select_target(target)

    with pytest.raises(ValueError, match="windows-sapi-zh"):
        session.set_voice(PresenterVoiceSettings(language="zh"))

    response = session.answer_question("chat")

    assert response.answer_text.startswith("Chat panel")


def test_session_rejects_incompatible_target_without_changing_current_state() -> None:
    session = ControllerSession()
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    compatible_target = MaterialPackageTarget(
        profile=load_desktop_profile(speech="windows-sapi-zh"),
        package=package,
        flow_id="meeting-control-map-demo",
    )
    incompatible_target = MaterialPackageTarget(
        profile=load_desktop_profile(),
        package=package,
        flow_id="meeting-control-map-demo",
    )
    session.set_voice(PresenterVoiceSettings(language="zh", tone="conversational"))
    session.select_target(compatible_target)

    with pytest.raises(ValueError, match="windows-sapi-zh"):
        session.select_target(incompatible_target)

    with pytest.raises(ValueError, match="English voice"):
        session.set_voice(PresenterVoiceSettings(language="en"))
    response = session.answer_question("chat")

    assert "聊天" in response.answer_text
