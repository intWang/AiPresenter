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
