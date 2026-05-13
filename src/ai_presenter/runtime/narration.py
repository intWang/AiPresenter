import time
from collections.abc import Callable

from ai_presenter.config.models import NarrationConfig
from ai_presenter.domain.state import MeetingState, PresenterEvent
from ai_presenter.providers.base import NarrationProvider


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
        self._last_spoken_at = -1_000_000.0
        self._event_spoken_at: dict[str, float] = {}

    def maybe_narrate(
        self,
        state: MeetingState,
        events: list[PresenterEvent],
    ) -> str | None:
        if state.confidence < self._config.confidence_threshold:
            return None
        eligible = self._eligible_events(events)
        if not eligible:
            return None
        now = self._now()
        if now - self._last_spoken_at < self._config.min_seconds_between_utterances:
            return None

        text = self._provider.narrate(state, eligible).strip()
        if not text:
            return None
        self._last_spoken_at = now
        for event in eligible:
            self._event_spoken_at[event.type] = now
        return text

    def _eligible_events(self, events: list[PresenterEvent]) -> list[PresenterEvent]:
        now = self._now()
        eligible: list[PresenterEvent] = []
        for event in events:
            last = self._event_spoken_at.get(event.type)
            if last is None or now - last >= self._config.repeat_cooldown_seconds:
                eligible.append(event)
        return eligible
