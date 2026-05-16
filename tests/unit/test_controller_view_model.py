from ai_presenter.runtime.controller_view_model import ControllerOperatorSnapshot
from ai_presenter.runtime.controller_view_model import ControllerVoiceReadiness
from ai_presenter.runtime.controller_view_model import build_controller_operator_view_model
from ai_presenter.runtime.controller_view_model import controller_operator_summary_rows
from ai_presenter.runtime.controller_view_model import render_controller_operator_summary
from ai_presenter.runtime.controller_view_model import render_controller_operator_summary_rows
from ai_presenter.runtime.voice import PresenterVoiceSettings


def test_material_package_view_model_is_ready_and_startable() -> None:
    view_model = build_controller_operator_view_model(
        ControllerOperatorSnapshot(
            source_mode="material_package",
            material_package_id="ringcentral-video",
            material_flow_id="meeting-control-map-demo",
            running_app_label="",
            has_running_app_selection=False,
            has_scanned_running_app=False,
            scanned_package_id="",
            scanned_flow_id="",
            voice=PresenterVoiceSettings(),
            voice_readiness=None,
            run_status="Ready",
            is_running=False,
            is_stopping=False,
            question_text="",
            last_question_outcome="",
        )
    )

    assert view_model.source_label == "Material package"
    assert view_model.target_label == "ringcentral-video"
    assert view_model.flow_label == "meeting-control-map-demo"
    assert view_model.voice_label == "English / Professional"
    assert view_model.scan_label == "Package target ready"
    assert view_model.run_label == "Ready"
    assert view_model.question_label == "No question yet"
    assert view_model.buttons.start_enabled is True
    assert view_model.buttons.pause_enabled is False
    assert view_model.buttons.end_enabled is False
    assert view_model.buttons.refresh_enabled is True
    assert view_model.buttons.scan_enabled is False
    assert view_model.buttons.submit_enabled is False


def test_ready_material_package_has_no_start_reason_and_submit_needs_question() -> None:
    view_model = build_controller_operator_view_model(
        ControllerOperatorSnapshot(
            source_mode="material_package",
            material_package_id="ringcentral-video",
            material_flow_id="meeting-control-map-demo",
            running_app_label="",
            has_running_app_selection=False,
            has_scanned_running_app=False,
            scanned_package_id="",
            scanned_flow_id="",
            voice=PresenterVoiceSettings(),
            voice_readiness=None,
            run_status="Ready",
            is_running=False,
            is_stopping=False,
            question_text="",
            last_question_outcome="",
        )
    )

    assert view_model.buttons.start_enabled is True
    assert view_model.disabled_reasons.start == ""
    assert view_model.buttons.submit_enabled is False
    assert view_model.disabled_reasons.submit == "Type a question to enable Submit."


def test_material_package_missing_voice_assets_blocks_start_and_submit() -> None:
    view_model = build_controller_operator_view_model(
        ControllerOperatorSnapshot(
            source_mode="material_package",
            material_package_id="ringcentral-video",
            material_flow_id="meeting-control-map-demo",
            running_app_label="",
            has_running_app_selection=False,
            has_scanned_running_app=False,
            scanned_package_id="",
            scanned_flow_id="",
            voice=PresenterVoiceSettings(language="zh", tone="friendly"),
            voice_readiness=ControllerVoiceReadiness(
                status="FAIL",
                label="FAIL",
                detail="speech=windows-sapi-zh requires installed SAPI voice matching Huihui",
            ),
            run_status="Ready",
            is_running=False,
            is_stopping=False,
            question_text="chat",
            last_question_outcome="",
        )
    )

    assert "Huihui" in view_model.voice_readiness_label
    assert view_model.buttons.start_enabled is False
    assert view_model.buttons.submit_enabled is False


def test_missing_voice_assets_explain_start_and_submit_disabled() -> None:
    view_model = build_controller_operator_view_model(
        ControllerOperatorSnapshot(
            source_mode="material_package",
            material_package_id="ringcentral-video",
            material_flow_id="meeting-control-map-demo",
            running_app_label="",
            has_running_app_selection=False,
            has_scanned_running_app=False,
            scanned_package_id="",
            scanned_flow_id="",
            voice=PresenterVoiceSettings(language="zh", tone="friendly"),
            voice_readiness=ControllerVoiceReadiness(
                status="FAIL",
                label="FAIL",
                detail="speech=windows-sapi-zh requires installed SAPI voice matching Huihui",
            ),
            run_status="Ready",
            is_running=False,
            is_stopping=False,
            question_text="chat",
            last_question_outcome="",
        )
    )

    assert view_model.buttons.start_enabled is False
    assert view_model.buttons.submit_enabled is False
    assert "Selected voice assets are not ready" in view_model.disabled_reasons.start
    assert "Huihui" in view_model.disabled_reasons.start
    assert "Selected voice assets are not ready" in view_model.disabled_reasons.submit
    assert "Huihui" in view_model.disabled_reasons.submit


def test_incompatible_spanish_local_voice_explains_start_and_submit_disabled() -> None:
    view_model = build_controller_operator_view_model(
        ControllerOperatorSnapshot(
            source_mode="material_package",
            material_package_id="ringcentral-video",
            material_flow_id="meeting-control-map-demo",
            running_app_label="",
            has_running_app_selection=False,
            has_scanned_running_app=False,
            scanned_package_id="",
            scanned_flow_id="",
            voice=PresenterVoiceSettings(language="es"),
            voice_readiness=ControllerVoiceReadiness(
                status="FAIL",
                label="FAIL",
                detail=(
                    "Profile ringcentral-video-bind-speaker with speech provider "
                    "windows-sapi-en cannot use Spanish / Professional. Spanish "
                    "voice output requires speech provider openai."
                ),
            ),
            run_status="Ready",
            is_running=False,
            is_stopping=False,
            question_text="chat",
            last_question_outcome="",
        )
    )

    assert view_model.voice_label == "Spanish / Professional"
    assert view_model.buttons.start_enabled is False
    assert view_model.buttons.submit_enabled is False
    assert "requires speech provider openai" in view_model.disabled_reasons.start
    assert "requires speech provider openai" in view_model.disabled_reasons.submit


def test_material_package_ready_voice_assets_preserve_start_behavior() -> None:
    view_model = build_controller_operator_view_model(
        ControllerOperatorSnapshot(
            source_mode="material_package",
            material_package_id="ringcentral-video",
            material_flow_id="meeting-control-map-demo",
            running_app_label="",
            has_running_app_selection=False,
            has_scanned_running_app=False,
            scanned_package_id="",
            scanned_flow_id="",
            voice=PresenterVoiceSettings(language="zh", tone="friendly"),
            voice_readiness=ControllerVoiceReadiness(
                status="OK",
                label="OK",
                detail="speech=windows-sapi-zh found installed SAPI voice matching Huihui",
            ),
            run_status="Ready",
            is_running=False,
            is_stopping=False,
            question_text="chat",
            last_question_outcome="",
        )
    )

    assert view_model.voice_readiness_label == "OK"
    assert view_model.buttons.start_enabled is True
    assert view_model.buttons.submit_enabled is True


def test_spanish_openai_view_model_is_startable_without_local_assets() -> None:
    view_model = build_controller_operator_view_model(
        ControllerOperatorSnapshot(
            source_mode="material_package",
            material_package_id="ringcentral-video",
            material_flow_id="meeting-control-map-demo",
            running_app_label="",
            has_running_app_selection=False,
            has_scanned_running_app=False,
            scanned_package_id="",
            scanned_flow_id="",
            voice=PresenterVoiceSettings(language="es"),
            voice_readiness=None,
            run_status="Ready",
            is_running=False,
            is_stopping=False,
            question_text="panel de participantes",
            last_question_outcome="",
        )
    )

    assert view_model.voice_label == "Spanish / Professional"
    assert view_model.voice_readiness_label == "Not required"
    assert view_model.buttons.start_enabled is True
    assert view_model.buttons.submit_enabled is True
    assert view_model.disabled_reasons.start == ""
    assert view_model.disabled_reasons.submit == ""


def test_not_applicable_voice_readiness_preserves_existing_start_behavior() -> None:
    view_model = build_controller_operator_view_model(
        ControllerOperatorSnapshot(
            source_mode="material_package",
            material_package_id="ringcentral-video",
            material_flow_id="meeting-control-map-demo",
            running_app_label="",
            has_running_app_selection=False,
            has_scanned_running_app=False,
            scanned_package_id="",
            scanned_flow_id="",
            voice=PresenterVoiceSettings(),
            voice_readiness=None,
            run_status="Ready",
            is_running=False,
            is_stopping=False,
            question_text="chat",
            last_question_outcome="",
        )
    )

    assert view_model.voice_readiness_label == "Not required"
    assert view_model.buttons.start_enabled is True
    assert view_model.buttons.submit_enabled is True


def test_running_app_requires_scan_before_start_or_submit() -> None:
    view_model = build_controller_operator_view_model(
        ControllerOperatorSnapshot(
            source_mode="running_desktop_app",
            material_package_id="ringcentral-video",
            material_flow_id="meeting-control-map-demo",
            running_app_label="Demo App (Demo:10)",
            has_running_app_selection=True,
            has_scanned_running_app=False,
            scanned_package_id="",
            scanned_flow_id="",
            voice=PresenterVoiceSettings(language="zh", tone="concise"),
            voice_readiness=None,
            run_status="Selected running app needs scanning",
            is_running=False,
            is_stopping=False,
            question_text="chat",
            last_question_outcome="",
        )
    )

    assert view_model.source_label == "Running desktop app"
    assert view_model.target_label == "Demo App (Demo:10) needs scan"
    assert view_model.flow_label == ""
    assert view_model.voice_label == "Chinese / Concise"
    assert view_model.scan_label == "Scan required"
    assert view_model.question_label == "Scan required before questions"
    assert view_model.buttons.start_enabled is False
    assert view_model.buttons.scan_enabled is True
    assert view_model.buttons.submit_enabled is False


def test_running_app_unscanned_explains_start_and_submit_scan_required() -> None:
    view_model = build_controller_operator_view_model(
        ControllerOperatorSnapshot(
            source_mode="running_desktop_app",
            material_package_id="ringcentral-video",
            material_flow_id="meeting-control-map-demo",
            running_app_label="Demo App (Demo:10)",
            has_running_app_selection=True,
            has_scanned_running_app=False,
            scanned_package_id="",
            scanned_flow_id="",
            voice=PresenterVoiceSettings(),
            voice_readiness=None,
            run_status="Selected running app needs scanning",
            is_running=False,
            is_stopping=False,
            question_text="chat",
            last_question_outcome="",
        )
    )

    assert view_model.buttons.start_enabled is False
    assert view_model.disabled_reasons.start == "Scan the selected running app first."
    assert view_model.buttons.submit_enabled is False
    assert view_model.disabled_reasons.submit == (
        "Scan the selected running app before questions."
    )


def test_running_app_without_selection_explains_select_app_before_actions() -> None:
    view_model = build_controller_operator_view_model(
        ControllerOperatorSnapshot(
            source_mode="running_desktop_app",
            material_package_id="ringcentral-video",
            material_flow_id="meeting-control-map-demo",
            running_app_label="No running apps found",
            has_running_app_selection=False,
            has_scanned_running_app=False,
            scanned_package_id="",
            scanned_flow_id="",
            voice=PresenterVoiceSettings(),
            voice_readiness=None,
            run_status="Ready",
            is_running=False,
            is_stopping=False,
            question_text="chat",
            last_question_outcome="",
        )
    )

    assert view_model.buttons.start_enabled is False
    assert view_model.disabled_reasons.start == "Select a running app, then scan it."
    assert view_model.buttons.submit_enabled is False
    assert view_model.disabled_reasons.submit == (
        "Select and scan a running app before questions."
    )


def test_operator_view_model_labels_expanded_tone() -> None:
    view_model = build_controller_operator_view_model(
        ControllerOperatorSnapshot(
            source_mode="material_package",
            material_package_id="ringcentral-video",
            material_flow_id="meeting-control-map-demo",
            running_app_label="",
            has_running_app_selection=False,
            has_scanned_running_app=False,
            scanned_package_id="",
            scanned_flow_id="",
            voice=PresenterVoiceSettings(tone="coach"),
            voice_readiness=None,
            run_status="Ready",
            is_running=False,
            is_stopping=False,
            question_text="",
            last_question_outcome="",
        )
    )

    assert view_model.voice_label == "English / Coach"


def test_running_app_scanned_selection_is_ready() -> None:
    view_model = build_controller_operator_view_model(
        ControllerOperatorSnapshot(
            source_mode="running_desktop_app",
            material_package_id="ringcentral-video",
            material_flow_id="meeting-control-map-demo",
            running_app_label="Demo App (Demo:10)",
            has_running_app_selection=True,
            has_scanned_running_app=True,
            scanned_package_id="temp.demo.10",
            scanned_flow_id="temp-demo",
            voice=PresenterVoiceSettings(tone="conversational"),
            voice_readiness=None,
            run_status="Ready",
            is_running=False,
            is_stopping=False,
            question_text="chat",
            last_question_outcome="Queued safe demo: temp.demo.chat",
        )
    )

    assert view_model.target_label == "temp.demo.10"
    assert view_model.flow_label == "temp-demo"
    assert view_model.scan_label == "Scanned temp.demo.10"
    assert view_model.question_label == "Queued safe demo: temp.demo.chat"
    assert view_model.buttons.start_enabled is True
    assert view_model.buttons.scan_enabled is True
    assert view_model.buttons.submit_enabled is True


def test_running_state_disables_target_churn_and_enables_controls() -> None:
    view_model = build_controller_operator_view_model(
        ControllerOperatorSnapshot(
            source_mode="material_package",
            material_package_id="ringcentral-video",
            material_flow_id="meeting-control-map-demo",
            running_app_label="",
            has_running_app_selection=False,
            has_scanned_running_app=False,
            scanned_package_id="",
            scanned_flow_id="",
            voice=PresenterVoiceSettings(),
            voice_readiness=None,
            run_status="Running",
            is_running=True,
            is_stopping=False,
            question_text="chat",
            last_question_outcome="",
        )
    )

    assert view_model.buttons.start_enabled is False
    assert view_model.run_label == "Running"
    assert view_model.buttons.pause_enabled is True
    assert view_model.buttons.end_enabled is True
    assert view_model.buttons.refresh_enabled is False
    assert view_model.buttons.scan_enabled is False
    assert view_model.buttons.submit_enabled is True


def test_running_state_explains_start_disabled_but_allows_submit() -> None:
    view_model = build_controller_operator_view_model(
        ControllerOperatorSnapshot(
            source_mode="material_package",
            material_package_id="ringcentral-video",
            material_flow_id="meeting-control-map-demo",
            running_app_label="",
            has_running_app_selection=False,
            has_scanned_running_app=False,
            scanned_package_id="",
            scanned_flow_id="",
            voice=PresenterVoiceSettings(),
            voice_readiness=None,
            run_status="Running",
            is_running=True,
            is_stopping=False,
            question_text="chat",
            last_question_outcome="",
        )
    )

    assert view_model.buttons.start_enabled is False
    assert view_model.disabled_reasons.start == "Demo is already running."
    assert view_model.buttons.submit_enabled is True
    assert view_model.disabled_reasons.submit == ""


def test_ending_state_keeps_end_visible_but_blocks_new_actions() -> None:
    view_model = build_controller_operator_view_model(
        ControllerOperatorSnapshot(
            source_mode="material_package",
            material_package_id="ringcentral-video",
            material_flow_id="meeting-control-map-demo",
            running_app_label="",
            has_running_app_selection=False,
            has_scanned_running_app=False,
            scanned_package_id="",
            scanned_flow_id="",
            voice=PresenterVoiceSettings(),
            voice_readiness=None,
            run_status="Ending",
            is_running=True,
            is_stopping=True,
            question_text="chat",
            last_question_outcome="",
        )
    )

    assert view_model.buttons.start_enabled is False
    assert view_model.buttons.pause_enabled is False
    assert view_model.buttons.end_enabled is True
    assert view_model.buttons.refresh_enabled is False
    assert view_model.buttons.scan_enabled is False
    assert view_model.buttons.submit_enabled is False


def test_ending_state_explains_start_and_submit_disabled() -> None:
    view_model = build_controller_operator_view_model(
        ControllerOperatorSnapshot(
            source_mode="material_package",
            material_package_id="ringcentral-video",
            material_flow_id="meeting-control-map-demo",
            running_app_label="",
            has_running_app_selection=False,
            has_scanned_running_app=False,
            scanned_package_id="",
            scanned_flow_id="",
            voice=PresenterVoiceSettings(),
            voice_readiness=None,
            run_status="Ending",
            is_running=True,
            is_stopping=True,
            question_text="chat",
            last_question_outcome="",
        )
    )

    assert view_model.buttons.start_enabled is False
    assert view_model.disabled_reasons.start == "Controller is ending; wait for Ended."
    assert view_model.buttons.submit_enabled is False
    assert view_model.disabled_reasons.submit == "Controller is ending; wait for Ended."


def test_render_operator_summary_includes_action_reasons_only_when_blocked() -> None:
    blocked = build_controller_operator_view_model(
        ControllerOperatorSnapshot(
            source_mode="running_desktop_app",
            material_package_id="ringcentral-video",
            material_flow_id="meeting-control-map-demo",
            running_app_label="Demo App (Demo:10)",
            has_running_app_selection=True,
            has_scanned_running_app=False,
            scanned_package_id="",
            scanned_flow_id="",
            voice=PresenterVoiceSettings(),
            voice_readiness=None,
            run_status="Selected running app needs scanning",
            is_running=False,
            is_stopping=False,
            question_text="chat",
            last_question_outcome="",
        )
    )
    ready = build_controller_operator_view_model(
        ControllerOperatorSnapshot(
            source_mode="material_package",
            material_package_id="ringcentral-video",
            material_flow_id="meeting-control-map-demo",
            running_app_label="",
            has_running_app_selection=False,
            has_scanned_running_app=False,
            scanned_package_id="",
            scanned_flow_id="",
            voice=PresenterVoiceSettings(),
            voice_readiness=None,
            run_status="Ready",
            is_running=False,
            is_stopping=False,
            question_text="chat",
            last_question_outcome="",
        )
    )

    blocked_summary = render_controller_operator_summary(blocked)
    ready_summary = render_controller_operator_summary(ready)

    assert (
        "Actions: Start blocked: Scan the selected running app first.; "
        "Submit blocked: Scan the selected running app before questions."
    ) in blocked_summary
    assert "Actions:" not in ready_summary


def test_operator_summary_rows_split_core_fields() -> None:
    view_model = build_controller_operator_view_model(
        ControllerOperatorSnapshot(
            source_mode="material_package",
            material_package_id="ringcentral-video",
            material_flow_id="meeting-control-map-demo",
            running_app_label="",
            has_running_app_selection=False,
            has_scanned_running_app=False,
            scanned_package_id="",
            scanned_flow_id="",
            voice=PresenterVoiceSettings(),
            voice_readiness=None,
            run_status="Ready",
            is_running=False,
            is_stopping=False,
            question_text="",
            last_question_outcome="",
        )
    )

    rows = controller_operator_summary_rows(view_model)

    assert [(row.key, row.label, row.value) for row in rows] == [
        ("target", "Target", "Material package: ringcentral-video"),
        ("flow", "Flow", "meeting-control-map-demo"),
        ("voice", "Voice", "English / Professional | assets: Not required"),
        ("state", "State", "Ready | scan: Package target ready"),
        ("question", "Question", "No question yet"),
        ("actions", "Actions", "Submit blocked: Type a question to enable Submit."),
    ]
    assert render_controller_operator_summary_rows(view_model) == (
        "Target: Material package: ringcentral-video",
        "Flow: meeting-control-map-demo",
        "Voice: English / Professional | assets: Not required",
        "State: Ready | scan: Package target ready",
        "Question: No question yet",
        "Actions: Submit blocked: Type a question to enable Submit.",
    )


def test_operator_summary_rows_include_actions_only_when_blocked() -> None:
    blocked = build_controller_operator_view_model(
        ControllerOperatorSnapshot(
            source_mode="running_desktop_app",
            material_package_id="ringcentral-video",
            material_flow_id="meeting-control-map-demo",
            running_app_label="Demo App (Demo:10)",
            has_running_app_selection=True,
            has_scanned_running_app=False,
            scanned_package_id="",
            scanned_flow_id="",
            voice=PresenterVoiceSettings(),
            voice_readiness=None,
            run_status="Selected running app needs scanning",
            is_running=False,
            is_stopping=False,
            question_text="chat",
            last_question_outcome="",
        )
    )
    ready = build_controller_operator_view_model(
        ControllerOperatorSnapshot(
            source_mode="material_package",
            material_package_id="ringcentral-video",
            material_flow_id="meeting-control-map-demo",
            running_app_label="",
            has_running_app_selection=False,
            has_scanned_running_app=False,
            scanned_package_id="",
            scanned_flow_id="",
            voice=PresenterVoiceSettings(),
            voice_readiness=None,
            run_status="Ready",
            is_running=False,
            is_stopping=False,
            question_text="chat",
            last_question_outcome="",
        )
    )

    blocked_rows = controller_operator_summary_rows(blocked)
    ready_rows = controller_operator_summary_rows(ready)
    actions = next(row for row in blocked_rows if row.key == "actions")

    assert actions.label == "Actions"
    assert "Start blocked: Scan the selected running app first." in actions.value
    assert "Submit blocked: Scan the selected running app before questions." in actions.value
    assert all(row.key != "actions" for row in ready_rows)
