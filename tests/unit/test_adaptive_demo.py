from ai_presenter.domain.state import MeetingState
from ai_presenter.packages.models import DemoStep, DemoStepAction, DemoStepNarration
from ai_presenter.runtime.adaptive_demo import adjust_ringcentral_demo_step


def make_step(step_id: str, entrypoint_id: str, text: str = "Original narration.") -> DemoStep:
    return DemoStep(
        id=step_id,
        title="Step",
        action=DemoStepAction(entrypointId=entrypoint_id, operation="open"),
        narration=DemoStepNarration(text=text, placement="during", actionOffsetMs=350),
    )


def test_rewrites_empty_room_add_coworkers_to_toolbar_invite_when_multiple_participants_are_present() -> None:
    step = make_step(
        "control-map-add-coworkers",
        "ringcentral.video.main.add-coworkers",
        "Add coworkers opens the invite dialog from the empty room.",
    )

    adjusted = adjust_ringcentral_demo_step(step, MeetingState(participant_count=2))

    assert adjusted is not None
    assert adjusted.action.entrypoint_id == "ringcentral.video.toolbar.invite"
    assert adjusted.narration.text == (
        "Because people are already in the meeting, Invite is for adding more participants or "
        "copying meeting details without changing the current conversation."
    )


def test_rewrites_toolbar_invite_narration_for_active_multi_person_meeting() -> None:
    step = make_step(
        "explain-invite",
        "ringcentral.video.toolbar.invite",
        "The Invite button brings someone into the empty meeting.",
    )

    adjusted = adjust_ringcentral_demo_step(step, MeetingState(participant_count=3))

    assert adjusted is not None
    assert adjusted.narration.text == (
        "Because people are already in the meeting, Invite is for adding more participants or "
        "copying meeting details without changing the current conversation."
    )
    assert adjusted.narration.placement == "during"
    assert adjusted.narration.action_offset_ms == 350


def test_keeps_unrelated_steps_unchanged() -> None:
    step = make_step(
        "control-map-participants",
        "ringcentral.video.toolbar.participants",
        "Participants opens the roster.",
    )

    adjusted = adjust_ringcentral_demo_step(step, MeetingState(participant_count=2))

    assert adjusted is step
