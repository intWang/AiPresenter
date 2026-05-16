from ai_presenter.domain.state import MeetingState
from ai_presenter.packages.models import DemoStep, DemoStepNarration

_ACTIVE_MEETING_INVITE_NARRATION = (
    "Because people are already in the meeting, Invite is for adding more participants or "
    "copying meeting details without changing the current conversation."
)
_ACTIVE_MEETING_INVITE_LOCALIZED_NARRATION = {
    "zh": "因为已经有人在会议中，Invite 用来继续添加参会人，或复制会议详情，而不会改变当前对话。"
}


def adjust_ringcentral_demo_step(step: DemoStep, state: MeetingState | None) -> DemoStep | None:
    if state is None or state.participant_count is None or state.participant_count < 2:
        return step

    if step.action.entrypoint_id == "ringcentral.video.main.add-coworkers":
        return step.model_copy(
            update={
                "action": step.action.model_copy(
                    update={"entrypoint_id": "ringcentral.video.toolbar.invite"}
                ),
                "narration": _active_meeting_invite_narration(step.narration),
            }
        )

    if step.action.entrypoint_id == "ringcentral.video.toolbar.invite":
        return step.model_copy(
            update={
                "narration": _active_meeting_invite_narration(step.narration)
            }
        )

    return step


def _active_meeting_invite_narration(narration: DemoStepNarration) -> DemoStepNarration:
    return narration.model_copy(
        update={
            "text": _ACTIVE_MEETING_INVITE_NARRATION,
            "localized_text": dict(_ACTIVE_MEETING_INVITE_LOCALIZED_NARRATION),
        }
    )
