import re
from dataclasses import dataclass

from ai_presenter.desktop.base import VisibleControl, VisibleWindow
from ai_presenter.packages.models import MaterialPackage

_RISKY_WORDS = {
    "delete",
    "remove",
    "leave",
    "end",
    "send",
    "submit",
    "pay",
    "purchase",
    "transfer",
    "record",
    "share",
    "invite",
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
    if control_type.casefold() in {"tab", "tabitem", "menuitem"}:
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
    entrypoints = []
    steps = [
        {
            "id": "overview",
            "title": "App overview",
            "action": {"entrypointId": f"{app_id}.overview", "operation": "explain"},
            "narration": {
                "text": (
                    f"This is {window.title}. I will introduce visible controls and "
                    "avoid risky actions."
                ),
                "placement": "before",
            },
        }
    ]
    entrypoints.append(
        {
            "id": f"{app_id}.overview",
            "title": "App overview",
            "area": window.title,
            "purpose": f"Introduce the visible surface of {window.title}.",
            "openSteps": [],
            "presenterNotes": ["Generated from a running desktop window."],
        }
    )
    explainers = {
        "overview": {
            "shortScript": (
                f"{window.title} is a running desktop app selected for a quick "
                "generated demo."
            ),
            "details": ["This package was generated in memory from visible UI controls."],
            "relatedEntrypointIds": [f"{app_id}.overview"],
        }
    }

    for control in controls:
        control_id = f"{app_id}.{_slug(control.name)}"
        safety = classify_control_safety(control.name, control.control_type)
        open_steps = []
        operation = "open" if safety.is_safe else "explain"
        if safety.is_safe:
            open_steps.append(
                {
                    "action": "clickWindowControl",
                    "target": control.name,
                    "match": {
                        "controlType": control.control_type,
                        "cleanup": "escape",
                    },
                }
            )
        entrypoints.append(
            {
                "id": control_id,
                "title": control.name,
                "area": window.title,
                "purpose": f"Explain the {control.name} control in {window.title}.",
                "openSteps": open_steps,
                "presenterNotes": [safety.reason, f"controlType={control.control_type}"],
            }
        )
        steps.append(
            {
                "id": _slug(control.name),
                "title": control.name,
                "action": {"entrypointId": control_id, "operation": operation},
                "narration": {
                    "text": f"{control.name} is visible in this app. {safety.reason}.",
                    "placement": "during" if safety.is_safe else "before",
                    "actionOffsetMs": 300,
                },
            }
        )
        explainers[_slug(control.name)] = {
            "shortScript": f"{control.name} is a visible {control.control_type} control.",
            "details": [safety.reason],
            "relatedEntrypointIds": [control_id],
        }

    return MaterialPackage.model_validate(
        {
            "appId": app_id,
            "appName": window.title or window.process,
            "version": 1,
            "profileIds": [f"{app_id}.profile"],
            "operationEntrypoints": entrypoints,
            "demoFlows": [
                {
                    "id": "temp-demo",
                    "title": f"{window.title} generated demo",
                    "goal": "Introduce visible controls safely.",
                    "steps": steps,
                }
            ],
            "explainers": explainers,
            "qa": [],
            "manualControls": [],
        }
    )


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return slug or "item"
