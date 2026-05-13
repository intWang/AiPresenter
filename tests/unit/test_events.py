from ai_presenter.domain.state import MeetingState
from ai_presenter.runtime.events import EventDetector


def test_detects_initial_meeting_joined_event():
    detector = EventDetector()
    current = MeetingState(meeting_joined=True, confidence=0.9)

    events = detector.detect(previous=None, current=current)

    assert [event.type for event in events] == ["meeting_joined"]


def test_detects_mic_state_change():
    detector = EventDetector()
    previous = MeetingState(meeting_joined=True, mic_muted=False, confidence=0.9)
    current = MeetingState(meeting_joined=True, mic_muted=True, confidence=0.9)

    events = detector.detect(previous=previous, current=current)

    assert len(events) == 1
    assert events[0].type == "mic_state_changed"
    assert events[0].payload == {"micMuted": True}


def test_ignores_low_confidence_state():
    detector = EventDetector(confidence_threshold=0.75)
    current = MeetingState(meeting_joined=True, confidence=0.4)

    events = detector.detect(previous=None, current=current)

    assert events == []
