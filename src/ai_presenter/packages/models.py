from collections.abc import Mapping
from dataclasses import dataclass
import re
from types import MappingProxyType
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, field_validator, model_validator

_STOPWORDS = {
    "a",
    "can",
    "control",
    "could",
    "do",
    "how",
    "i",
    "in",
    "meeting",
    "open",
    "please",
    "show",
    "the",
    "to",
    "where",
}
_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
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
    question_aliases: dict[str, list[str]] = Field(default_factory=dict, alias="questionAliases")


@dataclass(frozen=True)
class EntrypointQuestionAlias:
    entrypoint_id: str
    language: str
    alias: str
    normalized_alias: str


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
    localized_questions: dict[str, list[str]] = Field(default_factory=dict, alias="localizedQuestions")
    localized_answers: dict[str, str] = Field(default_factory=dict, alias="localizedAnswers")
    related_entrypoint_ids: list[str] = Field(default_factory=list, alias="relatedEntrypointIds")


@dataclass(frozen=True)
class QuestionAnswerMatchCandidate:
    item: QuestionAnswer
    question: str
    normalized_question: str
    meaningful_tokens: frozenset[str]


@dataclass(frozen=True)
class EntrypointMatchCandidate:
    entrypoint: OperationEntrypoint
    id_tokens: frozenset[str]
    title_tokens: frozenset[str]
    area_tokens: frozenset[str]
    purpose_tokens: frozenset[str]
    title_or_id_tokens: frozenset[str]


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
    _entrypoints_by_id: dict[str, OperationEntrypoint] = PrivateAttr(default_factory=dict)
    _demo_flows_by_id: dict[str, DemoFlow] = PrivateAttr(default_factory=dict)
    _entrypoint_question_aliases: tuple[EntrypointQuestionAlias, ...] = PrivateAttr(
        default_factory=tuple
    )
    _qa_question_candidates: tuple[QuestionAnswerMatchCandidate, ...] = PrivateAttr(
        default_factory=tuple
    )
    _entrypoint_match_candidates: tuple[EntrypointMatchCandidate, ...] = PrivateAttr(
        default_factory=tuple
    )

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
        entrypoint_question_aliases: list[EntrypointQuestionAlias] = []
        demo_flow_ids: set[str] = set()
        demo_flows_by_id: dict[str, DemoFlow] = {}
        for entrypoint in self.operation_entrypoints:
            if entrypoint.id in entrypoint_ids:
                raise ValueError(f"duplicate operation entrypoint id: {entrypoint.id}")
            entrypoint_ids.add(entrypoint.id)
            entrypoints_by_id[entrypoint.id] = entrypoint
            for language, aliases in entrypoint.question_aliases.items():
                for alias in aliases:
                    normalized_alias = alias.strip().casefold()
                    if not normalized_alias:
                        continue
                    entrypoint_question_aliases.append(
                        EntrypointQuestionAlias(
                            entrypoint_id=entrypoint.id,
                            language=language,
                            alias=alias.strip(),
                            normalized_alias=normalized_alias,
                        )
                    )

        for flow in self.demo_flows:
            if flow.id in demo_flow_ids:
                raise ValueError(f"duplicate demo flow id: {flow.id}")
            demo_flow_ids.add(flow.id)
            demo_flows_by_id[flow.id] = flow
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
        self._entrypoints_by_id = entrypoints_by_id
        self._demo_flows_by_id = demo_flows_by_id
        self._entrypoint_question_aliases = tuple(entrypoint_question_aliases)
        self._qa_question_candidates = _build_qa_question_candidates(self.qa)
        self._entrypoint_match_candidates = _build_entrypoint_match_candidates(
            self.operation_entrypoints
        )
        return self

    @property
    def entrypoints_by_id(self) -> Mapping[str, OperationEntrypoint]:
        return MappingProxyType(self._entrypoints_by_id)

    @property
    def demo_flows_by_id(self) -> Mapping[str, DemoFlow]:
        return MappingProxyType(self._demo_flows_by_id)

    @property
    def entrypoint_question_aliases(self) -> tuple[EntrypointQuestionAlias, ...]:
        return self._entrypoint_question_aliases

    @property
    def qa_question_candidates(self) -> tuple[QuestionAnswerMatchCandidate, ...]:
        return self._qa_question_candidates

    @property
    def entrypoint_match_candidates(self) -> tuple[EntrypointMatchCandidate, ...]:
        return self._entrypoint_match_candidates

    def entrypoint_by_id(self, entrypoint_id: str) -> OperationEntrypoint:
        try:
            return self._entrypoints_by_id[entrypoint_id]
        except KeyError:
            raise KeyError(f"Unknown operation entrypoint: {entrypoint_id}") from None

    def demo_flow_by_id(self, flow_id: str) -> DemoFlow:
        try:
            return self._demo_flows_by_id[flow_id]
        except KeyError:
            available = ", ".join(self._demo_flows_by_id) or "none"
            raise KeyError(
                f"Unknown demo flow: {flow_id}. Available flows: {available}"
            ) from None

    def with_demo_flow(self, flow: DemoFlow) -> "MaterialPackage":
        data = self.model_dump(by_alias=True)
        data["demoFlows"] = [*data.get("demoFlows", []), flow.model_dump(by_alias=True)]
        return MaterialPackage.model_validate(data)


def match_field_tokens(text: str) -> frozenset[str]:
    return frozenset(_TOKEN_PATTERN.findall(text.casefold()))


def match_meaningful_tokens(text: str) -> frozenset[str]:
    return frozenset(
        token for token in match_field_tokens(text) if token not in _STOPWORDS and len(token) >= 3
    )


def _build_qa_question_candidates(
    items: list[QuestionAnswer],
) -> tuple[QuestionAnswerMatchCandidate, ...]:
    candidates: list[QuestionAnswerMatchCandidate] = []
    for item in items:
        for question in _qa_questions(item):
            candidates.append(
                QuestionAnswerMatchCandidate(
                    item=item,
                    question=question,
                    normalized_question=question.casefold(),
                    meaningful_tokens=match_meaningful_tokens(question),
                )
            )
    return tuple(candidates)


def _qa_questions(item: QuestionAnswer) -> list[str]:
    questions = [item.question]
    for localized in item.localized_questions.values():
        questions.extend(localized)
    return questions


def _build_entrypoint_match_candidates(
    entrypoints: list[OperationEntrypoint],
) -> tuple[EntrypointMatchCandidate, ...]:
    candidates: list[EntrypointMatchCandidate] = []
    for entrypoint in entrypoints:
        id_tokens = match_field_tokens(entrypoint.id)
        title_tokens = match_field_tokens(entrypoint.title)
        candidates.append(
            EntrypointMatchCandidate(
                entrypoint=entrypoint,
                id_tokens=id_tokens,
                title_tokens=title_tokens,
                area_tokens=match_field_tokens(entrypoint.area),
                purpose_tokens=match_field_tokens(entrypoint.purpose),
                title_or_id_tokens=title_tokens | id_tokens,
            )
        )
    return tuple(candidates)


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
