import re
from dataclasses import dataclass

from ai_presenter.desktop.base import VisibleControl, VisibleWindow
from ai_presenter.packages.models import (
    DemoFlow,
    DemoStep,
    DemoStepAction,
    DemoStepNarration,
    Explainer,
    MaterialPackage,
    OperationEntrypoint,
    PackageOpenStep,
)

_RISKY_WORDS = {
    "delete",
    "end",
    "share",
    "invite",
    "leave",
    "lock",
    "lower hand",
    "mute",
    "pay",
    "purchase",
    "raise hand",
    "reaction",
    "record",
    "recording",
    "remove",
    "send",
    "start",
    "stop",
    "submit",
    "toggle",
    "transfer",
    "turn",
    "unlock",
    "unmute",
}
_SAFE_WORDS = {"settings", "preferences", "view", "menu", "help", "info", "details"}


@dataclass(frozen=True)
class ControlSafety:
    is_safe: bool
    reason: str


def classify_control_safety(name: str, control_type: str) -> ControlSafety:
    normalized = name.casefold()
    for word in _RISKY_WORDS:
        if word in normalized:
            return ControlSafety(False, f"risky label contains {word}")
    if control_type.casefold() in {"tab", "tabitem"}:
        return ControlSafety(True, f"safe control type {control_type}")
    for word in _SAFE_WORDS:
        if word in normalized:
            return ControlSafety(True, f"safe label contains {word}")
    return ControlSafety(False, "unknown safety defaults to explain-only")


def build_temporary_package(
    *,
    window: VisibleWindow,
    controls: tuple[VisibleControl, ...],
) -> MaterialPackage:
    app_id = f"temp.{_slug(window.process)}.{window.pid}"
    used_slugs = {"overview": 1}
    occurrences: dict[tuple[str, str], int] = {}
    entrypoints = [
        OperationEntrypoint(
            id=f"{app_id}.overview",
            title="App overview",
            area=window.title,
            purpose=f"Introduce the visible surface of {window.title}.",
            openSteps=[],
            presenterNotes=["Generated from a running desktop window."],
        )
    ]
    steps = [
        DemoStep(
            id="overview",
            title="App overview",
            action=DemoStepAction(entrypointId=f"{app_id}.overview", operation="explain"),
            narration=DemoStepNarration(
                text=(
                    f"This is {window.title}. I will introduce visible controls and "
                    "avoid risky actions."
                ),
                placement="before",
            ),
        )
    ]
    explainers = {
        "overview": Explainer(
            shortScript=(
                f"{window.title} is a running desktop app selected for a quick "
                "generated demo."
            ),
            details=["This package was generated in memory from visible UI controls."],
            relatedEntrypointIds=[f"{app_id}.overview"],
        )
    }

    for control in controls:
        slug = _unique_slug(_slug(control.name), used_slugs)
        control_id = f"{app_id}.{slug}"
        safety = classify_control_safety(control.name, control.control_type)
        occurrence_key = (control.name, control.control_type)
        occurrence = occurrences.get(occurrence_key, 0) + 1
        occurrences[occurrence_key] = occurrence
        open_steps: list[PackageOpenStep] = []
        operation = "open" if safety.is_safe else "explain"
        if safety.is_safe:
            match = {"controlType": control.control_type, "cleanup": "escape"}
            if occurrence > 1:
                match["occurrence"] = str(occurrence)
            open_steps.append(
                PackageOpenStep(
                    action="clickWindowControl",
                    target=control.name,
                    match=match,
                )
            )
        entrypoints.append(
            OperationEntrypoint(
                id=control_id,
                title=control.name,
                area=window.title,
                purpose=f"Explain the {control.name} control in {window.title}.",
                openSteps=open_steps,
                presenterNotes=[safety.reason, f"controlType={control.control_type}"],
            )
        )
        steps.append(
            DemoStep(
                id=slug,
                title=control.name,
                action=DemoStepAction(entrypointId=control_id, operation=operation),
                narration=DemoStepNarration(
                    text=f"{control.name} is visible in this app. {safety.reason}.",
                    placement="during" if safety.is_safe else "before",
                    actionOffsetMs=300,
                ),
            )
        )
        explainers[slug] = Explainer(
            shortScript=f"{control.name} is a visible {control.control_type} control.",
            details=[safety.reason],
            relatedEntrypointIds=[control_id],
        )

    return MaterialPackage(
        appId=app_id,
        appName=window.title or window.process,
        version=1,
        profileIds=[f"{app_id}.profile"],
        operationEntrypoints=entrypoints,
        demoFlows=[
            DemoFlow(
                id="temp-demo",
                title=f"{window.title} generated demo",
                goal="Introduce visible controls safely.",
                steps=steps,
            )
        ],
        explainers=explainers,
        qa=[],
        manualControls=[],
    )


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return slug or "item"


def _unique_slug(base_slug: str, used_slugs: dict[str, int]) -> str:
    next_count = used_slugs.get(base_slug, 0) + 1
    used_slugs[base_slug] = next_count
    if next_count == 1:
        return base_slug
    return f"{base_slug}-{next_count}"
