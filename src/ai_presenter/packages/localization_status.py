from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from ai_presenter.packages.models import MaterialPackage


@dataclass(frozen=True)
class FlowLocalizationStatus:
    flow_id: str
    localized_steps: int
    total_steps: int
    missing_step_ids: tuple[str, ...]


@dataclass(frozen=True)
class LocalizationStatusReport:
    package_id: str
    package_version: int
    language: str
    flow_statuses: tuple[FlowLocalizationStatus, ...]
    demo_localized_steps: int
    demo_total_steps: int
    qa_localized_questions: int
    qa_localized_answers: int
    qa_total: int
    missing_question_indexes: tuple[tuple[int, str], ...]
    missing_answer_indexes: tuple[tuple[int, str], ...]
    entrypoints_with_aliases: int
    entrypoint_total: int
    alias_total: int
    _flow_by_id: Mapping[str, FlowLocalizationStatus]

    @property
    def flow_by_id(self) -> Mapping[str, FlowLocalizationStatus]:
        return self._flow_by_id

    @property
    def required_localization_complete(self) -> bool:
        return (
            self.demo_localized_steps == self.demo_total_steps
            and self.qa_localized_questions == self.qa_total
            and self.qa_localized_answers == self.qa_total
        )


def build_localization_status(
    package: MaterialPackage,
    *,
    language: str = "zh",
) -> LocalizationStatusReport:
    flow_statuses: list[FlowLocalizationStatus] = []
    demo_localized_steps = 0
    demo_total_steps = 0
    for flow in package.demo_flows:
        missing: list[str] = []
        localized = 0
        for step in flow.steps:
            demo_total_steps += 1
            if step.narration.localized_text.get(language, "").strip():
                localized += 1
                demo_localized_steps += 1
            else:
                missing.append(step.id)
        flow_statuses.append(
            FlowLocalizationStatus(
                flow_id=flow.id,
                localized_steps=localized,
                total_steps=len(flow.steps),
                missing_step_ids=tuple(missing),
            )
        )

    missing_questions: list[tuple[int, str]] = []
    missing_answers: list[tuple[int, str]] = []
    for index, item in enumerate(package.qa, start=1):
        if not _has_nonblank_text(item.localized_questions.get(language, [])):
            missing_questions.append((index, item.question))
        if not item.localized_answers.get(language, "").strip():
            missing_answers.append((index, item.question))

    entrypoints_with_aliases = 0
    alias_total = 0
    for entrypoint in package.operation_entrypoints:
        aliases = [
            alias for alias in entrypoint.question_aliases.get(language, []) if alias.strip()
        ]
        if aliases:
            entrypoints_with_aliases += 1
            alias_total += len(aliases)

    flow_by_id = MappingProxyType({status.flow_id: status for status in flow_statuses})
    return LocalizationStatusReport(
        package_id=package.app_id,
        package_version=package.version,
        language=language,
        flow_statuses=tuple(flow_statuses),
        demo_localized_steps=demo_localized_steps,
        demo_total_steps=demo_total_steps,
        qa_localized_questions=len(package.qa) - len(missing_questions),
        qa_localized_answers=len(package.qa) - len(missing_answers),
        qa_total=len(package.qa),
        missing_question_indexes=tuple(missing_questions),
        missing_answer_indexes=tuple(missing_answers),
        entrypoints_with_aliases=entrypoints_with_aliases,
        entrypoint_total=len(package.operation_entrypoints),
        alias_total=alias_total,
        _flow_by_id=flow_by_id,
    )


def _has_nonblank_text(values: list[str]) -> bool:
    return any(value.strip() for value in values)


def render_localization_status_lines(report: LocalizationStatusReport) -> list[str]:
    lines = [
        f"Package: {report.package_id}",
        f"Package version: {report.package_version}",
        f"Language: {report.language}",
        "",
        "Demo flows:",
    ]
    for flow in report.flow_statuses:
        lines.append(
            f"- {flow.flow_id}: {flow.localized_steps}/{flow.total_steps} narration localized"
        )
        if flow.missing_step_ids:
            lines.append(f"  missing: {', '.join(flow.missing_step_ids)}")
    lines.extend(
        [
            "",
            "Q&A:",
            f"- localized questions: {report.qa_localized_questions}/{report.qa_total}",
        ]
    )
    if report.missing_question_indexes:
        lines.append(
            "  missing questions: "
            + ", ".join(
                f"#{index} {question}" for index, question in report.missing_question_indexes
            )
        )
    lines.append(f"- localized answers: {report.qa_localized_answers}/{report.qa_total}")
    if report.missing_answer_indexes:
        lines.append(
            "  missing answers: "
            + ", ".join(
                f"#{index} {question}" for index, question in report.missing_answer_indexes
            )
        )
    lines.extend(
        [
            "",
            "Entrypoint aliases:",
            (
                f"- questionAliases.{report.language} present on "
                f"{report.entrypoints_with_aliases}/{report.entrypoint_total} entrypoints "
                f"({report.alias_total} aliases)"
            ),
            "",
            (
                "Localization report: "
                f"{report.demo_localized_steps}/{report.demo_total_steps} demo steps, "
                f"{report.qa_localized_questions}/{report.qa_total} Q&A questions, "
                f"{report.qa_localized_answers}/{report.qa_total} Q&A answers localized "
                f"for {report.language}."
            ),
        ]
    )
    return lines
