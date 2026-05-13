import time
from collections.abc import Callable, Hashable, Mapping
from typing import TypeAlias

from ai_presenter.config.models import NarrationConfig
from ai_presenter.domain.state import MeetingState, PresenterEvent
from ai_presenter.providers.base import NarrationProvider

PayloadFingerprint: TypeAlias = tuple[tuple[str, Hashable], ...]
EventFingerprint: TypeAlias = tuple[str, PayloadFingerprint]


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
        self._last_spoken_at = now
        for event in eligible:
            self._event_spoken_at[self._event_fingerprint(event)] = now
        return text

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
