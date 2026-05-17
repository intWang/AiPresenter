from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from dataclasses import replace
from pathlib import Path
from types import MappingProxyType

from ai_presenter.packages.models import MaterialPackage

_BACKTICKED_ID_RE = re.compile(r"`([^`]+)`")
_NON_SLUG_RE = re.compile(r"[^a-z0-9]+")

_REQUIRED_CHECKLIST_HEADERS = (
    "Priority",
    "Route Or Group",
    "Entrypoints",
    "Current State",
    "Validate",
    "Cleanup",
    "Privacy Boundary",
    "Record Result",
)
_REQUIRED_EVIDENCE_HEADERS = ("Entrypoint", "Evidence Level", "Main Gap")
_REQUIRED_BLOCKED_HEADERS = ("Route", "Entrypoint", "Reason")
_TARGET_ID_HEADER = "Target ID"
_OPTIONAL_TARGET_ID_HEADERS = (_TARGET_ID_HEADER,)
_NON_EVIDENCE_NOTE = "repo-derived planning list only; not live acceptance evidence."
_EVIDENCE_CAPTURE_NOTE = (
    "Evidence reminder: P0/P1 manual evidence is metadata-first. "
    "Prefer UIA/window metadata and sanitized product-control labels; screenshots require "
    "a clear verification need and privacy review path; redact or omit private meeting "
    "content before recording results."
)
_ALLOWED_EVIDENCE_LEVELS = ("Accepted", "Observed", "Repo-tested", "Backlog", "Blocked")
_ACCEPTANCE_FIELD_RE = re.compile(r"^-\s*([^:]+):\s*(.*)$")
_DATED_MANUAL_ACCEPTANCE_HEADING_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}\b.*manual ringcentral acceptance",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ValidationTarget:
    id: str
    priority: str
    route_or_group: str
    entrypoint_ids: tuple[str, ...]
    flow_ids: tuple[str, ...]
    current_state: str
    validate: str
    cleanup: str
    privacy_boundary: str
    record_result: str
    evidence_levels: Mapping[str, str]
    evidence_gaps: Mapping[str, str]
    blocked_reason: str | None = None


@dataclass(frozen=True)
class ValidationTargetCatalog:
    package_id: str
    checklist_path: Path
    evidence_path: Path | None
    targets: tuple[ValidationTarget, ...]
    targets_by_id: Mapping[str, ValidationTarget]


@dataclass(frozen=True)
class EvidenceIndexIntegrityReport:
    package_id: str
    entrypoint_count: int
    evidence_entrypoint_count: int
    evidence_levels: Mapping[str, str]
    evidence_gaps: Mapping[str, str]


def discover_validation_targets(
    package: MaterialPackage,
    *,
    checklist_text: str,
    checklist_path: Path,
    evidence_text: str | None = None,
    evidence_path: Path | None = None,
    include_blocked: bool = False,
) -> ValidationTargetCatalog:
    if evidence_text and evidence_text.strip():
        evidence_report = validate_entrypoint_evidence_index(package, evidence_text)
        evidence_levels = evidence_report.evidence_levels
        evidence_gaps = evidence_report.evidence_gaps
    else:
        evidence_levels, evidence_gaps = {}, {}
    targets = _parse_priority_checklist(
        package=package,
        checklist_text=checklist_text,
        evidence_levels=evidence_levels,
        evidence_gaps=evidence_gaps,
    )
    if include_blocked:
        targets.extend(
            _parse_blocked_targets(
                package=package,
                checklist_text=checklist_text,
                evidence_levels=evidence_levels,
                evidence_gaps=evidence_gaps,
            )
        )
    _validate_unique_target_ids(targets)
    target_tuple = tuple(targets)
    return ValidationTargetCatalog(
        package_id=package.app_id,
        checklist_path=checklist_path,
        evidence_path=evidence_path,
        targets=target_tuple,
        targets_by_id=MappingProxyType({target.id: target for target in target_tuple}),
    )


def validate_entrypoint_evidence_index(
    package: MaterialPackage,
    evidence_text: str,
    *,
    acceptance_text: str | None = None,
) -> EvidenceIndexIntegrityReport:
    evidence_levels, evidence_gaps = _parse_entrypoint_evidence(evidence_text)
    _validate_entrypoint_evidence_integrity(package, evidence_levels)
    if acceptance_text is not None:
        _validate_accepted_entrypoints_have_passing_manual_runs(
            evidence_levels=evidence_levels,
            acceptance_text=acceptance_text,
        )
    return EvidenceIndexIntegrityReport(
        package_id=package.app_id,
        entrypoint_count=len(package.entrypoints_by_id),
        evidence_entrypoint_count=len(evidence_levels),
        evidence_levels=evidence_levels,
        evidence_gaps=evidence_gaps,
    )


def target_by_id(catalog: ValidationTargetCatalog, target_id: str) -> ValidationTarget:
    try:
        return catalog.targets_by_id[target_id]
    except KeyError:
        available = ", ".join(catalog.targets_by_id) or "none"
        raise ValueError(
            f"Unknown validation target: {target_id}. Available targets: {available}"
        ) from None


def acceptance_draft_command(package_id: str, target: ValidationTarget) -> str:
    checklist_target = f'{target.priority} {target.route_or_group}'
    command = ["ai-presenter", "acceptance-draft", "--package", package_id]
    if len(target.entrypoint_ids) == 1 and not target.flow_ids:
        command.extend(["--entrypoint", target.entrypoint_ids[0]])
    elif len(target.flow_ids) == 1 and not target.entrypoint_ids:
        command.extend(["--flow", target.flow_ids[0]])
    elif len(target.flow_ids) == 1 and len(target.entrypoint_ids) == 1:
        command.extend(["--flow", target.flow_ids[0]])
        command.extend(["--entrypoint", target.entrypoint_ids[0]])
    command.extend(["--checklist-target", f'"{checklist_target}"'])
    return " ".join(command)


def render_validation_target_lines(
    catalog: ValidationTargetCatalog,
    *,
    priority: str | None = None,
    target_id: str | None = None,
    include_draft_command: bool = True,
) -> list[str]:
    selected_targets = _filter_targets(catalog, priority=priority, target_id=target_id)
    lines = [
        f"Package: {catalog.package_id}",
        f"Checklist: {_display_path(catalog.checklist_path)}",
        f"Evidence: {_display_path(catalog.evidence_path) if catalog.evidence_path else 'none'}",
        f"Note: {_NON_EVIDENCE_NOTE}",
    ]
    if _should_render_evidence_capture_note(catalog, selected_targets):
        lines.append(_EVIDENCE_CAPTURE_NOTE)
    lines.append("")
    for index, target in enumerate(selected_targets):
        if index:
            lines.append("")
        lines.extend(
            _render_target_block(
                catalog.package_id,
                target,
                include_draft_command,
                include_entrypoint_draft_examples=target_id is not None,
            )
        )
    return lines


def _should_render_evidence_capture_note(
    catalog: ValidationTargetCatalog,
    selected_targets: list[ValidationTarget],
) -> bool:
    if catalog.package_id != "ringcentral-video":
        return False
    return any(
        target.blocked_reason is None and target.priority.casefold() in {"p0", "p1"}
        for target in selected_targets
    )


def _filter_targets(
    catalog: ValidationTargetCatalog,
    *,
    priority: str | None,
    target_id: str | None,
) -> list[ValidationTarget]:
    targets = list(catalog.targets)
    if target_id is not None:
        targets = [target_by_id(catalog, target_id)]
    if priority is not None:
        priority_filter = priority.strip().casefold()
        targets = [target for target in targets if target.priority.casefold() == priority_filter]
    return targets


def _render_target_block(
    package_id: str,
    target: ValidationTarget,
    include_draft_command: bool,
    *,
    include_entrypoint_draft_examples: bool = False,
) -> list[str]:
    lines = [f"- {target.id} [{target.priority}] {target.route_or_group}"]
    if target.entrypoint_ids:
        lines.append(f"  entrypoints: {', '.join(target.entrypoint_ids)}")
    if target.flow_ids:
        lines.append(f"  flows: {', '.join(target.flow_ids)}")
    lines.append(f"  evidence: {_format_evidence(target)}")
    lines.append(f"  current: {target.current_state}")
    lines.append(f"  validate: {target.validate}")
    if target.cleanup:
        lines.append(f"  cleanup: {target.cleanup}")
    if target.privacy_boundary:
        lines.append(f"  privacy: {target.privacy_boundary}")
    if target.blocked_reason is not None:
        lines.append(f"  blocked: {target.blocked_reason}")
    if include_draft_command and target.blocked_reason is None:
        lines.append(f"  draft: {acceptance_draft_command(package_id, target)}")
        if include_entrypoint_draft_examples:
            examples = _entrypoint_draft_example_commands(package_id, target)
            if examples:
                lines.append("  entrypoint draft examples:")
                lines.extend(f"    - {example}" for example in examples)
    return lines


def _entrypoint_draft_example_commands(
    package_id: str,
    target: ValidationTarget,
) -> list[str]:
    if target.flow_ids or len(target.entrypoint_ids) <= 1:
        return []
    return [
        acceptance_draft_command(
            package_id,
            replace(target, entrypoint_ids=(entrypoint_id,)),
        )
        for entrypoint_id in target.entrypoint_ids
    ]


def _format_evidence(target: ValidationTarget) -> str:
    if not target.entrypoint_ids:
        return "unknown"
    return ", ".join(
        f"{entrypoint_id}={target.evidence_levels.get(entrypoint_id, 'unknown')}"
        for entrypoint_id in target.entrypoint_ids
    )


def _parse_priority_checklist(
    *,
    package: MaterialPackage,
    checklist_text: str,
    evidence_levels: Mapping[str, str],
    evidence_gaps: Mapping[str, str],
) -> list[ValidationTarget]:
    section = _extract_section(checklist_text, "Priority Checklist")
    rows = _parse_first_table(
        section,
        _REQUIRED_CHECKLIST_HEADERS,
        "Priority Checklist",
        optional_headers=_OPTIONAL_TARGET_ID_HEADERS,
    )
    targets: list[ValidationTarget] = []
    for row in rows:
        route_or_group = row["route or group"]
        ids = _extract_ids(row["entrypoints"])
        entrypoint_ids, flow_ids = _classify_ids(package, route_or_group, ids)
        target_evidence_levels, target_evidence_gaps = _evidence_for(
            entrypoint_ids,
            evidence_levels,
            evidence_gaps,
        )
        targets.append(
            ValidationTarget(
                id=_target_id_from_row(
                    row,
                    fallback_id=_target_id(row["priority"], route_or_group),
                    route_or_group=route_or_group,
                ),
                priority=row["priority"],
                route_or_group=route_or_group,
                entrypoint_ids=entrypoint_ids,
                flow_ids=flow_ids,
                current_state=row["current state"],
                validate=row["validate"],
                cleanup=row["cleanup"],
                privacy_boundary=row["privacy boundary"],
                record_result=row["record result"],
                evidence_levels=target_evidence_levels,
                evidence_gaps=target_evidence_gaps,
            )
        )
    return targets


def _parse_blocked_targets(
    *,
    package: MaterialPackage,
    checklist_text: str,
    evidence_levels: Mapping[str, str],
    evidence_gaps: Mapping[str, str],
) -> list[ValidationTarget]:
    section = _extract_section(checklist_text, "Do Not Execute Yet")
    rows = _parse_first_table(
        section,
        _REQUIRED_BLOCKED_HEADERS,
        "Do Not Execute Yet",
        optional_headers=_OPTIONAL_TARGET_ID_HEADERS,
    )
    targets: list[ValidationTarget] = []
    for row in rows:
        route_or_group = row["route"]
        ids = _extract_ids(row["entrypoint"])
        entrypoint_ids, flow_ids = _classify_ids(package, route_or_group, ids)
        target_evidence_levels, target_evidence_gaps = _evidence_for(
            entrypoint_ids,
            evidence_levels,
            evidence_gaps,
        )
        reason = row["reason"]
        targets.append(
            ValidationTarget(
                id=_target_id_from_row(
                    row,
                    fallback_id=f"blocked-{_slug(route_or_group)}",
                    route_or_group=route_or_group,
                ),
                priority="P3",
                route_or_group=route_or_group,
                entrypoint_ids=entrypoint_ids,
                flow_ids=flow_ids,
                current_state="Do not execute",
                validate="Do not execute without separate confirmation workflow.",
                cleanup="",
                privacy_boundary=reason,
                record_result="Do not execute",
                evidence_levels=target_evidence_levels,
                evidence_gaps=target_evidence_gaps,
                blocked_reason=reason,
            )
        )
    return targets


def _parse_entrypoint_evidence(evidence_text: str) -> tuple[dict[str, str], dict[str, str]]:
    if not evidence_text.strip():
        return {}, {}
    section = _extract_section(evidence_text, "Entry Point Evidence Table")
    rows = _parse_first_table(section, _REQUIRED_EVIDENCE_HEADERS, "Entry Point Evidence Table")
    evidence_levels: dict[str, str] = {}
    evidence_gaps: dict[str, str] = {}
    for row in rows:
        ids = _extract_ids(row["entrypoint"])
        if not ids:
            display_entrypoint = row["entrypoint"].strip() or "<blank>"
            raise ValueError(
                f"evidence row missing backticked entrypoint id: {display_entrypoint}"
            )
        if len(ids) > 1:
            joined_ids = ", ".join(ids)
            raise ValueError(f"evidence row references multiple entrypoint ids: {joined_ids}")
        entrypoint_id = ids[0]
        if entrypoint_id in evidence_levels:
            raise ValueError(f"duplicate evidence entrypoint id: {entrypoint_id}")
        evidence_level = _strip_backticks(row["evidence level"])
        if evidence_level not in _ALLOWED_EVIDENCE_LEVELS:
            allowed = ", ".join(_ALLOWED_EVIDENCE_LEVELS)
            display_level = evidence_level or "<blank>"
            raise ValueError(
                f"invalid evidence level for {entrypoint_id}: {display_level}. "
                f"Expected one of: {allowed}"
            )
        evidence_levels[entrypoint_id] = evidence_level
        evidence_gaps[entrypoint_id] = row["main gap"]
    return evidence_levels, evidence_gaps


def _validate_accepted_entrypoints_have_passing_manual_runs(
    *,
    evidence_levels: Mapping[str, str],
    acceptance_text: str,
) -> None:
    for entrypoint_id, evidence_level in evidence_levels.items():
        if evidence_level != "Accepted":
            continue
        if _has_passing_manual_acceptance_run(entrypoint_id, acceptance_text):
            continue
        raise ValueError(
            f"Accepted evidence for {entrypoint_id} requires a dated passing "
            "live/manual acceptance run in acceptance-runs.md"
        )


def _has_passing_manual_acceptance_run(entrypoint_id: str, acceptance_text: str) -> bool:
    for heading, body in _iter_acceptance_run_sections(acceptance_text):
        if _DATED_MANUAL_ACCEPTANCE_HEADING_RE.match(heading) is None:
            continue
        fields = _parse_acceptance_fields(body)
        if entrypoint_id not in _extract_ids(fields.get("entrypoint ids tested", "")):
            continue
        if _first_field_token(fields.get("outcome", "")) != "pass":
            continue
        if _first_field_token(fields.get("accepted promotion eligible", "")) != "yes":
            continue
        if not fields.get("promotion rationale", "").strip():
            continue
        if not (
            fields.get("recovery", "").strip()
            or fields.get("cleanup", "").strip()
        ):
            continue
        if not fields.get("privacy notes", "").strip():
            continue
        return True
    return False


def _iter_acceptance_run_sections(acceptance_text: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []
    current_heading: str | None = None
    current_body: list[str] = []
    for line in acceptance_text.splitlines():
        if line.startswith("## "):
            if current_heading is not None:
                sections.append((current_heading, "\n".join(current_body)))
            current_heading = line.removeprefix("## ").strip()
            current_body = []
            continue
        if current_heading is not None:
            current_body.append(line)
    if current_heading is not None:
        sections.append((current_heading, "\n".join(current_body)))
    return sections


def _parse_acceptance_fields(section_body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in section_body.splitlines():
        match = _ACCEPTANCE_FIELD_RE.match(line.strip())
        if match is None:
            continue
        fields[match.group(1).strip().casefold()] = match.group(2).strip()
    return fields


def _first_field_token(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        return ""
    return stripped.split(maxsplit=1)[0].strip(".,;:").casefold()


def _extract_section(text: str, heading: str) -> str:
    heading_line = f"## {heading}"
    lines = text.splitlines()
    start_index: int | None = None
    for index, line in enumerate(lines):
        if line.strip() == heading_line:
            start_index = index + 1
            break
    if start_index is None:
        raise ValueError(f"Missing markdown section: {heading_line}")
    end_index = len(lines)
    for index in range(start_index, len(lines)):
        if lines[index].startswith("## "):
            end_index = index
            break
    return "\n".join(lines[start_index:end_index])


def _parse_first_table(
    section: str,
    required_headers: tuple[str, ...],
    section_name: str,
    optional_headers: tuple[str, ...] = (),
) -> list[dict[str, str]]:
    table_lines = [line.strip() for line in section.splitlines() if line.strip().startswith("|")]
    if len(table_lines) < 2:
        raise ValueError(f"Missing markdown table in section: {section_name}")

    headers = [_normalize_header(header) for header in _split_table_row(table_lines[0])]
    missing_headers = [
        _normalize_header(header)
        for header in required_headers
        if _normalize_header(header) not in headers
    ]
    if missing_headers:
        missing = ", ".join(missing_headers)
        raise ValueError(f"Missing required table headers in {section_name}: {missing}")

    header_index = {header: index for index, header in enumerate(headers)}
    headers_to_capture = tuple(required_headers) + tuple(
        header
        for header in optional_headers
        if _normalize_header(header) in header_index
    )
    rows: list[dict[str, str]] = []
    for table_line in table_lines[2:]:
        cells = _split_table_row(table_line)
        if not any(cells):
            continue
        row: dict[str, str] = {}
        for header in headers_to_capture:
            normalized = _normalize_header(header)
            cell_index = header_index[normalized]
            row[normalized] = cells[cell_index] if cell_index < len(cells) else ""
        rows.append(row)
    return rows


def _normalize_header(header: str) -> str:
    return header.strip().casefold()


def _split_table_row(row: str) -> list[str]:
    return [cell.strip() for cell in row.strip().strip("|").split("|")]


def _extract_ids(cell: str) -> tuple[str, ...]:
    return tuple(match.strip() for match in _BACKTICKED_ID_RE.findall(cell) if match.strip())


def _classify_ids(
    package: MaterialPackage,
    route_or_group: str,
    ids: tuple[str, ...],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    entrypoint_ids: list[str] = []
    flow_ids: list[str] = []
    for package_id in ids:
        if package_id in package.entrypoints_by_id:
            entrypoint_ids.append(package_id)
        elif package_id in package.demo_flows_by_id:
            flow_ids.append(package_id)
        else:
            raise ValueError(
                f"Checklist target {route_or_group} references unknown package id: {package_id}"
            )
    return tuple(entrypoint_ids), tuple(flow_ids)


def _slug(value: str) -> str:
    slug = _NON_SLUG_RE.sub("-", value.strip().casefold()).strip("-")
    return slug or "target"


def _target_id(priority: str, route_or_group: str) -> str:
    return f"{priority.strip().casefold()}-{_slug(route_or_group)}"


def _target_id_from_row(
    row: Mapping[str, str],
    *,
    fallback_id: str,
    route_or_group: str,
) -> str:
    target_id_key = _normalize_header(_TARGET_ID_HEADER)
    if target_id_key not in row:
        return fallback_id
    explicit_id = _strip_backticks(row[target_id_key]).strip()
    if not explicit_id:
        raise ValueError(f"blank validation target id for {route_or_group}")
    return explicit_id


def _evidence_for(
    entrypoint_ids: tuple[str, ...],
    evidence_levels: Mapping[str, str],
    evidence_gaps: Mapping[str, str],
) -> tuple[dict[str, str], dict[str, str]]:
    return (
        {
            entrypoint_id: evidence_levels.get(entrypoint_id, "unknown")
            for entrypoint_id in entrypoint_ids
        },
        {entrypoint_id: evidence_gaps.get(entrypoint_id, "") for entrypoint_id in entrypoint_ids},
    )


def _validate_entrypoint_evidence_integrity(
    package: MaterialPackage,
    evidence_levels: Mapping[str, str],
) -> None:
    package_entrypoint_ids = set(package.entrypoints_by_id)
    evidence_entrypoint_ids = set(evidence_levels)
    unknown_ids = sorted(evidence_entrypoint_ids - package_entrypoint_ids)
    if unknown_ids:
        raise ValueError(
            "evidence index references unknown entrypoint: "
            + _format_id_list_with_count(unknown_ids)
        )
    missing_ids = sorted(package_entrypoint_ids - evidence_entrypoint_ids)
    if missing_ids:
        raise ValueError(
            "evidence index missing package entrypoint: "
            + _format_id_list_with_count(missing_ids)
        )


def _validate_unique_target_ids(targets: list[ValidationTarget]) -> None:
    seen: set[str] = set()
    for target in targets:
        if target.id in seen:
            raise ValueError(f"duplicate validation target id: {target.id}")
        seen.add(target.id)


def _format_id_list_with_count(ids: list[str]) -> str:
    if len(ids) == 1:
        return ids[0]
    return f"{', '.join(ids[:5])}; and {len(ids) - 5} more" if len(ids) > 5 else ", ".join(ids)


def _strip_backticks(value: str) -> str:
    stripped = value.strip()
    if stripped.startswith("`") and stripped.endswith("`") and len(stripped) >= 2:
        return stripped[1:-1]
    return stripped


def _display_path(path: Path | None) -> str:
    if path is None:
        return "none"
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)
