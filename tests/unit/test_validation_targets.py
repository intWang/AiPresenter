from pathlib import Path

import pytest

from ai_presenter.acceptance.validation_targets import acceptance_draft_command
from ai_presenter.acceptance.validation_targets import discover_validation_targets
from ai_presenter.acceptance.validation_targets import render_validation_target_lines
from ai_presenter.acceptance.validation_targets import target_by_id
from ai_presenter.acceptance.validation_targets import validate_entrypoint_evidence_index
from ai_presenter.acceptance.validation_targets import ValidationTargetCatalog
from ai_presenter.packages.loader import load_material_package
from ai_presenter.packages.models import MaterialPackage


def load_ringcentral_package() -> MaterialPackage:
    return load_material_package(Path("packages/ringcentral-video.yaml"))


def load_checklist_text() -> str:
    return Path("docs/knowledge/ringcentral-video/validation-checklist-index.md").read_text(
        encoding="utf-8"
    )


def load_evidence_text() -> str:
    return Path("docs/knowledge/ringcentral-video/evidence-index.md").read_text(encoding="utf-8")


def discover_catalog(
    *,
    checklist_text: str | None = None,
    evidence_text: str | None = None,
    include_blocked: bool = False,
) -> ValidationTargetCatalog:
    return discover_validation_targets(
        load_ringcentral_package(),
        checklist_text=checklist_text or load_checklist_text(),
        checklist_path=Path("docs/knowledge/ringcentral-video/validation-checklist-index.md"),
        evidence_text=evidence_text if evidence_text is not None else load_evidence_text(),
        evidence_path=Path("docs/knowledge/ringcentral-video/evidence-index.md"),
        include_blocked=include_blocked,
    )


def priority_checklist_with_target_id_rows(*rows: str) -> str:
    return "\n".join(
        [
            "# Validation Checklist",
            "",
            "## Priority Checklist",
            "",
            "| Priority | Target ID | Route Or Group | Entrypoints | Current State | Validate | Cleanup | Privacy Boundary | Record Result |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            *rows,
            "",
            "## Do Not Execute Yet",
            "",
            "| Route | Entrypoint | Reason |",
            "| --- | --- | --- |",
        ]
    )


def priority_checklist_without_target_id_rows(*rows: str) -> str:
    return "\n".join(
        [
            "# Validation Checklist",
            "",
            "## Priority Checklist",
            "",
            "| Priority | Route Or Group | Entrypoints | Current State | Validate | Cleanup | Privacy Boundary | Record Result |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
            *rows,
            "",
            "## Do Not Execute Yet",
            "",
            "| Route | Entrypoint | Reason |",
            "| --- | --- | --- |",
        ]
    )


def evidence_without_entrypoint(entrypoint_id: str) -> str:
    return "\n".join(
        line
        for line in load_evidence_text().splitlines()
        if not line.startswith(f"| `{entrypoint_id}` |")
    )


def evidence_with_extra_row(row: str) -> str:
    return load_evidence_text().replace("\n## Flow Coverage", f"\n{row}\n\n## Flow Coverage")


def evidence_with_level(entrypoint_id: str, level: str) -> str:
    lines = []
    for line in load_evidence_text().splitlines():
        if line.startswith(f"| `{entrypoint_id}` |"):
            cells = line.split("|")
            cells[3] = f" `{level}` "
            line = "|".join(cells)
        lines.append(line)
    return "\n".join(lines)


def test_discover_validation_targets_uses_explicit_target_ids() -> None:
    checklist_text = priority_checklist_with_target_id_rows(
        "| P0 | rcv-custom-add-coworkers | Add coworkers modal | `ringcentral.video.main.add-coworkers` | Current | Validate | Cleanup | Privacy | `acceptance-runs.md` |"
    )

    catalog = discover_catalog(checklist_text=checklist_text)
    target = target_by_id(catalog, "rcv-custom-add-coworkers")

    assert target.route_or_group == "Add coworkers modal"
    with pytest.raises(ValueError, match="Unknown validation target: p0-add-coworkers-modal"):
        target_by_id(catalog, "p0-add-coworkers-modal")


def test_discover_validation_targets_rejects_duplicate_validation_target_ids() -> None:
    checklist_text = priority_checklist_with_target_id_rows(
        "| P0 | rcv-duplicate | Add coworkers modal | `ringcentral.video.main.add-coworkers` | Current | Validate | Cleanup | Privacy | `acceptance-runs.md` |",
        "| P0 | rcv-duplicate | Chat panel | `ringcentral.video.toolbar.chat` | Current | Validate | Cleanup | Privacy | `acceptance-runs.md` |",
    )

    with pytest.raises(ValueError, match="duplicate validation target id: rcv-duplicate"):
        discover_catalog(checklist_text=checklist_text)


def test_discover_validation_targets_rejects_blank_explicit_target_id() -> None:
    checklist_text = priority_checklist_with_target_id_rows(
        "| P0 |   | Add coworkers modal | `ringcentral.video.main.add-coworkers` | Current | Validate | Cleanup | Privacy | `acceptance-runs.md` |"
    )

    with pytest.raises(ValueError, match="blank validation target id for Add coworkers modal"):
        discover_catalog(checklist_text=checklist_text)


def test_discover_validation_targets_falls_back_to_generated_ids_without_target_id_header() -> None:
    checklist_text = priority_checklist_without_target_id_rows(
        "| P0 | Add coworkers modal | `ringcentral.video.main.add-coworkers` | Current | Validate | Cleanup | Privacy | `acceptance-runs.md` |"
    )

    catalog = discover_catalog(checklist_text=checklist_text)
    target = target_by_id(catalog, "p0-add-coworkers-modal")

    assert target.route_or_group == "Add coworkers modal"


def test_discover_validation_targets_reads_priority_checklist_rows() -> None:
    catalog = discover_catalog()

    target = target_by_id(catalog, "rcv-add-coworkers-modal")

    assert target.priority == "P0"
    assert target.route_or_group == "Add coworkers modal"
    assert target.entrypoint_ids == ("ringcentral.video.main.add-coworkers",)
    assert target.flow_ids == ()
    assert "no live click acceptance" in target.current_state
    assert "Modal close" in target.cleanup
    assert "invite links" in target.privacy_boundary
    assert target.evidence_levels["ringcentral.video.main.add-coworkers"] == "Observed"


def test_evidence_index_integrity_covers_every_ringcentral_entrypoint_once() -> None:
    package = load_ringcentral_package()

    report = validate_entrypoint_evidence_index(package, load_evidence_text())

    assert report.entrypoint_count == 27
    assert report.evidence_entrypoint_count == 27
    assert set(report.evidence_levels) == set(package.entrypoints_by_id)


def test_discover_validation_targets_has_no_unknown_evidence_for_real_catalog() -> None:
    catalog = discover_catalog(include_blocked=True)

    unknown_refs = [
        entrypoint_id
        for target in catalog.targets
        for entrypoint_id, level in target.evidence_levels.items()
        if level == "unknown"
    ]

    assert unknown_refs == []


def test_evidence_index_integrity_rejects_missing_package_entrypoint() -> None:
    evidence_text = evidence_without_entrypoint("ringcentral.video.toolbar.chat")

    with pytest.raises(
        ValueError,
        match="evidence index missing package entrypoint: ringcentral.video.toolbar.chat",
    ):
        validate_entrypoint_evidence_index(load_ringcentral_package(), evidence_text)


def test_evidence_index_integrity_rejects_unknown_entrypoint() -> None:
    evidence_text = evidence_with_extra_row(
        "| `ringcentral.video.toolbar.missing` | Executable UIA route | `Observed` | Test | Gap |"
    )

    with pytest.raises(
        ValueError,
        match="evidence index references unknown entrypoint: ringcentral.video.toolbar.missing",
    ):
        validate_entrypoint_evidence_index(load_ringcentral_package(), evidence_text)


def test_evidence_index_integrity_rejects_unbackticked_entrypoint_cell() -> None:
    evidence_text = evidence_with_extra_row(
        "| ringcentral.video.toolbar.missing | Executable UIA route | `Observed` | Test | Gap |"
    )

    with pytest.raises(
        ValueError,
        match="evidence row missing backticked entrypoint id: ringcentral.video.toolbar.missing",
    ):
        validate_entrypoint_evidence_index(load_ringcentral_package(), evidence_text)


def test_evidence_index_integrity_rejects_duplicate_entrypoint() -> None:
    evidence_text = evidence_with_extra_row(
        "| `ringcentral.video.toolbar.chat` | Executable UIA route | `Observed` | Test | Gap |"
    )

    with pytest.raises(
        ValueError,
        match="duplicate evidence entrypoint id: ringcentral.video.toolbar.chat",
    ):
        validate_entrypoint_evidence_index(load_ringcentral_package(), evidence_text)


def test_evidence_index_integrity_rejects_invalid_evidence_level() -> None:
    evidence_text = evidence_with_level("ringcentral.video.toolbar.chat", "Rumored")

    with pytest.raises(
        ValueError,
        match="invalid evidence level for ringcentral.video.toolbar.chat: Rumored",
    ):
        validate_entrypoint_evidence_index(load_ringcentral_package(), evidence_text)


def test_discover_validation_targets_separates_flow_ids_from_entrypoints() -> None:
    catalog = discover_catalog()

    target = target_by_id(catalog, "rcv-controller-chat-question")

    assert target.entrypoint_ids == ("ringcentral.video.toolbar.chat",)
    assert target.flow_ids == ("meeting-control-map-demo",)


def test_discover_validation_targets_filters_by_priority_in_renderer() -> None:
    catalog = discover_catalog()

    text = "\n".join(render_validation_target_lines(catalog, priority="P0"))

    assert "rcv-add-coworkers-modal" in text
    assert "rcv-controller-chat-question" in text
    assert "rcv-top-bar-routes" not in text


def test_target_by_id_reports_available_ids_for_missing_target() -> None:
    catalog = discover_catalog()

    with pytest.raises(ValueError, match="Unknown validation target: missing-target") as exc_info:
        target_by_id(catalog, "missing-target")

    assert "rcv-add-coworkers-modal" in str(exc_info.value)


def test_discover_validation_targets_rejects_unknown_checklist_entrypoint() -> None:
    checklist_text = load_checklist_text().replace(
        "ringcentral.video.toolbar.chat",
        "ringcentral.video.toolbar.missing",
        1,
    )

    with pytest.raises(ValueError, match="ringcentral.video.toolbar.missing") as exc_info:
        discover_catalog(checklist_text=checklist_text)

    assert "Controller queued Chat question" in str(exc_info.value)


def test_discover_validation_targets_rejects_duplicate_ids_from_real_checklist_edits() -> None:
    duplicate_row = (
        "\n| P0 | rcv-add-coworkers-modal | Add coworkers modal duplicate | `ringcentral.video.main.add-coworkers` | "
        "Duplicate | Validate | Cleanup | Privacy | `acceptance-runs.md` |"
    )
    checklist_text = load_checklist_text().replace(
        "\n## Do Not Execute Yet",
        f"{duplicate_row}\n\n## Do Not Execute Yet",
    )

    with pytest.raises(ValueError, match="duplicate validation target id: rcv-add-coworkers-modal"):
        discover_catalog(checklist_text=checklist_text)


def test_discover_validation_targets_can_include_blocked_rows() -> None:
    catalog = discover_catalog(include_blocked=True)

    recording = target_by_id(catalog, "rcv-recording")
    leave = target_by_id(catalog, "rcv-leave-end-meeting")

    assert recording.entrypoint_ids == ("ringcentral.video.more.recording",)
    assert recording.blocked_reason is not None
    assert "consent" in recording.blocked_reason
    assert leave.entrypoint_ids == ("ringcentral.video.toolbar.leave",)
    assert leave.blocked_reason is not None
    assert "destructive" in leave.blocked_reason


def test_render_validation_target_lines_suppresses_blocked_draft_command() -> None:
    catalog = discover_catalog(include_blocked=True)

    text = "\n".join(render_validation_target_lines(catalog, target_id="rcv-recording"))

    assert "blocked:" in text
    assert "Do not execute" in text
    assert "draft:" not in text
    assert "acceptance-draft" not in text


def test_render_validation_target_lines_keeps_normal_draft_command() -> None:
    catalog = discover_catalog()

    text = "\n".join(render_validation_target_lines(catalog, target_id="rcv-add-coworkers-modal"))

    assert "draft:" in text
    assert (
        "ai-presenter acceptance-draft --package ringcentral-video "
        "--entrypoint ringcentral.video.main.add-coworkers"
    ) in text


def test_acceptance_draft_command_uses_entrypoint_only_for_single_entrypoint_target() -> None:
    catalog = discover_catalog()
    target = target_by_id(catalog, "rcv-add-coworkers-modal")

    command = acceptance_draft_command(catalog.package_id, target)

    assert "--entrypoint ringcentral.video.main.add-coworkers" in command
    assert '--checklist-target "P0 Add coworkers modal"' in command


def test_acceptance_draft_command_includes_flow_and_entrypoint_for_single_mixed_target() -> None:
    catalog = discover_catalog()
    target = target_by_id(catalog, "rcv-controller-chat-question")

    command = acceptance_draft_command(catalog.package_id, target)

    assert "--flow meeting-control-map-demo" in command
    assert "--entrypoint ringcentral.video.toolbar.chat" in command
    assert '--checklist-target "P0 Controller queued Chat question"' in command


def test_acceptance_draft_command_omits_entrypoint_for_group_target() -> None:
    catalog = discover_catalog()
    target = target_by_id(catalog, "rcv-top-bar-routes")

    command = acceptance_draft_command(catalog.package_id, target)

    assert "--entrypoint" not in command
    assert "--flow" not in command
    assert '--checklist-target "P1 Top-bar coordinate routes"' in command
