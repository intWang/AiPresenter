from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ai_presenter.adapters.base import AppAdapter
    from ai_presenter.desktop.base import ObservationDriver, WindowHandle
    from ai_presenter.domain.state import MeetingState
    from ai_presenter.media.output import MediaOutput
    from ai_presenter.providers.base import SpeechProvider
    from ai_presenter.runtime.events import EventDetector
    from ai_presenter.runtime.narration import NarrationEngine


class PresenterLoop:
    def __init__(
        self,
        *,
        observation_driver: ObservationDriver,
        adapter: AppAdapter,
        event_detector: EventDetector,
        narration_engine: NarrationEngine,
        speech_provider: SpeechProvider,
        media_output: MediaOutput,
    ) -> None:
        self._observation_driver = observation_driver
        self._adapter = adapter
        self._event_detector = event_detector
        self._narration_engine = narration_engine
        self._speech_provider = speech_provider
        self._media_output = media_output
        self._previous_state: MeetingState | None = None

    def run_once(self, handle: WindowHandle) -> None:
        observation = self._observation_driver.capture(handle)
        current_state = self._adapter.extract_state(observation)
        events = self._event_detector.detect(
            previous=self._previous_state,
            current=current_state,
            occurred_at=observation.captured_at,
        )
        self._previous_state = current_state

        text = self._narration_engine.maybe_narrate(current_state, events)
        if text is None:
            return

        audio = self._speech_provider.synthesize(text)
        self._media_output.play(audio)
