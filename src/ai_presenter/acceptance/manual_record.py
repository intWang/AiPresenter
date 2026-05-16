from collections.abc import Iterable
from dataclasses import dataclass

from ai_presenter.packages.models import DemoFlow
from ai_presenter.packages.models import MaterialPackage
from ai_presenter.packages.models import OperationEntrypoint
from ai_presenter.packages.models import PackageOpenStep

_REQUIRED_MANUAL_ACCEPTANCE_FIELDS = (
    "Tester",
    "RingCentral app/build",
    "App channel",
    "Windows version",
    "Locale",
    "DPI/display scale",
    "Monitor setup",
    "Audio devices",
    "Virtual mic",
    "Profile",
    "Package flow",
    "Meeting role",
    "Meeting scenario",
    "Participant count",
    "Window bounds",
    "Evidence files",
    "Steps executed",
    "Pass/fail",
    "Failures",
    "Recovery",
    "Privacy notes",
    "Locator updates needed",
)

_PRIVACY_REMINDER = (
    "Draft reminder: do not record private chat text, participant names, invite links, "
    "meeting IDs, shared content, notes, transcripts, device lists, account details, "
    "or report contents."
)


@dataclass(frozen=True)
class AcceptanceDraftRequest:
    profile_id: str | None = None
    flow_id: str | None = None
    entrypoint_id: str | None = None
    checklist_target: str | None = None
    tester: str | None = None
    local_time: str | None = None


@dataclass(frozen=True)
class AcceptanceTargetSummary:
    flow: DemoFlow | None
    entrypoint: OperationEntrypoint | None
    checklist_target: str | None


def required_manual_acceptance_fields() -> tuple[str, ...]:
    return _REQUIRED_MANUAL_ACCEPTANCE_FIELDS


def build_acceptance_target_summary(
    package: MaterialPackage,
    request: AcceptanceDraftRequest,
) -> AcceptanceTargetSummary:
    if not any((request.flow_id, request.entrypoint_id, request.checklist_target)):
        raise ValueError("Provide at least one target: --flow, --entrypoint, or --checklist-target.")

    flow = _resolve_flow(package, request.flow_id)
    entrypoint = _resolve_entrypoint(package, request.entrypoint_id)
    checklist_target = _normalize_optional_text(request.checklist_target)
    _reject_direct_no_step_entrypoint(entrypoint)

    if flow is not None and entrypoint is not None:
        flow_entrypoints = {step.action.entrypoint_id for step in flow.steps}
        if entrypoint.id not in flow_entrypoints:
            raise ValueError(f"Entrypoint {entrypoint.id} is not used by selected flow {flow.id}.")

    return AcceptanceTargetSummary(
        flow=flow,
        entrypoint=entrypoint,
        checklist_target=checklist_target,
    )


def _reject_direct_no_step_entrypoint(entrypoint: OperationEntrypoint | None) -> None:
    if entrypoint is None or entrypoint.open_steps:
        return
    raise ValueError(
        f"Entrypoint {entrypoint.id} has no executable open steps; "
        "direct acceptance drafts require a separate confirmation workflow "
        "before live execution."
    )


def render_manual_acceptance_draft(
    package: MaterialPackage,
    request: AcceptanceDraftRequest,
) -> str:
    summary = build_acceptance_target_summary(package, request)
    lines: list[str] = [
        f"## {request.local_time or 'YYYY-MM-DD HH:mm Local'} - Manual RingCentral Acceptance Draft",
        "",
        (
            "> Draft only: this is not acceptance evidence until filled after the manual run "
            "and appended to `acceptance-runs.md`."
        ),
        "> No live RingCentral action has been performed by this helper.",
        "",
        "### Package Context",
        "",
        f"- Package: `{package.app_id}` ({package.app_name})",
        f"- Package version: {package.version}",
        f"- Profile: {request.profile_id or ''}",
    ]

    if summary.flow is not None:
        lines.extend(_render_flow_context(summary.flow))
    if summary.entrypoint is not None:
        lines.extend(_render_entrypoint_context(summary.entrypoint))
    if summary.checklist_target is not None:
        lines.extend(["", "### Checklist Context", "", f"- Checklist target: {summary.checklist_target}"])

    lines.extend(["", "### Manual Acceptance Fields", ""])
    field_prefills = {
        "Tester": request.tester or "",
        "Profile": request.profile_id or "",
        "Package flow": summary.flow.id if summary.flow is not None else "",
        "Steps executed": _intended_steps(summary),
        "Privacy notes": _privacy_notes(summary),
    }
    for field in required_manual_acceptance_fields():
        lines.append(f"- {field}: {field_prefills.get(field, '')}")

    lines.extend(
        [
            "",
            "### Proof-Order Reminder",
            "",
            "- Draft-only fields above are placeholders until the manual run is complete.",
            "- Keep pass/fail, failures, recovery, evidence files, and locator updates blank until observed.",
            "",
            "### Post-Run Documentation Order",
            "",
            "1. Complete the fields above only after the manual run.",
            "2. Append the completed record to `acceptance-runs.md` first.",
            (
                "3. Update `locator-matrix.md`, `state-matrix.md`, `privacy-matrix.md`, "
                "and `evidence-index.md` only when the completed run justifies it."
            ),
        ]
    )
    return "\n".join(lines) + "\n"


def _resolve_flow(package: MaterialPackage, flow_id: str | None) -> DemoFlow | None:
    if flow_id is None:
        return None
    try:
        return package.demo_flow_by_id(flow_id)
    except KeyError as exc:
        raise ValueError(str(exc.args[0])) from exc


def _resolve_entrypoint(
    package: MaterialPackage,
    entrypoint_id: str | None,
) -> OperationEntrypoint | None:
    if entrypoint_id is None:
        return None
    try:
        return package.entrypoint_by_id(entrypoint_id)
    except KeyError as exc:
        raise ValueError(str(exc.args[0])) from exc


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _render_flow_context(flow: DemoFlow) -> list[str]:
    entrypoints = ", ".join(dict.fromkeys(step.action.entrypoint_id for step in flow.steps))
    return [
        "",
        "### Flow Context",
        "",
        f"- Flow: `{flow.id}` ({flow.title})",
        f"- Goal: {flow.goal}",
        f"- Referenced entrypoints: {entrypoints}",
    ]


def _render_entrypoint_context(entrypoint: OperationEntrypoint) -> list[str]:
    lines = [
        "",
        "### Entrypoint Context",
        "",
        f"- Entrypoint: `{entrypoint.id}` ({entrypoint.title})",
        f"- Area: {entrypoint.area}",
        f"- Purpose: {entrypoint.purpose}",
        "- Open steps:",
    ]
    open_steps = _format_open_steps(entrypoint.open_steps)
    if open_steps:
        lines.extend(f"  - {step}" for step in open_steps)
    else:
        lines.append("  - None; explain-only or blocked route.")
        lines.extend(
            [
                "",
                "### Explain-only or blocked route warning",
                "",
                (
                    "- This route has no executable open steps in the package; do not execute "
                    "the live action without a separate confirmation workflow."
                ),
            ]
        )
    if entrypoint.presenter_notes:
        lines.append("- Presenter notes:")
        lines.extend(f"  - {note}" for note in entrypoint.presenter_notes)
    return lines


def _format_open_steps(open_steps: Iterable[PackageOpenStep]) -> list[str]:
    formatted: list[str] = []
    for step in open_steps:
        parts = [step.action]
        if step.target:
            parts.append(f"target={step.target}")
        cleanup = step.match.get("cleanup")
        if cleanup:
            parts.append(f"cleanup={cleanup}")
        formatted.append(" ".join(parts))
    return formatted


def _intended_steps(summary: AcceptanceTargetSummary) -> str:
    if summary.flow is not None and summary.entrypoint is not None:
        return (
            f"Intended flow: {summary.flow.id}; "
            f"intended target during flow: {summary.entrypoint.id}; "
            "fill with actual steps after the run."
        )
    if summary.entrypoint is not None:
        return f"Intended target: {summary.entrypoint.id}; fill with actual steps after the run."
    if summary.flow is not None:
        return f"Intended flow: {summary.flow.id}; fill with actual steps after the run."
    if summary.checklist_target is not None:
        return f"Intended checklist target: {summary.checklist_target}; fill with actual steps after the run."
    return ""


def _privacy_notes(summary: AcceptanceTargetSummary) -> str:
    reminders = [_PRIVACY_REMINDER]
    if summary.entrypoint is not None and not summary.entrypoint.open_steps:
        reminders.append(
            "Explain-only or blocked route; do not execute the live action without confirmation workflow."
        )
    return " ".join(reminders)
