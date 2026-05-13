from dataclasses import replace
from datetime import datetime
from typing import Callable
from typing import TypeVar

from ai_presenter.domain.state import MeetingState, PresenterEvent
from ai_presenter.domain.state import utc_now

T = TypeVar("T")


class EventDetector:
    def __init__(
        self,
        confidence_threshold: float = 0.75,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._confidence_threshold = confidence_threshold
        self._clock = clock

    def detect(
        self,
        previous: MeetingState | None,
        current: MeetingState,
        occurred_at: datetime | None = None,
    ) -> list[PresenterEvent]:
        if current.confidence < self._confidence_threshold:
            return []

        events: list[PresenterEvent] = []
        event_time = occurred_at if occurred_at is not None else self._clock()

        if previous is None:
            if current.meeting_joined is True:
                events.append(self._event("meeting_joined", {}, current.confidence, event_time))
            if current.active_dialog:
                events.append(
                    self._event(
                        "dialog_appeared",
                        {"activeDialog": current.active_dialog},
                        current.confidence,
                        event_time,
                    )
                )
            return events

        if previous.meeting_joined is not True and current.meeting_joined is True:
            events.append(self._event("meeting_joined", {}, current.confidence, event_time))

        if previous.mic_muted != current.mic_muted and current.mic_muted is not None:
            events.append(
                self._event(
                    "mic_state_changed",
                    {"micMuted": current.mic_muted},
                    current.confidence,
                    event_time,
                )
            )

        if previous.camera_off != current.camera_off and current.camera_off is not None:
            events.append(
                self._event(
                    "camera_state_changed",
                    {"cameraOff": current.camera_off},
                    current.confidence,
                    event_time,
                )
            )

        if (
            previous.participant_count != current.participant_count
            and current.participant_count is not None
        ):
            events.append(
                self._event(
                    "participant_count_changed",
                    {"participantCount": current.participant_count},
                    current.confidence,
                    event_time,
                )
            )

        if previous.active_dialog != current.active_dialog and current.active_dialog:
            events.append(
                self._event(
                    "dialog_appeared",
                    {"activeDialog": current.active_dialog},
                    current.confidence,
                    event_time,
                )
            )

        if previous.connection_warning != current.connection_warning and current.connection_warning:
            events.append(
                self._event(
                    "connection_warning",
                    {"connectionWarning": current.connection_warning},
                    current.confidence,
                    event_time,
                )
            )

        return events

    def _event(
        self,
        event_type: str,
        payload: dict[str, object],
        confidence: float,
        occurred_at: datetime,
    ) -> PresenterEvent:
        return PresenterEvent(event_type, payload, confidence, occurred_at)


class StateReducer:
    def reduce(
        self,
        current: MeetingState,
        candidates: list[MeetingState],
    ) -> MeetingState:
        state = current
        confidence = current.confidence

        for candidate in candidates:
            confidence = min(confidence, candidate.confidence)
            state = replace(
                state,
                meeting_joined=self._latest(state.meeting_joined, candidate.meeting_joined),
                mic_muted=self._latest(state.mic_muted, candidate.mic_muted),
                camera_off=self._latest(state.camera_off, candidate.camera_off),
                active_dialog=self._latest(state.active_dialog, candidate.active_dialog),
                participant_count=self._latest(
                    state.participant_count,
                    candidate.participant_count,
                ),
                connection_warning=self._latest(
                    state.connection_warning,
                    candidate.connection_warning,
                ),
                confidence=confidence,
            )

        return state

    def _latest(self, previous: T | None, candidate: T | None) -> T | None:
        if candidate is None:
            return previous
        return candidate
