from dataclasses import dataclass
from typing import Protocol
from typing import TypeVar

from ai_presenter.domain.state import MeetingState, PresenterEvent, RawObservation

ProviderT = TypeVar("ProviderT")


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


class ProviderRegistrationError(ValueError):
    pass


class ProviderLookupError(LookupError):
    pass


class ProviderRegistry:
    def __init__(self) -> None:
        self._vision: dict[str, VisionProvider] = {}
        self._narration: dict[str, NarrationProvider] = {}
        self._speech: dict[str, SpeechProvider] = {}

    def register_vision(self, name: str, provider: VisionProvider) -> None:
        self._register("vision", name, provider, self._vision)

    def register_narration(self, name: str, provider: NarrationProvider) -> None:
        self._register("narration", name, provider, self._narration)

    def register_speech(self, name: str, provider: SpeechProvider) -> None:
        self._register("speech", name, provider, self._speech)

    def vision(self, name: str) -> VisionProvider:
        return self._lookup("vision", name, self._vision)

    def narration(self, name: str) -> NarrationProvider:
        return self._lookup("narration", name, self._narration)

    def speech(self, name: str) -> SpeechProvider:
        return self._lookup("speech", name, self._speech)

    def _register(
        self,
        kind: str,
        name: str,
        provider: ProviderT,
        providers: dict[str, ProviderT],
    ) -> None:
        if name in providers:
            raise ProviderRegistrationError(f"{kind} provider '{name}' is already registered.")
        providers[name] = provider

    def _lookup(
        self,
        kind: str,
        name: str,
        providers: dict[str, ProviderT],
    ) -> ProviderT:
        try:
            return providers[name]
        except KeyError as error:
            available = ", ".join(sorted(providers)) or "none"
            raise ProviderLookupError(
                f"Unknown {kind} provider '{name}'. Available {kind} providers: {available}."
            ) from error
