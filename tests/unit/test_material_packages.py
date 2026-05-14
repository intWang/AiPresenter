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
            assert_supported_open_step(entrypoint.open_steps[0])
            assert step.narration.placement == "during"
            assert step.narration.action_offset_ms <= 500
        step.narration.text.encode("ascii")
    assert package.entrypoint_by_id("ringcentral.video.top.report-issue").presenter_notes[0].startswith(
        "This opens a foreground dialog"
    )
    notes_entrypoint = package.entrypoint_by_id("ringcentral.video.more.notes")
    assert notes_entrypoint.open_steps[-1].action == "clickWindowControl"
    assert notes_entrypoint.open_steps[-1].match["cleanup"] == "toggle"
    assert package.entrypoint_by_id("ringcentral.video.toolbar.audio-menu").purpose.startswith(
        "Open microphone and speaker"
    )
    assert package.explainers["participants"].short_script.startswith("Participants")
    assert package.explainers["audio"].short_script.startswith("The audio controls")
    assert package.qa[0].question == "How do I protect my real background?"


def test_meeting_control_map_demo_is_directed_and_complete() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = next(flow for flow in package.demo_flows if flow.id == "meeting-control-map-demo")

    assert flow.title == "Meeting Control Map"
    assert flow.steps[0].id == "control-map-overview"
    assert flow.steps[-1].id == "control-map-summary"
    assert flow.steps[-1].action.operation == "explain"

    entrypoint_ids = [step.action.entrypoint_id for step in flow.steps]
    assert entrypoint_ids == [
        "ringcentral.video.overview",
        "ringcentral.video.top.meeting-info",
        "ringcentral.video.top.network-quality",
        "ringcentral.video.top.views",
        "ringcentral.video.top.report-issue",
        "ringcentral.video.main.add-coworkers",
        "ringcentral.video.toolbar.participants",
        "ringcentral.video.toolbar.chat",
        "ringcentral.video.toolbar.audio",
        "ringcentral.video.toolbar.audio-menu",
        "ringcentral.video.toolbar.video",
        "ringcentral.video.toolbar.video-menu",
        "ringcentral.video.toolbar.share",
        "ringcentral.video.toolbar.react",
        "ringcentral.video.toolbar.raise-hand",
        "ringcentral.video.toolbar.more",
        "ringcentral.video.more.recording",
        "ringcentral.video.more.notes",
        "ringcentral.video.more.background",
        "ringcentral.video.more.settings",
        "ringcentral.video.toolbar.leave",
        "ringcentral.video.overview",
    ]

    for step in flow.steps:
        step.narration.text.encode("ascii")
        entrypoint = package.entrypoint_by_id(step.action.entrypoint_id)
        if step.action.operation in {"open", "toggle"}:
            assert_supported_open_step(entrypoint.open_steps[0])
            assert step.narration.placement == "during"
            assert step.narration.action_offset_ms <= 500

    recording_step = next(step for step in flow.steps if step.id == "control-map-recording")
    leave_step = next(step for step in flow.steps if step.id == "control-map-leave")
    assert recording_step.action.operation == "explain"
    assert leave_step.action.operation == "explain"


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


def assert_supported_open_step(step: object) -> None:
    action = getattr(step, "action")
    match = getattr(step, "match")
    if action == "clickWindowRelative":
        assert "x" in match or "xFromRight" in match
        assert "y" in match or "yFromBottom" in match
        return
    if action == "clickWindowControl":
        assert getattr(step, "target")
        return
    raise AssertionError(f"Unexpected package open step action: {action}")


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
