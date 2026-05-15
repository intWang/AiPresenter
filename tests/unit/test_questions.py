from pathlib import Path

from ai_presenter.packages.loader import load_material_package
from ai_presenter.runtime.questions import answer_question
from ai_presenter.runtime.voice import PresenterVoiceSettings


def test_answers_package_qa_match_in_english() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="How do I protect my real background?",
        voice=PresenterVoiceSettings(language="en", tone="professional"),
    )

    assert response.answer_text.startswith("Open Settings")
    assert response.entrypoint_id == "ringcentral.video.settings.background"


def test_answers_entrypoint_match_in_chinese() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="chat",
        voice=PresenterVoiceSettings(language="zh", tone="conversational"),
    )

    assert "聊天" in response.answer_text
    assert response.entrypoint_id == "ringcentral.video.toolbar.chat"


def test_risky_entrypoint_answer_is_not_operable() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="leave meeting",
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id == "ringcentral.video.toolbar.leave"
    assert response.can_operate is False


def test_open_chat_matches_chat_entrypoint() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="open chat",
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id == "ringcentral.video.toolbar.chat"


def test_notes_matches_notes_entrypoint() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="notes",
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id == "ringcentral.video.more.notes"


def test_participants_matches_participants_entrypoint() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="participants",
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id == "ringcentral.video.toolbar.participants"


def test_invite_people_prefers_invite_entrypoint() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="invite people",
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id == "ringcentral.video.toolbar.invite"
    assert response.entrypoint_id not in {
        "ringcentral.video.toolbar.leave",
        "ringcentral.video.toolbar.participants",
    }


def test_bring_people_into_meeting_matches_invite_package_qa() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="how do i bring people into the meeting",
        voice=PresenterVoiceSettings(),
    )

    assert response.answer_text.startswith("Use Invite")
    assert response.entrypoint_id == "ringcentral.video.toolbar.invite"
    assert response.entrypoint_id != "ringcentral.video.toolbar.leave"


def test_share_screen_answer_is_not_operable() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="share screen",
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id == "ringcentral.video.toolbar.share"
    assert response.can_operate is False


def test_recording_answer_is_not_operable() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="recording",
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id == "ringcentral.video.more.recording"
    assert response.can_operate is False


def test_no_match_fallback_is_not_operable() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="quantum waffle",
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id is None
    assert response.can_operate is False


def test_settings_prefers_settings_entrypoint() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="settings",
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id in {
        "ringcentral.video.more.settings",
        "ringcentral.video.settings.background",
        "ringcentral.video.settings.video",
    }
    assert response.entrypoint_id != "ringcentral.video.toolbar.audio-menu"
