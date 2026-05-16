from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ai_presenter.runtime.voice import PresenterVoiceSettings
from ai_presenter.runtime.voice import language_label
from ai_presenter.runtime.voice import tone_label

ControllerSourceMode = Literal["material_package", "running_desktop_app"]
ControllerVoiceReadinessStatus = Literal["OK", "FAIL"]


@dataclass(frozen=True)
class ControllerVoiceReadiness:
    status: ControllerVoiceReadinessStatus
    label: str
    detail: str = ""


@dataclass(frozen=True)
class ControllerOperatorSnapshot:
    source_mode: ControllerSourceMode
    material_package_id: str
    material_flow_id: str
    running_app_label: str
    has_running_app_selection: bool
    has_scanned_running_app: bool
    scanned_package_id: str
    scanned_flow_id: str
    voice: PresenterVoiceSettings
    voice_readiness: ControllerVoiceReadiness | None
    run_status: str
    is_running: bool
    is_stopping: bool
    question_text: str
    last_question_outcome: str


@dataclass(frozen=True)
class ControllerButtonStates:
    start_enabled: bool
    pause_enabled: bool
    end_enabled: bool
    refresh_enabled: bool
    scan_enabled: bool
    submit_enabled: bool


@dataclass(frozen=True)
class ControllerDisabledActionReasons:
    start: str = ""
    submit: str = ""


@dataclass(frozen=True)
class ControllerOperatorViewModel:
    source_label: str
    target_label: str
    flow_label: str
    voice_label: str
    voice_readiness_label: str
    scan_label: str
    run_label: str
    question_label: str
    buttons: ControllerButtonStates
    disabled_reasons: ControllerDisabledActionReasons


@dataclass(frozen=True)
class ControllerOperatorSummaryRow:
    key: str
    label: str
    value: str


def build_controller_operator_view_model(
    snapshot: ControllerOperatorSnapshot,
) -> ControllerOperatorViewModel:
    target_ready = _target_ready(snapshot)
    voice_ready = _voice_ready(snapshot.voice_readiness)
    question_text_present = bool(snapshot.question_text.strip())
    can_start_new_action = not snapshot.is_running and not snapshot.is_stopping
    disabled_reasons = ControllerDisabledActionReasons(
        start=_start_disabled_reason(snapshot, target_ready, voice_ready),
        submit=_submit_disabled_reason(
            snapshot,
            target_ready,
            voice_ready,
            question_text_present,
        ),
    )

    return ControllerOperatorViewModel(
        source_label=_source_label(snapshot.source_mode),
        target_label=_target_label(snapshot),
        flow_label=_flow_label(snapshot),
        voice_label=render_voice_label(snapshot.voice),
        voice_readiness_label=_voice_readiness_label(snapshot.voice_readiness),
        scan_label=_scan_label(snapshot),
        run_label=snapshot.run_status,
        question_label=_question_label(snapshot),
        buttons=ControllerButtonStates(
            start_enabled=can_start_new_action and target_ready and voice_ready,
            pause_enabled=snapshot.is_running and not snapshot.is_stopping,
            end_enabled=snapshot.is_running or snapshot.is_stopping,
            refresh_enabled=not snapshot.is_running and not snapshot.is_stopping,
            scan_enabled=(
                snapshot.source_mode == "running_desktop_app"
                and snapshot.has_running_app_selection
                and can_start_new_action
            ),
            submit_enabled=(
                question_text_present
                and target_ready
                and voice_ready
                and not snapshot.is_stopping
            ),
        ),
        disabled_reasons=disabled_reasons,
    )


def render_voice_label(voice: PresenterVoiceSettings) -> str:
    return f"{language_label(voice.language)} / {tone_label(voice.tone)}"


def render_controller_operator_summary(view_model: ControllerOperatorViewModel) -> str:
    return " | ".join(render_controller_operator_summary_rows(view_model))


def render_controller_operator_summary_rows(
    view_model: ControllerOperatorViewModel,
) -> tuple[str, ...]:
    return tuple(f"{row.label}: {row.value}" for row in controller_operator_summary_rows(view_model))


def controller_operator_summary_rows(
    view_model: ControllerOperatorViewModel,
) -> tuple[ControllerOperatorSummaryRow, ...]:
    action_reasons = []
    if view_model.disabled_reasons.start:
        action_reasons.append(f"Start blocked: {view_model.disabled_reasons.start}")
    if view_model.disabled_reasons.submit:
        action_reasons.append(f"Submit blocked: {view_model.disabled_reasons.submit}")
    rows = [
        ControllerOperatorSummaryRow(
            key="target",
            label="Target",
            value=f"{view_model.source_label}: {view_model.target_label}",
        ),
        ControllerOperatorSummaryRow(
            key="flow",
            label="Flow",
            value=view_model.flow_label or "-",
        ),
        ControllerOperatorSummaryRow(
            key="voice",
            label="Voice",
            value=f"{view_model.voice_label} | assets: {view_model.voice_readiness_label}",
        ),
        ControllerOperatorSummaryRow(
            key="state",
            label="State",
            value=f"{view_model.run_label} | scan: {view_model.scan_label}",
        ),
        ControllerOperatorSummaryRow(
            key="question",
            label="Question",
            value=view_model.question_label,
        ),
    ]
    if action_reasons:
        rows.append(
            ControllerOperatorSummaryRow(
                key="actions",
                label="Actions",
                value="; ".join(action_reasons),
            )
        )
    return tuple(rows)


def _source_label(source_mode: ControllerSourceMode) -> str:
    if source_mode == "running_desktop_app":
        return "Running desktop app"
    return "Material package"


def _target_ready(snapshot: ControllerOperatorSnapshot) -> bool:
    if snapshot.source_mode == "material_package":
        return bool(snapshot.material_package_id and snapshot.material_flow_id)
    return snapshot.has_running_app_selection and snapshot.has_scanned_running_app


def _voice_ready(readiness: ControllerVoiceReadiness | None) -> bool:
    return readiness is None or readiness.status == "OK"


def _voice_readiness_label(readiness: ControllerVoiceReadiness | None) -> str:
    if readiness is None:
        return "Not required"
    if readiness.status == "OK":
        return readiness.label or "OK"
    detail = readiness.detail.strip()
    return f"{readiness.label}: {detail}" if detail else readiness.label


def _start_disabled_reason(
    snapshot: ControllerOperatorSnapshot,
    target_ready: bool,
    voice_ready: bool,
) -> str:
    if snapshot.is_stopping:
        return "Controller is ending; wait for Ended."
    if snapshot.is_running:
        return "Demo is already running."
    if snapshot.source_mode == "running_desktop_app":
        if not snapshot.has_running_app_selection:
            return "Select a running app, then scan it."
        if not snapshot.has_scanned_running_app:
            return "Scan the selected running app first."
    elif not target_ready:
        return "Select a material package and flow."
    if not voice_ready:
        return _voice_disabled_reason(snapshot.voice_readiness)
    return ""


def _submit_disabled_reason(
    snapshot: ControllerOperatorSnapshot,
    target_ready: bool,
    voice_ready: bool,
    question_text_present: bool,
) -> str:
    if snapshot.is_stopping:
        return "Controller is ending; wait for Ended."
    if not question_text_present:
        return "Type a question to enable Submit."
    if snapshot.source_mode == "running_desktop_app":
        if not snapshot.has_running_app_selection:
            return "Select and scan a running app before questions."
        if not snapshot.has_scanned_running_app:
            return "Scan the selected running app before questions."
    elif not target_ready:
        return "Select a material package and flow."
    if not voice_ready:
        return _voice_disabled_reason(snapshot.voice_readiness)
    return ""


def _voice_disabled_reason(readiness: ControllerVoiceReadiness | None) -> str:
    return f"Selected voice assets are not ready: {_voice_readiness_label(readiness)}"


def _target_label(snapshot: ControllerOperatorSnapshot) -> str:
    if snapshot.source_mode == "material_package":
        return snapshot.material_package_id
    if snapshot.has_scanned_running_app and snapshot.scanned_package_id:
        return snapshot.scanned_package_id
    label = snapshot.running_app_label or "No running app selected"
    return f"{label} needs scan" if snapshot.has_running_app_selection else label


def _flow_label(snapshot: ControllerOperatorSnapshot) -> str:
    if snapshot.source_mode == "material_package":
        return snapshot.material_flow_id
    return snapshot.scanned_flow_id if snapshot.has_scanned_running_app else ""


def _scan_label(snapshot: ControllerOperatorSnapshot) -> str:
    if snapshot.source_mode == "material_package":
        return "Package target ready"
    if not snapshot.has_running_app_selection:
        return "No running app selected"
    if snapshot.has_scanned_running_app and snapshot.scanned_package_id:
        return f"Scanned {snapshot.scanned_package_id}"
    return "Scan required"


def _question_label(snapshot: ControllerOperatorSnapshot) -> str:
    if snapshot.last_question_outcome:
        return snapshot.last_question_outcome
    if (
        snapshot.source_mode == "running_desktop_app"
        and snapshot.question_text.strip()
        and not _target_ready(snapshot)
    ):
        return "Scan required before questions"
    return "No question yet"
