from __future__ import annotations

import logging
from collections.abc import Iterable
from typing import TYPE_CHECKING
from typing import TypeVar

from ai_presenter.config.models import ObservationSource
from ai_presenter.domain.state import MeetingState

if TYPE_CHECKING:
    from ai_presenter.adapters.base import AppAdapter
    from ai_presenter.desktop.base import ObservationDriver, WindowHandle
    from ai_presenter.media.output import MediaOutput
    from ai_presenter.providers.base import SpeechProvider, VisionProvider
    from ai_presenter.runtime.events import EventDetector
    from ai_presenter.runtime.narration import NarrationEngine

logger = logging.getLogger("ai_presenter.runtime.presenter")
T = TypeVar("T")


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
        observation_sources: Iterable[ObservationSource] | None = None,
        vision_provider: VisionProvider | None = None,
    ) -> None:
        self._observation_driver = observation_driver
        self._adapter = adapter
        self._event_detector = event_detector
        self._narration_engine = narration_engine
        self._speech_provider = speech_provider
        self._media_output = media_output
        self._observation_sources = (
            None if observation_sources is None else tuple(observation_sources)
        )
        self._vision_provider = vision_provider
        self._previous_state: MeetingState | None = None

    def run_once(self, handle: WindowHandle) -> None:
        observation = self._observation_driver.capture(handle, self._observation_sources)
        logger.info(
            "observation_captured process=%s pid=%s class=%s",
            handle.process,
            handle.pid,
            handle.window_class,
        )
        adapter_state = self._adapter.extract_state(observation)
        vision_states = []
        if self._vision_provider is not None:
            vision_states.append(self._vision_provider.recognize(observation))
        current_state = _merge_provider_states(adapter_state, vision_states)
        logger.info("state_extracted confidence=%s", current_state.confidence)
        events = self._event_detector.detect(
            previous=self._previous_state,
            current=current_state,
            occurred_at=observation.captured_at,
        )
        logger.info("events_detected count=%s types=%s", len(events), [event.type for event in events])

        if not events:
            if self._event_detector.is_confident(current_state):
                self._previous_state = current_state
            logger.info("narration_skipped reason=no_events")
            return
        narration = self._narration_engine.prepare_narration(current_state, events)
        if narration is None:
            logger.info("narration_skipped reason=policy")
            return

        logger.info("narration_generated events=%s", [event.type for event in events])
        audio = self._speech_provider.synthesize(narration.text)
        self._media_output.play(audio)
        self._narration_engine.commit(narration)
        self._previous_state = current_state
        logger.info("media_output_completed mime_type=%s bytes=%s", audio.mime_type, len(audio.data))


_MEETING_STATE_FIELDS = (
    "meeting_joined",
    "mic_muted",
    "camera_off",
    "active_dialog",
    "participant_count",
    "connection_warning",
)


def _merge_provider_states(
    adapter_state: MeetingState,
    vision_states: list[MeetingState],
) -> MeetingState:
    evidence_states = [
        state for state in [adapter_state, *vision_states] if _has_state_evidence(state)
    ]
    if not evidence_states:
        return adapter_state

    states_by_confidence = sorted(evidence_states, key=lambda state: state.confidence, reverse=True)
    primary = states_by_confidence[0]
    return MeetingState(
        meeting_joined=_first_non_none(state.meeting_joined for state in states_by_confidence),
        mic_muted=_first_non_none(state.mic_muted for state in states_by_confidence),
        camera_off=_first_non_none(state.camera_off for state in states_by_confidence),
        active_dialog=_first_non_none(state.active_dialog for state in states_by_confidence),
        participant_count=_first_non_none(
            state.participant_count for state in states_by_confidence
        ),
        connection_warning=_first_non_none(
            state.connection_warning for state in states_by_confidence
        ),
        confidence=primary.confidence,
    )


def _first_non_none(values: Iterable[T | None]) -> T | None:
    for value in values:
        if value is not None:
            return value
    return None


def _has_state_evidence(state: MeetingState) -> bool:
    return any(getattr(state, field_name) is not None for field_name in _MEETING_STATE_FIELDS)
