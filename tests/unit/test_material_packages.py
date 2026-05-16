import re
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
RINGCENTRAL_KNOWLEDGE_DOC_REF_RE = re.compile(
    r"docs/knowledge/ringcentral-video/([A-Za-z0-9._-]+\.md)"
)
RINGCENTRAL_KNOWLEDGE_DRAFT_PREFIXES = ("draft-", "scratch-")


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
    assert notes_entrypoint.question_policy == "answerOnly"
    assert (
        package.entrypoint_by_id("ringcentral.video.top.meeting-info").question_policy
        == "answerOnly"
    )
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


def test_material_package_parses_localized_entrypoint_title_and_purpose() -> None:
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
                    "localizedTitles": {
                        "es": "Panel de participantes",
                        "ja": "\u53c2\u52a0\u8005\u30d1\u30cd\u30eb",
                        "zh": "  ",
                    },
                    "localizedPurposes": {
                        "es": "Abre la lista de participantes.",
                        "ja": "  ",
                    },
                    "openSteps": [],
                }
            ],
            "demoFlows": [],
            "manualControls": [],
        }
    )

    entrypoint = package.entrypoint_by_id("demo.participants")

    assert entrypoint.localized_titles["es"] == "Panel de participantes"
    assert entrypoint.localized_purposes["es"] == "Abre la lista de participantes."
    assert entrypoint.title_for_language("es") == "Panel de participantes"
    assert entrypoint.purpose_for_language("es") == "Abre la lista de participantes."
    assert entrypoint.title_for_language("zh") == entrypoint.title
    assert entrypoint.purpose_for_language("ja") == entrypoint.purpose


def test_entrypoint_localized_title_and_purpose_do_not_affect_match_candidates() -> None:
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
                    "localizedPurposes": {"es": "Abre la lista de participantes."},
                    "openSteps": [],
                }
            ],
            "demoFlows": [],
            "manualControls": [],
        }
    )

    candidate = package.entrypoint_match_candidates[0]

    assert "participantes" not in candidate.title_tokens
    assert "abre" not in candidate.purpose_tokens
    assert "participantes" not in candidate.purpose_tokens


def test_material_package_still_rejects_unknown_entrypoint_keys() -> None:
    with pytest.raises(ValidationError, match="extra_forbidden"):
        MaterialPackage.model_validate(
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
                        "localizedTitle": {"es": "Panel de participantes"},
                        "openSteps": [],
                    }
                ],
                "demoFlows": [],
                "manualControls": [],
            }
        )


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
    assert report.demo_localized_steps == 51
    assert report.demo_total_steps == 51
    assert report.qa_localized_questions == 12
    assert report.qa_localized_answers == 12
    assert report.qa_total == 12
    assert report.entrypoints_with_aliases == 13
    assert report.entrypoint_total == 27
    assert report.alias_total == 34
    assert report.required_localization_complete is True
    assert report.flow_by_id["vbg-blur-demo"].localized_steps == 4
    assert report.flow_by_id["vbg-blur-demo"].total_steps == 4
    assert report.flow_by_id["meeting-basics-demo"].localized_steps == 3
    assert report.flow_by_id["meeting-basics-demo"].total_steps == 3
    assert report.flow_by_id["meeting-controls-tour"].localized_steps == 22
    assert report.flow_by_id["meeting-controls-tour"].total_steps == 22
    assert report.flow_by_id["meeting-control-map-demo"].localized_steps == 22
    assert report.flow_by_id["meeting-control-map-demo"].total_steps == 22
    assert report.flow_by_id["meeting-control-map-demo"].missing_step_ids == ()


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
                    "localizedTitles": {"zh": "Localized panel"},
                    "localizedPurposes": {"zh": "Open localized panel."},
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
    assert report.entrypoint_titles_present == 1
    assert report.entrypoint_purposes_present == 1
    assert report.alias_total == 1
    assert "- onboarding-demo: 1/2 narration localized" in lines
    assert "  missing: missing" in lines
    assert "  missing answers: #1 Where is the panel?" in lines
    assert "- localizedTitles.zh present on 1/2 entrypoints" in lines
    assert "- localizedPurposes.zh present on 1/2 entrypoints" in lines


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


def test_entrypoint_title_and_purpose_counts_do_not_gate_required_localization() -> None:
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
                    "localizedTitles": {"es": "Panel"},
                    "localizedPurposes": {"es": "Abre el panel."},
                    "openSteps": [],
                },
                {
                    "id": "demo.other",
                    "title": "Other",
                    "area": "Main",
                    "purpose": "Open other.",
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
                                "localizedText": {"es": "Muestra el panel."},
                            },
                        }
                    ],
                }
            ],
            "qa": [
                {
                    "question": "Where is the panel?",
                    "answer": "Open Panel.",
                    "localizedQuestions": {"es": ["Donde esta el panel?"]},
                    "localizedAnswers": {"es": "Abre Panel."},
                    "relatedEntrypointIds": ["demo.panel"],
                }
            ],
            "manualControls": [],
        }
    )

    report = build_localization_status(package, language="es")

    assert report.entrypoint_titles_present == 1
    assert report.entrypoint_purposes_present == 1
    assert report.entrypoint_total == 2
    assert report.required_localization_complete is True


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


def test_localization_status_marks_french_coverage_incomplete() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    report = build_localization_status(package, language="fr")

    assert report.required_localization_complete is False


def test_ringcentral_spanish_seed_qa_and_aliases_are_present() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    item = next(qa for qa in package.qa if qa.question == "How do I protect my real background?")
    aliases = package.entrypoint_by_id(
        "ringcentral.video.settings.background"
    ).question_aliases.get("es", [])
    questions = item.localized_questions.get("es", [])
    answer = item.localized_answers.get("es", "")

    assert len(questions) == 2
    assert any("fondo real" in question for question in questions)
    assert any("habitación" in question and "reunión" in question for question in questions)
    assert "privacidad" in answer
    assert "Settings" in answer
    assert "Background" in answer
    assert "Blur" in answer
    assert set(aliases) == {
        "ajustes de fondo",
        "configuración de fondo",
        "fondo virtual",
        "desenfocar fondo",
    }


def test_ringcentral_spanish_entrypoint_copy_pilot_is_present() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    expected_spanish_display_copy = {
        "ringcentral.video.overview": (
            "Resumen de la reunión",
            (
                "Presenta la superficie de RingCentral Video antes de abrir controles "
                "individuales."
            ),
        ),
        "ringcentral.video.top.network-quality": (
            "Calidad de red",
            (
                "Abre Network quality para revisar packet loss, jitter y latency de Share, "
                "video y audio cuando la reunión se siente inestable."
            ),
        ),
        "ringcentral.video.top.views": (
            "Diseño de vista",
            (
                "Abre Views para revisar Gallery view o Full screen en tu vista local "
                "sin cambiar audio, video ni participantes."
            ),
        ),
        "ringcentral.video.toolbar.more": (
            "Más acciones",
            (
                "Abre More para mostrar acciones adicionales de la reunión y explicar "
                "su ubicación sin iniciar grabaciones ni otros cambios."
            ),
        ),
        "ringcentral.video.more.settings": (
            "Ajustes",
            (
                "Abre Settings para revisar opciones de audio, video, Background, "
                "Translation, Join preferences y General sin cambiar configuraciones "
                "ni leer datos privados."
            ),
        ),
    }

    for entrypoint_id, (title, purpose) in expected_spanish_display_copy.items():
        entrypoint = package.entrypoint_by_id(entrypoint_id)
        assert entrypoint.localized_titles == {"es": title}
        assert entrypoint.localized_purposes == {"es": purpose}

    localized_entrypoint_ids = {
        entrypoint.id
        for entrypoint in package.operation_entrypoints
        if entrypoint.localized_titles or entrypoint.localized_purposes
    }
    assert localized_entrypoint_ids == set(expected_spanish_display_copy)


def test_ringcentral_package_owns_spanish_aliases_for_location_routes() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    aliases_by_entrypoint: dict[str, set[str]] = {}
    for alias in package.entrypoint_question_aliases:
        if alias.language != "es":
            continue
        aliases_by_entrypoint.setdefault(alias.entrypoint_id, set()).add(alias.alias)

    expected_aliases = {
        "ringcentral.develop.video.tab": {
            "pestaña de video en ringcentral",
            "sección de video de ringcentral",
        },
        "ringcentral.develop.video.start": {
            "botón start en ringcentral video",
            "entrada de reunión instantánea en ringcentral",
        },
        "ringcentral.video.overview": {
            "resumen de la ventana de reunión",
            "mapa de controles de reunión",
            "orientación de controles de reunión",
        },
        "ringcentral.video.top.meeting-info": {
            "ubicación de meeting information",
            "panel de información de la reunión",
            "entrada de detalles de la reunión",
        },
        "ringcentral.video.top.network-quality": {
            "ubicación de network quality",
            "panel de calidad de red",
            "diagnóstico de conexión de reunión",
        },
        "ringcentral.video.top.views": {
            "menú de vista de reunión",
            "selector de diseño de vista",
            "ubicación de views",
        },
        "ringcentral.video.top.report-issue": {
            "ubicación de report issue",
            "entrada para reportar problema técnico",
        },
        "ringcentral.video.main.add-coworkers": {
            "ubicación de add coworkers",
            "aviso para agregar compañeros en sala vacía",
        },
        "ringcentral.video.toolbar.audio": {
            "ubicación del botón mute",
            "control del micrófono en la barra",
            "estado del micrófono en reunión",
        },
        "ringcentral.video.toolbar.audio-menu": {
            "menú de audio de la reunión",
            "selector de micrófono y altavoz",
            "ubicación de audio options",
        },
        "ringcentral.video.toolbar.video": {
            "ubicación de start video",
            "control de cámara en la barra",
            "estado de la cámara en reunión",
        },
        "ringcentral.video.toolbar.video-menu": {
            "menú de cámara en la reunión",
            "selector de cámara en video",
            "ubicación de more video settings",
        },
        "ringcentral.video.settings.video": {
            "configuración avanzada de video",
            "ajustes de cámara y calidad",
        },
        "ringcentral.video.settings.background": {
            "ajustes de fondo",
            "configuración de fondo",
            "fondo virtual",
            "desenfocar fondo",
        },
        "ringcentral.video.toolbar.share": {
            "ubicación del botón share",
            "entrada para compartir contenido",
            "selector de compartir pantalla",
        },
        "ringcentral.video.toolbar.invite": {
            "ubicación de invite",
            "entrada para invitar participantes",
            "panel de invitación de la reunión",
        },
        "ringcentral.video.toolbar.participants": {
            "panel de participantes",
            "lista de participantes",
            "controles de participantes",
        },
        "ringcentral.video.toolbar.chat": {
            "panel de chat de la reunión",
            "entrada del chat en la reunión",
            "superficie de chat de la reunión",
        },
        "ringcentral.video.toolbar.react": {
            "ubicación de reactions",
            "botón de reacciones en la barra",
            "panel de señales de reacción",
        },
        "ringcentral.video.toolbar.raise-hand": {
            "ubicación de raise hand",
            "botón de levantar la mano",
            "control de mano levantada",
        },
        "ringcentral.video.toolbar.more": {
            "menú de más acciones",
            "más controles de reunión",
        },
        "ringcentral.video.more.recording": {
            "ubicación de start recording",
            "entrada de recording en more",
        },
        "ringcentral.video.more.notes": {
            "ubicación de notes and transcript",
            "panel de notas y transcripción",
            "entrada de notes en more",
        },
        "ringcentral.video.more.background": {
            "ubicación de background en more",
            "fondo desde el menú more",
        },
        "ringcentral.video.more.settings": {
            "ubicación de settings en more",
            "centro de ajustes de reunión",
        },
        "ringcentral.video.toolbar.leave": {
            "ubicación del botón leave",
            "opciones para abandonar la reunión",
        },
    }

    assert set(aliases_by_entrypoint) == set(expected_aliases)
    for entrypoint_id, aliases in expected_aliases.items():
        assert aliases == aliases_by_entrypoint[entrypoint_id]


def test_ringcentral_localization_status_reports_complete_spanish_package() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    report = build_localization_status(package, language="es")

    assert report.package_id == "ringcentral-video"
    assert report.language == "es"
    assert report.demo_localized_steps == 51
    assert report.demo_total_steps == 51
    assert report.qa_localized_questions == 12
    assert report.qa_localized_answers == 12
    assert report.qa_total == 12
    assert report.entrypoints_with_aliases == 26
    assert report.entrypoint_total == 27
    assert report.alias_total == 69
    assert report.entrypoint_titles_present == 5
    assert report.entrypoint_purposes_present == 5
    assert report.required_localization_complete is True
    assert report.flow_by_id["vbg-blur-demo"].localized_steps == 4
    assert report.flow_by_id["vbg-blur-demo"].total_steps == 4
    assert report.flow_by_id["vbg-blur-demo"].missing_step_ids == ()
    assert report.flow_by_id["meeting-basics-demo"].localized_steps == 3
    assert report.flow_by_id["meeting-basics-demo"].total_steps == 3
    assert report.flow_by_id["meeting-basics-demo"].missing_step_ids == ()
    assert report.flow_by_id["meeting-controls-tour"].localized_steps == 22
    assert report.flow_by_id["meeting-controls-tour"].total_steps == 22
    assert report.flow_by_id["meeting-controls-tour"].missing_step_ids == ()
    assert report.flow_by_id["meeting-control-map-demo"].localized_steps == 22
    assert report.flow_by_id["meeting-control-map-demo"].total_steps == 22
    assert report.flow_by_id["meeting-control-map-demo"].missing_step_ids == ()


def test_ringcentral_spanish_display_metadata_counts_match_durable_docs() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    report = build_localization_status(package, language="es")
    assert report.required_localization_complete is True

    durable_doc_paths = (
        Path("docs/knowledge/language-lifecycle.md"),
        Path("docs/knowledge/ringcentral-video/source-index.md"),
    )
    expected_counts = {
        "localizedTitles.es": report.entrypoint_titles_present,
        "localizedPurposes.es": report.entrypoint_purposes_present,
    }

    for doc_path in durable_doc_paths:
        doc_text = doc_path.read_text(encoding="utf-8")
        for metadata_key, present_count in expected_counts.items():
            count_pattern = re.compile(
                rf"`?{re.escape(metadata_key)}`?.{{0,80}}"
                rf"`?{present_count}/{report.entrypoint_total}`?.{{0,20}}"
                r"entrypoints",
                re.DOTALL,
            )
            assert count_pattern.search(doc_text), (
                f"{doc_path} must mention {metadata_key} on "
                f"{present_count}/{report.entrypoint_total} entrypoints"
            )


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


def test_ringcentral_package_owns_japanese_aliases_for_meeting_control_routes() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    aliases_by_entrypoint: dict[str, set[str]] = {}
    for alias in package.entrypoint_question_aliases:
        if alias.language != "ja":
            continue
        aliases_by_entrypoint.setdefault(alias.entrypoint_id, set()).add(alias.alias)

    expected_aliases = {
        "ringcentral.video.overview": {"会議画面の概要", "会議画面の見取り図"},
        "ringcentral.video.top.meeting-info": {
            "会議情報の場所",
            "Meeting information の場所",
            "会議詳細の入口",
        },
        "ringcentral.video.top.network-quality": {
            "ネットワーク品質",
            "接続品質",
            "通話が不安定",
        },
        "ringcentral.video.top.views": {
            "表示レイアウト",
            "表示切り替え",
            "ギャラリービュー",
        },
        "ringcentral.video.toolbar.audio": {"マイク", "ミュート", "音声"},
        "ringcentral.video.toolbar.audio-menu": {
            "音声メニュー",
            "マイクメニュー",
            "スピーカーメニュー",
        },
        "ringcentral.video.toolbar.video-menu": {
            "カメラメニュー",
            "ビデオメニュー",
            "カメラ選択",
        },
        "ringcentral.video.toolbar.react": {
            "React ボタンの場所",
            "リアクション欄の場所",
        },
        "ringcentral.video.toolbar.raise-hand": {
            "挙手ボタンの場所",
            "挙手の場所",
        },
        "ringcentral.video.more.recording": {
            "Start recording の場所",
            "録画ボタンの場所",
        },
        "ringcentral.video.more.notes": {
            "Notes and Transcript の場所",
            "ノートと文字起こしの場所",
        },
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


def test_material_package_normalizes_latin_diacritics_for_matching() -> None:
    package = MaterialPackage.model_validate(
        {
            "appId": "demo",
            "appName": "Demo",
            "version": 1,
            "profileIds": ["demo-profile"],
            "operationEntrypoints": [
                {
                    "id": "demo.camera",
                    "title": "Camera",
                    "area": "Main",
                    "purpose": "Open camera.",
                    "questionAliases": {
                        "es": [
                            "configuración de cámara",
                            "botón de micrófono",
                            "panel de transcripción",
                        ]
                    },
                }
            ],
            "demoFlows": [],
            "qa": [
                {
                    "question": "¿Dónde está la reunión?",
                    "localizedQuestions": {
                        "es": ["¿Dónde está el botón de cámara?"],
                        "ja": ["ボタンはどこですか"],
                    },
                    "answer": "Open camera.",
                }
            ],
            "manualControls": [],
        }
    )

    aliases = package.entrypoint_question_aliases
    assert [alias.alias for alias in aliases] == [
        "configuración de cámara",
        "botón de micrófono",
        "panel de transcripción",
    ]
    assert [alias.normalized_alias for alias in aliases] == [
        "configuracion de camara",
        "boton de microfono",
        "panel de transcripcion",
    ]
    assert package.qa_question_candidates[0].normalized_question == "¿donde esta la reunion?"
    assert package.qa_question_candidates[1].normalized_question == "¿donde esta el boton de camara?"
    assert package.qa_question_candidates[2].normalized_question == "ボタンはどこですか"
    assert package.qa_question_candidates[1].meaningful_tokens >= {
        "donde",
        "esta",
        "boton",
        "camara",
    }


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


def test_ringcentral_knowledge_docs_are_registered_in_navigation_indexes() -> None:
    knowledge_dir = Path("docs/knowledge/ringcentral-video")
    source_text = (knowledge_dir / "source-index.md").read_text(encoding="utf-8")
    evidence_text = (knowledge_dir / "evidence-index.md").read_text(encoding="utf-8")
    navigation_text = f"{source_text}\n{evidence_text}"
    doc_paths = [
        path
        for path in sorted(knowledge_dir.glob("*.md"))
        if not path.name.startswith(RINGCENTRAL_KNOWLEDGE_DRAFT_PREFIXES)
        and "<!-- nav: ignore -->" not in path.read_text(encoding="utf-8")
    ]

    missing_from_source_index = [
        path.name
        for path in doc_paths
        if path.name != "source-index.md"
        and f"`docs/knowledge/ringcentral-video/{path.name}`" not in source_text
    ]
    missing_from_evidence_index = [
        path.name
        for path in doc_paths
        if path.name != "evidence-index.md"
        and f"`docs/knowledge/ringcentral-video/{path.name}`" not in evidence_text
    ]
    missing_from_navigation = [
        path.name
        for path in doc_paths
        if f"`docs/knowledge/ringcentral-video/{path.name}`" not in navigation_text
    ]
    dangling_knowledge_refs = sorted(
        name
        for name in set(RINGCENTRAL_KNOWLEDGE_DOC_REF_RE.findall(navigation_text))
        if not (knowledge_dir / name).is_file()
    )

    assert missing_from_source_index == []
    assert missing_from_evidence_index == []
    assert missing_from_navigation == []
    assert dangling_knowledge_refs == []


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


def test_ringcentral_spanish_qas_and_demo_flows_are_localized() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    expected_spanish_demo_steps = [
        "vbg-blur-demo:open-video-settings",
        "vbg-blur-demo:open-background-panel",
        "vbg-blur-demo:select-blur",
        "vbg-blur-demo:verify-meeting-video",
        "meeting-basics-demo:show-mic",
        "meeting-basics-demo:show-participants",
        "meeting-basics-demo:show-chat",
        "meeting-controls-tour:meeting-overview",
        "meeting-controls-tour:explain-meeting-info",
        "meeting-controls-tour:explain-network-quality",
        "meeting-controls-tour:explain-view-layout",
        "meeting-controls-tour:explain-report-issue",
        "meeting-controls-tour:explain-add-coworkers",
        "meeting-controls-tour:explain-invite",
        "meeting-controls-tour:explain-participants",
        "meeting-controls-tour:explain-chat",
        "meeting-controls-tour:explain-microphone",
        "meeting-controls-tour:explain-audio-menu",
        "meeting-controls-tour:explain-camera",
        "meeting-controls-tour:explain-camera-menu",
        "meeting-controls-tour:explain-share",
        "meeting-controls-tour:explain-reactions",
        "meeting-controls-tour:explain-raise-hand",
        "meeting-controls-tour:explain-more",
        "meeting-controls-tour:explain-recording",
        "meeting-controls-tour:explain-notes",
        "meeting-controls-tour:explain-background-settings",
        "meeting-controls-tour:explain-settings",
        "meeting-controls-tour:explain-leave",
        "meeting-control-map-demo:control-map-overview",
        "meeting-control-map-demo:control-map-meeting-info",
        "meeting-control-map-demo:control-map-network",
        "meeting-control-map-demo:control-map-views",
        "meeting-control-map-demo:control-map-report",
        "meeting-control-map-demo:control-map-add-coworkers",
        "meeting-control-map-demo:control-map-participants",
        "meeting-control-map-demo:control-map-chat",
        "meeting-control-map-demo:control-map-microphone",
        "meeting-control-map-demo:control-map-audio-menu",
        "meeting-control-map-demo:control-map-camera",
        "meeting-control-map-demo:control-map-camera-menu",
        "meeting-control-map-demo:control-map-share",
        "meeting-control-map-demo:control-map-reactions",
        "meeting-control-map-demo:control-map-raise-hand",
        "meeting-control-map-demo:control-map-more",
        "meeting-control-map-demo:control-map-recording",
        "meeting-control-map-demo:control-map-notes",
        "meeting-control-map-demo:control-map-background",
        "meeting-control-map-demo:control-map-settings",
        "meeting-control-map-demo:control-map-leave",
        "meeting-control-map-demo:control-map-summary",
    ]

    missing_questions = [
        item.question for item in package.qa if not item.localized_questions.get("es")
    ]
    missing_answers = [
        item.question
        for item in package.qa
        if not item.localized_answers.get("es", "").strip()
    ]
    spanish_demo_steps = [
        f"{flow.id}:{step.id}"
        for flow in package.demo_flows
        for step in flow.steps
        if step.narration.localized_text.get("es")
    ]

    assert missing_questions == []
    assert missing_answers == []
    assert spanish_demo_steps == expected_spanish_demo_steps

    vbg_flow = package.demo_flow_by_id("vbg-blur-demo")
    vbg_text_by_step = {
        step.id: step.narration.localized_text["es"] for step in vbg_flow.steps
    }
    assert "Settings" in vbg_text_by_step["open-video-settings"]
    assert "Background" in vbg_text_by_step["open-background-panel"]
    assert "Blur" in vbg_text_by_step["select-blur"]
    assert "Stop video" in vbg_text_by_step["verify-meeting-video"]

    basics_flow = package.demo_flow_by_id("meeting-basics-demo")
    basics_text_by_step = {
        step.id: step.narration.localized_text["es"] for step in basics_flow.steps
    }
    assert "Participants" in basics_text_by_step["show-participants"]
    assert "Chat" in basics_text_by_step["show-chat"]
    assert "privado" in basics_text_by_step["show-chat"]

    controls_flow = package.demo_flow_by_id("meeting-controls-tour")
    controls_text_by_step = {
        step.id: step.narration.localized_text["es"] for step in controls_flow.steps
    }
    assert "RingCentral Video" in controls_text_by_step["meeting-overview"]
    assert "Meeting ID" in controls_text_by_step["explain-meeting-info"]
    assert "Network quality" in controls_text_by_step["explain-network-quality"]
    assert "Gallery view" in controls_text_by_step["explain-view-layout"]
    assert "Report" in controls_text_by_step["explain-report-issue"]
    assert "Add coworkers" in controls_text_by_step["explain-add-coworkers"]
    assert "Invite" in controls_text_by_step["explain-invite"]
    assert "Participants" in controls_text_by_step["explain-participants"]
    assert "Chat" in controls_text_by_step["explain-chat"]
    assert "Mute" in controls_text_by_step["explain-microphone"]
    assert "Audio options" in controls_text_by_step["explain-audio-menu"]
    assert "Start video" in controls_text_by_step["explain-camera"]
    assert "More video settings" in controls_text_by_step["explain-camera-menu"]
    assert "Share" in controls_text_by_step["explain-share"]
    assert "Reactions" in controls_text_by_step["explain-reactions"]
    assert "Raise hand" in controls_text_by_step["explain-raise-hand"]
    assert "More" in controls_text_by_step["explain-more"]
    assert "Recording" in controls_text_by_step["explain-recording"]
    assert "Notes" in controls_text_by_step["explain-notes"]
    assert "Background" in controls_text_by_step["explain-background-settings"]
    assert "Settings" in controls_text_by_step["explain-settings"]
    assert "Leave" in controls_text_by_step["explain-leave"]
    assert "no hago clic" in controls_text_by_step["explain-leave"]

    map_flow = package.demo_flow_by_id("meeting-control-map-demo")
    map_text_by_step = {
        step.id: step.narration.localized_text["es"] for step in map_flow.steps
    }
    assert "RingCentral Video" in map_text_by_step["control-map-overview"]
    assert "Meeting information" in map_text_by_step["control-map-meeting-info"]
    assert "Network quality" in map_text_by_step["control-map-network"]
    assert "Views" in map_text_by_step["control-map-views"]
    assert "Report" in map_text_by_step["control-map-report"]
    assert "Add coworkers" in map_text_by_step["control-map-add-coworkers"]
    assert "Participants" in map_text_by_step["control-map-participants"]
    assert "Chat" in map_text_by_step["control-map-chat"]
    assert "Mute" in map_text_by_step["control-map-microphone"]
    assert "Audio options" in map_text_by_step["control-map-audio-menu"]
    assert "Start video" in map_text_by_step["control-map-camera"]
    assert "More video settings" in map_text_by_step["control-map-camera-menu"]
    assert "Share" in map_text_by_step["control-map-share"]
    assert "Reactions" in map_text_by_step["control-map-reactions"]
    assert "Raise hand" in map_text_by_step["control-map-raise-hand"]
    assert "More" in map_text_by_step["control-map-more"]
    assert "Recording" in map_text_by_step["control-map-recording"]
    assert "Notes" in map_text_by_step["control-map-notes"]
    assert "Background" in map_text_by_step["control-map-background"]
    assert "Settings" in map_text_by_step["control-map-settings"]
    assert "Leave" in map_text_by_step["control-map-leave"]
    assert "no hago clic" in map_text_by_step["control-map-leave"]


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


def test_meeting_controls_tour_has_japanese_top_bar_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-controls-tour")
    expected_step_ids = [
        "meeting-overview",
        "explain-meeting-info",
        "explain-network-quality",
        "explain-view-layout",
    ]

    assert [step.id for step in flow.steps[:4]] == expected_step_ids
    for step_id in expected_step_ids:
        step = next(step for step in flow.steps if step.id == step_id)
        ja_text = step.narration.localized_text["ja"]
        assert ja_text.strip(), step_id
        assert has_cjk(ja_text), step_id

    meeting_info = next(step for step in flow.steps if step.id == "explain-meeting-info")
    meeting_info_text = meeting_info.narration.localized_text["ja"]
    assert "Meeting ID" in meeting_info_text
    assert "読み上げません" in meeting_info_text

    view_layout = next(step for step in flow.steps if step.id == "explain-view-layout")
    assert "他の参加者" in view_layout.narration.localized_text["ja"]


def test_meeting_controls_tour_has_japanese_report_issue_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-controls-tour")
    step = next(step for step in flow.steps if step.id == "explain-report-issue")

    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "Report" in ja_text
    assert "原因" in ja_text
    assert "決めつけません" in ja_text
    assert "閉じます" in ja_text
    assert "送信" not in ja_text


def test_meeting_controls_tour_has_japanese_add_coworkers_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-controls-tour")
    step = next(step for step in flow.steps if step.id == "explain-add-coworkers")

    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "Add coworkers" in ja_text
    assert "Invite" in ja_text
    assert "リンク" in ja_text
    assert "メール" in ja_text
    assert "読み上げません" in ja_text
    assert "閉じます" in ja_text
    assert "送信" not in ja_text


def test_meeting_controls_tour_has_japanese_invite_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-controls-tour")
    step = next(step for step in flow.steps if step.id == "explain-invite")

    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "Invite" in ja_text
    assert "ツールバー" in ja_text
    assert "進行中の会議" in ja_text
    assert "会議情報" in ja_text
    assert "読み上げません" in ja_text
    assert "閉じます" in ja_text
    assert "送信" not in ja_text


def test_meeting_controls_tour_has_japanese_participants_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-controls-tour")
    step = next(step for step in flow.steps if step.id == "explain-participants")

    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "Participants" in ja_text
    assert "参加者" in ja_text
    assert "人数" in ja_text
    assert "名前" in ja_text
    assert "役割" in ja_text
    assert "読み上げません" in ja_text
    assert "閉じます" in ja_text
    assert "ミュートしません" in ja_text


def test_meeting_controls_tour_has_japanese_chat_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-controls-tour")
    step = next(step for step in flow.steps if step.id == "explain-chat")

    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "Chat" in ja_text
    assert "メッセージ" in ja_text
    assert "全員" in ja_text
    assert "非公開" in ja_text
    assert "読み上げません" in ja_text
    assert "閉じます" in ja_text
    assert "送信しません" in ja_text


def test_meeting_controls_tour_has_japanese_microphone_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-controls-tour")
    step = next(step for step in flow.steps if step.id == "explain-microphone")

    assert step.action.operation == "point"
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "Mute" in ja_text
    assert "マイク" in ja_text
    assert "プライバシー" in ja_text
    assert "話す前" in ja_text
    assert "確認" in ja_text
    assert "ミュート解除" in ja_text
    assert "切り替えません" in ja_text


def test_meeting_controls_tour_has_japanese_audio_menu_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-controls-tour")
    step = next(step for step in flow.steps if step.id == "explain-audio-menu")

    assert step.action.operation == "open"
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "マイク" in ja_text
    assert "スピーカー" in ja_text
    assert "デバイス" in ja_text
    assert "コンピューター音声" in ja_text
    assert "電話音声" in ja_text
    assert "音声設定" in ja_text
    assert "切り替えません" in ja_text
    assert "閉じます" in ja_text


def test_meeting_controls_tour_has_japanese_camera_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-controls-tour")
    step = next(step for step in flow.steps if step.id == "explain-camera")

    assert step.action.operation == "point"
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "Start video" in ja_text
    assert "Stop video" in ja_text
    assert "ローカル" in ja_text
    assert "カメラ" in ja_text
    assert "オン" in ja_text
    assert "オフ" in ja_text
    assert "ユーザー" in ja_text
    assert "明確な指示" in ja_text
    assert "しません" in ja_text
    assert "背景" not in ja_text
    assert "設定" not in ja_text


def test_meeting_controls_tour_has_japanese_camera_menu_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-controls-tour")
    step = next(step for step in flow.steps if step.id == "explain-camera-menu")

    assert step.action.operation == "open"
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "カメラ" in ja_text
    assert "選択" in ja_text
    assert "背景" in ja_text
    assert "ビデオ設定" in ja_text
    assert "ユーザー" in ja_text
    assert "明確な指示" in ja_text
    assert "切り替えません" in ja_text
    assert "変更しません" in ja_text
    assert "閉じます" in ja_text
    assert "Start video" not in ja_text
    assert "Stop video" not in ja_text


def test_meeting_controls_tour_has_japanese_share_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-controls-tour")
    step = next(step for step in flow.steps if step.id == "explain-share")

    assert step.action.operation == "open"
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "Share" in ja_text
    assert "画面" in ja_text
    assert "アプリケーション" in ja_text
    assert "ウィンドウ" in ja_text
    assert "システム音声" in ja_text
    assert "ユーザー" in ja_text
    assert "確認" in ja_text
    assert "最終的な Share ボタン" in ja_text
    assert "押しません" in ja_text
    assert "読み上げません" in ja_text
    assert "閉じます" in ja_text
    assert "開始します" not in ja_text


def test_meeting_controls_tour_has_japanese_reactions_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-controls-tour")
    step = next(step for step in flow.steps if step.id == "explain-reactions")

    assert step.action.entrypoint_id == "ringcentral.video.toolbar.react"
    assert step.action.operation == "open"
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "React" in ja_text
    assert "リアクション" in ja_text
    assert "ハート" in ja_text
    assert "いいね" in ja_text
    assert "祝福" in ja_text
    assert "拍手" in ja_text
    assert "スマイル" in ja_text
    assert "Be right back" in ja_text
    assert "会議中に見える" in ja_text
    assert "ユーザー" in ja_text
    assert "明確な指示" in ja_text
    assert "送信しません" in ja_text
    assert "閉じます" in ja_text
    assert "Raise hand" not in ja_text
    assert "手を上げ" not in ja_text
    assert "送信します" not in ja_text


def test_meeting_controls_tour_has_japanese_raise_hand_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-controls-tour")
    step = next(step for step in flow.steps if step.id == "explain-raise-hand")

    assert step.action.entrypoint_id == "ringcentral.video.toolbar.raise-hand"
    assert step.action.operation == "toggle"
    assert step.narration.placement == "during"
    assert step.narration.action_offset_ms == 350
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "Raise hand" in ja_text
    assert "注目" in ja_text
    assert "発言機会" in ja_text
    assert "遮らず" in ja_text
    assert "トグル" in ja_text
    assert "リアクションとは別" in ja_text
    assert "注意喚起シグナル" in ja_text
    assert "手を上げ" in ja_text
    assert "手を下げ" in ja_text
    assert "会議中に見える" in ja_text
    assert "ユーザー" in ja_text
    assert "明確な指示" in ja_text
    assert "手を下げたり" in ja_text
    assert "上げたまま" in ja_text
    assert "実演を明確に確認" in ja_text
    assert "実演" in ja_text
    assert "実演後" in ja_text
    assert "ハート" not in ja_text
    assert "いいね" not in ja_text
    assert "拍手" not in ja_text
    assert "Be right back" not in ja_text
    assert "送信しません" not in ja_text


def test_meeting_controls_tour_has_japanese_more_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-controls-tour")
    step = next(step for step in flow.steps if step.id == "explain-more")

    assert step.action.entrypoint_id == "ringcentral.video.toolbar.more"
    assert step.action.operation == "open"
    assert step.narration.placement == "during"
    assert step.narration.action_offset_ms == 350
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "More" in ja_text
    assert "拡張メニュー" in ja_text
    assert "より深い会議ツール" in ja_text
    assert "Notes" in ja_text
    assert "ツールバー" in ja_text
    assert "Start recording" in ja_text
    assert "Background" in ja_text
    assert "Settings" in ja_text
    assert "説明するだけ" in ja_text
    assert "録画" in ja_text
    assert "背景" in ja_text
    assert "設定" in ja_text
    assert "ユーザー" in ja_text
    assert "明確に求める" in ja_text
    assert "録画を開始します" not in ja_text
    assert "Background を開きます" not in ja_text
    assert "Settings を開きます" not in ja_text
    assert "変更します" not in ja_text
    assert "選択します" not in ja_text
    assert "Leave" not in ja_text


def test_meeting_controls_tour_has_japanese_recording_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-controls-tour")
    step = next(step for step in flow.steps if step.id == "explain-recording")

    assert step.action.entrypoint_id == "ringcentral.video.more.recording"
    assert step.action.operation == "explain"
    assert step.narration.placement == "before"
    assert step.narration.action_offset_ms == 0
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "Start recording" in ja_text
    assert "会議状態" in ja_text
    assert "変更" in ja_text
    assert "参加者" in ja_text
    assert "ツアー" in ja_text
    assert "入口" in ja_text
    assert "説明するだけ" in ja_text
    assert "録画" in ja_text
    assert "開始" in ja_text
    assert "停止" in ja_text
    assert "ユーザー" in ja_text
    assert "確認" in ja_text
    assert "権限" in ja_text
    assert "同意" in ja_text
    assert "録画を開始します" not in ja_text
    assert "録画を停止します" not in ja_text
    assert "クリック" not in ja_text
    assert "押します" not in ja_text
    assert "選択します" not in ja_text
    assert "許可されています" not in ja_text
    assert "同意済み" not in ja_text
    assert "録画中" not in ja_text


def test_meeting_controls_tour_has_japanese_notes_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-controls-tour")
    step = next(step for step in flow.steps if step.id == "explain-notes")

    assert step.action.entrypoint_id == "ringcentral.video.more.notes"
    assert step.action.operation == "open"
    assert step.narration.placement == "during"
    assert step.narration.action_offset_ms == 400
    notes_entrypoint = package.entrypoint_by_id("ringcentral.video.more.notes")
    assert [open_step.target for open_step in notes_entrypoint.open_steps] == [
        "More",
        "onconf.controls.NOTES",
    ]
    assert notes_entrypoint.open_steps[0].match["occurrence"] == "3"
    assert notes_entrypoint.open_steps[1].match["alternateTargets"] == "Notes"
    assert notes_entrypoint.open_steps[1].match["cleanup"] == "sidePanel"
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "Notes" in ja_text
    assert "Notes and Transcript" in ja_text
    assert "Start notes" in ja_text
    assert "Also record this meeting" in ja_text
    assert "会議メモ" in ja_text
    assert "録画" in ja_text
    assert "ユーザー" in ja_text
    assert "明確に求める" in ja_text
    assert "操作しません" in ja_text
    assert "場所" in ja_text
    assert "役割" in ja_text
    assert "閉じます" in ja_text
    assert "開始します" not in ja_text
    assert "録画します" not in ja_text
    assert "クリック" not in ja_text
    assert "押します" not in ja_text
    assert "選択します" not in ja_text
    assert "Start notes を押します" not in ja_text
    assert "Also record this meeting を選択します" not in ja_text
    assert "録画を開始します" not in ja_text


def test_meeting_controls_tour_has_japanese_background_settings_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-controls-tour")
    step = next(step for step in flow.steps if step.id == "explain-background-settings")

    assert step.action.entrypoint_id == "ringcentral.video.more.background"
    assert step.action.operation == "open"
    assert step.narration.placement == "during"
    assert step.narration.action_offset_ms == 400
    background_entrypoint = package.entrypoint_by_id("ringcentral.video.more.background")
    assert [open_step.target for open_step in background_entrypoint.open_steps] == [
        "More",
        "Background",
    ]
    assert background_entrypoint.open_steps[0].match["occurrence"] == "3"
    assert background_entrypoint.open_steps[0].match["controlType"] == "button"
    assert background_entrypoint.open_steps[1].match["cleanup"] == "settings"
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "Background" in ja_text
    assert "Settings" in ja_text
    assert "Off" in ja_text
    assert "Blur" in ja_text
    assert "仮想背景" in ja_text
    assert "動画背景" in ja_text
    assert "アップロード" in ja_text
    assert "Mirror my video" in ja_text
    assert "プライバシー" in ja_text
    assert "ユーザー" in ja_text
    assert "明確に求める" in ja_text
    assert "変更しません" in ja_text
    assert "閉じます" in ja_text
    assert "背景を変更します" not in ja_text
    assert "Blur を選択します" not in ja_text
    assert "アップロードします" not in ja_text
    assert "クリック" not in ja_text
    assert "押します" not in ja_text
    assert "選択します" not in ja_text
    assert "適用します" not in ja_text
    assert "切り替えます" not in ja_text


def test_meeting_controls_tour_has_japanese_settings_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-controls-tour")
    step = next(step for step in flow.steps if step.id == "explain-settings")

    assert step.action.entrypoint_id == "ringcentral.video.more.settings"
    assert step.action.operation == "open"
    assert step.narration.placement == "during"
    assert step.narration.action_offset_ms == 400
    settings_entrypoint = package.entrypoint_by_id("ringcentral.video.more.settings")
    assert [open_step.target for open_step in settings_entrypoint.open_steps] == [
        "More",
        "Settings",
    ]
    assert settings_entrypoint.open_steps[0].match["occurrence"] == "3"
    assert settings_entrypoint.open_steps[0].match["controlType"] == "button"
    assert settings_entrypoint.open_steps[1].match["cleanup"] == "settings"
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "Settings" in ja_text
    assert "Audio" in ja_text
    assert "Video" in ja_text
    assert "Background" in ja_text
    assert "Translation" in ja_text
    assert "Join preferences" in ja_text
    assert "General" in ja_text
    assert "場所" in ja_text
    assert "役割" in ja_text
    assert "説明するだけ" in ja_text
    assert "ユーザー" in ja_text
    assert "明確に求める" in ja_text
    assert "変更しません" in ja_text
    assert "閉じます" in ja_text
    assert "音声を変更します" not in ja_text
    assert "ビデオを変更します" not in ja_text
    assert "背景を変更します" not in ja_text
    assert "翻訳を有効にします" not in ja_text
    assert "入会設定を変更します" not in ja_text
    assert "General を変更します" not in ja_text
    assert "選択します" not in ja_text
    assert "切り替えます" not in ja_text
    assert "適用します" not in ja_text
    assert "クリック" not in ja_text
    assert "押します" not in ja_text


def test_meeting_controls_tour_has_japanese_leave_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-controls-tour")
    step = next(step for step in flow.steps if step.id == "explain-leave")

    assert step.action.entrypoint_id == "ringcentral.video.toolbar.leave"
    assert step.action.operation == "explain"
    assert step.narration.placement == "before"
    leave_entrypoint = package.entrypoint_by_id("ringcentral.video.toolbar.leave")
    assert leave_entrypoint.open_steps == []
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "Leave" in ja_text
    assert "会議" in ja_text
    assert "退出" in ja_text
    assert "破壊的" in ja_text
    assert "コントロール" in ja_text
    assert "説明するだけ" in ja_text
    assert "ユーザー" in ja_text
    assert "明確" in ja_text
    assert "確認" in ja_text
    assert "ホスト" in ja_text
    assert "全員" in ja_text
    assert "クリック" not in ja_text
    assert "押します" not in ja_text
    assert "選択します" not in ja_text
    assert "退出します" not in ja_text
    assert "終了します" not in ja_text
    assert "会議を終了" not in ja_text
    assert "Leave を押します" not in ja_text
    assert "Leave をクリック" not in ja_text


def test_meeting_control_map_has_japanese_overview_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-control-map-demo")
    step = next(step for step in flow.steps if step.id == "control-map-overview")

    assert flow.steps[0].id == "control-map-overview"
    assert step.action.entrypoint_id == "ringcentral.video.overview"
    assert step.action.operation == "explain"
    assert step.narration.placement == "before"
    assert step.narration.action_offset_ms == 0
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "コントロールマップ" in ja_text
    assert "上部" in ja_text
    assert "状態" in ja_text
    assert "ネットワーク" in ja_text
    assert "健全性" in ja_text
    assert "中央" in ja_text
    assert "ライブ会議キャンバス" in ja_text
    assert "下部" in ja_text
    assert "参加者" in ja_text
    assert "メディア" in ja_text
    assert "共有" in ja_text
    assert "リアクション" in ja_text
    assert "退出" in ja_text
    assert "コントロール" in ja_text
    assert "クリック" not in ja_text
    assert "押します" not in ja_text
    assert "開きます" not in ja_text
    assert "切り替えます" not in ja_text
    assert "変更します" not in ja_text
    assert "開始します" not in ja_text
    assert "送信します" not in ja_text
    assert "録画します" not in ja_text
    assert "退出します" not in ja_text


def test_meeting_control_map_has_japanese_meeting_info_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-control-map-demo")
    step = next(step for step in flow.steps if step.id == "control-map-meeting-info")

    assert step.action.entrypoint_id == "ringcentral.video.top.meeting-info"
    assert step.action.operation == "open"
    assert step.narration.placement == "during"
    assert step.narration.action_offset_ms == 350
    report = build_localization_status(package, language="ja")
    meeting_info_entrypoint = package.entrypoint_by_id(
        "ringcentral.video.top.meeting-info"
    )
    assert meeting_info_entrypoint.question_aliases["ja"] == [
        "会議情報の場所",
        "Meeting information の場所",
        "会議詳細の入口",
    ]
    assert report.entrypoints_with_aliases == 13
    assert report.alias_total == 34
    assert len(meeting_info_entrypoint.open_steps) == 1
    open_step = meeting_info_entrypoint.open_steps[0]
    assert open_step.action == "clickWindowRelative"
    assert open_step.target == "Meeting information"
    assert open_step.match["x"] == "31"
    assert open_step.match["y"] == "21"
    assert open_step.match["cleanup"] == "escape"
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "Meeting information" in ja_text
    assert "会議情報" in ja_text
    assert "Meeting ID" in ja_text
    assert "リンク" in ja_text
    assert "ダイヤルイン" in ja_text
    assert "暗号化" in ja_text
    assert "非公開" in ja_text
    assert "読み上げません" in ja_text
    assert "ユーザー" in ja_text
    assert "明示的" in ja_text
    assert "コピーします" not in ja_text
    assert "リンクをコピー" not in ja_text
    assert "ダイヤルします" not in ja_text
    assert "共有します" not in ja_text
    assert "送信します" not in ja_text
    assert "切り替えます" not in ja_text
    assert "変更します" not in ja_text
    assert "招待します" not in ja_text
    assert "開始します" not in ja_text
    assert "読み上げます" not in ja_text


def test_meeting_control_map_has_japanese_network_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-control-map-demo")
    step = next(step for step in flow.steps if step.id == "control-map-network")

    assert step.action.entrypoint_id == "ringcentral.video.top.network-quality"
    assert step.action.operation == "open"
    assert step.narration.placement == "during"
    assert step.narration.action_offset_ms == 350
    report = build_localization_status(package, language="ja")
    network_entrypoint = package.entrypoint_by_id(
        "ringcentral.video.top.network-quality"
    )
    assert network_entrypoint.question_aliases["ja"] == [
        "ネットワーク品質",
        "接続品質",
        "通話が不安定",
    ]
    assert report.entrypoints_with_aliases == 13
    assert report.alias_total == 34
    assert len(network_entrypoint.open_steps) == 1
    open_step = network_entrypoint.open_steps[0]
    assert open_step.action == "clickWindowRelative"
    assert open_step.target == "Network quality"
    assert open_step.match["x"] == "68"
    assert open_step.match["y"] == "21"
    assert open_step.match["cleanup"] == "escape"
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "Network quality" in ja_text
    assert "会議" in ja_text
    assert "健全性" in ja_text
    assert "音声" in ja_text
    assert "ビデオ" in ja_text
    assert "共有" in ja_text
    assert "パケットロス" in ja_text
    assert "ジッター" in ja_text
    assert "遅延" in ja_text
    assert "観測値" in ja_text
    assert "原因を決めつけ" in ja_text
    assert "修復" in ja_text
    assert "約束" in ja_text
    assert "修復します" not in ja_text
    assert "直します" not in ja_text
    assert "改善します" not in ja_text
    assert "設定を変更します" not in ja_text
    assert "切り替えます" not in ja_text
    assert "正確な原因です" not in ja_text
    assert "問題を解決します" not in ja_text
    assert "必ず" not in ja_text
    assert "保証します" not in ja_text


def test_meeting_control_map_has_japanese_views_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-control-map-demo")
    step = next(step for step in flow.steps if step.id == "control-map-views")

    assert step.action.entrypoint_id == "ringcentral.video.top.views"
    assert step.action.operation == "open"
    assert step.narration.placement == "during"
    assert step.narration.action_offset_ms == 350
    report = build_localization_status(package, language="ja")
    views_entrypoint = package.entrypoint_by_id("ringcentral.video.top.views")
    assert views_entrypoint.question_aliases["ja"] == [
        "表示レイアウト",
        "表示切り替え",
        "ギャラリービュー",
    ]
    assert report.entrypoints_with_aliases == 13
    assert report.alias_total == 34
    assert len(views_entrypoint.open_steps) == 1
    open_step = views_entrypoint.open_steps[0]
    assert open_step.action == "clickWindowRelative"
    assert open_step.target == "Views"
    assert open_step.match["xFromRight"] == "237"
    assert open_step.match["y"] == "21"
    assert open_step.match["cleanup"] == "escape"
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "Views" in ja_text
    assert "View layout" in ja_text
    assert "Gallery view" in ja_text
    assert "Full screen" in ja_text
    assert "会議" in ja_text
    assert "表示" in ja_text
    assert "音声" in ja_text
    assert "ビデオ" in ja_text
    assert "参加者" in ja_text
    assert "共有" in ja_text
    assert "説明" in ja_text
    assert "扱いません" in ja_text
    assert "切り替えます" not in ja_text
    assert "選択します" not in ja_text
    assert "変更します" not in ja_text
    assert "Gallery view を選択" not in ja_text
    assert "Full screen にします" not in ja_text
    assert "全画面にします" not in ja_text
    assert "音声を変更" not in ja_text
    assert "ビデオを変更" not in ja_text
    assert "共有を開始" not in ja_text
    assert "共有を変更" not in ja_text
    assert "参加者を変更" not in ja_text


def test_meeting_control_map_has_japanese_report_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-control-map-demo")
    step = next(step for step in flow.steps if step.id == "control-map-report")

    assert step.action.entrypoint_id == "ringcentral.video.top.report-issue"
    assert step.action.operation == "open"
    assert step.narration.placement == "during"
    assert step.narration.action_offset_ms == 400
    report_entrypoint = package.entrypoint_by_id(
        "ringcentral.video.top.report-issue"
    )
    assert len(report_entrypoint.open_steps) == 1
    open_step = report_entrypoint.open_steps[0]
    assert open_step.action == "clickWindowRelative"
    assert open_step.target == "Report"
    assert open_step.match["xFromRight"] == "168"
    assert open_step.match["y"] == "21"
    assert open_step.match["cleanup"] == "modal"
    assert report_entrypoint.presenter_notes[0].startswith(
        "This opens a foreground dialog"
    )
    assert (
        "Do not pick an issue category during a feature tour"
        in report_entrypoint.presenter_notes[1]
    )
    assert "dialog X" in report_entrypoint.presenter_notes[2]
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "Report issue" in ja_text
    assert "Report" in ja_text
    assert "Audio" in ja_text
    assert "Video" in ja_text
    assert "Screen sharing" in ja_text
    assert "Meeting join" in ja_text
    assert "Notes" in ja_text
    assert "Transcript" in ja_text
    assert "Other" in ja_text
    assert "音声" in ja_text
    assert "ビデオ" in ja_text
    assert "画面共有" in ja_text
    assert "参加" in ja_text
    assert "その他" in ja_text
    assert "問題" in ja_text
    assert "トラブルシューティング" in ja_text
    assert "ダイアログ" in ja_text
    assert "会議コントロール" in ja_text
    assert "遮る" in ja_text
    assert "閉じます" in ja_text
    assert "原因は断定しません" in ja_text
    assert "送信" not in ja_text
    assert "提出" not in ja_text
    assert "報告します" not in ja_text
    assert "カテゴリ" not in ja_text
    assert "選択します" not in ja_text
    assert "ログを" not in ja_text
    assert "ログや" not in ja_text
    assert "アップロード" not in ja_text
    assert "診断データ" not in ja_text
    assert "サポート" not in ja_text
    assert "解決します" not in ja_text
    assert "修復" not in ja_text
    assert "改善します" not in ja_text
    assert "保証します" not in ja_text
    assert "必ず" not in ja_text


def test_meeting_control_map_has_japanese_add_coworkers_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-control-map-demo")
    step = next(step for step in flow.steps if step.id == "control-map-add-coworkers")

    assert step.action.entrypoint_id == "ringcentral.video.main.add-coworkers"
    assert step.action.operation == "open"
    assert step.narration.placement == "during"
    assert step.narration.action_offset_ms == 350
    add_coworkers_entrypoint = package.entrypoint_by_id(
        "ringcentral.video.main.add-coworkers"
    )
    assert len(add_coworkers_entrypoint.open_steps) == 1
    open_step = add_coworkers_entrypoint.open_steps[0]
    assert open_step.action == "clickWindowControl"
    assert open_step.target == "Add coworkers"
    assert open_step.match["controlType"] == "button"
    assert open_step.match["cleanup"] == "modal"
    assert "name/email field" in add_coworkers_entrypoint.presenter_notes[0]
    assert "suggestions" in add_coworkers_entrypoint.presenter_notes[0]
    assert "Copy meeting link" in add_coworkers_entrypoint.presenter_notes[0]
    assert "Cancel" in add_coworkers_entrypoint.presenter_notes[0]
    assert "Invite" in add_coworkers_entrypoint.presenter_notes[0]
    assert "Invite toolbar control" in add_coworkers_entrypoint.presenter_notes[1]
    assert "empty-room" in add_coworkers_entrypoint.presenter_notes[2]
    assert "first one here" in add_coworkers_entrypoint.presenter_notes[2]
    assert "dialog X or Cancel" in add_coworkers_entrypoint.presenter_notes[3]
    assert "blocks the toolbar" in add_coworkers_entrypoint.presenter_notes[3]
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "Add coworkers" in ja_text
    assert "Invite" in ja_text
    assert "空の会議" in ja_text
    assert "招待" in ja_text
    assert "同僚" in ja_text
    assert "検索" in ja_text
    assert "会議リンク" in ja_text
    assert "候補" in ja_text
    assert "名前" in ja_text
    assert "メールアドレス" in ja_text
    assert "読み上げません" in ja_text
    assert "ユーザー" in ja_text
    assert "明示的" in ja_text
    assert "確認" in ja_text
    assert "閉じます" in ja_text
    assert "招待します" not in ja_text
    assert "Invite を押します" not in ja_text
    assert "送信します" not in ja_text
    assert "追加します" not in ja_text
    assert "入力します" not in ja_text
    assert "検索します" not in ja_text
    assert "コピーします" not in ja_text
    assert "読み上げます" not in ja_text
    assert "参加者がいる場合も" not in ja_text
    assert "必ず" not in ja_text


def test_meeting_control_map_has_japanese_participants_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-control-map-demo")
    step = next(step for step in flow.steps if step.id == "control-map-participants")

    assert step.action.entrypoint_id == "ringcentral.video.toolbar.participants"
    assert step.action.operation == "open"
    assert step.narration.placement == "during"
    assert step.narration.action_offset_ms == 350
    participants_entrypoint = package.entrypoint_by_id(
        "ringcentral.video.toolbar.participants"
    )
    assert participants_entrypoint.question_aliases["ja"] == [
        "参加者",
        "参加者一覧",
        "参加者パネル",
    ]
    assert len(participants_entrypoint.open_steps) == 1
    open_step = participants_entrypoint.open_steps[0]
    assert open_step.action == "clickWindowControl"
    assert open_step.target == "Participants"
    assert open_step.match["controlType"] == "button"
    assert open_step.match["cleanup"] == "toggle"
    assert "attendee count" in participants_entrypoint.presenter_notes[0]
    assert "meeting control" in participants_entrypoint.presenter_notes[0]
    assert "Do not identify participants" in participants_entrypoint.presenter_notes[1]
    assert "verified and allowed" in participants_entrypoint.presenter_notes[1]
    assert "Participant and Chat tabs" in participants_entrypoint.presenter_notes[2]
    assert "search" in participants_entrypoint.presenter_notes[2]
    assert "invite" in participants_entrypoint.presenter_notes[2]
    assert "lock" in participants_entrypoint.presenter_notes[2]
    assert "mute" in participants_entrypoint.presenter_notes[2]
    assert "raise-hand" in participants_entrypoint.presenter_notes[2]
    assert "more controls" in participants_entrypoint.presenter_notes[2]
    assert "Toggle the Participants button" in participants_entrypoint.presenter_notes[3]
    assert "before opening Chat" in participants_entrypoint.presenter_notes[3]
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "Participants" in ja_text
    assert "参加者" in ja_text
    assert "一覧" in ja_text
    assert "人数" in ja_text
    assert "Invite" in ja_text
    assert "ロック" in ja_text
    assert "ミュート" in ja_text
    assert "挙手" in ja_text
    assert "その他" in ja_text
    assert "ユーザー" in ja_text
    assert "明示的" in ja_text
    assert "求め" in ja_text
    assert "表示内容" in ja_text
    assert "確認" in ja_text
    assert "読み上げません" in ja_text
    assert "閉じます" in ja_text
    assert "名前を読み上げます" not in ja_text
    assert "参加者を特定します" not in ja_text
    assert "ミュートします" not in ja_text
    assert "ロックします" not in ja_text
    assert "Invite を押します" not in ja_text
    assert "招待します" not in ja_text
    assert "検索します" not in ja_text
    assert "挙手させます" not in ja_text
    assert "操作します" not in ja_text
    assert "全員" not in ja_text
    assert "必ず" not in ja_text


def test_meeting_control_map_has_japanese_chat_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-control-map-demo")
    step = next(step for step in flow.steps if step.id == "control-map-chat")

    assert step.action.entrypoint_id == "ringcentral.video.toolbar.chat"
    assert step.action.operation == "open"
    assert step.narration.placement == "during"
    assert step.narration.action_offset_ms == 350
    chat_entrypoint = package.entrypoint_by_id("ringcentral.video.toolbar.chat")
    assert chat_entrypoint.question_aliases["ja"] == [
        "チャット",
        "チャットパネル",
        "メッセージ",
    ]
    assert len(chat_entrypoint.open_steps) == 1
    open_step = chat_entrypoint.open_steps[0]
    assert open_step.action == "clickWindowControl"
    assert open_step.target == "Chat"
    assert open_step.match["controlType"] == "button"
    assert open_step.match["cleanup"] == "toggle"
    assert "collaboration side panel" in chat_entrypoint.presenter_notes[0]
    assert "Do not read private chat text aloud" in chat_entrypoint.presenter_notes[1]
    assert "explicitly asks" in chat_entrypoint.presenter_notes[1]
    assert "Within everyone" in chat_entrypoint.presenter_notes[2]
    assert "Privately" in chat_entrypoint.presenter_notes[2]
    assert "message box" in chat_entrypoint.presenter_notes[2]
    assert "Toggle the Chat button" in chat_entrypoint.presenter_notes[3]
    assert "close the side panel" in chat_entrypoint.presenter_notes[3]
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "Chat" in ja_text
    assert "文字" in ja_text
    assert "サイド" in ja_text
    assert "リンク" in ja_text
    assert "フォローアップ" in ja_text
    assert "個別" in ja_text
    assert "メッセージ" in ja_text
    assert "プライベート" in ja_text
    assert "ユーザー" in ja_text
    assert "明示的" in ja_text
    assert "求め" in ja_text
    assert "読み上げません" in ja_text
    assert "Within everyone" in ja_text
    assert "Privately" in ja_text
    assert "閉じます" in ja_text
    assert "読み上げます" not in ja_text
    assert "読みます" not in ja_text
    assert "送信します" not in ja_text
    assert "入力します" not in ja_text
    assert "返信します" not in ja_text
    assert "開示します" not in ja_text
    assert "共有します" not in ja_text
    assert "全員に送ります" not in ja_text
    assert "必ず" not in ja_text
    assert "自動" not in ja_text


def test_meeting_control_map_has_japanese_microphone_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-control-map-demo")
    step = next(step for step in flow.steps if step.id == "control-map-microphone")

    assert step.action.entrypoint_id == "ringcentral.video.toolbar.audio"
    assert step.action.operation == "point"
    assert step.narration.placement == "before"
    assert step.narration.action_offset_ms == 0
    audio_entrypoint = package.entrypoint_by_id("ringcentral.video.toolbar.audio")
    assert audio_entrypoint.question_aliases["ja"] == [
        "マイク",
        "ミュート",
        "音声",
    ]
    assert len(audio_entrypoint.open_steps) == 1
    open_step = audio_entrypoint.open_steps[0]
    assert open_step.action == "clickWindowControl"
    assert open_step.target == "Mute"
    assert open_step.match["alternateTargets"] == "Unmute"
    assert open_step.match["controlType"] == "button"
    assert "cleanup" not in open_step.match
    assert "Unmute and Mute" in audio_entrypoint.presenter_notes[0]
    assert "current state" in audio_entrypoint.presenter_notes[0]
    assert "audio privacy" in audio_entrypoint.presenter_notes[1]
    assert "meeting readiness" in audio_entrypoint.presenter_notes[1]
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "Microphone" in ja_text
    assert "メディア" in ja_text
    assert "準備" in ja_text
    assert "発言" in ja_text
    assert "音声" in ja_text
    assert "ミュート" in ja_text
    assert "プライバシー" in ja_text
    assert "スイッチ" in ja_text
    assert "確認" in ja_text
    assert "ユーザー" in ja_text
    assert "明示的" in ja_text
    assert "クリックします" not in ja_text
    assert "押します" not in ja_text
    assert "切り替えます" not in ja_text
    assert "ミュートします" not in ja_text
    assert "ミュート解除します" not in ja_text
    assert "オンにします" not in ja_text
    assert "オフにします" not in ja_text
    assert "変更します" not in ja_text
    assert "操作します" not in ja_text
    assert "自動" not in ja_text
    assert "必ず" not in ja_text


def test_meeting_control_map_has_japanese_audio_menu_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-control-map-demo")
    step = next(step for step in flow.steps if step.id == "control-map-audio-menu")

    assert step.action.entrypoint_id == "ringcentral.video.toolbar.audio-menu"
    assert step.action.operation == "open"
    assert step.narration.placement == "during"
    assert step.narration.action_offset_ms == 350
    report = build_localization_status(package, language="ja")
    audio_menu_entrypoint = package.entrypoint_by_id(
        "ringcentral.video.toolbar.audio-menu"
    )
    assert audio_menu_entrypoint.question_aliases["ja"] == [
        "音声メニュー",
        "マイクメニュー",
        "スピーカーメニュー",
    ]
    assert report.entrypoints_with_aliases == 13
    assert report.alias_total == 34
    assert len(audio_menu_entrypoint.open_steps) == 1
    open_step = audio_menu_entrypoint.open_steps[0]
    assert open_step.action == "clickWindowControl"
    assert open_step.target == "More"
    assert open_step.match["occurrence"] == "1"
    assert open_step.match["controlType"] == "button"
    assert open_step.match["cleanup"] == "escape"
    assert "Microphone" in audio_menu_entrypoint.presenter_notes[0]
    assert "Speaker" in audio_menu_entrypoint.presenter_notes[0]
    assert "Leave computer audio" in audio_menu_entrypoint.presenter_notes[0]
    assert "Use phone audio" in audio_menu_entrypoint.presenter_notes[0]
    assert "More audio settings" in audio_menu_entrypoint.presenter_notes[0]
    assert "wrong microphone or speaker" in audio_menu_entrypoint.presenter_notes[1]
    assert "system-default-audio-devices toast" in audio_menu_entrypoint.presenter_notes[2]
    assert "only when visible" in audio_menu_entrypoint.presenter_notes[2]
    assert "overlaps Add" in audio_menu_entrypoint.presenter_notes[2]
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "マイク" in ja_text
    assert "スピーカー" in ja_text
    assert "音声" in ja_text
    assert "メニュー" in ja_text
    assert "コンピューター音声" in ja_text
    assert "電話音声" in ja_text
    assert "音声設定" in ja_text
    assert "復旧" in ja_text
    assert "ユーザー" in ja_text
    assert "明示的" in ja_text
    assert "選択します" not in ja_text
    assert "切り替えます" not in ja_text
    assert "退出します" not in ja_text
    assert "変更します" not in ja_text
    assert "開きます" not in ja_text
    assert "テストします" not in ja_text
    assert "接続します" not in ja_text
    assert "読み上げます" not in ja_text
    assert "自動" not in ja_text
    assert "必ず" not in ja_text


def test_meeting_control_map_has_japanese_camera_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-control-map-demo")
    step = next(step for step in flow.steps if step.id == "control-map-camera")

    assert step.action.entrypoint_id == "ringcentral.video.toolbar.video"
    assert step.action.operation == "point"
    assert step.narration.placement == "before"
    assert step.narration.action_offset_ms == 0
    report = build_localization_status(package, language="ja")
    camera_entrypoint = package.entrypoint_by_id("ringcentral.video.toolbar.video")
    assert "ja" not in camera_entrypoint.question_aliases
    assert report.entrypoints_with_aliases == 13
    assert report.alias_total == 34
    assert len(camera_entrypoint.open_steps) == 1
    open_step = camera_entrypoint.open_steps[0]
    assert open_step.action == "clickWindowControl"
    assert open_step.target == "Start video"
    assert open_step.match["alternateTargets"] == "Stop video"
    assert open_step.match["controlType"] == "button"
    assert "cleanup" not in open_step.match
    assert "Start video and Stop video" in camera_entrypoint.presenter_notes[0]
    assert "alternates" in camera_entrypoint.presenter_notes[0]
    assert "caret" in camera_entrypoint.presenter_notes[1]
    assert "camera" in camera_entrypoint.presenter_notes[1]
    assert "video settings" in camera_entrypoint.presenter_notes[1]
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "カメラ" in ja_text
    assert "Start video" in ja_text
    assert "Stop video" in ja_text
    assert "見える" in ja_text
    assert "状態" in ja_text
    assert "ユーザー" in ja_text
    assert "明示的" in ja_text
    assert "クリックします" not in ja_text
    assert "押します" not in ja_text
    assert "オンにします" not in ja_text
    assert "オフにします" not in ja_text
    assert "切り替えます" not in ja_text
    assert "変更します" not in ja_text
    assert "選択します" not in ja_text
    assert "開きます" not in ja_text
    assert "背景" not in ja_text
    assert "設定" not in ja_text
    assert "デバイス" not in ja_text
    assert "自動" not in ja_text
    assert "必ず" not in ja_text


def test_meeting_control_map_has_japanese_camera_menu_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-control-map-demo")
    step = next(step for step in flow.steps if step.id == "control-map-camera-menu")

    assert step.action.entrypoint_id == "ringcentral.video.toolbar.video-menu"
    assert step.action.operation == "open"
    assert step.narration.placement == "during"
    assert step.narration.action_offset_ms == 350
    report = build_localization_status(package, language="ja")
    camera_menu_entrypoint = package.entrypoint_by_id(
        "ringcentral.video.toolbar.video-menu"
    )
    assert camera_menu_entrypoint.question_aliases["ja"] == [
        "カメラメニュー",
        "ビデオメニュー",
        "カメラ選択",
    ]
    assert report.entrypoints_with_aliases == 13
    assert report.alias_total == 34
    assert report.flow_by_id["meeting-control-map-demo"].missing_step_ids == ()
    assert len(camera_menu_entrypoint.open_steps) == 1
    open_step = camera_menu_entrypoint.open_steps[0]
    assert open_step.action == "clickWindowControl"
    assert open_step.target == "More"
    assert open_step.match["occurrence"] == "2"
    assert open_step.match["controlType"] == "button"
    assert open_step.match["cleanup"] == "escape"
    assert "selected camera" in camera_menu_entrypoint.presenter_notes[0]
    assert "More video settings" in camera_menu_entrypoint.presenter_notes[0]
    assert (
        "background, quality, and camera configuration"
        in camera_menu_entrypoint.presenter_notes[1]
    )
    assert "Close the menu with Escape" in camera_menu_entrypoint.presenter_notes[2]
    camera_step = next(step for step in flow.steps if step.id == "control-map-camera")
    assert camera_step.action.entrypoint_id == "ringcentral.video.toolbar.video"
    assert camera_step.action.operation == "point"
    share_step = next(step for step in flow.steps if step.id == "control-map-share")
    assert share_step.action.entrypoint_id == "ringcentral.video.toolbar.share"
    assert "ja" in share_step.narration.localized_text
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "カメラ" in ja_text
    assert "メニュー" in ja_text
    assert "More video settings" in ja_text
    assert "背景" in ja_text
    assert "画質" in ja_text
    assert "見え方" in ja_text
    assert "ユーザー" in ja_text
    assert "明示的" in ja_text
    assert "変更しません" in ja_text
    assert "閉じます" in ja_text
    assert "切り替えます" not in ja_text
    assert "選択します" not in ja_text
    assert "変更します" not in ja_text
    assert "開きます" not in ja_text
    assert "読み上げます" not in ja_text
    assert "適用します" not in ja_text
    assert "改善します" not in ja_text
    assert "確認します" not in ja_text
    assert "自動" not in ja_text
    assert "必ず" not in ja_text


def test_meeting_control_map_has_japanese_share_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-control-map-demo")
    step = next(step for step in flow.steps if step.id == "control-map-share")

    assert step.action.entrypoint_id == "ringcentral.video.toolbar.share"
    assert step.action.operation == "open"
    assert step.narration.placement == "during"
    assert step.narration.action_offset_ms == 400
    report = build_localization_status(package, language="ja")
    share_entrypoint = package.entrypoint_by_id("ringcentral.video.toolbar.share")
    assert "ja" not in share_entrypoint.question_aliases
    assert report.entrypoints_with_aliases == 13
    assert report.alias_total == 34
    assert report.flow_by_id["meeting-control-map-demo"].missing_step_ids == ()
    assert len(share_entrypoint.open_steps) == 1
    open_step = share_entrypoint.open_steps[0]
    assert open_step.action == "clickWindowControl"
    assert open_step.target == "Share"
    assert open_step.match["controlType"] == "button"
    assert open_step.match["cleanup"] == "escape"
    assert "must not infer shared-screen content" in share_entrypoint.presenter_notes[0]
    assert "entire screen" in share_entrypoint.presenter_notes[2]
    assert "application windows" in share_entrypoint.presenter_notes[2]
    assert "Share system audio" in share_entrypoint.presenter_notes[2]
    assert "Do not click the final Share button" in share_entrypoint.presenter_notes[3]
    camera_menu_step = next(
        step for step in flow.steps if step.id == "control-map-camera-menu"
    )
    assert "ja" in camera_menu_step.narration.localized_text
    reactions_step = next(step for step in flow.steps if step.id == "control-map-reactions")
    assert reactions_step.action.entrypoint_id == "ringcentral.video.toolbar.react"
    assert "ja" in reactions_step.narration.localized_text
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "Share" in ja_text
    assert "画面" in ja_text
    assert "アプリケーション" in ja_text
    assert "ウィンドウ" in ja_text
    assert "Share system audio" in ja_text
    assert "システム音声" in ja_text
    assert "候補" in ja_text
    assert "ユーザー" in ja_text
    assert "明示的" in ja_text
    assert "確認" in ja_text
    assert "最終的な Share ボタン" in ja_text
    assert "押しません" in ja_text
    assert "読み上げません" in ja_text
    assert "閉じます" in ja_text
    assert "押します" not in ja_text
    assert "クリックします" not in ja_text
    assert "共有を開始します" not in ja_text
    assert "読み上げます" not in ja_text
    assert "推測します" not in ja_text
    assert "選択します" not in ja_text
    assert "選びます" not in ja_text
    assert "オンにします" not in ja_text
    assert "自動" not in ja_text
    assert "必ず" not in ja_text


def test_meeting_control_map_has_japanese_reactions_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-control-map-demo")
    step = next(step for step in flow.steps if step.id == "control-map-reactions")

    assert step.action.entrypoint_id == "ringcentral.video.toolbar.react"
    assert step.action.operation == "open"
    assert step.narration.placement == "during"
    assert step.narration.action_offset_ms == 350
    report = build_localization_status(package, language="ja")
    reactions_entrypoint = package.entrypoint_by_id("ringcentral.video.toolbar.react")
    assert reactions_entrypoint.question_aliases["ja"] == [
        "React ボタンの場所",
        "リアクション欄の場所",
    ]
    assert report.entrypoints_with_aliases == 13
    assert report.alias_total == 34
    assert report.flow_by_id["meeting-control-map-demo"].missing_step_ids == ()
    assert len(reactions_entrypoint.open_steps) == 1
    open_step = reactions_entrypoint.open_steps[0]
    assert open_step.action == "clickWindowControl"
    assert open_step.target == "React"
    assert open_step.match["controlType"] == "button"
    assert open_step.match["cleanup"] == "escape"
    assert "lightweight feedback signals" in reactions_entrypoint.presenter_notes[0]
    assert "Observed reactions include" in reactions_entrypoint.presenter_notes[2]
    assert "heart" in reactions_entrypoint.presenter_notes[2]
    assert "thumbs up" in reactions_entrypoint.presenter_notes[2]
    assert "celebration" in reactions_entrypoint.presenter_notes[2]
    assert "clap" in reactions_entrypoint.presenter_notes[2]
    assert "smile" in reactions_entrypoint.presenter_notes[2]
    assert "Be right back" in reactions_entrypoint.presenter_notes[2]
    assert "Close the reaction strip with Escape" in reactions_entrypoint.presenter_notes[3]
    share_step = next(step for step in flow.steps if step.id == "control-map-share")
    assert "ja" in share_step.narration.localized_text
    raise_hand_step = next(step for step in flow.steps if step.id == "control-map-raise-hand")
    assert raise_hand_step.action.entrypoint_id == "ringcentral.video.toolbar.raise-hand"
    assert raise_hand_step.action.operation == "toggle"
    assert "ja" in raise_hand_step.narration.localized_text
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "Reactions" in ja_text
    assert "リアクション" in ja_text
    assert "軽いフィードバック" in ja_text
    assert "承認" in ja_text
    assert "祝福" in ja_text
    assert "拍手" in ja_text
    assert "Be right back" in ja_text
    assert "会議中に見えるシグナル" in ja_text
    assert "ユーザー" in ja_text
    assert "明示的" in ja_text
    assert "送信しません" in ja_text
    assert "閉じます" in ja_text
    assert "Raise hand" not in ja_text
    assert "手を上げ" not in ja_text
    assert "手を下げ" not in ja_text
    assert "発言機会" not in ja_text
    assert "リアクションを送信します" not in ja_text
    assert "送信します" not in ja_text
    assert "送ります" not in ja_text
    assert "選択します" not in ja_text
    assert "選びます" not in ja_text
    assert "クリックします" not in ja_text
    assert "押します" not in ja_text
    assert "リアクションを送ります" not in ja_text
    assert "自動" not in ja_text
    assert "必ず" not in ja_text


def test_meeting_control_map_has_japanese_raise_hand_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-control-map-demo")
    step = next(step for step in flow.steps if step.id == "control-map-raise-hand")

    assert step.action.entrypoint_id == "ringcentral.video.toolbar.raise-hand"
    assert step.action.operation == "toggle"
    assert step.narration.placement == "during"
    assert step.narration.action_offset_ms == 350
    report = build_localization_status(package, language="ja")
    raise_hand_entrypoint = package.entrypoint_by_id(
        "ringcentral.video.toolbar.raise-hand"
    )
    assert raise_hand_entrypoint.question_aliases["ja"] == [
        "挙手ボタンの場所",
        "挙手の場所",
    ]
    assert report.entrypoints_with_aliases == 13
    assert report.alias_total == 34
    assert report.flow_by_id["meeting-control-map-demo"].missing_step_ids == ()
    assert len(raise_hand_entrypoint.open_steps) == 1
    open_step = raise_hand_entrypoint.open_steps[0]
    assert open_step.action == "clickWindowControl"
    assert open_step.target == "Raise hand"
    assert open_step.match["alternateTargets"] == "onconf.reactions.REMOVE_RAISE_HAND"
    assert open_step.match["controlType"] == "button"
    assert open_step.match["cleanup"] == "toggle"
    assert "moderated meeting demos" in raise_hand_entrypoint.presenter_notes[0]
    assert "toggles state" in raise_hand_entrypoint.presenter_notes[1]
    assert "hand indicator appears" in raise_hand_entrypoint.presenter_notes[1]
    assert "Click again to lower the hand" in raise_hand_entrypoint.presenter_notes[2]
    reactions_step = next(step for step in flow.steps if step.id == "control-map-reactions")
    assert reactions_step.action.entrypoint_id == "ringcentral.video.toolbar.react"
    assert reactions_step.action.operation == "open"
    assert "ja" in reactions_step.narration.localized_text
    more_step = next(step for step in flow.steps if step.id == "control-map-more")
    assert more_step.action.entrypoint_id == "ringcentral.video.toolbar.more"
    assert "ja" in more_step.narration.localized_text
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "Raise hand" in ja_text
    assert "司会進行" in ja_text
    assert "発話を遮らず" in ja_text
    assert "発言機会" in ja_text
    assert "トグル" in ja_text
    assert "会議中に見えるシグナル" in ja_text
    assert "手を上げ" in ja_text
    assert "手を下げ" in ja_text
    assert "ユーザー" in ja_text
    assert "明示的" in ja_text
    assert "実演後は手を下げます" in ja_text
    assert "リアクションとは別" in ja_text
    assert "いいね" not in ja_text
    assert "拍手" not in ja_text
    assert "祝福" not in ja_text
    assert "スマイル" not in ja_text
    assert "Be right back" not in ja_text
    assert "軽いフィードバック" not in ja_text
    assert "送信します" not in ja_text
    assert "選択します" not in ja_text
    assert "クリックします" not in ja_text
    assert "自動" not in ja_text
    assert "手を上げたままにします" not in ja_text
    assert "あとで下げます" not in ja_text
    assert "必要なら下げます" not in ja_text


def test_meeting_control_map_has_japanese_more_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-control-map-demo")
    step = next(step for step in flow.steps if step.id == "control-map-more")

    assert step.action.entrypoint_id == "ringcentral.video.toolbar.more"
    assert step.action.operation == "open"
    assert step.narration.placement == "during"
    assert step.narration.action_offset_ms == 350
    report = build_localization_status(package, language="ja")
    more_entrypoint = package.entrypoint_by_id("ringcentral.video.toolbar.more")
    assert "ja" not in more_entrypoint.question_aliases
    assert report.entrypoints_with_aliases == 13
    assert report.alias_total == 34
    assert report.flow_by_id["meeting-control-map-demo"].missing_step_ids == ()
    assert len(more_entrypoint.open_steps) == 1
    open_step = more_entrypoint.open_steps[0]
    assert open_step.action == "clickWindowControl"
    assert open_step.target == "More"
    assert open_step.match["occurrence"] == "3"
    assert open_step.match["controlType"] == "button"
    assert open_step.match["cleanup"] == "escape"
    assert "expansion point" in more_entrypoint.presenter_notes[0]
    assert "Notes is a direct toolbar button" in more_entrypoint.presenter_notes[1]
    assert "Start recording" in more_entrypoint.presenter_notes[1]
    assert "Background" in more_entrypoint.presenter_notes[1]
    assert "Settings" in more_entrypoint.presenter_notes[1]
    assert "Close the menu with Escape" in more_entrypoint.presenter_notes[2]
    raise_hand_step = next(step for step in flow.steps if step.id == "control-map-raise-hand")
    assert raise_hand_step.action.entrypoint_id == "ringcentral.video.toolbar.raise-hand"
    assert "ja" in raise_hand_step.narration.localized_text
    recording_step = next(step for step in flow.steps if step.id == "control-map-recording")
    assert recording_step.action.entrypoint_id == "ringcentral.video.more.recording"
    assert "ja" in recording_step.narration.localized_text
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "More" in ja_text
    assert "拡張メニュー" in ja_text
    assert "入口" in ja_text
    assert "Notes" in ja_text
    assert "Start recording" in ja_text
    assert "Background" in ja_text
    assert "Settings" in ja_text
    assert "使用頻度" in ja_text
    assert "慎重" in ja_text
    assert "ユーザー" in ja_text
    assert "明確に求める" in ja_text
    assert "実行しません" in ja_text
    assert "録画します" not in ja_text
    assert "録画を始めます" not in ja_text
    assert "録画を開始します" not in ja_text
    assert "Notes を開始します" not in ja_text
    assert "メモを取ります" not in ja_text
    assert "文字起こしします" not in ja_text
    assert "内容を読み上げます" not in ja_text
    assert "要約します" not in ja_text
    assert "Background を変更します" not in ja_text
    assert "Blur にします" not in ja_text
    assert "背景を選びます" not in ja_text
    assert "Settings を調整します" not in ja_text
    assert "設定を変更します" not in ja_text
    assert "翻訳をオンにします" not in ja_text
    assert "デバイスを切り替えます" not in ja_text
    assert "Leave をクリックします" not in ja_text
    assert "退出します" not in ja_text
    assert "会議を終了します" not in ja_text
    assert "自動" not in ja_text
    assert "すぐに" not in ja_text


def test_meeting_control_map_has_japanese_recording_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-control-map-demo")
    step = next(step for step in flow.steps if step.id == "control-map-recording")

    assert step.action.entrypoint_id == "ringcentral.video.more.recording"
    assert step.action.operation == "explain"
    assert step.narration.placement == "before"
    assert step.narration.action_offset_ms == 0
    report = build_localization_status(package, language="ja")
    recording_entrypoint = package.entrypoint_by_id("ringcentral.video.more.recording")
    assert recording_entrypoint.question_aliases["ja"] == [
        "Start recording の場所",
        "録画ボタンの場所",
    ]
    assert report.entrypoints_with_aliases == 13
    assert report.alias_total == 34
    assert report.flow_by_id["meeting-control-map-demo"].missing_step_ids == ()
    assert recording_entrypoint.open_steps == []
    assert "Observed under More as Start recording." in recording_entrypoint.presenter_notes
    assert "Treat this as a state-changing action during a tour." in (
        recording_entrypoint.presenter_notes
    )
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "Start recording" in ja_text
    assert "会議の状態" in ja_text
    assert "参加者" in ja_text
    assert "同意" in ja_text
    assert "ポリシー" in ja_text
    assert "ホスト権限" in ja_text
    assert "入口" in ja_text
    assert "録画の開始や停止は行いません" in ja_text
    assert "明確に求め" in ja_text
    assert "通知" in ja_text
    assert "録画します" not in ja_text
    assert "録画を始めます" not in ja_text
    assert "録画を開始します" not in ja_text
    assert "録画を停止します" not in ja_text
    assert "Start recording をクリック" not in ja_text
    assert "クリックします" not in ja_text
    assert "自動" not in ja_text


def test_meeting_control_map_has_japanese_notes_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-control-map-demo")
    step = next(step for step in flow.steps if step.id == "control-map-notes")

    assert step.action.entrypoint_id == "ringcentral.video.more.notes"
    assert step.action.operation == "open"
    assert step.narration.placement == "during"
    assert step.narration.action_offset_ms == 400
    report = build_localization_status(package, language="ja")
    notes_entrypoint = package.entrypoint_by_id("ringcentral.video.more.notes")
    assert notes_entrypoint.question_aliases["ja"] == [
        "Notes and Transcript の場所",
        "ノートと文字起こしの場所",
    ]
    assert report.entrypoints_with_aliases == 13
    assert report.alias_total == 34
    assert report.flow_by_id["meeting-control-map-demo"].missing_step_ids == ()
    assert len(notes_entrypoint.open_steps) == 2
    more_step, notes_step = notes_entrypoint.open_steps
    assert more_step.action == "clickWindowControl"
    assert more_step.target == "More"
    assert more_step.match["occurrence"] == "3"
    assert more_step.match["controlType"] == "button"
    assert notes_step.action == "clickWindowControl"
    assert notes_step.target == "onconf.controls.NOTES"
    assert notes_step.match["alternateTargets"] == "Notes"
    assert notes_step.match["controlType"] == "menuitem"
    assert notes_step.match["cleanup"] == "sidePanel"
    assert "Notes is nested under the More menu." in notes_entrypoint.presenter_notes[0]
    assert "Start notes" in notes_entrypoint.presenter_notes[3]
    assert "Also record this meeting" in notes_entrypoint.presenter_notes[3]
    assert "only explains the panel" in notes_entrypoint.presenter_notes[4]
    assert "Close the panel before continuing." in notes_entrypoint.presenter_notes[5]
    recording_step = next(step for step in flow.steps if step.id == "control-map-recording")
    assert "ja" in recording_step.narration.localized_text
    background_step = next(step for step in flow.steps if step.id == "control-map-background")
    assert "ja" in background_step.narration.localized_text
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "Notes and Transcript" in ja_text
    assert "会議メモ" in ja_text
    assert "文字起こし" in ja_text
    assert "パネル" in ja_text
    assert "Start notes" in ja_text
    assert "Also record this meeting" in ja_text
    assert "録画" in ja_text
    assert "表示して説明" in ja_text
    assert "開始しません" in ja_text
    assert "ユーザー" in ja_text
    assert "明確" in ja_text
    assert "同意" in ja_text
    assert "閉じます" in ja_text
    assert "Notes を開始します" not in ja_text
    assert "Start notes を押します" not in ja_text
    assert "録画を開始します" not in ja_text
    assert "Also record this meeting を選択" not in ja_text
    assert "文字起こしを開始します" not in ja_text
    assert "メモを作成します" not in ja_text
    assert "内容を読み上げます" not in ja_text
    assert "要約します" not in ja_text
    assert "クリックします" not in ja_text
    assert "自動" not in ja_text


def test_meeting_control_map_has_japanese_background_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-control-map-demo")
    step = next(step for step in flow.steps if step.id == "control-map-background")

    assert step.action.entrypoint_id == "ringcentral.video.more.background"
    assert step.action.operation == "open"
    assert step.narration.placement == "during"
    assert step.narration.action_offset_ms == 400
    report = build_localization_status(package, language="ja")
    background_entrypoint = package.entrypoint_by_id("ringcentral.video.more.background")
    assert "ja" not in background_entrypoint.question_aliases
    assert report.entrypoints_with_aliases == 13
    assert report.alias_total == 34
    assert report.flow_by_id["meeting-control-map-demo"].missing_step_ids == ()
    assert len(background_entrypoint.open_steps) == 2
    more_step, background_step = background_entrypoint.open_steps
    assert more_step.action == "clickWindowControl"
    assert more_step.target == "More"
    assert more_step.match["occurrence"] == "3"
    assert more_step.match["controlType"] == "button"
    assert background_step.action == "clickWindowControl"
    assert background_step.target == "Background"
    assert background_step.match["cleanup"] == "settings"
    assert "Settings dialog tabs" in background_entrypoint.presenter_notes[0]
    assert "Off" in background_entrypoint.presenter_notes[1]
    assert "Blur" in background_entrypoint.presenter_notes[1]
    assert "built-in static backgrounds" in background_entrypoint.presenter_notes[1]
    assert "video backgrounds" in background_entrypoint.presenter_notes[1]
    assert "upload" in background_entrypoint.presenter_notes[1]
    assert "Mirror my video" in background_entrypoint.presenter_notes[1]
    assert "Close the Settings dialog" in background_entrypoint.presenter_notes[2]
    notes_step = next(step for step in flow.steps if step.id == "control-map-notes")
    assert "ja" in notes_step.narration.localized_text
    settings_step = next(step for step in flow.steps if step.id == "control-map-settings")
    assert "ja" in settings_step.narration.localized_text
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "Background" in ja_text
    assert "背景" in ja_text
    assert "プライバシー" in ja_text
    assert "見え方" in ja_text
    assert "Off" in ja_text
    assert "Blur" in ja_text
    assert "画像" in ja_text
    assert "動画背景" in ja_text
    assert "アップロード" in ja_text
    assert "Mirror my video" in ja_text
    assert "候補" in ja_text
    assert "表示して説明" in ja_text
    assert "変更しません" in ja_text
    assert "選びません" in ja_text
    assert "明確に求め" in ja_text
    assert "表示された選択肢" in ja_text
    assert "部屋" in ja_text
    assert "背景サムネイル" in ja_text
    assert "視覚内容" in ja_text
    assert "読み取ったり説明したりしません" in ja_text
    assert "閉じます" in ja_text
    assert "Blur にします" not in ja_text
    assert "背景を変更します" not in ja_text
    assert "背景を選択します" not in ja_text
    assert "背景を選びます" not in ja_text
    assert "画像をアップロードします" not in ja_text
    assert "動画背景を適用します" not in ja_text
    assert "Mirror my video をオンにします" not in ja_text
    assert "部屋を確認します" not in ja_text
    assert "サムネイルを説明します" not in ja_text
    assert "プライバシーを保護します" not in ja_text
    assert "完全に隠します" not in ja_text
    assert "クリックします" not in ja_text
    assert "自動" not in ja_text


def test_meeting_control_map_has_japanese_settings_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-control-map-demo")
    step = next(step for step in flow.steps if step.id == "control-map-settings")

    assert step.action.entrypoint_id == "ringcentral.video.more.settings"
    assert step.action.operation == "open"
    assert step.narration.placement == "during"
    assert step.narration.action_offset_ms == 400
    report = build_localization_status(package, language="ja")
    settings_entrypoint = package.entrypoint_by_id("ringcentral.video.more.settings")
    assert "ja" not in settings_entrypoint.question_aliases
    assert report.entrypoints_with_aliases == 13
    assert report.alias_total == 34
    assert report.flow_by_id["meeting-control-map-demo"].missing_step_ids == ()
    assert len(settings_entrypoint.open_steps) == 2
    more_step, settings_step = settings_entrypoint.open_steps
    assert more_step.action == "clickWindowControl"
    assert more_step.target == "More"
    assert more_step.match["occurrence"] == "3"
    assert more_step.match["controlType"] == "button"
    assert settings_step.action == "clickWindowControl"
    assert settings_step.target == "Settings"
    assert settings_step.match["cleanup"] == "settings"
    assert "current or last selected section" in settings_entrypoint.presenter_notes[0]
    assert "audio" in settings_entrypoint.presenter_notes[1]
    assert "video" in settings_entrypoint.presenter_notes[1]
    assert "background" in settings_entrypoint.presenter_notes[1]
    assert "translation" in settings_entrypoint.presenter_notes[1]
    assert "join preferences" in settings_entrypoint.presenter_notes[1]
    assert "general settings" in settings_entrypoint.presenter_notes[1]
    assert "Close the Settings dialog" in settings_entrypoint.presenter_notes[2]
    background_step = next(step for step in flow.steps if step.id == "control-map-background")
    assert "ja" in background_step.narration.localized_text
    leave_step = next(step for step in flow.steps if step.id == "control-map-leave")
    assert "ja" in leave_step.narration.localized_text
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "Settings" in ja_text
    assert "設定センター" in ja_text
    assert "音声" in ja_text
    assert "ビデオ" in ja_text
    assert "背景" in ja_text
    assert "翻訳" in ja_text
    assert "入会設定" in ja_text
    assert "一般設定" in ja_text
    assert "表示して説明" in ja_text
    assert "変更しません" in ja_text
    assert "切り替えません" in ja_text
    assert "オンにしません" in ja_text
    assert "明確に求め" in ja_text
    assert "表示された項目と影響" in ja_text
    assert "デバイス名" in ja_text
    assert "アカウント情報" in ja_text
    assert "保存済みの参加設定" in ja_text
    assert "プライベート" in ja_text
    assert "読み上げたり記録したりしません" in ja_text
    assert "閉じます" in ja_text
    assert "デバイスを切り替えます" not in ja_text
    assert "音声を変更します" not in ja_text
    assert "ビデオを変更します" not in ja_text
    assert "翻訳をオンにします" not in ja_text
    assert "入会設定を変更します" not in ja_text
    assert "一般設定を変更します" not in ja_text
    assert "デバイス名を読み上げます" not in ja_text
    assert "アカウント情報を記録します" not in ja_text
    assert "クリックします" not in ja_text
    assert "保存します" not in ja_text
    assert "自動" not in ja_text


def test_meeting_control_map_has_japanese_leave_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-control-map-demo")
    step = next(step for step in flow.steps if step.id == "control-map-leave")

    assert step.action.entrypoint_id == "ringcentral.video.toolbar.leave"
    assert step.action.operation == "explain"
    assert step.narration.placement == "before"
    assert step.narration.action_offset_ms == 0
    report = build_localization_status(package, language="ja")
    leave_entrypoint = package.entrypoint_by_id("ringcentral.video.toolbar.leave")
    assert leave_entrypoint.title == "Leave meeting"
    assert leave_entrypoint.area == "Meeting toolbar"
    assert leave_entrypoint.purpose == "Leave or end the meeting."
    assert leave_entrypoint.open_steps == []
    assert "ja" not in leave_entrypoint.question_aliases
    assert report.entrypoints_with_aliases == 13
    assert report.alias_total == 34
    assert report.flow_by_id["meeting-control-map-demo"].missing_step_ids == ()
    assert "Treat this as destructive during a tour." in leave_entrypoint.presenter_notes
    assert any(
        "left-meeting state" in note and "without clicking it" in note
        for note in leave_entrypoint.presenter_notes
    )
    assert any(
        "verbal confirmation" in note and "leave or end action" in note
        for note in leave_entrypoint.presenter_notes
    )
    settings_step = next(step for step in flow.steps if step.id == "control-map-settings")
    assert "ja" in settings_step.narration.localized_text
    summary_step = next(step for step in flow.steps if step.id == "control-map-summary")
    assert "ja" in summary_step.narration.localized_text
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "Leave" in ja_text
    assert "現在の会議" in ja_text
    assert "退出" in ja_text
    assert "参加状態" in ja_text
    assert "ホスト" in ja_text
    assert "全員に影響" in ja_text
    assert "場所と役割だけ" in ja_text
    assert "明確に求め" in ja_text
    assert "表示された選択肢と影響" in ja_text
    assert "口頭で確認" in ja_text
    assert "クリックしたり" in ja_text
    assert "確定したりしません" in ja_text
    assert "クリックします" not in ja_text
    assert "押します" not in ja_text
    assert "選択します" not in ja_text
    assert "退出します" not in ja_text
    assert "終了します" not in ja_text
    assert "会議を終了します" not in ja_text
    assert "End meeting を選びます" not in ja_text
    assert "安全" not in ja_text
    assert "元に戻" not in ja_text
    assert "ホストです" not in ja_text
    assert "自動" not in ja_text
    assert "すぐに" not in ja_text


def test_meeting_control_map_has_japanese_summary_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-control-map-demo")
    step = next(step for step in flow.steps if step.id == "control-map-summary")

    assert step.action.entrypoint_id == "ringcentral.video.overview"
    assert step.action.operation == "explain"
    assert step.narration.placement == "before"
    assert step.narration.action_offset_ms == 0
    report = build_localization_status(package, language="ja")
    overview_entrypoint = package.entrypoint_by_id("ringcentral.video.overview")
    assert overview_entrypoint.title == "Meeting overview"
    assert overview_entrypoint.area == "Meeting window"
    assert overview_entrypoint.open_steps == []
    assert overview_entrypoint.question_aliases["ja"] == [
        "会議画面の概要",
        "会議画面の見取り図",
    ]
    assert report.demo_localized_steps == 51
    assert report.demo_total_steps == 51
    assert report.required_localization_complete is True
    assert report.entrypoints_with_aliases == 13
    assert report.alias_total == 34
    assert report.flow_by_id["meeting-control-map-demo"].localized_steps == 22
    assert report.flow_by_id["meeting-control-map-demo"].total_steps == 22
    assert report.flow_by_id["meeting-control-map-demo"].missing_step_ids == ()
    assert "narrative bridge" in overview_entrypoint.presenter_notes[0]
    assert "No UI action is required" in overview_entrypoint.presenter_notes[1]
    leave_step = next(step for step in flow.steps if step.id == "control-map-leave")
    assert "ja" in leave_step.narration.localized_text
    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "RingCentral Video" in ja_text
    assert "コントロールマップ" in ja_text
    assert "上部バー" in ja_text
    assert "状態確認" in ja_text
    assert "トラブルシューティング" in ja_text
    assert "参加者" in ja_text
    assert "共同作業" in ja_text
    assert "音声" in ja_text
    assert "ビデオ" in ja_text
    assert "参加準備" in ja_text
    assert "共有" in ja_text
    assert "リアクション" in ja_text
    assert "フィードバック" in ja_text
    assert "More" in ja_text
    assert "深い設定" in ja_text
    assert "慎重" in ja_text
    assert "Leave" in ja_text
    assert "退出" in ja_text
    assert "場所と役割" in ja_text
    assert "明確に依頼" in ja_text
    assert "画面上の選択肢と影響" in ja_text
    assert "実行しません" in ja_text
    assert "クリックします" not in ja_text
    assert "押します" not in ja_text
    assert "選択します" not in ja_text
    assert "開きます" not in ja_text
    assert "開始します" not in ja_text
    assert "送信します" not in ja_text
    assert "共有します" not in ja_text
    assert "録画します" not in ja_text
    assert "退出します" not in ja_text
    assert "終了します" not in ja_text
    assert "変更します" not in ja_text
    assert "切り替えます" not in ja_text
    assert "読み上げます" not in ja_text
    assert "要約します" not in ja_text
    assert "実行します" not in ja_text
    assert "自動" not in ja_text
    assert "すべて" not in ja_text
    assert "完全" not in ja_text
    assert "必ず" not in ja_text
    assert "保証" not in ja_text
    assert "安全" not in ja_text


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
