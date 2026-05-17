import logging
from pathlib import Path

import pytest

from ai_presenter.packages.loader import load_material_package
from ai_presenter.packages.models import MaterialPackage
from ai_presenter.packages.models import match_field_tokens
from ai_presenter.packages.models import normalize_question_prompt
from ai_presenter.runtime import questions as questions_module
from ai_presenter.runtime.questions import answer_question
from ai_presenter.runtime.session import create_question_interrupt_step
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


def test_halfwidth_japanese_input_is_not_folded_into_package_alias(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = MaterialPackage.model_validate(
        {
            "appId": "demo",
            "appName": "Demo",
            "version": 1,
            "profileIds": ["demo-profile"],
            "operationEntrypoints": [
                {
                    "id": "demo.camera-menu",
                    "title": "Camera menu",
                    "area": "Toolbar",
                    "purpose": "Open camera menu.",
                    "questionAliases": {"ja": ["\u30ab\u30e1\u30e9\u30e1\u30cb\u30e5\u30fc"]},
                    "openSteps": [
                        {
                            "action": "clickWindowControl",
                            "target": "Camera",
                            "match": {"controlType": "button"},
                        }
                    ],
                }
            ],
            "demoFlows": [],
            "manualControls": [],
        }
    )
    monkeypatch.setattr(questions_module, "_ENTRYPOINT_ALIASES", {})

    response = answer_question(
        package=package,
        question="\uff76\uff92\uff97\uff92\uff86\uff6d\uff70",
        voice=PresenterVoiceSettings(language="ja"),
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


def test_entrypoint_answer_uses_localized_title_and_purpose() -> None:
    package = MaterialPackage.model_validate(
        {
            "appId": "demo",
            "appName": "Demo",
            "version": 1,
            "profileIds": ["demo-profile"],
            "operationEntrypoints": [
                {
                    "id": "demo.participants",
                    "title": "Participants panel",
                    "area": "Toolbar",
                    "purpose": "Open participant list.",
                    "localizedTitles": {"es": "Panel de participantes"},
                    "localizedPurposes": {"es": "Abre la lista de participantes."},
                    "questionAliases": {"es": ["participantes"]},
                    "openSteps": [],
                }
            ],
            "demoFlows": [],
            "manualControls": [],
        }
    )

    response = answer_question(
        package=package,
        question="Donde estan los participantes?",
        voice=PresenterVoiceSettings(language="es"),
    )

    assert response.answer_text == "Panel de participantes: Abre la lista de participantes."
    assert response.entrypoint_id == "demo.participants"


def test_entrypoint_answer_uses_localized_title_with_english_purpose_fallback() -> None:
    package = MaterialPackage.model_validate(
        {
            "appId": "demo",
            "appName": "Demo",
            "version": 1,
            "profileIds": ["demo-profile"],
            "operationEntrypoints": [
                {
                    "id": "demo.participants",
                    "title": "Participants panel",
                    "area": "Toolbar",
                    "purpose": "Open participant list.",
                    "localizedTitles": {"es": "Panel de participantes"},
                    "questionAliases": {"es": ["participantes"]},
                    "openSteps": [],
                }
            ],
            "demoFlows": [],
            "manualControls": [],
        }
    )

    response = answer_question(
        package=package,
        question="participantes",
        voice=PresenterVoiceSettings(language="es"),
    )

    assert response.answer_text == "Panel de participantes: Open participant list."


def test_spanish_entrypoint_answer_keeps_alias_label_when_localized_title_missing() -> None:
    package = MaterialPackage.model_validate(
        {
            "appId": "demo",
            "appName": "Demo",
            "version": 1,
            "profileIds": ["demo-profile"],
            "operationEntrypoints": [
                {
                    "id": "demo.participants",
                    "title": "Participants panel",
                    "area": "Toolbar",
                    "purpose": "Open participant list.",
                    "questionAliases": {"es": ["panel de participantes"]},
                    "openSteps": [],
                }
            ],
            "demoFlows": [],
            "manualControls": [],
        }
    )

    response = answer_question(
        package=package,
        question="panel de participantes",
        voice=PresenterVoiceSettings(language="es"),
    )

    assert response.answer_text == "panel de participantes: Open participant list."


def test_non_spanish_entrypoint_answer_uses_canonical_title_without_localized_copy() -> None:
    package = MaterialPackage.model_validate(
        {
            "appId": "demo",
            "appName": "Demo",
            "version": 1,
            "profileIds": ["demo-profile"],
            "operationEntrypoints": [
                {
                    "id": "demo.camera",
                    "title": "Camera menu",
                    "area": "Toolbar",
                    "purpose": "Open camera options.",
                    "questionAliases": {"ja": ["\u30ab\u30e1\u30e9"]},
                    "openSteps": [],
                }
            ],
            "demoFlows": [],
            "manualControls": [],
        }
    )

    response = answer_question(
        package=package,
        question="\u30ab\u30e1\u30e9",
        voice=PresenterVoiceSettings(language="ja"),
    )

    assert response.answer_text == "Camera menu: Open camera options."


def test_localized_entrypoint_title_alone_does_not_create_a_match() -> None:
    package = MaterialPackage.model_validate(
        {
            "appId": "demo",
            "appName": "Demo",
            "version": 1,
            "profileIds": ["demo-profile"],
            "operationEntrypoints": [
                {
                    "id": "demo.attendees",
                    "title": "Attendees",
                    "area": "Toolbar",
                    "purpose": "Open attendee controls.",
                    "localizedTitles": {"es": "Panel de participantes"},
                    "openSteps": [],
                }
            ],
            "demoFlows": [],
            "manualControls": [],
        }
    )

    response = answer_question(
        package=package,
        question="panel de participantes",
        voice=PresenterVoiceSettings(language="es"),
    )

    assert response.entrypoint_id is None
    assert response.can_operate is False


@pytest.mark.parametrize(
    ("question", "expected_entrypoint_id"),
    [
        (
            "selector de microfono y altavoz",
            "ringcentral.video.toolbar.audio-menu",
        ),
        (
            "menu de camara en la reunion",
            "ringcentral.video.toolbar.video-menu",
        ),
        (
            "ubicacion de background en more",
            "ringcentral.video.more.background",
        ),
    ],
)
def test_ringcentral_spanish_alias_routes_render_optional_display_metadata(
    question: str,
    expected_entrypoint_id: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    expected_entrypoint = package.entrypoint_by_id(expected_entrypoint_id)

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="es"),
    )

    assert response.entrypoint_id == expected_entrypoint_id
    assert response.answer_text == (
        f"{expected_entrypoint.localized_titles['es']}: "
        f"{expected_entrypoint.localized_purposes['es']}"
    )


def test_ringcentral_spanish_display_metadata_is_not_part_of_match_candidates() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    entrypoint_ids = (
        "ringcentral.video.toolbar.audio-menu",
        "ringcentral.video.toolbar.video-menu",
        "ringcentral.video.more.background",
    )
    candidates_by_entrypoint_id = {
        candidate.entrypoint.id: candidate for candidate in package.entrypoint_match_candidates
    }

    for entrypoint_id in entrypoint_ids:
        entrypoint = package.entrypoint_by_id(entrypoint_id)
        candidate = candidates_by_entrypoint_id[entrypoint_id]
        canonical_tokens = (
            match_field_tokens(entrypoint.id)
            | match_field_tokens(entrypoint.title)
            | match_field_tokens(entrypoint.area)
            | match_field_tokens(entrypoint.purpose)
        )
        localized_tokens = match_field_tokens(
            " ".join(
                [
                    entrypoint.localized_titles["es"],
                    entrypoint.localized_purposes["es"],
                ]
            )
        )
        candidate_tokens = (
            candidate.id_tokens
            | candidate.title_tokens
            | candidate.title_or_id_tokens
            | candidate.area_tokens
            | candidate.purpose_tokens
        )

        assert candidate.id_tokens == match_field_tokens(entrypoint.id)
        assert candidate.title_tokens == match_field_tokens(entrypoint.title)
        assert candidate.title_or_id_tokens == (
            match_field_tokens(entrypoint.id) | match_field_tokens(entrypoint.title)
        )
        assert candidate.area_tokens == match_field_tokens(entrypoint.area)
        assert candidate.purpose_tokens == match_field_tokens(entrypoint.purpose)
        assert (localized_tokens - canonical_tokens).isdisjoint(candidate_tokens)


def test_ringcentral_spanish_display_metadata_fragments_do_not_create_matches() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    entrypoint_ids = (
        "ringcentral.video.toolbar.audio-menu",
        "ringcentral.video.toolbar.video-menu",
        "ringcentral.video.more.background",
    )
    all_candidate_tokens = set().union(
        *(
            candidate.id_tokens
            | candidate.title_tokens
            | candidate.title_or_id_tokens
            | candidate.area_tokens
            | candidate.purpose_tokens
            for candidate in package.entrypoint_match_candidates
        )
    )

    for entrypoint_id in entrypoint_ids:
        entrypoint = package.entrypoint_by_id(entrypoint_id)
        localized_tokens = match_field_tokens(
            " ".join(
                [
                    entrypoint.localized_titles["es"],
                    entrypoint.localized_purposes["es"],
                ]
            )
        )
        localized_only_query = " ".join(sorted(localized_tokens - all_candidate_tokens))
        assert localized_only_query

        entrypoint_match = questions_module._match_entrypoint(
            package,
            normalize_question_prompt(localized_only_query),
        )

        assert entrypoint_match is None


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


@pytest.mark.parametrize(
    "question",
    [
        "Share my screen",
        "Start sharing",
        "Stop sharing",
        "Read the shared screen",
        "Can you describe what's on screen?",
        "Show my screen",
        "Share system audio",
        "Turn on share system audio",
        "Include system audio",
        "Share computer audio",
        "Can you share system audio?",
    ],
)
def test_ringcentral_english_screen_sharing_questions_stay_qa_first(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id == "ringcentral.video.toolbar.share"
    assert response.can_operate is False
    assert "Screen sharing can expose private content" in response.answer_text
    assert "Screen sharing:" not in response.answer_text
    assert "Start meeting:" not in response.answer_text
    assert create_question_interrupt_step(package, response) is None


@pytest.mark.parametrize(
    "question",
    [
        "Show full screen",
        "Switch to full screen",
        "Where is full screen?",
        "Full screen view",
        "Go full screen",
        "Enter full screen mode",
        "Exit full screen",
        "Leave full screen mode",
    ],
)
def test_ringcentral_full_screen_questions_route_to_view_layout(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id == "ringcentral.video.top.views"
    assert response.entrypoint_id != "ringcentral.video.toolbar.share"
    assert response.entrypoint_id != "ringcentral.video.toolbar.leave"
    assert response.can_operate is True
    assert create_question_interrupt_step(package, response) is not None
    assert response.answer_text.startswith("View layout menu:")
    assert "Screen sharing:" not in response.answer_text


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


@pytest.mark.parametrize(
    "question",
    [
        "Read the invite link",
        "Copy the invite link",
        "Invite John",
        "Send the invite",
        "Who can I invite?",
    ],
)
def test_ringcentral_english_invite_privacy_questions_stay_qa_first(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id == "ringcentral.video.toolbar.invite"
    assert response.can_operate is False
    assert "private invite links" in response.answer_text
    assert "send invites" in response.answer_text
    assert "Invite participants:" not in response.answer_text
    assert create_question_interrupt_step(package, response) is None


@pytest.mark.parametrize(
    "question",
    [
        "Copy meeting link",
        "Can you copy the meeting link?",
        "Copy the meeting URL",
        "Can you paste the meeting link?",
        "Read the meeting link aloud",
        "Can you read the meeting ID?",
        "Read the dial-in number",
        "What is the dial-in number?",
        "Copy the dial-in details",
        "Read dial-in details aloud",
        "Who is the host?",
        "Read the host information",
        "Copy host info",
        "Read meeting details aloud",
    ],
)
def test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id == "ringcentral.video.top.meeting-info"
    assert response.can_operate is False
    assert "Meeting IDs and links are private meeting details" in response.answer_text
    assert "Meeting information:" not in response.answer_text
    assert "https://" not in response.answer_text
    assert "ringcentral.com" not in response.answer_text
    assert "123456789" not in response.answer_text
    assert "copied" not in response.answer_text.casefold()
    assert "dialed" not in response.answer_text.casefold()
    assert create_question_interrupt_step(package, response) is None


@pytest.mark.parametrize(
    "question",
    [
        "Is this meeting encrypted?",
        "Is the meeting encrypted?",
        "Can you check encryption status?",
        "Show encryption status",
        "Show meeting encryption status",
        "Where can I see encryption?",
        "Where is end-to-end encryption?",
        "Is end-to-end encryption enabled?",
        "What is the encryption status?",
        "Can you verify encryption?",
        "Can you verify end-to-end encryption?",
        "Is end-to-end encryption on?",
        "Open encryption settings",
        "Show encryption settings",
        "Change encryption settings",
        "Turn off end-to-end encryption",
        "Leave encryption off",
        "Security status",
        "What is the security status?",
        "Is the meeting secure?",
        "Can you verify meeting security?",
        "Share meeting security status",
        "Open security tab in RingCentralDevelop",
    ],
)
def test_ringcentral_encryption_status_questions_stay_meeting_info_answer_only(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id == "ringcentral.video.top.meeting-info"
    assert response.entrypoint_id != "ringcentral.video.toolbar.share"
    assert response.entrypoint_id != "ringcentral.video.toolbar.participants"
    assert response.entrypoint_id != "ringcentral.video.toolbar.leave"
    assert response.entrypoint_id != "ringcentral.video.top.network-quality"
    assert response.entrypoint_id != "ringcentral.video.settings.background"
    assert response.entrypoint_id != "ringcentral.video.more.settings"
    assert response.entrypoint_id != "ringcentral.develop.video.tab"
    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None
    assert response.answer_text.startswith("Encryption status:")
    assert "visible status is verified" in response.answer_text
    assert "Meeting information:" not in response.answer_text
    assert "https://" not in response.answer_text
    assert "ringcentral.com" not in response.answer_text
    assert "123456789" not in response.answer_text
    assert "copied" not in response.answer_text.casefold()
    assert "read" not in response.answer_text.casefold()
    assert "dialed" not in response.answer_text.casefold()


@pytest.mark.parametrize(
    ("question", "language", "expected_phrase"),
    [
        (
            "\u4f1a\u8bae\u4fe1\u606f\u91cc\u80fd\u770b\u5230\u52a0\u5bc6\u72b6\u6001\u5417",
            "zh",
            "\u52a0\u5bc6\u72b6\u6001",
        ),
        (
            "\u6697\u53f7\u5316\u72b6\u614b\u306f\u3069\u3053\u3067\u78ba\u8a8d\u3067\u304d\u307e\u3059\u304b",
            "ja",
            "\u6697\u53f7\u5316\u72b6\u614b",
        ),
        (
            "\u00bfD\u00f3nde veo el cifrado de la reuni\u00f3n?",
            "es",
            "cifrado",
        ),
    ],
)
def test_ringcentral_localized_encryption_status_questions_are_answer_only(
    question: str,
    language: str,
    expected_phrase: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language=language),
    )

    assert response.entrypoint_id == "ringcentral.video.top.meeting-info"
    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None
    assert expected_phrase in response.answer_text
    assert "https://" not in response.answer_text
    assert "ringcentral.com" not in response.answer_text
    assert "123456789" not in response.answer_text
    assert "copied" not in response.answer_text.casefold()
    assert "read" not in response.answer_text.casefold()
    assert "dialed" not in response.answer_text.casefold()


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


def test_ringcentral_microphone_button_location_routes_to_audio_without_interrupt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    monkeypatch.setattr(questions_module, "_ENTRYPOINT_ALIASES", {})

    response = answer_question(
        package=package,
        question="Where is the microphone button?",
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id == "ringcentral.video.toolbar.audio"
    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None


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


@pytest.mark.parametrize(
    "question",
    [
        "Record this meeting",
        "Start recording",
        "Stop recording",
        "Are we recording?",
        "Recording status",
    ],
)
def test_ringcentral_english_recording_action_questions_stay_qa_first(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id == "ringcentral.video.more.recording"
    assert response.can_operate is False
    assert "Recording changes the meeting state" in response.answer_text
    assert "Start recording:" not in response.answer_text
    assert create_question_interrupt_step(package, response) is None


@pytest.mark.parametrize(
    "question",
    [
        "Leave meeting",
        "End meeting",
        "Hang up",
        "End call",
        "Close meeting",
        "Can you leave the meeting?",
        "Can you end the meeting?",
    ],
)
def test_ringcentral_english_leave_end_questions_stay_qa_first(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id == "ringcentral.video.toolbar.leave"
    assert response.can_operate is False
    assert "Leaving or ending a meeting is destructive" in response.answer_text
    assert "Leave meeting:" not in response.answer_text
    assert create_question_interrupt_step(package, response) is None


def test_ringcentral_host_controls_question_returns_participants_guidance() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="where are host controls for participants",
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id is None
    assert response.can_operate is False
    assert "Participants" in response.answer_text
    assert "host" in response.answer_text
    assert "explicitly asks" in response.answer_text
    assert "verified" in response.answer_text


def test_ringcentral_careful_tone_preserves_privacy_question_route() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    professional = answer_question(
        package=package,
        question="where are host controls for participants",
        voice=PresenterVoiceSettings(),
    )
    careful = answer_question(
        package=package,
        question="where are host controls for participants",
        voice=PresenterVoiceSettings(tone="privacy"),
    )

    assert professional.entrypoint_id is None
    assert careful.entrypoint_id == professional.entrypoint_id
    assert careful.can_operate is professional.can_operate is False
    assert create_question_interrupt_step(package, careful) is None
    assert careful.answer_text.startswith("Safety note.")
    assert "explicitly asks" in careful.answer_text
    assert "verified" in careful.answer_text


@pytest.mark.parametrize(
    ("question", "expected_entrypoint_id", "expected_can_operate", "expected_interrupt"),
    [
        (
            "how do I handle meeting recording safely?",
            "ringcentral.video.more.recording",
            False,
            False,
        ),
        ("Read the transcript", None, False, False),
        ("meeting information", "ringcentral.video.top.meeting-info", False, False),
        ("Is this meeting encrypted?", "ringcentral.video.top.meeting-info", False, False),
        ("Open encryption settings", "ringcentral.video.top.meeting-info", False, False),
        (
            "Share meeting security status",
            "ringcentral.video.top.meeting-info",
            False,
            False,
        ),
        (
            "Can AiPresenter read meeting messages or participant names?",
            None,
            False,
            False,
        ),
        ("invite people", "ringcentral.video.toolbar.invite", False, False),
        ("share screen", "ringcentral.video.toolbar.share", False, False),
        ("participants", "ringcentral.video.toolbar.participants", True, True),
        ("leave meeting", "ringcentral.video.toolbar.leave", False, False),
        ("network quality", "ringcentral.video.top.network-quality", True, True),
    ],
)
def test_ringcentral_sensitive_prompt_routing_is_tone_invariant(
    question: str,
    expected_entrypoint_id: str | None,
    expected_can_operate: bool,
    expected_interrupt: bool,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    baseline = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(tone="professional"),
    )
    baseline_interrupt = create_question_interrupt_step(package, baseline) is not None

    assert baseline.entrypoint_id == expected_entrypoint_id
    assert baseline.can_operate is expected_can_operate
    assert baseline_interrupt is expected_interrupt

    for tone in ("friendly", "coach", "support", "empathetic", "privacy"):
        response = answer_question(
            package=package,
            question=question,
            voice=PresenterVoiceSettings(tone=tone),
        )

        assert response.entrypoint_id == baseline.entrypoint_id
        assert response.can_operate is baseline.can_operate
        assert (create_question_interrupt_step(package, response) is not None) is (
            baseline_interrupt
        )


def test_ringcentral_localized_host_controls_question_returns_chinese_guidance() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="\u4e3b\u6301\u4eba\u600e\u4e48\u7ba1\u7406\u53c2\u4f1a\u8005",
        voice=PresenterVoiceSettings(language="zh", tone="professional"),
    )

    assert response.entrypoint_id is None
    assert response.can_operate is False
    assert "Participants" in response.answer_text
    assert "\u660e\u786e\u8981\u6c42" in response.answer_text
    assert "\u5df2\u9a8c\u8bc1" in response.answer_text
    assert "\u59d3\u540d" in response.answer_text


@pytest.mark.parametrize(
    "question",
    [
        "Can you read chat messages?",
        "Read chat aloud",
        "Summarize the chat",
        "What did John say in chat?",
    ],
)
def test_ringcentral_chat_content_requests_stay_answer_only(question: str) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id is None
    assert response.entrypoint_id != "ringcentral.video.toolbar.chat"
    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None
    assert "chat messages" in response.answer_text
    assert "verified" in response.answer_text
    assert "Chat panel:" not in response.answer_text
    assert "Meeting information:" not in response.answer_text


@pytest.mark.parametrize(
    "question",
    [
        "Who is in the meeting?",
        "List participants",
        "Read participant names",
        "Show participant roles",
        "Read participant roles",
        "List participant roles",
        "Who is host or moderator?",
    ],
)
def test_ringcentral_participant_identity_requests_stay_answer_only(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id is None
    assert response.entrypoint_id != "ringcentral.video.toolbar.participants"
    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None
    assert "participant names" in response.answer_text
    assert "roles" in response.answer_text
    assert "private tabs" in response.answer_text
    assert "explicitly asks" in response.answer_text
    assert "verified" in response.answer_text
    assert "Participants panel:" not in response.answer_text
    assert "I could not find a matching control" not in response.answer_text


@pytest.mark.parametrize(
    "question",
    [
        "Mute all participants",
        "Remove a participant",
        "Lock the meeting",
        "Unlock the meeting",
        "Change meeting security",
        "Where are security settings?",
        "Open meeting security settings",
        "Meeting security settings",
    ],
)
def test_ringcentral_participant_host_action_requests_stay_answer_only(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id is None
    assert response.entrypoint_id != "ringcentral.video.toolbar.participants"
    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None
    assert "Do not mute others" in response.answer_text
    assert "lock the meeting" in response.answer_text
    assert "change security settings" in response.answer_text
    assert "explicitly asks" in response.answer_text
    assert "verified" in response.answer_text
    assert "Participants panel:" not in response.answer_text
    assert "Background settings:" not in response.answer_text
    assert "I could not find a matching control" not in response.answer_text


@pytest.mark.parametrize(
    "question",
    [
        "Where are captions?",
        "Can I use live transcription?",
        "How do I translate captions?",
        "Where are translated captions?",
        "Turn on captions",
        "Read caption text",
        "Show captions text",
        "Show live caption text",
        "Read captions aloud",
        "Can you read the captions?",
        "Can you read captions?",
        "Copy captions",
        "Can you copy the captions?",
        "Export captions",
        "Save captions",
        "Download captions",
        "Download transcript text",
    ],
)
def test_ringcentral_captions_and_translation_questions_are_answer_only(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id is None
    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None
    assert "Notes and Transcript" in response.answer_text
    assert "Settings" in response.answer_text
    assert "explicitly asks" in response.answer_text
    assert "verified" in response.answer_text
    assert "caption or transcript text" in response.answer_text
    assert "Microphone control:" not in response.answer_text
    assert "Meeting information:" not in response.answer_text
    assert "Notes and transcript:" not in response.answer_text
    assert "I could not find a matching control" not in response.answer_text
    assert "The caption says" not in response.answer_text
    assert "Here are the captions" not in response.answer_text
    assert "copied" not in response.answer_text.casefold()
    assert "exported" not in response.answer_text.casefold()
    assert "saved" not in response.answer_text.casefold()
    assert "downloaded" not in response.answer_text.casefold()
    assert "started" not in response.answer_text.casefold()
    assert "turned on" not in response.answer_text.casefold()


@pytest.mark.parametrize(
    "question",
    [
        "\u00bfPuede el presenter describir el contenido compartido en pantalla?",
        "\u00bfPuede leer los mensajes del chat o los nombres de participantes?",
        "\u00bfD\u00f3nde est\u00e1n los controles de grabaci\u00f3n despu\u00e9s de la reuni\u00f3n?",
    ],
)
def test_ringcentral_spanish_safety_questions_match_qas_without_runtime_spanish(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="en", tone="professional"),
    )

    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None


@pytest.mark.parametrize(
    "question",
    [
        "\u5b57\u5e55\u5728\u54ea\u91cc",
        "\u5b9e\u65f6\u8f6c\u5f55\u5728\u54ea\u91cc",
        "\u600e\u4e48\u7ffb\u8bd1\u5b57\u5e55",
    ],
)
def test_ringcentral_localized_caption_translation_questions_are_answer_only(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="zh", tone="professional"),
    )

    assert response.entrypoint_id is None
    assert response.can_operate is False
    assert "Notes and Transcript" in response.answer_text
    assert "Settings" in response.answer_text
    assert "\u660e\u786e\u8981\u6c42" in response.answer_text
    assert "\u5df2\u9a8c\u8bc1" in response.answer_text
    assert not response.answer_text.startswith("\u6211\u4f1a\u8c28\u614e\u8bf4\u660e")


def test_ringcentral_chinese_safety_qas_keep_authored_text_under_careful_tone() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="\u5b9e\u65f6\u8f6c\u5f55\u5728\u54ea\u91cc",
        voice=PresenterVoiceSettings(language="zh", tone="privacy"),
    )

    assert response.entrypoint_id is None
    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None
    assert "Notes and Transcript" in response.answer_text
    assert "\u660e\u786e\u8981\u6c42" in response.answer_text
    assert not response.answer_text.startswith("\u6211\u4f1a\u8c28\u614e\u8bf4\u660e")


@pytest.mark.parametrize(
    "question",
    [
        "Where can I find post-meeting recordings, transcripts, summaries, or insights?",
        "Where are RingCentral meeting recordings after the meeting?",
        "Can AiPresenter read post-meeting transcripts?",
        "Can you summarize the meeting after it ends?",
        "Where are post-meeting summaries or insights?",
    ],
)
def test_ringcentral_post_meeting_artifact_questions_are_answer_only(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id is None
    assert response.can_operate is False
    assert "post-meeting artifacts" in response.answer_text
    assert "recordings" in response.answer_text
    assert "transcripts" in response.answer_text
    assert "summaries" in response.answer_text
    assert "insights" in response.answer_text
    assert "may be available" in response.answer_text
    assert "explicitly asks" in response.answer_text
    assert "visible context is verified" in response.answer_text
    assert "Start recording:" not in response.answer_text


@pytest.mark.parametrize(
    "question",
    [
        "\u4f1a\u540e\u5f55\u5236\u5728\u54ea\u91cc",
        "\u4f1a\u540e\u8f6c\u5f55\u5728\u54ea\u91cc",
        "\u4f1a\u8bae\u6458\u8981\u548c\u6d1e\u5bdf\u5728\u54ea\u91cc",
    ],
)
def test_ringcentral_localized_post_meeting_artifact_questions_are_answer_only(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="zh", tone="professional"),
    )

    assert response.entrypoint_id is None
    assert response.can_operate is False
    assert "\u4f1a\u540e" in response.answer_text
    assert "\u5f55\u5236" in response.answer_text
    assert "\u8f6c\u5f55" in response.answer_text
    assert "\u6458\u8981" in response.answer_text
    assert "\u6d1e\u5bdf" in response.answer_text
    assert "\u53ef\u80fd" in response.answer_text
    assert "\u6743\u9650" in response.answer_text
    assert "\u53ef\u89c1\u4e0a\u4e0b\u6587\u5df2\u9a8c\u8bc1" in response.answer_text
    assert "Start recording:" not in response.answer_text


@pytest.mark.parametrize(
    ("question", "expected_fragments"),
    [
        (
            "\u5171\u6709\u753b\u9762\u306e\u5185\u5bb9\u3092\u8aac\u660e\u3067\u304d\u307e\u3059\u304b",
            ("\u5171\u6709", "\u660e\u793a\u7684", "\u78ba\u8a8d"),
        ),
        (
            "\u30c1\u30e3\u30c3\u30c8\u5185\u5bb9\u3084\u53c2\u52a0\u8005\u540d\u3092\u8aad\u307f\u4e0a\u3052\u3089\u308c\u307e\u3059\u304b",
            ("\u30c1\u30e3\u30c3\u30c8", "\u53c2\u52a0\u8005", "\u660e\u793a\u7684", "\u78ba\u8a8d"),
        ),
        (
            "\u5b57\u5e55\u306f\u3069\u3053\u306b\u3042\u308a\u307e\u3059\u304b",
            ("Notes and Transcript", "Settings", "\u660e\u793a\u7684", "\u78ba\u8a8d"),
        ),
        (
            "\u4f1a\u8b70\u5f8c\u306e\u9332\u753b\u3084\u6587\u5b57\u8d77\u3053\u3057\u306f\u3069\u3053\u306b\u3042\u308a\u307e\u3059\u304b",
            (
                "\u4f1a\u8b70\u5f8c",
                "\u9332\u753b",
                "\u6587\u5b57\u8d77\u3053\u3057",
                "\u8981\u7d04",
                "\u6d1e\u5bdf",
                "\u53ef\u80fd",
                "\u6a29\u9650",
                "\u78ba\u8a8d",
            ),
        ),
        (
            "\u4f1a\u8b70\u3092\u9332\u753b\u3059\u308b\u306b\u306f\u3069\u3046\u3059\u308c\u3070\u3044\u3044\u3067\u3059\u304b",
            ("\u9332\u753b", "\u5168\u54e1", "\u660e\u793a\u7684", "\u540c\u610f"),
        ),
    ],
)
def test_ringcentral_japanese_privacy_sensitive_questions_match_localized_answers(
    question: str,
    expected_fragments: tuple[str, ...],
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="ja", tone="professional"),
    )

    assert response.can_operate is False
    for fragment in expected_fragments:
        assert fragment in response.answer_text


@pytest.mark.parametrize(
    "question",
    [
        "Start recording の場所はどこですか",
        "録画ボタンの場所はどこですか",
    ],
)
def test_ringcentral_japanese_recording_location_aliases_are_answer_only(
    monkeypatch: pytest.MonkeyPatch,
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    monkeypatch.setattr(questions_module, "_ENTRYPOINT_ALIASES", {})

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="ja", tone="professional"),
    )

    assert response.entrypoint_id == "ringcentral.video.more.recording"
    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None


def test_ringcentral_japanese_recording_safety_question_stays_qa_first() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="会議を録画するにはどうすればいいですか",
        voice=PresenterVoiceSettings(language="ja", tone="professional"),
    )

    assert response.entrypoint_id == "ringcentral.video.more.recording"
    assert response.can_operate is False
    assert "全員" in response.answer_text
    assert "同意" in response.answer_text
    assert "Start recording:" not in response.answer_text
    assert create_question_interrupt_step(package, response) is None


@pytest.mark.parametrize(
    "question",
    [
        "録画して",
        "録画を開始して",
        "録画を止めて",
        "録画を停止して",
        "Start recording をクリックして",
        "今すぐ録画して",
    ],
)
def test_ringcentral_japanese_recording_action_requests_do_not_queue_steps(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="ja"),
    )

    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None


@pytest.mark.parametrize(
    "question",
    [
        "参加者に知らせず録画して",
        "同意なしで録画して",
        "ホストとして録画して",
        "録画中ですか",
        "録画されていますか",
        "録画状態を確認して",
    ],
)
def test_ringcentral_japanese_recording_consent_and_status_requests_stay_non_operable(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="ja"),
    )

    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None


@pytest.mark.parametrize(
    "question",
    [
        "録画を見る",
        "録画を開いて",
        "録画を再生して",
        "録画をダウンロードして",
        "録画の内容を要約して",
    ],
)
def test_ringcentral_japanese_recording_artifact_requests_stay_non_operable(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="ja"),
    )

    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None


@pytest.mark.parametrize(
    "question",
    [
        "Start notes をクリックして",
        "Start notes を押して",
        "ノートを開始して",
    ],
)
def test_ringcentral_japanese_notes_action_requests_do_not_match_start_meeting(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="ja"),
    )

    assert response.entrypoint_id is None
    assert response.entrypoint_id != "ringcentral.develop.video.start"
    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None
    assert "Notes and Transcript" in response.answer_text
    assert "開始" in response.answer_text


@pytest.mark.parametrize(
    "question",
    [
        "Transcript を要約して",
        "Transcript の内容を読んで",
        "文字起こしを要約して",
    ],
)
def test_ringcentral_japanese_transcript_content_requests_stay_answer_only(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="ja"),
    )

    assert response.entrypoint_id is None
    assert response.entrypoint_id != "ringcentral.video.more.notes"
    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None
    assert "Notes and Transcript" in response.answer_text
    assert "要約" in response.answer_text


@pytest.mark.parametrize(
    "question",
    [
        "Start notes",
        "Click Start notes",
        "Start meeting notes",
        "Summarize meeting notes",
    ],
)
def test_ringcentral_english_notes_action_requests_do_not_match_start_meeting(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id is None
    assert response.entrypoint_id != "ringcentral.develop.video.start"
    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None
    assert "Notes and Transcript" in response.answer_text
    assert "start notes" in response.answer_text.casefold()


@pytest.mark.parametrize(
    "question",
    [
        "Summarize the transcript",
        "Read the transcript",
    ],
)
def test_ringcentral_english_transcript_content_requests_stay_answer_only(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id is None
    assert response.entrypoint_id != "ringcentral.video.more.notes"
    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None
    assert "Notes and Transcript" in response.answer_text
    assert "transcript" in response.answer_text.casefold()


@pytest.mark.parametrize(
    "question",
    [
        "\u5f00\u59cb\u4f1a\u8bae\u7b14\u8bb0",
        "\u542f\u52a8\u4f1a\u8bae\u7b14\u8bb0",
        "\u70b9\u51fb Start notes",
    ],
)
def test_ringcentral_chinese_notes_action_requests_stay_answer_only(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="zh"),
    )

    assert response.entrypoint_id is None
    assert response.entrypoint_id != "ringcentral.video.more.notes"
    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None
    assert "Notes and Transcript" in response.answer_text
    assert "\u4e0d\u8981\u81ea\u52a8\u5f00\u542f" in response.answer_text


@pytest.mark.parametrize(
    "question",
    [
        "\u8bfb\u53d6\u8f6c\u5f55\u5185\u5bb9",
        "\u603b\u7ed3\u4f1a\u8bae\u7b14\u8bb0",
        "\u603b\u7ed3\u8f6c\u5f55",
        "\u590d\u5236\u8f6c\u5f55\u5185\u5bb9",
        "\u5bfc\u51fa\u8f6c\u5f55",
    ],
)
def test_ringcentral_chinese_transcript_content_requests_stay_answer_only(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="zh"),
    )

    assert response.entrypoint_id is None
    assert response.entrypoint_id != "ringcentral.video.more.notes"
    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None
    assert "Notes and Transcript" in response.answer_text
    assert "\u4e0d\u8981\u81ea\u52a8\u5f00\u542f" in response.answer_text


def test_ringcentral_show_me_where_notes_remains_location_lookup() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="Show me where Notes and Transcript is",
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id == "ringcentral.video.more.notes"
    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None
    assert "notes and transcript panel" in response.answer_text.casefold()


@pytest.mark.parametrize(
    "question",
    [
        "\u8f6c\u5f55\u5728\u54ea\u91cc",
        "\u4f1a\u8bae\u7b14\u8bb0\u5728\u54ea\u91cc",
        "\u8f6c\u5f55\u5165\u53e3\u5728\u54ea",
    ],
)
def test_ringcentral_chinese_notes_location_routes_still_match_notes(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="zh"),
    )

    assert response.entrypoint_id == "ringcentral.video.more.notes"
    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None


@pytest.mark.parametrize(
    "question",
    [
        "start meeting",
        "Start meeting をクリックして",
    ],
)
def test_ringcentral_start_meeting_questions_still_match_start_meeting(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="ja"),
    )

    assert response.entrypoint_id == "ringcentral.develop.video.start"
    assert response.can_operate is False


@pytest.mark.parametrize(
    "question",
    [
        "Notes and Transcript の場所はどこですか",
        "ノートと文字起こしの場所はどこですか",
    ],
)
def test_ringcentral_japanese_notes_location_routes_still_match_notes(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="ja"),
    )

    assert response.entrypoint_id == "ringcentral.video.more.notes"
    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None


def test_ringcentral_japanese_unmatched_question_returns_localized_no_match() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="\u305d\u306e\u6a5f\u80fd\u306f\u3069\u3053\u3067\u3059\u304b",
        voice=PresenterVoiceSettings(language="ja", tone="friendly"),
    )

    assert response.entrypoint_id is None
    assert response.can_operate is False
    assert response.answer_text == (
        "\u73fe\u5728\u306e\u30a2\u30d7\u30ea\u306e\u72b6\u6cc1\u3067\u306f"
        "\u4e00\u81f4\u3059\u308b\u30b3\u30f3\u30c8\u30ed\u30fc\u30eb\u304c\u898b\u3064\u304b\u308a\u307e\u305b\u3093\u3002"
    )


@pytest.mark.parametrize(
    "question",
    [
        "Can AiPresenter send a reaction or raise my hand?",
        "Can you send a thumbs up reaction?",
        "Can you raise my hand for me?",
        "How do I use reactions safely?",
        "How should AiPresenter handle raise hand?",
        "Raise my hand",
        "Lower my hand",
        "Send a thumbs up",
        "Send a reaction",
        "React with thumbs up",
        "Can you raise my hand?",
    ],
)
def test_ringcentral_reaction_and_raise_hand_safety_questions_are_answer_only(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id is None
    assert response.can_operate is False
    assert "Reactions" in response.answer_text
    assert "Raise hand" in response.answer_text
    assert "visible meeting signals" in response.answer_text
    assert "explicitly asks" in response.answer_text
    assert "Close the reaction strip" in response.answer_text
    assert "lower the hand" in response.answer_text


@pytest.mark.parametrize(
    ("question", "voice", "expected_fragments"),
    [
        (
            "\u53ef\u4ee5\u5e2e\u6211\u53d1\u8868\u60c5\u6216\u4e3e\u624b\u5417",
            PresenterVoiceSettings(language="zh", tone="professional"),
            ("\u53cd\u5e94", "\u4e3e\u624b", "\u53ef\u89c1", "\u660e\u786e\u8981\u6c42", "\u653e\u4e0b\u624b"),
        ),
        (
            "\u30ea\u30a2\u30af\u30b7\u30e7\u30f3\u3092\u9001\u3063\u305f\u308a\u624b\u3092\u4e0a\u3052\u305f\u308a\u3067\u304d\u307e\u3059\u304b",
            PresenterVoiceSettings(language="ja", tone="professional"),
            ("\u30ea\u30a2\u30af\u30b7\u30e7\u30f3", "\u624b\u3092\u4e0a\u3052", "\u8868\u793a", "\u660e\u793a\u7684", "\u4e0b\u3052"),
        ),
    ],
)
def test_ringcentral_localized_reaction_and_raise_hand_safety_questions_are_answer_only(
    question: str,
    voice: PresenterVoiceSettings,
    expected_fragments: tuple[str, ...],
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=voice,
    )

    assert response.entrypoint_id is None
    assert response.can_operate is False
    for fragment in expected_fragments:
        assert fragment in response.answer_text


@pytest.mark.parametrize(
    "question",
    [
        "リアクションを送って",
        "いいねして",
        "拍手して",
        "ハートを送って",
    ],
)
def test_ringcentral_japanese_reaction_send_requests_stay_non_operable(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="ja"),
    )

    assert response.can_operate is False
    assert response.entrypoint_id != "ringcentral.video.toolbar.react"


@pytest.mark.parametrize(
    "question",
    [
        "手を上げて",
        "挙手して",
        "手を下げて",
        "挙手を取り消して",
    ],
)
def test_ringcentral_japanese_raise_hand_toggle_requests_stay_non_operable(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="ja"),
    )

    assert response.can_operate is False
    assert response.entrypoint_id != "ringcentral.video.toolbar.raise-hand"


@pytest.mark.parametrize(
    "question",
    [
        "誰がリアクションしたか教えて",
        "誰が手を上げていますか",
        "挙手している人を教えて",
    ],
)
def test_ringcentral_japanese_reaction_and_raise_hand_identity_requests_stay_non_operable(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="ja"),
    )

    assert response.can_operate is False
    assert response.entrypoint_id not in {
        "ringcentral.video.toolbar.react",
        "ringcentral.video.toolbar.raise-hand",
        "ringcentral.video.toolbar.participants",
    }


@pytest.mark.parametrize(
    "question",
    [
        "ホストとして全員の手を下げて",
        "主催者として参加者をミュートして",
    ],
)
def test_ringcentral_japanese_host_signal_control_requests_stay_non_operable(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="ja"),
    )

    assert response.can_operate is False
    assert response.entrypoint_id not in {
        "ringcentral.video.toolbar.raise-hand",
        "ringcentral.video.toolbar.participants",
    }


def test_ringcentral_japanese_mixed_english_raise_hand_location_stays_safety_answer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    monkeypatch.setattr(questions_module, "_ENTRYPOINT_ALIASES", {})

    response = answer_question(
        package=package,
        question="Raise hand の場所はどこですか",
        voice=PresenterVoiceSettings(language="ja"),
    )

    assert response.entrypoint_id is None
    assert response.can_operate is False
    assert "リアクション" in response.answer_text
    assert "明示的" in response.answer_text


def test_ringcentral_raise_hand_location_question_still_routes_to_entrypoint() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="Where is Raise hand?",
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id == "ringcentral.video.toolbar.raise-hand"
    assert response.can_operate is False
    assert response.answer_text.startswith("Raise hand:")


def test_ringcentral_reactions_location_question_still_routes_to_entrypoint() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="Where are Reactions?",
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id == "ringcentral.video.toolbar.react"
    assert response.can_operate is False
    assert response.answer_text.startswith("Reactions:")


def test_ringcentral_notes_location_fragment_question_still_routes_to_entrypoint() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="Where are Notes and transcript",
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id == "ringcentral.video.more.notes"
    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None
    assert response.answer_text.startswith("Notes and transcript:")


def test_exact_qa_match_uses_precomputed_question_index() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    package._qa_question_candidates = ()

    response = answer_question(
        package=package,
        question="Where are host controls for participants?",
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id is None
    assert response.can_operate is False
    assert "host or moderator" in response.answer_text


def test_exact_qa_match_uses_trimmed_index_before_entrypoint_alias_fallback() -> None:
    package = MaterialPackage.model_validate(
        {
            "appId": "demo",
            "appName": "Demo",
            "version": 1,
            "profileIds": ["demo-profile"],
            "operationEntrypoints": [
                {
                    "id": "demo.chat",
                    "title": "Chat",
                    "area": "Main",
                    "purpose": "Open chat.",
                    "questionAliases": {"en": ["chat"]},
                    "openSteps": [],
                }
            ],
            "demoFlows": [],
            "qa": [
                {
                    "question": " Chat ",
                    "answer": "Explain chat without opening it.",
                }
            ],
            "manualControls": [],
        }
    )
    package._qa_question_candidates = ()

    response = answer_question(
        package=package,
        question="chat",
        voice=PresenterVoiceSettings(),
    )

    assert response.answer_text == "Explain chat without opening it."
    assert response.entrypoint_id is None
    assert response.can_operate is False


@pytest.mark.parametrize("question", ["   ", "quantum waffle"])
def test_blank_qa_prompt_is_never_a_runtime_match(question: str) -> None:
    package = MaterialPackage.model_validate(
        {
            "appId": "demo",
            "appName": "Demo",
            "version": 1,
            "profileIds": ["demo-profile"],
            "operationEntrypoints": [],
            "demoFlows": [],
            "qa": [
                {
                    "question": "Where is privacy?",
                    "answer": "Open privacy.",
                    "localizedQuestions": {"en": ["   "]},
                }
            ],
            "manualControls": [],
        }
    )

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(),
    )

    assert response.answer_text == "I could not find a matching control in the active app context."
    assert response.entrypoint_id is None
    assert response.can_operate is False


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
        if entrypoint_id == "ringcentral.video.top.network-quality":
            assert response.can_operate is True
        if entrypoint_id == "ringcentral.video.more.notes":
            assert response.can_operate is False
            assert create_question_interrupt_step(package, response) is None


def test_ringcentral_japanese_meeting_control_questions_match_package_aliases_without_legacy_table(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    monkeypatch.setattr(questions_module, "_ENTRYPOINT_ALIASES", {})

    expected = {
        "会議情報の場所はどこですか": (
            "ringcentral.video.top.meeting-info",
            False,
        ),
        "Meeting information の場所はどこですか": (
            "ringcentral.video.top.meeting-info",
            False,
        ),
        "会議詳細の入口はどこですか": (
            "ringcentral.video.top.meeting-info",
            False,
        ),
        "会議画面の概要を教えて": ("ringcentral.video.overview", False),
        "会議画面の見取り図はありますか": ("ringcentral.video.overview", False),
        "React ボタンの場所はどこですか": (
            "ringcentral.video.toolbar.react",
            False,
        ),
        "リアクション欄の場所はどこですか": (
            "ringcentral.video.toolbar.react",
            False,
        ),
        "挙手ボタンの場所はどこですか": (
            "ringcentral.video.toolbar.raise-hand",
            False,
        ),
        "挙手の場所はどこですか": (
            "ringcentral.video.toolbar.raise-hand",
            False,
        ),
        "Start recording の場所はどこですか": (
            "ringcentral.video.more.recording",
            False,
        ),
        "録画ボタンの場所はどこですか": (
            "ringcentral.video.more.recording",
            False,
        ),
        "Notes and Transcript の場所はどこですか": (
            "ringcentral.video.more.notes",
            False,
        ),
        "ノートと文字起こしの場所はどこですか": (
            "ringcentral.video.more.notes",
            False,
        ),
        "ネットワーク品質を確認したい": (
            "ringcentral.video.top.network-quality",
            True,
        ),
        "表示レイアウトはどこですか": ("ringcentral.video.top.views", True),
        "音声メニューはどこですか": (
            "ringcentral.video.toolbar.audio-menu",
            False,
        ),
        "スピーカーメニューはどこですか": (
            "ringcentral.video.toolbar.audio-menu",
            False,
        ),
        "カメラメニューはどこですか": (
            "ringcentral.video.toolbar.video-menu",
            True,
        ),
        "カメラ選択はどこですか": (
            "ringcentral.video.toolbar.video-menu",
            True,
        ),
        "マイクはどこですか": ("ringcentral.video.toolbar.audio", False),
        "参加者一覧はどこですか": (
            "ringcentral.video.toolbar.participants",
            True,
        ),
        "チャットパネルはどこですか": ("ringcentral.video.toolbar.chat", True),
    }

    for question, (entrypoint_id, can_operate) in expected.items():
        response = answer_question(
            package=package,
            question=question,
            voice=PresenterVoiceSettings(language="ja"),
        )
        assert response.entrypoint_id == entrypoint_id
        assert response.can_operate is can_operate

    notes_response = answer_question(
        package=package,
        question="ノートと文字起こしの場所はどこですか",
        voice=PresenterVoiceSettings(language="ja"),
    )
    assert notes_response.entrypoint_id == "ringcentral.video.more.notes"
    assert notes_response.can_operate is False
    assert create_question_interrupt_step(package, notes_response) is None

    camera_response = answer_question(
        package=package,
        question="カメラメニューはどこですか",
        voice=PresenterVoiceSettings(language="ja"),
    )
    assert camera_response.entrypoint_id != "ringcentral.video.toolbar.video"


def test_ringcentral_spanish_location_questions_match_package_aliases_without_legacy_table(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    monkeypatch.setattr(questions_module, "_ENTRYPOINT_ALIASES", {})

    expected = {
        "¿Dónde está la pestaña de video en ringcentral?": (
            "ringcentral.develop.video.tab",
            False,
        ),
        "¿Dónde está el botón start en ringcentral video?": (
            "ringcentral.develop.video.start",
            False,
        ),
        "Explícame el mapa de controles de reunión": (
            "ringcentral.video.overview",
            False,
        ),
        "¿Dónde está la ubicación de meeting information?": (
            "ringcentral.video.top.meeting-info",
            False,
        ),
        "¿Dónde veo la ubicación de network quality?": (
            "ringcentral.video.top.network-quality",
            True,
        ),
        "¿Dónde está el menú de vista de reunión?": (
            "ringcentral.video.top.views",
            True,
        ),
        "¿Dónde está la ubicación de report issue?": (
            "ringcentral.video.top.report-issue",
            True,
        ),
        "¿Dónde está la ubicación de add coworkers?": (
            "ringcentral.video.main.add-coworkers",
            False,
        ),
        "¿Dónde está la ubicación del botón mute?": (
            "ringcentral.video.toolbar.audio",
            False,
        ),
        "¿Dónde está el menú de audio de la reunión?": (
            "ringcentral.video.toolbar.audio-menu",
            False,
        ),
        "¿Dónde está la ubicación de start video?": (
            "ringcentral.video.toolbar.video",
            False,
        ),
        "¿Dónde está el menú de cámara en la reunión?": (
            "ringcentral.video.toolbar.video-menu",
            True,
        ),
        "¿Dónde está la configuración avanzada de video?": (
            "ringcentral.video.settings.video",
            True,
        ),
        "¿Dónde están los ajustes de fondo?": (
            "ringcentral.video.settings.background",
            True,
        ),
        "¿Dónde está el selector de compartir pantalla?": (
            "ringcentral.video.toolbar.share",
            False,
        ),
        "¿Dónde está la ubicación de invite?": (
            "ringcentral.video.toolbar.invite",
            False,
        ),
        "Muéstrame el panel de participantes": (
            "ringcentral.video.toolbar.participants",
            True,
        ),
        "¿Dónde está el panel de chat de la reunión?": (
            "ringcentral.video.toolbar.chat",
            True,
        ),
        "¿Dónde está la ubicación de reactions?": (
            "ringcentral.video.toolbar.react",
            False,
        ),
        "¿Dónde está el botón de levantar la mano?": (
            "ringcentral.video.toolbar.raise-hand",
            False,
        ),
        "¿Dónde está el menú de más acciones?": (
            "ringcentral.video.toolbar.more",
            True,
        ),
        "¿Dónde está la ubicación de start recording?": (
            "ringcentral.video.more.recording",
            False,
        ),
        "¿Dónde está la ubicación de notes and transcript?": (
            "ringcentral.video.more.notes",
            False,
        ),
        "¿Dónde está la ubicación de background en more?": (
            "ringcentral.video.more.background",
            True,
        ),
        "¿Dónde está la ubicación de settings en more?": (
            "ringcentral.video.more.settings",
            True,
        ),
        "¿Dónde está la ubicación del botón leave?": (
            "ringcentral.video.toolbar.leave",
            False,
        ),
    }

    for question, (entrypoint_id, can_operate) in expected.items():
        response = answer_question(
            package=package,
            question=question,
            voice=PresenterVoiceSettings(language="en"),
        )
        assert response.entrypoint_id == entrypoint_id
        assert response.can_operate is can_operate

    notes_response = answer_question(
        package=package,
        question="¿Dónde está la ubicación de notes and transcript?",
        voice=PresenterVoiceSettings(language="en"),
    )
    assert create_question_interrupt_step(package, notes_response) is None


def test_spanish_entrypoint_answer_uses_package_alias_label() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="panel de participantes",
        voice=PresenterVoiceSettings(language="es"),
    )

    assert response.entrypoint_id == "ringcentral.video.toolbar.participants"
    assert response.can_operate is True
    assert response.answer_text.startswith("panel de participantes:")
    assert not response.answer_text.startswith("Participants panel:")


@pytest.mark.parametrize(
    ("question", "entrypoint_id", "title", "purpose", "english_purpose"),
    [
        (
            "resumen de la ventana de reunión",
            "ringcentral.video.overview",
            "Resumen de la reunión",
            (
                "Presenta la superficie de RingCentral Video antes de abrir controles "
                "individuales."
            ),
            (
                "Introduce the RingCentral Video meeting surface before opening "
                "individual controls."
            ),
        ),
        (
            "panel de calidad de red",
            "ringcentral.video.top.network-quality",
            "Calidad de red",
            (
                "Abre Network quality para revisar packet loss, jitter y latency de Share, "
                "video y audio cuando la reunión se siente inestable."
            ),
            (
                "Show diagnostic network quality for sharing, video, and audio, "
                "including packet loss, jitter, and latency."
            ),
        ),
        (
            "menú de vista de reunión",
            "ringcentral.video.top.views",
            "Diseño de vista",
            (
                "Abre Views para revisar Gallery view o Full screen en tu vista local "
                "sin cambiar audio, video ni participantes."
            ),
            "Switch the meeting layout, including Gallery view and Full screen.",
        ),
        (
            "menú de más acciones",
            "ringcentral.video.toolbar.more",
            "Más acciones",
            (
                "Abre More para mostrar acciones adicionales de la reunión y explicar "
                "su ubicación sin iniciar grabaciones ni otros cambios."
            ),
            "Open additional meeting actions.",
        ),
        (
            "ubicación de settings en more",
            "ringcentral.video.more.settings",
            "Ajustes",
            (
                "Abre Settings para revisar opciones de audio, video, Background, "
                "Translation, Join preferences y General sin cambiar configuraciones "
                "ni leer datos privados."
            ),
            "Open the Settings dialog.",
        ),
    ],
)
def test_ringcentral_spanish_entrypoint_answer_uses_localized_pilot_copy(
    question: str,
    entrypoint_id: str,
    title: str,
    purpose: str,
    english_purpose: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="es"),
    )

    assert response.entrypoint_id == entrypoint_id
    assert response.answer_text == f"{title}: {purpose}"
    assert english_purpose not in response.answer_text


def test_ringcentral_spanish_unseeded_entrypoint_keeps_alias_label_fallback() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="panel de participantes",
        voice=PresenterVoiceSettings(language="es"),
    )

    assert response.entrypoint_id == "ringcentral.video.toolbar.participants"
    assert response.answer_text == (
        "panel de participantes: Open participant list and meeting people controls."
    )
    assert not response.answer_text.startswith("Participants panel:")


@pytest.mark.parametrize(
    ("question", "language"),
    [
        ("panel de participantes", "en"),
        ("\u8c01\u5728\u4f1a\u8bae\u91cc", "zh"),
        ("\u53c2\u52a0\u8005\u4e00\u89a7\u306f\u3069\u3053\u3067\u3059\u304b", "ja"),
    ],
)
def test_non_spanish_entrypoint_answers_keep_canonical_title_label(
    question: str,
    language: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language=language),
    )

    assert response.entrypoint_id == "ringcentral.video.toolbar.participants"
    assert response.answer_text.startswith("Participants panel:")
    assert not response.answer_text.startswith("panel de participantes:")


@pytest.mark.parametrize(
    ("question", "entrypoint_id"),
    [
        ("¿Puede leer los mensajes del chat o los nombres de participantes?", None),
        (
            "¿Puede el presenter describir el contenido compartido en pantalla?",
            "ringcentral.video.toolbar.share",
        ),
        (
            "¿Cómo manejo la grabación de la reunión de forma segura?",
            "ringcentral.video.more.recording",
        ),
        (
            "¿Puede AiPresenter enviar una reacción o levantar la mano de forma segura?",
            None,
        ),
    ],
)
def test_ringcentral_spanish_safety_questions_stay_qa_first_with_aliases(
    monkeypatch: pytest.MonkeyPatch,
    question: str,
    entrypoint_id: str | None,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    monkeypatch.setattr(questions_module, "_ENTRYPOINT_ALIASES", {})

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="en"),
    )

    assert response.entrypoint_id == entrypoint_id
    assert response.can_operate is False


def test_ringcentral_spanish_unaccented_location_questions_match_curated_aliases(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    monkeypatch.setattr(questions_module, "_ENTRYPOINT_ALIASES", {})

    expected = {
        "Donde esta el menu de camara en la reunion?": (
            "ringcentral.video.toolbar.video-menu",
            True,
        ),
        "Donde esta el panel de informacion de la reunion?": (
            "ringcentral.video.top.meeting-info",
            False,
        ),
        "Donde esta el boton de levantar la mano?": (
            "ringcentral.video.toolbar.raise-hand",
            False,
        ),
        "Donde esta la configuracion avanzada de video?": (
            "ringcentral.video.settings.video",
            True,
        ),
        "Donde esta el estado del microfono en reunion?": (
            "ringcentral.video.toolbar.audio",
            False,
        ),
        "Donde esta el panel de notas y transcripcion?": (
            "ringcentral.video.more.notes",
            False,
        ),
    }

    for question, (entrypoint_id, can_operate) in expected.items():
        response = answer_question(
            package=package,
            question=question,
            voice=PresenterVoiceSettings(language="en"),
        )
        assert response.entrypoint_id == entrypoint_id
        assert response.can_operate is can_operate


@pytest.mark.parametrize(
    ("question", "entrypoint_id"),
    [
        (
            "Como manejo la grabacion de la reunion de forma segura?",
            "ringcentral.video.more.recording",
        ),
        (
            "Puede AiPresenter enviar una reaccion o levantar la mano de forma segura?",
            None,
        ),
        ("Puede leer los mensajes del chat o los nombres de participantes?", None),
    ],
)
def test_ringcentral_spanish_unaccented_safety_questions_stay_qa_first(
    monkeypatch: pytest.MonkeyPatch,
    question: str,
    entrypoint_id: str | None,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    monkeypatch.setattr(questions_module, "_ENTRYPOINT_ALIASES", {})

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="en"),
    )

    assert response.entrypoint_id == entrypoint_id
    assert response.can_operate is False


def test_ringcentral_japanese_chat_privacy_question_stays_answer_only_with_aliases(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    monkeypatch.setattr(questions_module, "_ENTRYPOINT_ALIASES", {})

    response = answer_question(
        package=package,
        question="チャット内容や参加者名を読み上げられますか",
        voice=PresenterVoiceSettings(language="ja", tone="professional"),
    )

    assert response.entrypoint_id is None
    assert response.can_operate is False
    assert "チャットメッセージ" in response.answer_text
    assert "読み上げません" in response.answer_text


def test_ringcentral_japanese_audio_troubleshooting_question_stays_qa_with_aliases(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    monkeypatch.setattr(questions_module, "_ENTRYPOINT_ALIASES", {})

    response = answer_question(
        package=package,
        question="音声や映像が途切れるときはどうすればいいですか",
        voice=PresenterVoiceSettings(language="ja", tone="professional"),
    )

    assert response.entrypoint_id == "ringcentral.video.top.network-quality"
    assert response.can_operate is True
    assert "Network quality" in response.answer_text
    assert "パケットロス" in response.answer_text


@pytest.mark.parametrize(
    "question",
    [
        "meeting information",
        "where is the meeting ID",
        "where is the meeting link",
        "会議情報の場所はどこですか",
        "Meeting information の場所はどこですか",
        "会議詳細の入口はどこですか",
        "\u4f1a\u8bae\u53f7\u5728\u54ea\u91cc",
    ],
)
def test_meeting_info_privacy_questions_are_answer_only(question: str) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    language = "en"
    if any("\u3040" <= char <= "\u30ff" for char in question):
        language = "ja"
    elif "\u4f1a\u8bae" in question:
        language = "zh"

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language=language),
    )

    assert response.entrypoint_id == "ringcentral.video.top.meeting-info"
    assert response.can_operate is False
    assert "Meeting information:" in response.answer_text
    assert "meeting ID" in response.answer_text
    assert "copy link" in response.answer_text
    assert "https://" not in response.answer_text
    assert "ringcentral.com" not in response.answer_text
    assert "123456789" not in response.answer_text


def test_chinese_meeting_link_short_question_uses_privacy_qa() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="\u4f1a\u8bae\u94fe\u63a5",
        voice=PresenterVoiceSettings(language="zh"),
    )

    assert response.entrypoint_id == "ringcentral.video.top.meeting-info"
    assert response.can_operate is False
    assert "\u79c1\u4eba\u4f1a\u8bae\u8be6\u60c5" in response.answer_text
    assert "Meeting information:" not in response.answer_text
    assert create_question_interrupt_step(package, response) is None


@pytest.mark.parametrize(
    "question",
    [
        "会議IDを読んで",
        "会議リンクをコピーして",
        "招待リンクをコピーして",
    ],
)
def test_ringcentral_japanese_meeting_info_value_or_copy_requests_stay_non_operable(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="ja"),
    )

    assert response.can_operate is False
    assert response.entrypoint_id not in {
        "ringcentral.video.toolbar.add-coworkers",
        "ringcentral.video.toolbar.invite",
    }


@pytest.mark.parametrize(
    "question",
    [
        "UIを全部制御できますか",
        "全コントロールを操作して",
    ],
)
def test_ringcentral_japanese_overview_control_overclaims_stay_non_operable(
    question: str,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(language="ja"),
    )

    assert response.can_operate is False


def test_meeting_info_privacy_gate_does_not_depend_on_risky_words(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    monkeypatch.setattr(questions_module, "_RISKY_ENTRYPOINT_WORDS", frozenset())

    response = answer_question(
        package=package,
        question="meeting information",
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id == "ringcentral.video.top.meeting-info"
    assert response.can_operate is False


def test_notes_privacy_gate_does_not_depend_on_risky_words(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    monkeypatch.setattr(questions_module, "_RISKY_ENTRYPOINT_WORDS", frozenset())

    response = answer_question(
        package=package,
        question="notes",
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id == "ringcentral.video.more.notes"
    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None


def test_network_quality_question_remains_operable_without_answer_only_policy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    monkeypatch.setattr(questions_module, "_RISKY_ENTRYPOINT_WORDS", frozenset())

    response = answer_question(
        package=package,
        question="network quality",
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id == "ringcentral.video.top.network-quality"
    assert response.can_operate is True


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


def test_legacy_alias_matches_are_precomputed_longest_first(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        questions_module,
        "_ENTRYPOINT_ALIASES",
        {
            "demo.short": ("aa",),
            "demo.long": ("AAAA", "bbb"),
        },
    )

    assert questions_module._legacy_entrypoint_alias_matches() == (
        ("demo.long", "aaaa"),
        ("demo.long", "bbb"),
        ("demo.short", "aa"),
    )


def test_legacy_alias_match_cache_rebuilds_after_in_place_alias_change(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    aliases = {"demo.short": ("aa",)}
    monkeypatch.setattr(questions_module, "_ENTRYPOINT_ALIASES", aliases)

    assert questions_module._legacy_entrypoint_alias_matches() == (("demo.short", "aa"),)

    aliases["demo.long"] = ("BBBB",)

    assert questions_module._legacy_entrypoint_alias_matches() == (
        ("demo.long", "bbbb"),
        ("demo.short", "aa"),
    )


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
    assert response.can_operate is False
    assert create_question_interrupt_step(package, response) is None


def test_participants_matches_participants_entrypoint() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="participants",
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id == "ringcentral.video.toolbar.participants"
    assert response.answer_text.startswith("Participants panel:")
    assert "host or moderator" not in response.answer_text


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
    assert "Recording changes the meeting state" in response.answer_text
    assert "participant consent" in response.answer_text
    assert "Start recording:" not in response.answer_text


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


def test_chinese_no_match_fallback_is_localized_and_not_operable() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="quantum waffle",
        voice=PresenterVoiceSettings(language="zh", tone="professional"),
    )

    assert response.entrypoint_id is None
    assert response.can_operate is False
    assert "\u5f53\u524d\u5e94\u7528\u4e0a\u4e0b\u6587" in response.answer_text
    assert "I could not find" not in response.answer_text


def test_spanish_no_match_fallback_is_localized_and_not_operable() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="quantum waffle",
        voice=PresenterVoiceSettings(language="es", tone="professional"),
    )

    assert response.entrypoint_id is None
    assert response.can_operate is False
    assert "No encontre" in response.answer_text
    assert "I could not find" not in response.answer_text


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
