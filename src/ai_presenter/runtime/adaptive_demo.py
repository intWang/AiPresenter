from ai_presenter.domain.state import MeetingState
from ai_presenter.packages.models import DemoStep

_ACTIVE_MEETING_INVITE_NARRATION = (
    "Because people are already in the meeting, Invite is for adding more participants or "
    "copying meeting details without changing the current conversation."
)


def adjust_ringcentral_demo_step(step: DemoStep, state: MeetingState | None) -> DemoStep | None:
    if state is None or state.participant_count is None or state.participant_count < 2:
        return step

    if step.action.entrypoint_id == "ringcentral.video.main.add-coworkers":
        return step.model_copy(
            update={
                "action": step.action.model_copy(
                    update={"entrypoint_id": "ringcentral.video.toolbar.invite"}
                ),
                "narration": step.narration.model_copy(
                    update={"text": _ACTIVE_MEETING_INVITE_NARRATION}
                ),
            }
        )

    if step.action.entrypoint_id == "ringcentral.video.toolbar.invite":
        return step.model_copy(
            update={
                "narration": step.narration.model_copy(
                    update={"text": _ACTIVE_MEETING_INVITE_NARRATION}
                )
            }
        )

    return step
