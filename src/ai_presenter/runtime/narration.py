import time
from collections.abc import Callable, Hashable, Mapping
from dataclasses import dataclass
from typing import TypeAlias

from ai_presenter.config.models import NarrationConfig
from ai_presenter.domain.state import MeetingState, PresenterEvent
from ai_presenter.providers.base import NarrationProvider

PayloadFingerprint: TypeAlias = tuple[tuple[str, Hashable], ...]
EventFingerprint: TypeAlias = tuple[str, PayloadFingerprint]


@dataclass(frozen=True)
class PreparedNarration:
    text: str
    events: tuple[PresenterEvent, ...]
    prepared_at: float


class NarrationEngine:
    def __init__(
        self,
        config: NarrationConfig,
        provider: NarrationProvider,
        now: Callable[[], float] | None = None,
    ) -> None:
        self._config = config
        self._provider = provider
        self._now = now or time.monotonic
        self._last_spoken_at = float("-inf")
        self._event_spoken_at: dict[EventFingerprint, float] = {}

    def maybe_narrate(
        self,
        state: MeetingState,
        events: list[PresenterEvent],
    ) -> str | None:
        prepared = self.prepare_narration(state, events)
        if prepared is None:
            return None
        self.commit(prepared, spoken_at=prepared.prepared_at)
        return prepared.text

    def prepare_narration(
        self,
        state: MeetingState,
        events: list[PresenterEvent],
    ) -> PreparedNarration | None:
        if state.confidence < self._config.confidence_threshold:
            return None
        now = self._now()
        eligible = self._eligible_events(events, now)
        if not eligible:
            return None
        if now - self._last_spoken_at < self._config.min_seconds_between_utterances:
            return None

        text = self._provider.narrate(state, eligible).strip()
        if not text:
            return None
        return PreparedNarration(text=text, events=tuple(eligible), prepared_at=now)

    def commit(self, narration: PreparedNarration, spoken_at: float | None = None) -> None:
        committed_at = self._now() if spoken_at is None else spoken_at
        self._last_spoken_at = committed_at
        for event in narration.events:
            self._event_spoken_at[self._event_fingerprint(event)] = committed_at

    def _eligible_events(self, events: list[PresenterEvent], now: float) -> list[PresenterEvent]:
        eligible: list[PresenterEvent] = []
        seen_fingerprints: set[EventFingerprint] = set()
        for event in events:
            fingerprint = self._event_fingerprint(event)
            if fingerprint in seen_fingerprints:
                continue
            seen_fingerprints.add(fingerprint)

            last = self._event_spoken_at.get(fingerprint)
            if last is None or now - last >= self._config.repeat_cooldown_seconds:
                eligible.append(event)
        return eligible

    def _event_fingerprint(self, event: PresenterEvent) -> EventFingerprint:
        return (
            event.type,
            tuple(
                (key, self._normalize_payload_value(event.payload[key]))
                for key in sorted(event.payload)
            ),
        )

    def _normalize_payload_value(self, value: object) -> Hashable:
        if value is None or isinstance(value, str | int | float | bool):
            return value
        if isinstance(value, Mapping):
            return tuple(
                (str(key), self._normalize_payload_value(nested_value))
                for key, nested_value in sorted(value.items(), key=lambda item: str(item[0]))
            )
        if isinstance(value, list | tuple):
            return tuple(self._normalize_payload_value(item) for item in value)
        raise TypeError("PresenterEvent payload values must be JSON-like primitives, mappings, or lists.")
