from ai_presenter.domain.state import MeetingState, PresenterEvent


class EventDetector:
    def __init__(self, confidence_threshold: float = 0.75) -> None:
        self._confidence_threshold = confidence_threshold

    def detect(
        self,
        previous: MeetingState | None,
        current: MeetingState,
    ) -> list[PresenterEvent]:
        if current.confidence < self._confidence_threshold:
            return []

        events: list[PresenterEvent] = []

        if previous is None:
            if current.meeting_joined is True:
                events.append(PresenterEvent("meeting_joined", {}, current.confidence))
            if current.active_dialog:
                events.append(
                    PresenterEvent(
                        "dialog_appeared",
                        {"activeDialog": current.active_dialog},
                        current.confidence,
                    )
                )
            return events

        if previous.mic_muted != current.mic_muted and current.mic_muted is not None:
            events.append(
                PresenterEvent(
                    "mic_state_changed",
                    {"micMuted": current.mic_muted},
                    current.confidence,
                )
            )

        if previous.camera_off != current.camera_off and current.camera_off is not None:
            events.append(
                PresenterEvent(
                    "camera_state_changed",
                    {"cameraOff": current.camera_off},
                    current.confidence,
                )
            )

        if (
            previous.participant_count != current.participant_count
            and current.participant_count is not None
        ):
            events.append(
                PresenterEvent(
                    "participant_count_changed",
                    {"participantCount": current.participant_count},
                    current.confidence,
                )
            )

        if previous.active_dialog != current.active_dialog and current.active_dialog:
            events.append(
                PresenterEvent(
                    "dialog_appeared",
                    {"activeDialog": current.active_dialog},
                    current.confidence,
                )
            )

        if previous.connection_warning != current.connection_warning and current.connection_warning:
            events.append(
                PresenterEvent(
                    "connection_warning",
                    {"connectionWarning": current.connection_warning},
                    current.confidence,
                )
            )

        return events
