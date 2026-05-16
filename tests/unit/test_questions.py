import logging
from pathlib import Path

import pytest

from ai_presenter.packages.loader import load_material_package
from ai_presenter.packages.models import MaterialPackage
from ai_presenter.runtime import questions as questions_module
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


def test_chinese_chat_question_matches_chat_entrypoint() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="聊天在哪里",
        voice=PresenterVoiceSettings(language="zh", tone="professional"),
    )

    assert response.entrypoint_id == "ringcentral.video.toolbar.chat"
    assert response.can_operate is True


def test_chinese_invite_question_matches_but_stays_non_operable() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="怎么邀请别人",
        voice=PresenterVoiceSettings(language="zh"),
    )

    assert response.entrypoint_id == "ringcentral.video.toolbar.invite"
    assert response.can_operate is False


def test_chinese_share_and_leave_questions_remain_text_only() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    share = answer_question(
        package=package,
        question="怎么共享屏幕",
        voice=PresenterVoiceSettings(language="zh"),
    )
    leave = answer_question(
        package=package,
        question="怎么离开会议",
        voice=PresenterVoiceSettings(language="zh"),
    )

    assert share.entrypoint_id == "ringcentral.video.toolbar.share"
    assert share.can_operate is False
    assert leave.entrypoint_id == "ringcentral.video.toolbar.leave"
    assert leave.can_operate is False


def test_chinese_background_question_matches_background_settings() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="怎么设置背景",
        voice=PresenterVoiceSettings(language="zh"),
    )

    assert response.entrypoint_id in {
        "ringcentral.video.settings.background",
        "ringcentral.video.more.background",
    }


def test_mojibake_chinese_input_is_not_treated_as_supported_alias() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="èŠå¤©",
        voice=PresenterVoiceSettings(language="zh"),
    )

    assert response.entrypoint_id is None
    assert response.can_operate is False


def test_package_owned_alias_matches_without_legacy_alias_table() -> None:
    package = MaterialPackage.model_validate(
        {
            "appId": "demo",
            "appName": "Demo",
            "version": 1,
            "profileIds": ["demo-profile"],
            "operationEntrypoints": [
                {
                    "id": "demo.panel",
                    "title": "Panel",
                    "area": "Main",
                    "purpose": "Open the demo panel.",
                    "questionAliases": {"zh": ["自定义面板"]},
                    "openSteps": [
                        {
                            "action": "clickWindowControl",
                            "target": "Panel",
                            "match": {"controlType": "button"},
                        }
                    ],
                }
            ],
            "demoFlows": [],
            "manualControls": [],
        }
    )

    response = answer_question(
        package=package,
        question="自定义面板在哪里",
        voice=PresenterVoiceSettings(language="zh"),
    )

    assert response.entrypoint_id == "demo.panel"
    assert response.can_operate is True


def test_package_owned_alias_takes_precedence_over_legacy_alias_table() -> None:
    package = MaterialPackage.model_validate(
        {
            "appId": "demo",
            "appName": "Demo",
            "version": 1,
            "profileIds": ["demo-profile"],
            "operationEntrypoints": [
                {
                    "id": "ringcentral.video.toolbar.chat",
                    "title": "Legacy Chat",
                    "area": "Main",
                    "purpose": "Open the legacy chat panel.",
                    "openSteps": [
                        {
                            "action": "clickWindowControl",
                            "target": "Chat",
                            "match": {"controlType": "button"},
                        }
                    ],
                },
                {
                    "id": "demo.package.override",
                    "title": "Package Override",
                    "area": "Main",
                    "purpose": "Open the package-owned answer panel.",
                    "questionAliases": {"zh": ["聊天"]},
                    "openSteps": [
                        {
                            "action": "clickWindowControl",
                            "target": "Override",
                            "match": {"controlType": "button"},
                        }
                    ],
                },
            ],
            "demoFlows": [],
            "manualControls": [],
        }
    )

    response = answer_question(
        package=package,
        question="聊天在哪里",
        voice=PresenterVoiceSettings(language="zh"),
    )

    assert response.entrypoint_id == "demo.package.override"


def test_longest_package_owned_alias_wins() -> None:
    package = MaterialPackage.model_validate(
        {
            "appId": "demo",
            "appName": "Demo",
            "version": 1,
            "profileIds": ["demo-profile"],
            "operationEntrypoints": [
                {
                    "id": "demo.short",
                    "title": "Short",
                    "area": "Main",
                    "purpose": "Open the short match panel.",
                    "questionAliases": {"zh": ["共享"]},
                    "openSteps": [
                        {
                            "action": "clickWindowControl",
                            "target": "Short",
                            "match": {"controlType": "button"},
                        }
                    ],
                },
                {
                    "id": "demo.long",
                    "title": "Long",
                    "area": "Main",
                    "purpose": "Open the long match panel.",
                    "questionAliases": {"zh": ["共享屏幕"]},
                    "openSteps": [
                        {
                            "action": "clickWindowControl",
                            "target": "Long",
                            "match": {"controlType": "button"},
                        }
                    ],
                },
            ],
            "demoFlows": [],
            "manualControls": [],
        }
    )

    response = answer_question(
        package=package,
        question="怎么共享屏幕",
        voice=PresenterVoiceSettings(language="zh"),
    )

    assert response.entrypoint_id == "demo.long"


def test_package_owned_equal_length_aliases_keep_source_order() -> None:
    package = MaterialPackage.model_validate(
        {
            "appId": "demo",
            "appName": "Demo",
            "version": 1,
            "profileIds": ["demo-profile"],
            "operationEntrypoints": [
                {
                    "id": "demo.alpha",
                    "title": "Alpha",
                    "area": "Main",
                    "purpose": "Open alpha.",
                    "questionAliases": {"en": ["alpha"]},
                },
                {
                    "id": "demo.bravo",
                    "title": "Bravo",
                    "area": "Main",
                    "purpose": "Open bravo.",
                    "questionAliases": {"en": ["bravo"]},
                },
            ],
            "demoFlows": [],
            "manualControls": [],
        }
    )

    response = answer_question(
        package=package,
        question="alpha bravo",
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id == "demo.alpha"


def test_localized_qa_question_returns_localized_answer() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="怎么保护我的真实背景",
        voice=PresenterVoiceSettings(language="zh", tone="professional"),
    )

    assert response.entrypoint_id == "ringcentral.video.settings.background"
    assert response.answer_text.startswith("打开 Settings")
    assert "Blur" in response.answer_text


def test_ringcentral_localized_shared_screen_qa_returns_chinese_answer() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="你能说明共享屏幕内容吗",
        voice=PresenterVoiceSettings(language="zh", tone="professional"),
    )

    assert response.entrypoint_id == "ringcentral.video.toolbar.share"
    assert response.can_operate is False
    assert "共享内容" in response.answer_text
    assert "approved observation" not in response.answer_text


def test_ringcentral_localized_invite_qa_returns_chinese_answer_and_stays_non_operable() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="我是第一个人怎么邀请同事入会",
        voice=PresenterVoiceSettings(language="zh", tone="friendly"),
    )

    assert response.entrypoint_id == "ringcentral.video.toolbar.invite"
    assert response.can_operate is False
    assert "Add coworkers" in response.answer_text
    assert "不要朗读" in response.answer_text


def test_ringcentral_localized_audio_video_readiness_qa_returns_chinese_answer() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="开会前怎么确认声音视频",
        voice=PresenterVoiceSettings(language="zh", tone="coach"),
    )

    assert response.entrypoint_id == "ringcentral.video.toolbar.audio"
    assert response.can_operate is False
    assert "麦克风" in response.answer_text
    assert "摄像头" in response.answer_text


@pytest.mark.parametrize("question", ["怎么录制会议", "记录会议"])
def test_ringcentral_localized_recording_question_returns_chinese_safety_answer(question: str) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="zh", tone="friendly"),
    )

    assert response.entrypoint_id == "ringcentral.video.more.recording"
    assert response.can_operate is False
    assert "参会者同意" in response.answer_text
    assert "Start recording:" not in response.answer_text


def test_ringcentral_chinese_questions_match_package_aliases_without_legacy_table(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    monkeypatch.setattr(questions_module, "_ENTRYPOINT_ALIASES", {})

    expected = {
        "谁在会议里": "ringcentral.video.toolbar.participants",
        "换麦克风": "ringcentral.video.toolbar.audio-menu",
        "换摄像头": "ringcentral.video.toolbar.video-menu",
        "网络质量": "ringcentral.video.top.network-quality",
        "会议号在哪里": "ringcentral.video.top.meeting-info",
        "会议笔记在哪里": "ringcentral.video.more.notes",
        "记录会议": "ringcentral.video.more.recording",
        "拉人入会": "ringcentral.video.main.add-coworkers",
    }

    for question, entrypoint_id in expected.items():
        response = answer_question(
            package=package,
            question=question,
            voice=PresenterVoiceSettings(language="zh"),
        )
        assert response.entrypoint_id == entrypoint_id


def test_legacy_alias_table_remains_dynamic_for_runtime_matching(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    monkeypatch.setattr(
        questions_module,
        "_ENTRYPOINT_ALIASES",
        {"ringcentral.video.toolbar.chat": ("legacy dynamic route",)},
    )

    response = answer_question(
        package=package,
        question="legacy dynamic route",
        voice=PresenterVoiceSettings(),
    )

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
    assert response.can_operate is False


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


def test_camera_toggle_answer_is_not_operable() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="camera",
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id in {
        "ringcentral.video.toolbar.video",
        "ringcentral.video.toolbar.video-menu",
    }
    assert response.can_operate is False


def test_start_meeting_answer_is_not_operable() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="start meeting",
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id == "ringcentral.develop.video.start"
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


def test_answer_question_logs_timing_without_question_text(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    times = iter([1.0, 1.123])
    monkeypatch.setattr(questions_module, "perf_counter", lambda: next(times), raising=False)

    with caplog.at_level(logging.INFO, logger="ai_presenter.runtime.questions"):
        response = answer_question(
            package=package,
            question="How do I protect my real background?",
            voice=PresenterVoiceSettings(),
        )

    message = caplog.records[-1].getMessage()
    assert response.entrypoint_id == "ringcentral.video.settings.background"
    assert "question_answered" in message
    assert "duration_ms=123.00" in message
    assert "package=ringcentral-video" in message
    assert "entrypoint=ringcentral.video.settings.background" in message
    assert response.can_operate is True
    assert "can_operate=True" in message
    assert "How do I protect" not in message
    assert response.answer_text not in message


def test_answer_question_logs_failure_without_question_or_exception_text(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    times = iter([4.0, 4.01])
    monkeypatch.setattr(questions_module, "perf_counter", lambda: next(times), raising=False)

    def fail_answer(**_: object) -> questions_module.QuestionResponse:
        raise RuntimeError("private answer text")

    monkeypatch.setattr(questions_module, "_answer_question", fail_answer)

    with caplog.at_level(logging.INFO, logger="ai_presenter.runtime.questions"):
        with pytest.raises(RuntimeError, match="private answer text"):
            answer_question(
                package=package,
                question="private board agenda",
                voice=PresenterVoiceSettings(language="zh", tone="conversational"),
            )

    message = caplog.records[-1].getMessage()
    assert "question_answered" in message
    assert "status=error" in message
    assert "duration_ms=10.00" in message
    assert "package=ringcentral-video" in message
    assert "language=zh" in message
    assert "tone=conversational" in message
    assert "private board agenda" not in message
    assert "private answer text" not in message


def test_answer_question_logs_canonical_language_for_language_alias(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    times = iter([5.0, 5.02])
    monkeypatch.setattr(questions_module, "perf_counter", lambda: next(times), raising=False)

    with caplog.at_level(logging.INFO, logger="ai_presenter.runtime.questions"):
        response = answer_question(
            package=package,
            question="怎么保护我的真实背景",
            voice=PresenterVoiceSettings(language="zh-CN", tone="friendly"),
        )

    message = caplog.records[-1].getMessage()
    assert response.entrypoint_id == "ringcentral.video.settings.background"
    assert "language=zh" in message
    assert "language=zh-CN" not in message
    assert "tone=friendly" in message
