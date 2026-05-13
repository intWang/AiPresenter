from dataclasses import dataclass
from typing import Protocol

from ai_presenter.domain.state import MeetingState, PresenterEvent, RawObservation


@dataclass(frozen=True)
class SpeechAudio:
    data: bytes
    mime_type: str
    sample_rate: int
    channels: int


class VisionProvider(Protocol):
    def recognize(self, observation: RawObservation) -> MeetingState:
        ...


class NarrationProvider(Protocol):
    def narrate(self, state: MeetingState, events: list[PresenterEvent]) -> str:
        ...


class SpeechProvider(Protocol):
    def synthesize(self, text: str) -> SpeechAudio:
        ...


class ProviderRegistry:
    def __init__(self) -> None:
        self._vision: dict[str, VisionProvider] = {}
        self._narration: dict[str, NarrationProvider] = {}
        self._speech: dict[str, SpeechProvider] = {}

    def register_vision(self, name: str, provider: VisionProvider) -> None:
        self._vision[name] = provider

    def register_narration(self, name: str, provider: NarrationProvider) -> None:
        self._narration[name] = provider

    def register_speech(self, name: str, provider: SpeechProvider) -> None:
        self._speech[name] = provider

    def vision(self, name: str) -> VisionProvider:
        return self._vision[name]

    def narration(self, name: str) -> NarrationProvider:
        return self._narration[name]

    def speech(self, name: str) -> SpeechProvider:
        return self._speech[name]
