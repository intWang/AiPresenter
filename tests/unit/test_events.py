from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from typing import Any, cast

import pytest

from ai_presenter.domain.state import RawObservation, WindowMetadata
from ai_presenter.domain.state import MeetingState
from ai_presenter.domain.state import PresenterEvent
from ai_presenter.runtime.events import EventDetector, StateReducer


def test_detects_initial_meeting_joined_event() -> None:
    detector = EventDetector()
    current = MeetingState(meeting_joined=True, confidence=0.9)

    events = detector.detect(previous=None, current=current)

    assert [event.type for event in events] == ["meeting_joined"]


def test_detects_mic_state_change() -> None:
    detector = EventDetector()
    previous = MeetingState(meeting_joined=True, mic_muted=False, confidence=0.9)
    current = MeetingState(meeting_joined=True, mic_muted=True, confidence=0.9)

    events = detector.detect(previous=previous, current=current)

    assert len(events) == 1
    assert events[0].type == "mic_state_changed"
    assert events[0].payload == {"micMuted": True}


def test_detects_later_meeting_joined_transition() -> None:
    detector = EventDetector()
    previous = MeetingState(meeting_joined=False, confidence=0.9)
    current = MeetingState(meeting_joined=True, confidence=0.9)

    events = detector.detect(previous=previous, current=current)

    assert [event.type for event in events] == ["meeting_joined"]


def test_detects_camera_state_change() -> None:
    detector = EventDetector()
    previous = MeetingState(meeting_joined=True, camera_off=False, confidence=0.9)
    current = MeetingState(meeting_joined=True, camera_off=True, confidence=0.9)

    events = detector.detect(previous=previous, current=current)

    assert len(events) == 1
    assert events[0].type == "camera_state_changed"
    assert events[0].payload == {"cameraOff": True}


def test_detects_participant_count_change() -> None:
    detector = EventDetector()
    previous = MeetingState(meeting_joined=True, participant_count=2, confidence=0.9)
    current = MeetingState(meeting_joined=True, participant_count=3, confidence=0.9)

    events = detector.detect(previous=previous, current=current)

    assert len(events) == 1
    assert events[0].type == "participant_count_changed"
    assert events[0].payload == {"participantCount": 3}


def test_detects_dialog_appeared() -> None:
    detector = EventDetector()
    previous = MeetingState(meeting_joined=True, active_dialog=None, confidence=0.9)
    current = MeetingState(meeting_joined=True, active_dialog="share-screen", confidence=0.9)

    events = detector.detect(previous=previous, current=current)

    assert len(events) == 1
    assert events[0].type == "dialog_appeared"
    assert events[0].payload == {"activeDialog": "share-screen"}


def test_detects_connection_warning() -> None:
    detector = EventDetector()
    previous = MeetingState(meeting_joined=True, connection_warning=None, confidence=0.9)
    current = MeetingState(meeting_joined=True, connection_warning="unstable", confidence=0.9)

    events = detector.detect(previous=previous, current=current)

    assert len(events) == 1
    assert events[0].type == "connection_warning"
    assert events[0].payload == {"connectionWarning": "unstable"}


def test_filters_events_by_enabled_event_types() -> None:
    detector = EventDetector(enabled_event_types=("camera_state_changed",))
    previous = MeetingState(
        meeting_joined=True,
        mic_muted=False,
        camera_off=False,
        confidence=0.9,
    )
    current = MeetingState(
        meeting_joined=True,
        mic_muted=True,
        camera_off=True,
        confidence=0.9,
    )

    events = detector.detect(previous=previous, current=current)

    assert [event.type for event in events] == ["camera_state_changed"]


def test_empty_enabled_event_types_suppresses_all_events() -> None:
    detector = EventDetector(enabled_event_types=())
    current = MeetingState(meeting_joined=True, confidence=0.9)

    assert detector.detect(previous=None, current=current) == []


def test_uses_injected_clock_for_event_timestamps() -> None:
    occurred_at = datetime(2026, 5, 13, 12, 0, tzinfo=timezone.utc)
    detector = EventDetector(clock=lambda: occurred_at)
    current = MeetingState(meeting_joined=True, confidence=0.9)

    events = detector.detect(previous=None, current=current)

    assert events[0].occurred_at == occurred_at


def test_can_override_event_timestamp_per_detection() -> None:
    clock_time = datetime(2026, 5, 13, 12, 0, tzinfo=timezone.utc)
    explicit_time = datetime(2026, 5, 13, 12, 1, tzinfo=timezone.utc)
    detector = EventDetector(clock=lambda: clock_time)
    current = MeetingState(meeting_joined=True, confidence=0.9)

    events = detector.detect(previous=None, current=current, occurred_at=explicit_time)

    assert events[0].occurred_at == explicit_time


def test_ignores_low_confidence_state() -> None:
    detector = EventDetector(confidence_threshold=0.75)
    current = MeetingState(meeting_joined=True, confidence=0.4)

    events = detector.detect(previous=None, current=current)

    assert events == []


def test_reports_whether_state_meets_confidence_threshold() -> None:
    detector = EventDetector(confidence_threshold=0.75)

    assert detector.is_confident(MeetingState(confidence=0.75)) is True
    assert detector.is_confident(MeetingState(confidence=0.74)) is False


def test_reducer_merges_latest_non_none_fields_with_conservative_confidence() -> None:
    reducer = StateReducer()
    current = MeetingState(
        meeting_joined=True,
        mic_muted=False,
        participant_count=2,
        confidence=0.95,
    )
    candidate = MeetingState(mic_muted=True, active_dialog="permissions", confidence=0.8)
    later_candidate = MeetingState(active_dialog=None, camera_off=True, confidence=0.9)

    state = reducer.reduce(current, [candidate, later_candidate])

    assert state == MeetingState(
        meeting_joined=True,
        mic_muted=True,
        camera_off=True,
        active_dialog="permissions",
        participant_count=2,
        confidence=0.8,
    )


def test_reducer_handles_empty_candidates() -> None:
    current = MeetingState(meeting_joined=True, confidence=0.9)
    reducer = StateReducer()

    state = reducer.reduce(current, [])

    assert state == current


def test_reducer_ignores_confidence_from_states_without_field_evidence() -> None:
    reducer = StateReducer()
    current = MeetingState(confidence=0.2)
    candidate = MeetingState(meeting_joined=True, confidence=0.9)

    state = reducer.reduce(current, [candidate])

    assert state.meeting_joined is True
    assert state.confidence == 0.9


def test_raw_observation_stores_ui_text_immutably() -> None:
    ui_text = ["Join", "Mute"]
    observation = RawObservation(
        metadata=WindowMetadata(
            process="app",
            pid=1,
            window_class="window",
            title="Meeting",
            bounds=(0, 0, 100, 100),
        ),
        ui_text=ui_text,
    )

    ui_text.append("Late mutation")

    assert observation.ui_text == ("Join", "Mute")
    with pytest.raises(FrozenInstanceError):
        setattr(observation, "ui_text", ("Changed",))


def test_presenter_event_stores_payload_immutably() -> None:
    payload = {"micMuted": True}
    event = PresenterEvent("mic_state_changed", payload, 0.9)

    payload["micMuted"] = False

    assert event.payload == {"micMuted": True}
    with pytest.raises(TypeError):
        cast(Any, event.payload)["micMuted"] = False
