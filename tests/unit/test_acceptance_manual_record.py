from pathlib import Path

import pytest

from ai_presenter.acceptance.manual_record import AcceptanceDraftRequest
from ai_presenter.acceptance.manual_record import render_manual_acceptance_draft
from ai_presenter.acceptance.manual_record import required_manual_acceptance_fields
from ai_presenter.packages.loader import load_material_package
from ai_presenter.packages.models import MaterialPackage


def load_ringcentral_package() -> MaterialPackage:
    return load_material_package(Path("packages/ringcentral-video.yaml"))


def assert_manual_draft_boundary(draft: str) -> None:
    assert "Draft only" in draft
    assert "not acceptance evidence" in draft
    assert "No live RingCentral action has been performed by this helper." in draft
    assert "Accepted" not in draft
    assert "live validated" not in draft.casefold()


def test_manual_acceptance_draft_includes_all_required_template_fields() -> None:
    draft = render_manual_acceptance_draft(
        load_ringcentral_package(),
        AcceptanceDraftRequest(entrypoint_id="ringcentral.video.main.add-coworkers"),
    )

    for field in required_manual_acceptance_fields():
        assert f"- {field}:" in draft


def test_manual_acceptance_draft_prefills_entrypoint_context_without_claiming_acceptance() -> None:
    draft = render_manual_acceptance_draft(
        load_ringcentral_package(),
        AcceptanceDraftRequest(entrypoint_id="ringcentral.video.main.add-coworkers"),
    )

    assert_manual_draft_boundary(draft)
    assert "ringcentral.video.main.add-coworkers" in draft
    assert "Add coworkers" in draft
    assert "Meeting canvas" in draft
    assert "clickWindowControl target=Add coworkers cleanup=modal" in draft
    assert "- Pass/fail:" in draft


def test_manual_acceptance_draft_prefills_flow_steps() -> None:
    draft = render_manual_acceptance_draft(
        load_ringcentral_package(),
        AcceptanceDraftRequest(flow_id="meeting-control-map-demo"),
    )

    assert_manual_draft_boundary(draft)
    assert "meeting-control-map-demo" in draft
    assert "Meeting Control Map" in draft
    assert "ringcentral.video.toolbar.chat" in draft
    assert "ringcentral.video.main.add-coworkers" in draft


def test_manual_acceptance_draft_prefills_mixed_flow_and_entrypoint_steps() -> None:
    draft = render_manual_acceptance_draft(
        load_ringcentral_package(),
        AcceptanceDraftRequest(
            flow_id="meeting-control-map-demo",
            entrypoint_id="ringcentral.video.toolbar.chat",
            checklist_target="P0 Controller queued Chat question",
        ),
    )

    assert_manual_draft_boundary(draft)
    assert "### Flow Context" in draft
    assert "### Entrypoint Context" in draft
    assert "### Checklist Context" in draft
    assert "- Package flow: meeting-control-map-demo" in draft
    assert (
        "- Steps executed: Intended flow: meeting-control-map-demo; "
        "intended target during flow: ringcentral.video.toolbar.chat; "
        "fill with actual steps after the run."
    ) in draft


def test_manual_acceptance_draft_rejects_unknown_entrypoint() -> None:
    with pytest.raises(ValueError, match="Unknown operation entrypoint: missing"):
        render_manual_acceptance_draft(
            load_ringcentral_package(),
            AcceptanceDraftRequest(entrypoint_id="missing"),
        )


def test_manual_acceptance_draft_rejects_unknown_flow() -> None:
    with pytest.raises(ValueError, match="Unknown demo flow: missing-flow"):
        render_manual_acceptance_draft(
            load_ringcentral_package(),
            AcceptanceDraftRequest(flow_id="missing-flow"),
        )


def test_manual_acceptance_draft_rejects_entrypoint_outside_selected_flow() -> None:
    with pytest.raises(
        ValueError,
        match="is not used by selected flow vbg-blur-demo",
    ):
        render_manual_acceptance_draft(
            load_ringcentral_package(),
            AcceptanceDraftRequest(
                flow_id="vbg-blur-demo",
                entrypoint_id="ringcentral.video.toolbar.chat",
            ),
        )


def test_manual_acceptance_draft_rejects_no_open_step_entrypoint() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Entrypoint ringcentral.video.toolbar.leave has no executable open steps; "
            "direct acceptance drafts require a separate confirmation workflow"
        ),
    ):
        render_manual_acceptance_draft(
            load_ringcentral_package(),
            AcceptanceDraftRequest(entrypoint_id="ringcentral.video.toolbar.leave"),
        )
