from pathlib import Path
from types import MappingProxyType

import pytest
from pydantic import ValidationError

from ai_presenter.packages.localization_status import build_localization_status
from ai_presenter.packages.localization_status import render_localization_status_lines
from ai_presenter.packages.loader import load_material_package
from ai_presenter.packages.models import MaterialPackage
from ai_presenter.runtime.voice import PresenterVoiceSettings
from ai_presenter.runtime.voice import render_narration_text

EXECUTABLE_DEMO_STEP_OPERATIONS = {"open", "toggle", "select"}


def has_cjk(text: str) -> bool:
    return any("\u4e00" <= character <= "\u9fff" for character in text)


def test_loads_ringcentral_video_app_material_package() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    assert package.app_id == "ringcentral-video"
    assert package.app_name == "RingCentral Video"
    assert "ringcentral-video-codex-cli-speaker" in package.profile_ids
    assert "ringcentral-video-piper-speaker" in package.profile_ids
    assert package.operation_entrypoints[0].id == "ringcentral.develop.video.tab"
    assert package.entrypoint_by_id("ringcentral.video.settings.background").area == "Settings"
    assert package.entrypoint_by_id("ringcentral.video.toolbar.share").area == "Meeting toolbar"
    assert package.entrypoint_by_id("ringcentral.video.toolbar.chat").purpose == (
        "Open in-meeting chat."
    )
    assert package.demo_flows[0].id == "vbg-blur-demo"
    assert package.demo_flows[0].steps[1].action.entrypoint_id == (
        "ringcentral.video.settings.background"
    )
    controls_tour = next(flow for flow in package.demo_flows if flow.id == "meeting-controls-tour")
    assert controls_tour.steps[-1].action.entrypoint_id == "ringcentral.video.toolbar.leave"
    assert controls_tour.steps[-1].action.operation == "explain"
    assert controls_tour.steps[0].id == "meeting-overview"
    assert all(not step.id.endswith("-section") for step in controls_tour.steps)
    for step in controls_tour.steps:
        entrypoint = package.entrypoint_by_id(step.action.entrypoint_id)
        if step.action.operation in {"open", "toggle"}:
            assert_supported_open_step(entrypoint.open_steps[0])
            assert step.narration.placement == "during"
            assert step.narration.action_offset_ms <= 500
        step.narration.text.encode("ascii")
    assert package.entrypoint_by_id("ringcentral.video.top.report-issue").presenter_notes[0].startswith(
        "This opens a foreground dialog"
    )
    notes_entrypoint = package.entrypoint_by_id("ringcentral.video.more.notes")
    assert [step.target for step in notes_entrypoint.open_steps] == [
        "More",
        "onconf.controls.NOTES",
    ]
    assert notes_entrypoint.open_steps[0].match["controlType"] == "button"
    assert notes_entrypoint.open_steps[1].match["controlType"] == "menuitem"
    assert notes_entrypoint.open_steps[1].match["alternateTargets"] == "Notes"
    assert notes_entrypoint.open_steps[-1].match["cleanup"] == "sidePanel"
    assert package.entrypoint_by_id("ringcentral.video.toolbar.audio-menu").purpose.startswith(
        "Open microphone and speaker"
    )
    assert package.explainers["participants"].short_script.startswith("Participants")
    assert package.explainers["audio"].short_script.startswith("The audio controls")
    assert package.qa[0].question == "How do I protect my real background?"


def test_question_answers_support_localized_questions_and_answers() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    item = next(qa for qa in package.qa if qa.question == "How do I protect my real background?")

    assert "zh" in item.localized_questions
    assert "怎么保护我的真实背景" in item.localized_questions["zh"]
    assert item.localized_answers["zh"].startswith("打开 Settings")


def test_ringcentral_all_qa_items_have_chinese_localized_questions_and_answers() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    entrypoint_ids = {entrypoint.id for entrypoint in package.operation_entrypoints}

    for item in package.qa:
        assert item.localized_questions.get("zh"), item.question
        assert item.localized_answers.get("zh", "").strip(), item.question
        assert set(item.related_entrypoint_ids) <= entrypoint_ids


def test_ringcentral_all_qa_items_have_japanese_localized_questions_and_answers() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    entrypoint_ids = {entrypoint.id for entrypoint in package.operation_entrypoints}

    for item in package.qa:
        assert item.localized_questions.get("ja"), item.question
        assert item.localized_answers.get("ja", "").strip(), item.question
        assert set(item.related_entrypoint_ids) <= entrypoint_ids


def test_ringcentral_localization_status_reports_chinese_coverage() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    report = build_localization_status(package, language="zh")

    assert report.package_id == "ringcentral-video"
    assert report.package_version == 1
    assert report.language == "zh"
    assert report.demo_localized_steps == 51
    assert report.demo_total_steps == 51
    assert report.qa_localized_questions == 12
    assert report.qa_localized_answers == 12
    assert report.qa_total == 12
    assert report.entrypoints_with_aliases == 15
    assert report.entrypoint_total == 27
    assert report.alias_total == 49
    assert report.flow_by_id["meeting-controls-tour"].localized_steps == 22
    assert report.flow_by_id["meeting-controls-tour"].total_steps == 22


def test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    report = build_localization_status(package, language="ja")

    assert report.package_id == "ringcentral-video"
    assert report.language == "ja"
    assert report.demo_localized_steps == 7
    assert report.demo_total_steps == 51
    assert report.qa_localized_questions == 12
    assert report.qa_localized_answers == 12
    assert report.qa_total == 12
    assert report.entrypoints_with_aliases == 3
    assert report.entrypoint_total == 27
    assert report.alias_total == 9
    assert report.required_localization_complete is False
    assert report.flow_by_id["vbg-blur-demo"].localized_steps == 4
    assert report.flow_by_id["vbg-blur-demo"].total_steps == 4
    assert report.flow_by_id["meeting-basics-demo"].localized_steps == 3
    assert report.flow_by_id["meeting-basics-demo"].total_steps == 3
    assert report.flow_by_id["meeting-controls-tour"].localized_steps == 0


def test_localization_status_marks_required_chinese_coverage_complete() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    report = build_localization_status(package, language="zh")

    assert report.required_localization_complete is True


def test_localization_status_renders_partial_coverage_without_failing() -> None:
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
                    "purpose": "Open panel.",
                    "questionAliases": {"zh": ["panel alias"]},
                    "openSteps": [],
                },
                {
                    "id": "demo.other",
                    "title": "Other",
                    "area": "Main",
                    "purpose": "Other panel.",
                    "openSteps": [],
                },
            ],
            "demoFlows": [
                {
                    "id": "onboarding-demo",
                    "title": "Onboarding",
                    "goal": "Show onboarding.",
                    "steps": [
                        {
                            "id": "intro",
                            "title": "Intro",
                            "action": {
                                "entrypointId": "demo.panel",
                                "operation": "explain",
                            },
                            "narration": {
                                "text": "Show the panel.",
                                "localizedText": {"zh": "Localized panel."},
                            },
                        },
                        {
                            "id": "missing",
                            "title": "Missing",
                            "action": {
                                "entrypointId": "demo.other",
                                "operation": "explain",
                            },
                            "narration": {"text": "Show the missing panel."},
                        },
                    ],
                }
            ],
            "qa": [
                {
                    "question": "Where is the panel?",
                    "answer": "Open Panel.",
                    "localizedQuestions": {"zh": ["Panel?"]},
                    "localizedAnswers": {},
                    "relatedEntrypointIds": ["demo.panel"],
                }
            ],
            "manualControls": [],
        }
    )

    report = build_localization_status(package, language="zh")
    lines = render_localization_status_lines(report)

    assert report.demo_localized_steps == 1
    assert report.demo_total_steps == 2
    assert report.qa_localized_questions == 1
    assert report.qa_localized_answers == 0
    assert report.entrypoints_with_aliases == 1
    assert report.alias_total == 1
    assert "- onboarding-demo: 1/2 narration localized" in lines
    assert "  missing: missing" in lines
    assert "  missing answers: #1 Where is the panel?" in lines


def test_localization_status_treats_blank_localized_questions_as_missing() -> None:
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
                    "purpose": "Open panel.",
                    "openSteps": [],
                }
            ],
            "demoFlows": [],
            "qa": [
                {
                    "question": "Where is the panel?",
                    "answer": "Open Panel.",
                    "localizedQuestions": {"zh": ["  "]},
                    "localizedAnswers": {"zh": "打开面板。"},
                    "relatedEntrypointIds": ["demo.panel"],
                }
            ],
            "manualControls": [],
        }
    )

    report = build_localization_status(package, language="zh")
    lines = render_localization_status_lines(report)

    assert report.qa_localized_questions == 0
    assert report.qa_localized_answers == 1
    assert "  missing questions: #1 Where is the panel?" in lines


def test_localization_status_reports_zero_for_explicit_uncovered_language() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    report = build_localization_status(package, language="fr")

    assert report.language == "fr"
    assert report.demo_localized_steps == 0
    assert report.demo_total_steps == 51
    assert report.qa_localized_questions == 0
    assert report.qa_localized_answers == 0
    assert report.entrypoints_with_aliases == 0
    assert report.alias_total == 0


def test_localization_status_marks_uncovered_language_incomplete() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    report = build_localization_status(package, language="ja")

    assert report.required_localization_complete is False


def test_localization_status_completion_ignores_alias_coverage_gaps() -> None:
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
                    "purpose": "Open panel.",
                    "openSteps": [],
                }
            ],
            "demoFlows": [
                {
                    "id": "onboarding-demo",
                    "title": "Onboarding",
                    "goal": "Show onboarding.",
                    "steps": [
                        {
                            "id": "intro",
                            "title": "Intro",
                            "action": {
                                "entrypointId": "demo.panel",
                                "operation": "explain",
                            },
                            "narration": {
                                "text": "Show the panel.",
                                "localizedText": {"zh": "Localized panel."},
                            },
                        }
                    ],
                }
            ],
            "qa": [
                {
                    "question": "Where is the panel?",
                    "answer": "Open Panel.",
                    "localizedQuestions": {"zh": ["Where is the localized panel?"]},
                    "localizedAnswers": {"zh": "Open the localized panel."},
                    "relatedEntrypointIds": ["demo.panel"],
                }
            ],
            "manualControls": [],
        }
    )

    report = build_localization_status(package, language="zh")

    assert report.entrypoints_with_aliases == 0
    assert report.alias_total == 0
    assert report.required_localization_complete is True


def test_ringcentral_package_owns_chinese_aliases_for_question_routes() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    aliases_by_entrypoint: dict[str, set[str]] = {}
    for alias in package.entrypoint_question_aliases:
        if alias.language != "zh":
            continue
        aliases_by_entrypoint.setdefault(alias.entrypoint_id, set()).add(alias.alias)

    expected_aliases = {
        "ringcentral.video.main.add-coworkers": {"加同事", "邀请同事", "拉人入会"},
        "ringcentral.video.toolbar.participants": {"参会者", "参会人列表", "谁在会议里"},
        "ringcentral.video.toolbar.audio": {"麦克风", "静音", "声音"},
        "ringcentral.video.toolbar.audio-menu": {"音频设置", "换麦克风", "换扬声器"},
        "ringcentral.video.toolbar.video": {"摄像头", "开视频", "关视频"},
        "ringcentral.video.toolbar.video-menu": {"视频设置", "换摄像头", "摄像头菜单"},
        "ringcentral.video.top.network-quality": {"网络质量", "连接质量", "卡顿"},
        "ringcentral.video.top.meeting-info": {"会议信息", "会议号", "会议链接"},
        "ringcentral.video.more.notes": {"笔记", "转录", "会议笔记"},
        "ringcentral.video.more.recording": {"录制", "录像", "记录会议"},
    }

    for entrypoint_id, aliases in expected_aliases.items():
        assert aliases <= aliases_by_entrypoint.get(entrypoint_id, set())


def test_ringcentral_package_owns_japanese_aliases_for_meeting_basics_routes() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    aliases_by_entrypoint: dict[str, set[str]] = {}
    for alias in package.entrypoint_question_aliases:
        if alias.language != "ja":
            continue
        aliases_by_entrypoint.setdefault(alias.entrypoint_id, set()).add(alias.alias)

    expected_aliases = {
        "ringcentral.video.toolbar.audio": {"マイク", "ミュート", "音声"},
        "ringcentral.video.toolbar.participants": {"参加者", "参加者一覧", "参加者パネル"},
        "ringcentral.video.toolbar.chat": {"チャット", "チャットパネル", "メッセージ"},
    }

    assert set(aliases_by_entrypoint) == set(expected_aliases)
    for entrypoint_id, aliases in expected_aliases.items():
        assert aliases == aliases_by_entrypoint[entrypoint_id]


def test_operation_entrypoints_support_package_owned_question_aliases() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    chat = package.entrypoint_by_id("ringcentral.video.toolbar.chat")

    assert "zh" in chat.question_aliases
    assert "聊天在哪里" in chat.question_aliases["zh"]


def test_material_package_exposes_read_only_entrypoint_index() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    index = package.entrypoints_by_id

    assert isinstance(index, MappingProxyType)
    assert index["ringcentral.video.toolbar.chat"] is package.entrypoint_by_id(
        "ringcentral.video.toolbar.chat"
    )
    assert set(index) == {entrypoint.id for entrypoint in package.operation_entrypoints}


def test_entrypoint_by_id_preserves_unknown_id_error() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    with pytest.raises(KeyError, match="Unknown operation entrypoint: missing.entrypoint"):
        package.entrypoint_by_id("missing.entrypoint")


def test_material_package_exposes_read_only_demo_flow_index() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    index = package.demo_flows_by_id

    assert isinstance(index, MappingProxyType)
    assert index["meeting-control-map-demo"] is package.demo_flow_by_id(
        "meeting-control-map-demo"
    )
    assert set(index) == {flow.id for flow in package.demo_flows}


def test_demo_flow_by_id_preserves_unknown_id_error() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    with pytest.raises(
        KeyError,
        match="Unknown demo flow: missing-flow. Available flows:",
    ):
        package.demo_flow_by_id("missing-flow")


def test_material_package_exposes_precomputed_qa_question_candidates() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    item = package.qa[0]

    candidates = package.qa_question_candidates

    assert isinstance(candidates, tuple)
    assert any(candidate.item is item and candidate.question == item.question for candidate in candidates)
    localized_question = item.localized_questions["zh"][0]
    localized_candidate = next(
        candidate for candidate in candidates if candidate.question == localized_question
    )
    assert localized_candidate.item is item
    assert localized_candidate.normalized_question == localized_question.casefold()
    assert isinstance(localized_candidate.meaningful_tokens, frozenset)


def test_material_package_exposes_read_only_qa_question_index() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    item = package.qa[0]
    localized_question = item.localized_questions["zh"][0]

    index = package.qa_questions_by_normalized

    assert isinstance(index, MappingProxyType)
    assert index[item.question.casefold()] is item
    assert index[localized_question.casefold()] is item


def test_material_package_trims_and_skips_blank_qa_question_candidates() -> None:
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
                    "question": " Where is privacy? ",
                    "answer": "Open privacy.",
                    "localizedQuestions": {
                        "zh": [" \u9690\u79c1\u5728\u54ea\u91cc ", "  "],
                    },
                }
            ],
            "manualControls": [],
        }
    )

    normalized_questions = [
        candidate.normalized_question for candidate in package.qa_question_candidates
    ]

    assert normalized_questions == [
        "where is privacy?",
        "\u9690\u79c1\u5728\u54ea\u91cc",
    ]
    assert "" not in package.qa_questions_by_normalized
    assert package.qa_questions_by_normalized["where is privacy?"] is package.qa[0]
    assert package.qa_questions_by_normalized["\u9690\u79c1\u5728\u54ea\u91cc"] is package.qa[0]


def test_qa_question_index_keeps_first_duplicate_match() -> None:
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
                    "answer": "First answer.",
                },
                {
                    "question": "where is privacy?",
                    "answer": "Second answer.",
                },
            ],
            "manualControls": [],
        }
    )

    assert package.qa_questions_by_normalized["where is privacy?"] is package.qa[0]


def test_material_package_exposes_precomputed_entrypoint_match_candidates() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    candidates = package.entrypoint_match_candidates
    chat = package.entrypoint_by_id("ringcentral.video.toolbar.chat")
    chat_candidate = next(candidate for candidate in candidates if candidate.entrypoint is chat)

    assert isinstance(candidates, tuple)
    assert [candidate.entrypoint.id for candidate in candidates] == [
        entrypoint.id for entrypoint in package.operation_entrypoints
    ]
    assert "chat" in chat_candidate.id_tokens
    assert "chat" in chat_candidate.title_tokens
    assert chat_candidate.title_or_id_tokens == chat_candidate.title_tokens | chat_candidate.id_tokens


def test_with_demo_flow_rebuilds_runtime_indexes_for_appended_flow() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flows[0].model_copy(update={"id": "copy-flow"})

    copied = package.with_demo_flow(flow)

    assert copied.demo_flow_by_id("copy-flow").id == "copy-flow"
    assert "copy-flow" in copied.demo_flows_by_id
    assert "copy-flow" not in package.demo_flows_by_id
    assert copied.qa_question_candidates[0].item is copied.qa[0]
    assert copied.qa_questions_by_normalized[copied.qa[0].question.casefold()] is copied.qa[0]
    assert copied.entrypoint_match_candidates[0].entrypoint is copied.operation_entrypoints[0]
    assert copied.entrypoint_question_aliases_by_match_order
    assert (
        copied.entrypoint_question_aliases_by_match_order
        is not package.entrypoint_question_aliases_by_match_order
    )
    assert copied.qa_question_candidates[0].item is not package.qa[0]
    assert copied.qa_questions_by_normalized[copied.qa[0].question.casefold()] is not package.qa[0]
    assert copied.entrypoint_match_candidates[0].entrypoint is not package.operation_entrypoints[0]


def test_material_package_exposes_entrypoint_question_aliases_by_match_order() -> None:
    package = MaterialPackage.model_validate(
        {
            "appId": "demo",
            "appName": "Demo",
            "version": 1,
            "profileIds": ["demo-profile"],
            "operationEntrypoints": [
                {
                    "id": "demo.one",
                    "title": "One",
                    "area": "Main",
                    "purpose": "Open one.",
                    "questionAliases": {"en": ["aa", "bbbb"]},
                },
                {
                    "id": "demo.two",
                    "title": "Two",
                    "area": "Main",
                    "purpose": "Open two.",
                    "questionAliases": {"en": ["cccc", "d"]},
                },
            ],
            "demoFlows": [],
            "manualControls": [],
        }
    )

    assert [alias.normalized_alias for alias in package.entrypoint_question_aliases] == [
        "aa",
        "bbbb",
        "cccc",
        "d",
    ]
    assert [
        alias.normalized_alias
        for alias in package.entrypoint_question_aliases_by_match_order
    ] == ["bbbb", "cccc", "aa", "d"]


def test_material_package_exposes_normalized_question_alias_index() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    chat = package.entrypoint_by_id("ringcentral.video.toolbar.chat")
    expected_alias = chat.question_aliases["zh"][0]

    aliases = [
        alias
        for alias in package.entrypoint_question_aliases
        if alias.entrypoint_id == "ringcentral.video.toolbar.chat"
    ]

    assert aliases
    assert any(alias.language == "zh" for alias in aliases)
    assert any(alias.alias == expected_alias for alias in aliases)
    assert any(alias.normalized_alias == expected_alias.casefold() for alias in aliases)


def test_runtime_indexes_do_not_leak_into_model_dump() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    dumped = package.model_dump(by_alias=True)

    assert "entrypointsById" not in dumped
    assert "entrypointQuestionAliases" not in dumped
    assert "entrypointQuestionAliasesByMatchOrder" not in dumped
    assert "qaQuestionCandidates" not in dumped
    assert "qaQuestionsByNormalized" not in dumped
    assert "entrypointMatchCandidates" not in dumped
    assert "_entrypoints_by_id" not in dumped
    assert "_entrypoint_question_aliases" not in dumped
    assert "_entrypoint_question_aliases_by_match_order" not in dumped
    assert "_qa_question_candidates" not in dumped
    assert "_qa_questions_by_normalized" not in dumped
    assert "_entrypoint_match_candidates" not in dumped
    assert "operationEntrypoints" in dumped


def test_ringcentral_add_coworkers_uses_observed_uia_button_route() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    entrypoint = package.entrypoint_by_id("ringcentral.video.main.add-coworkers")

    assert len(entrypoint.open_steps) == 1
    step = entrypoint.open_steps[0]
    assert step.action == "clickWindowControl"
    assert step.target == "Add coworkers"
    assert step.match["controlType"] == "button"
    assert step.match["cleanup"] == "modal"


def test_ringcentral_validation_checklist_covers_package_routes() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    knowledge_dir = Path("docs/knowledge/ringcentral-video")

    checklist_text = (knowledge_dir / "validation-checklist-index.md").read_text(
        encoding="utf-8"
    )
    evidence_text = (knowledge_dir / "evidence-index.md").read_text(encoding="utf-8")
    source_text = (knowledge_dir / "source-index.md").read_text(encoding="utf-8")

    missing_entrypoints = [
        entrypoint.id
        for entrypoint in package.operation_entrypoints
        if entrypoint.id not in checklist_text
    ]
    missing_flows = [
        flow.id for flow in package.demo_flows if flow.id not in evidence_text
    ]

    assert missing_entrypoints == []
    assert missing_flows == []
    assert "validation-checklist-index.md" in evidence_text
    assert "validation-checklist-index.md" in source_text
    assert "acceptance-runs.md" in checklist_text
    assert "Do Not Execute Yet" in checklist_text
    assert "ringcentral.video.main.add-coworkers" in checklist_text
    assert "ringcentral.video.more.recording" in checklist_text
    assert "ringcentral.video.toolbar.leave" in checklist_text
    assert "runbook checkboxes are not acceptance evidence" in checklist_text


def test_demo_flow_actions_use_supported_executor_steps() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    for flow in package.demo_flows:
        for step in flow.steps:
            if step.action.operation not in EXECUTABLE_DEMO_STEP_OPERATIONS:
                continue

            entrypoint = package.entrypoint_by_id(step.action.entrypoint_id)
            assert entrypoint.open_steps, f"{flow.id}:{step.id} has no executable steps"
            for open_step in entrypoint.open_steps:
                assert_supported_open_step(open_step)

    vbg_flow = next(flow for flow in package.demo_flows if flow.id == "vbg-blur-demo")
    select_step = next(step for step in vbg_flow.steps if step.id == "select-blur")
    assert select_step.action.entrypoint_id == "ringcentral.video.settings.background.blur"


def test_ringcentral_material_package_explains_every_entrypoint() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    entrypoint_ids = {entrypoint.id for entrypoint in package.operation_entrypoints}
    explained_ids = {
        related_id
        for explainer in package.explainers.values()
        for related_id in explainer.related_entrypoint_ids
    }

    assert sorted(entrypoint_ids - explained_ids) == []


def test_meeting_control_map_demo_is_directed_and_complete() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = next(flow for flow in package.demo_flows if flow.id == "meeting-control-map-demo")

    assert flow.title == "Meeting Control Map"
    assert flow.steps[0].id == "control-map-overview"
    assert flow.steps[-1].id == "control-map-summary"
    assert flow.steps[-1].action.operation == "explain"

    entrypoint_ids = [step.action.entrypoint_id for step in flow.steps]
    assert entrypoint_ids == [
        "ringcentral.video.overview",
        "ringcentral.video.top.meeting-info",
        "ringcentral.video.top.network-quality",
        "ringcentral.video.top.views",
        "ringcentral.video.top.report-issue",
        "ringcentral.video.main.add-coworkers",
        "ringcentral.video.toolbar.participants",
        "ringcentral.video.toolbar.chat",
        "ringcentral.video.toolbar.audio",
        "ringcentral.video.toolbar.audio-menu",
        "ringcentral.video.toolbar.video",
        "ringcentral.video.toolbar.video-menu",
        "ringcentral.video.toolbar.share",
        "ringcentral.video.toolbar.react",
        "ringcentral.video.toolbar.raise-hand",
        "ringcentral.video.toolbar.more",
        "ringcentral.video.more.recording",
        "ringcentral.video.more.notes",
        "ringcentral.video.more.background",
        "ringcentral.video.more.settings",
        "ringcentral.video.toolbar.leave",
        "ringcentral.video.overview",
    ]

    for step in flow.steps:
        step.narration.text.encode("ascii")
        zh_text = step.narration.localized_text["zh"]
        assert zh_text
        assert any("\u4e00" <= character <= "\u9fff" for character in zh_text)
        assert not zh_text.startswith("我来说明一下")
        entrypoint = package.entrypoint_by_id(step.action.entrypoint_id)
        if step.action.operation in {"open", "toggle"}:
            assert_supported_open_step(entrypoint.open_steps[0])
            assert step.narration.placement == "during"
            assert step.narration.action_offset_ms <= 500

    recording_step = next(step for step in flow.steps if step.id == "control-map-recording")
    leave_step = next(step for step in flow.steps if step.id == "control-map-leave")
    assert recording_step.action.operation == "explain"
    assert leave_step.action.operation == "explain"


def test_short_ringcentral_demo_flows_have_chinese_localized_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    expected_step_ids = {
        "vbg-blur-demo": [
            "open-video-settings",
            "open-background-panel",
            "select-blur",
            "verify-meeting-video",
        ],
        "meeting-basics-demo": [
            "show-mic",
            "show-participants",
            "show-chat",
        ],
    }

    for flow_id, step_ids in expected_step_ids.items():
        flow = package.demo_flow_by_id(flow_id)
        assert [step.id for step in flow.steps] == step_ids
        for step in flow.steps:
            step.narration.text.encode("ascii")
            zh_text = step.narration.localized_text["zh"]
            assert zh_text.strip()
            assert has_cjk(zh_text)


def test_all_ringcentral_demo_flow_steps_have_chinese_localized_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    for flow in package.demo_flows:
        for step in flow.steps:
            step.narration.text.encode("ascii")
            zh_text = step.narration.localized_text["zh"]
            assert zh_text.strip(), f"{flow.id}:{step.id}"
            assert has_cjk(zh_text), f"{flow.id}:{step.id}"


def test_meeting_controls_tour_renders_chinese_narration_text() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-controls-tour")
    step = next(step for step in flow.steps if step.id == "explain-share")

    rendered = render_narration_text(
        step.narration,
        PresenterVoiceSettings(language="zh", tone="professional"),
    )

    assert rendered == step.narration.localized_text["zh"].strip()
    assert "Share" in rendered
    assert has_cjk(rendered)


def test_short_ringcentral_demo_flow_renders_chinese_narration_text() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("vbg-blur-demo")
    step = next(step for step in flow.steps if step.id == "select-blur")

    rendered = render_narration_text(
        step.narration,
        PresenterVoiceSettings(language="zh", tone="professional"),
    )

    assert rendered == step.narration.localized_text["zh"].strip()
    assert "Blur" in rendered
    assert has_cjk(rendered)


def test_meeting_basics_demo_has_japanese_localized_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-basics-demo")

    for step in flow.steps:
        ja_text = step.narration.localized_text["ja"]
        assert ja_text.strip(), step.id
        assert has_cjk(ja_text), step.id

    chat_step = next(step for step in flow.steps if step.id == "show-chat")
    chat_text = chat_step.narration.localized_text["ja"]
    assert "Chat" in chat_text
    assert "非公開" in chat_text


def test_rejects_duplicate_operation_entrypoint_ids(tmp_path: Path) -> None:
    package_path = tmp_path / "duplicate-entrypoints.yaml"
    package_path.write_text(
        """
appId: demo
appName: Demo
version: 1
profileIds: [demo-profile]
operationEntrypoints:
  - id: same
    title: First
    area: Main
    purpose: Open first
    openSteps: []
  - id: same
    title: Second
    area: Main
    purpose: Open second
    openSteps: []
demoFlows: []
manualControls: []
""",
        encoding="utf-8",
    )

    with pytest.raises(ValidationError, match="duplicate operation entrypoint id"):
        load_material_package(package_path)


def test_rejects_duplicate_demo_flow_ids(tmp_path: Path) -> None:
    package_path = tmp_path / "duplicate-flows.yaml"
    package_path.write_text(
        """
appId: demo
appName: Demo
version: 1
profileIds: [demo-profile]
operationEntrypoints:
  - id: demo.panel
    title: Panel
    area: Main
    purpose: Explain panel
    openSteps: []
demoFlows:
  - id: same-flow
    title: First
    goal: First
    steps: []
  - id: same-flow
    title: Second
    goal: Second
    steps: []
manualControls: []
""",
        encoding="utf-8",
    )

    with pytest.raises(ValidationError, match="duplicate demo flow id: same-flow"):
        load_material_package(package_path)


def assert_supported_open_step(step: object) -> None:
    action = getattr(step, "action")
    match = getattr(step, "match")
    if action == "clickWindowRelative":
        assert "x" in match or "xFromRight" in match
        assert "y" in match or "yFromBottom" in match
        return
    if action == "clickWindowControl":
        assert getattr(step, "target")
        return
    raise AssertionError(f"Unexpected package open step action: {action}")


def test_rejects_demo_flow_references_to_unknown_entrypoint(tmp_path: Path) -> None:
    package_path = tmp_path / "unknown-entrypoint.yaml"
    package_path.write_text(
        """
appId: demo
appName: Demo
version: 1
profileIds: [demo-profile]
operationEntrypoints:
  - id: known
    title: Known
    area: Main
    purpose: Open known
    openSteps: []
demoFlows:
  - id: demo-flow
    title: Demo Flow
    goal: Show the demo
    steps:
      - id: missing-step
        title: Missing
        action:
          entrypointId: missing
          operation: click
        narration:
          text: Open the missing entry point.
manualControls: []
""",
        encoding="utf-8",
    )

    with pytest.raises(ValidationError, match="unknown entrypoint"):
        load_material_package(package_path)


def test_rejects_executable_demo_step_without_open_steps(tmp_path: Path) -> None:
    package_path = tmp_path / "missing-open-steps.yaml"
    package_path.write_text(
        """
appId: demo
appName: Demo
version: 1
profileIds: [demo-profile]
operationEntrypoints:
  - id: demo.panel
    title: Panel
    area: Main
    purpose: Open panel
    openSteps: []
demoFlows:
  - id: demo-flow
    title: Demo Flow
    goal: Show the demo
    steps:
      - id: open-panel
        title: Open Panel
        action:
          entrypointId: demo.panel
          operation: open
        narration:
          text: Open the panel.
manualControls: []
""",
        encoding="utf-8",
    )

    with pytest.raises(ValidationError, match="has no executable open steps"):
        load_material_package(package_path)


def test_rejects_executable_demo_step_with_unsupported_open_action(tmp_path: Path) -> None:
    package_path = tmp_path / "unsupported-open-action.yaml"
    package_path.write_text(
        """
appId: demo
appName: Demo
version: 1
profileIds: [demo-profile]
operationEntrypoints:
  - id: demo.panel
    title: Panel
    area: Main
    purpose: Open panel
    openSteps:
      - action: clickMenu
        target: Panel
demoFlows:
  - id: demo-flow
    title: Demo Flow
    goal: Show the demo
    steps:
      - id: open-panel
        title: Open Panel
        action:
          entrypointId: demo.panel
          operation: open
        narration:
          text: Open the panel.
manualControls: []
""",
        encoding="utf-8",
    )

    with pytest.raises(ValidationError, match="unsupported executable open step action"):
        load_material_package(package_path)
