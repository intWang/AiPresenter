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
    def __init__(self, kind: str, name: str, message: str) -> None:
        self.kind = kind
        self.name = name
        super().__init__(message)


class ProviderLookupError(LookupError):
    def __init__(
        self,
        kind: str,
        name: str,
        available_names: tuple[str, ...],
        message: str,
    ) -> None:
        self.kind = kind
        self.name = name
        self.available_names = available_names
        super().__init__(message)


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
        normalized_name = self._normalize_name(kind, name, for_lookup=False)
        if normalized_name in providers:
            raise ProviderRegistrationError(
                kind,
                normalized_name,
                f"{kind} provider '{normalized_name}' is already registered.",
            )
        providers[normalized_name] = provider

    def _lookup(
        self,
        kind: str,
        name: str,
        providers: dict[str, ProviderT],
    ) -> ProviderT:
        normalized_name = self._normalize_name(kind, name, for_lookup=True)
        try:
            return providers[normalized_name]
        except KeyError as error:
            available_names = tuple(sorted(providers))
            available = ", ".join(available_names) or "none"
            raise ProviderLookupError(
                kind,
                normalized_name,
                available_names,
                f"Unknown {kind} provider '{normalized_name}'. "
                f"Available {kind} providers: {available}.",
            ) from error

    def _normalize_name(self, kind: str, name: str, *, for_lookup: bool) -> str:
        normalized_name = name.strip()
        if normalized_name:
            return normalized_name
        message = f"{kind} provider name cannot be blank."
        if for_lookup:
            raise ProviderLookupError(kind, normalized_name, (), message)
        raise ProviderRegistrationError(kind, normalized_name, message)
