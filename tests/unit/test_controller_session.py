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


def test_session_answer_after_running_app_scan() -> None:
    session = ControllerSession()
    window = VisibleWindow("Demo", 10, "DemoWindow", "Demo App", (0, 0, 800, 600))
    controls = (VisibleControl("Settings", "Button", (10, 10, 120, 40)),)

    session.scan_running_app(RunningAppTarget(window=window), controls)
    response = session.answer_question("settings")

    assert response.entrypoint_id == "temp.demo.10.settings"
    assert response.can_operate is True


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


def test_session_routes_chinese_voice_for_english_sapi_profile() -> None:
    session = ControllerSession()
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    target = MaterialPackageTarget(
        profile=load_desktop_profile(),
        package=package,
        flow_id="meeting-control-map-demo",
    )
    session.select_target(target)

    session.set_voice(PresenterVoiceSettings(language="zh"))

    response = session.answer_question("chat")

    assert response.answer_text


def test_session_routes_language_when_target_changes_between_sapi_profiles() -> None:
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

    session.select_target(incompatible_target)

    session.set_voice(PresenterVoiceSettings(language="en"))
    response = session.answer_question("chat")

    assert response.answer_text.startswith("Chat panel")


def test_session_creates_interrupt_step_for_safe_answer() -> None:
    session = ControllerSession()
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    target = MaterialPackageTarget(
        profile=load_desktop_profile(),
        package=package,
        flow_id="meeting-control-map-demo",
    )
    session.select_target(target)

    response = session.answer_question("chat")
    interrupt = session.create_interrupt_step(response)

    assert interrupt is not None
    assert interrupt.action.entrypoint_id == "ringcentral.video.toolbar.chat"
    assert interrupt.narration.text == response.answer_text


def test_session_does_not_create_interrupt_for_risky_answer() -> None:
    session = ControllerSession()
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    session.select_target(
        MaterialPackageTarget(
            profile=load_desktop_profile(),
            package=package,
            flow_id="meeting-control-map-demo",
        )
    )

    response = session.answer_question("leave meeting")

    assert session.create_interrupt_step(response) is None


@pytest.mark.parametrize(
    ("question", "voice"),
    [
        ("Please be brief", PresenterVoiceSettings(language="en")),
        ("\u8bf7\u7528\u4e2d\u6587\u56de\u7b54", PresenterVoiceSettings(language="zh")),
    ],
)
def test_session_does_not_create_interrupt_for_presenter_meta_answer(
    question: str,
    voice: PresenterVoiceSettings,
) -> None:
    session = ControllerSession()
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    session.select_target(
        MaterialPackageTarget(
            profile=load_desktop_profile(),
            package=package,
            flow_id="meeting-control-map-demo",
        )
    )
    session.set_voice(voice)

    response = session.answer_question(question)

    assert response.entrypoint_id is None
    assert response.can_operate is False
    assert response.answer_text.startswith("Presenter settings:")
    assert session.create_interrupt_step(response) is None


@pytest.mark.parametrize(
    ("question", "voice", "expected_entrypoint_id", "expected_answer"),
    [
        (
            "Please be brief and open chat",
            PresenterVoiceSettings(language="en"),
            "ringcentral.video.toolbar.chat",
            "Chat panel:",
        ),
        (
            "\u8bf7\u7528\u4e2d\u6587\u56de\u7b54\uff0c\u804a\u5929\u5728\u54ea\u91cc",
            PresenterVoiceSettings(language="zh"),
            "ringcentral.video.toolbar.chat",
            "\u804a\u5929",
        ),
        (
            "Please be brief and show network quality",
            PresenterVoiceSettings(language="en"),
            "ringcentral.video.top.network-quality",
            "Network quality:",
        ),
        (
            "Please be brief and open participants panel",
            PresenterVoiceSettings(language="en"),
            "ringcentral.video.toolbar.participants",
            "Participants panel:",
        ),
    ],
)
def test_session_creates_interrupt_for_safe_mixed_presenter_meta_answer(
    question: str,
    voice: PresenterVoiceSettings,
    expected_entrypoint_id: str,
    expected_answer: str,
) -> None:
    session = ControllerSession()
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    session.select_target(
        MaterialPackageTarget(
            profile=load_desktop_profile(),
            package=package,
            flow_id="meeting-control-map-demo",
        )
    )
    session.set_voice(voice)

    response = session.answer_question(question)
    interrupt = session.create_interrupt_step(response)

    assert response.entrypoint_id == expected_entrypoint_id
    assert response.can_operate is True
    assert expected_answer in response.answer_text
    assert not response.answer_text.startswith("Presenter settings:")
    assert interrupt is not None
    assert interrupt.action.entrypoint_id == expected_entrypoint_id
    assert interrupt.narration.text == response.answer_text


@pytest.mark.parametrize(
    ("question", "voice", "expected_entrypoint_id", "expected_answer"),
    [
        (
            "Please be brief and read meeting information aloud",
            PresenterVoiceSettings(language="en"),
            "ringcentral.video.top.meeting-info",
            "Meeting IDs and links are private meeting details",
        ),
        (
            "\u8bf7\u7b80\u6d01\u4e00\u70b9\uff0c\u590d\u5236\u4f1a\u8bae\u94fe\u63a5",
            PresenterVoiceSettings(language="zh"),
            "ringcentral.video.top.meeting-info",
            "\u79c1\u4eba\u4f1a\u8bae\u8be6\u60c5",
        ),
        (
            "Please be brief and open notes and transcript",
            PresenterVoiceSettings(language="en"),
            "ringcentral.video.more.notes",
            "Starting notes can change",
        ),
        (
            "Please be brief and show participants",
            PresenterVoiceSettings(language="en"),
            None,
            "participant names",
        ),
    ],
)
def test_session_does_not_create_interrupt_for_sensitive_mixed_presenter_meta_answer(
    question: str,
    voice: PresenterVoiceSettings,
    expected_entrypoint_id: str,
    expected_answer: str,
) -> None:
    session = ControllerSession()
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    session.select_target(
        MaterialPackageTarget(
            profile=load_desktop_profile(),
            package=package,
            flow_id="meeting-control-map-demo",
        )
    )
    session.set_voice(voice)

    response = session.answer_question(question)

    assert response.entrypoint_id == expected_entrypoint_id
    assert response.can_operate is False
    assert expected_answer in response.answer_text
    assert not response.answer_text.startswith("Presenter settings:")
    assert session.create_interrupt_step(response) is None


def test_session_does_not_create_interrupt_for_notes_question_policy() -> None:
    session = ControllerSession()
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    session.select_target(
        MaterialPackageTarget(
            profile=load_desktop_profile(),
            package=package,
            flow_id="meeting-control-map-demo",
        )
    )

    response = session.answer_question("Where are Notes and transcript")

    assert response.entrypoint_id == "ringcentral.video.more.notes"
    assert response.can_operate is False
    assert session.create_interrupt_step(response) is None
