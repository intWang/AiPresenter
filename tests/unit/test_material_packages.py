from pathlib import Path

import pytest
from pydantic import ValidationError

from ai_presenter.packages.loader import load_material_package


def test_loads_ringcentral_video_app_material_package() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    assert package.app_id == "ringcentral-video"
    assert package.app_name == "RingCentral Video"
    assert "ringcentral-video-codex-cli-speaker" in package.profile_ids
    assert package.operation_entrypoints[0].id == "ringcentral.develop.video.tab"
    assert package.entrypoint_by_id("ringcentral.video.settings.background").area == "Settings"
    assert package.entrypoint_by_id("ringcentral.video.toolbar.share").area == "Meeting toolbar"
    assert package.entrypoint_by_id("ringcentral.video.toolbar.chat").purpose == (
        "Open in-meeting chat."
    )
    assert package.demo_flows[0].id == "vbg-blur-demo"
    assert package.demo_flows[0].steps[1].action.entrypoint_id == (
        "ringcentral.video.settings.background"
    )
    controls_tour = next(flow for flow in package.demo_flows if flow.id == "meeting-controls-tour")
    assert controls_tour.steps[-1].action.entrypoint_id == "ringcentral.video.toolbar.leave"
    assert controls_tour.steps[-1].action.operation == "explain"
    assert controls_tour.steps[0].id == "meeting-overview"
    assert all(not step.id.endswith("-section") for step in controls_tour.steps)
    for step in controls_tour.steps:
        entrypoint = package.entrypoint_by_id(step.action.entrypoint_id)
        if step.action.operation in {"open", "toggle"}:
            assert entrypoint.open_steps[0].action == "clickWindowRelative"
            assert step.narration.placement == "during"
            assert step.narration.action_offset_ms <= 500
        step.narration.text.encode("ascii")
    assert package.entrypoint_by_id("ringcentral.video.top.report-issue").presenter_notes[0].startswith(
        "This opens a foreground dialog"
    )
    assert package.entrypoint_by_id("ringcentral.video.more.notes").open_steps[-1].match["cleanup"] == (
        "sidePanel"
    )
    assert package.entrypoint_by_id("ringcentral.video.toolbar.audio-menu").purpose.startswith(
        "Open microphone and speaker"
    )
    assert package.explainers["participants"].short_script.startswith("Participants")
    assert package.explainers["audio"].short_script.startswith("The audio controls")
    assert package.qa[0].question == "How do I protect my real background?"


def test_rejects_duplicate_operation_entrypoint_ids(tmp_path: Path) -> None:
    package_path = tmp_path / "duplicate-entrypoints.yaml"
    package_path.write_text(
        """
appId: demo
appName: Demo
version: 1
profileIds: [demo-profile]
operationEntrypoints:
  - id: same
    title: First
    area: Main
    purpose: Open first
    openSteps: []
  - id: same
    title: Second
    area: Main
    purpose: Open second
    openSteps: []
demoFlows: []
manualControls: []
""",
        encoding="utf-8",
    )

    with pytest.raises(ValidationError, match="duplicate operation entrypoint id"):
        load_material_package(package_path)


def test_rejects_demo_flow_references_to_unknown_entrypoint(tmp_path: Path) -> None:
    package_path = tmp_path / "unknown-entrypoint.yaml"
    package_path.write_text(
        """
appId: demo
appName: Demo
version: 1
profileIds: [demo-profile]
operationEntrypoints:
  - id: known
    title: Known
    area: Main
    purpose: Open known
    openSteps: []
demoFlows:
  - id: demo-flow
    title: Demo Flow
    goal: Show the demo
    steps:
      - id: missing-step
        title: Missing
        action:
          entrypointId: missing
          operation: click
        narration:
          text: Open the missing entry point.
manualControls: []
""",
        encoding="utf-8",
    )

    with pytest.raises(ValidationError, match="unknown entrypoint"):
        load_material_package(package_path)
