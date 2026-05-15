from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

_PASSIVE_DEMO_OPERATIONS = frozenset({"explain", "point", "verify"})
_EXECUTABLE_OPEN_STEP_ACTIONS = frozenset(
    {
        "clickWindowRelative",
        "clickWindowControl",
        "pressKey",
    }
)


class CamelModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class PackageOpenStep(CamelModel):
    action: str
    target: str | None = None
    match: dict[str, str] = Field(default_factory=dict)


class OperationEntrypoint(CamelModel):
    id: str
    title: str
    area: str
    purpose: str
    open_steps: list[PackageOpenStep] = Field(default_factory=list, alias="openSteps")
    presenter_notes: list[str] = Field(default_factory=list, alias="presenterNotes")


class DemoStepAction(CamelModel):
    entrypoint_id: str = Field(alias="entrypointId")
    operation: str
    target: str | None = None


class DemoStepNarration(CamelModel):
    text: str
    localized_text: dict[str, str] = Field(default_factory=dict, alias="localizedText")
    placement: Literal["before", "during", "after"] = "before"
    action_offset_ms: int = Field(default=0, alias="actionOffsetMs", ge=0)


class DemoStep(CamelModel):
    id: str
    title: str
    action: DemoStepAction
    narration: DemoStepNarration


class DemoFlow(CamelModel):
    id: str
    title: str
    goal: str
    steps: list[DemoStep]


class Explainer(CamelModel):
    short_script: str = Field(alias="shortScript")
    details: list[str] = Field(default_factory=list)
    related_entrypoint_ids: list[str] = Field(default_factory=list, alias="relatedEntrypointIds")


class QuestionAnswer(CamelModel):
    question: str
    answer: str
    related_entrypoint_ids: list[str] = Field(default_factory=list, alias="relatedEntrypointIds")


class ManualControl(CamelModel):
    name: str
    examples: list[str]
    handling: str


class MaterialPackage(CamelModel):
    app_id: str = Field(alias="appId")
    app_name: str = Field(alias="appName")
    version: int = Field(ge=1)
    profile_ids: list[str] = Field(alias="profileIds")
    operation_entrypoints: list[OperationEntrypoint] = Field(alias="operationEntrypoints")
    demo_flows: list[DemoFlow] = Field(default_factory=list, alias="demoFlows")
    explainers: dict[str, Explainer] = Field(default_factory=dict)
    qa: list[QuestionAnswer] = Field(default_factory=list)
    manual_controls: list[ManualControl] = Field(default_factory=list, alias="manualControls")

    @field_validator("app_id", "app_name")
    @classmethod
    def reject_blank_required_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("required package text cannot be blank")
        return normalized

    @model_validator(mode="after")
    def validate_entrypoint_references(self) -> "MaterialPackage":
        entrypoint_ids: set[str] = set()
        entrypoints_by_id: dict[str, OperationEntrypoint] = {}
        for entrypoint in self.operation_entrypoints:
            if entrypoint.id in entrypoint_ids:
                raise ValueError(f"duplicate operation entrypoint id: {entrypoint.id}")
            entrypoint_ids.add(entrypoint.id)
            entrypoints_by_id[entrypoint.id] = entrypoint

        for flow in self.demo_flows:
            for step in flow.steps:
                if step.action.entrypoint_id not in entrypoint_ids:
                    raise ValueError(
                        "demo flow "
                        f"{flow.id} step {step.id} references unknown entrypoint: "
                        f"{step.action.entrypoint_id}"
                    )
                _validate_demo_step_open_steps(
                    flow=flow,
                    step=step,
                    entrypoint=entrypoints_by_id[step.action.entrypoint_id],
                )

        for key, explainer in self.explainers.items():
            _validate_related_ids(
                owner=f"explainer {key}",
                related_ids=explainer.related_entrypoint_ids,
                entrypoint_ids=entrypoint_ids,
            )
        for item in self.qa:
            _validate_related_ids(
                owner=f"qa {item.question}",
                related_ids=item.related_entrypoint_ids,
                entrypoint_ids=entrypoint_ids,
            )
        return self

    def entrypoint_by_id(self, entrypoint_id: str) -> OperationEntrypoint:
        for entrypoint in self.operation_entrypoints:
            if entrypoint.id == entrypoint_id:
                return entrypoint
        raise KeyError(f"Unknown operation entrypoint: {entrypoint_id}")


def _validate_demo_step_open_steps(
    *,
    flow: DemoFlow,
    step: DemoStep,
    entrypoint: OperationEntrypoint,
) -> None:
    if step.action.operation in _PASSIVE_DEMO_OPERATIONS:
        return

    if not entrypoint.open_steps:
        raise ValueError(
            f"demo flow {flow.id} step {step.id} operation {step.action.operation} "
            f"has no executable open steps on entrypoint {entrypoint.id}"
        )

    for open_step in entrypoint.open_steps:
        if open_step.action not in _EXECUTABLE_OPEN_STEP_ACTIONS:
            raise ValueError(
                f"demo flow {flow.id} step {step.id} uses unsupported executable "
                f"open step action: {open_step.action}"
            )


def _validate_related_ids(
    *,
    owner: str,
    related_ids: list[str],
    entrypoint_ids: set[str],
) -> None:
    for related_id in related_ids:
        if related_id not in entrypoint_ids:
            raise ValueError(f"{owner} references unknown entrypoint: {related_id}")
