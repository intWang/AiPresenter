from typing import Protocol

from ai_presenter.domain.state import MeetingState, RawObservation


class AppAdapter(Protocol):
    def extract_state(self, observation: RawObservation) -> MeetingState:
        ...
