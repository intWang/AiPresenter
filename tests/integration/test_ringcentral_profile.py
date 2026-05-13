from pathlib import Path

from ai_presenter.adapters.ringcentral import RingCentralAdapter
from ai_presenter.config.loader import load_profile
from ai_presenter.config.models import DesktopAppProfile
from ai_presenter.domain.state import RawObservation, WindowMetadata
from ai_presenter.runtime.events import EventDetector


def make_observation(ui_text: list[str]) -> RawObservation:
    return RawObservation(
        metadata=WindowMetadata(
            process="RingCentralVideo",
            pid=10,
            window_class="RingCentralVideoClass",
            title="RingCentral Video",
            bounds=(0, 0, 1000, 800),
        ),
        ui_text=ui_text,
    )


def test_ringcentral_profile_uses_expected_binding():
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))

    assert isinstance(profile, DesktopAppProfile)
    assert profile.bind.process == "RingCentralVideo"
    assert profile.bind.window_class == "RingCentralVideoClass"


def test_ringcentral_adapter_extracts_mic_and_camera_from_ui_text():
    adapter = RingCentralAdapter()
    observation = make_observation(["Mute microphone", "Stop video", "Participants 3"])

    state = adapter.extract_state(observation)

    assert state.meeting_joined is True
    assert state.mic_muted is False
    assert state.camera_off is False
    assert state.participant_count == 3


def test_connection_warning_does_not_create_active_dialog():
    adapter = RingCentralAdapter()
    observation = make_observation(["Your connection is unstable"])

    state = adapter.extract_state(observation)

    assert state.active_dialog is None
    assert state.connection_warning == "connection issue"


def test_connection_settings_does_not_create_dialog_or_warning():
    adapter = RingCentralAdapter()
    observation = make_observation(["Connection settings"])

    state = adapter.extract_state(observation)

    assert state.active_dialog is None
    assert state.connection_warning is None


def test_mute_participants_does_not_set_self_mic_state():
    adapter = RingCentralAdapter()
    observation = make_observation(["Mute participants"])

    state = adapter.extract_state(observation)

    assert state.mic_muted is None


def test_bare_mute_labels_do_not_set_self_mic_state():
    adapter = RingCentralAdapter()

    muted_state = adapter.extract_state(make_observation(["Mute"]))
    unmuted_state = adapter.extract_state(make_observation(["Unmute"]))

    assert muted_state.mic_muted is None
    assert unmuted_state.mic_muted is None


def test_split_start_video_labels_do_not_set_camera_state():
    adapter = RingCentralAdapter()
    observation = make_observation(["Start", "video"])

    state = adapter.extract_state(observation)

    assert state.camera_off is None


def test_camera_settings_and_help_phrases_do_not_set_camera_state():
    adapter = RingCentralAdapter()

    start_settings = adapter.extract_state(make_observation(["Start video settings"]))
    stop_help = adapter.extract_state(make_observation(["Stop video help"]))

    assert start_settings.camera_off is None
    assert stop_help.camera_off is None


def test_participant_count_supports_parentheses():
    adapter = RingCentralAdapter()
    observation = make_observation(["Participants (3)"])

    state = adapter.extract_state(observation)

    assert state.participant_count == 3


def test_participant_count_supports_colon():
    adapter = RingCentralAdapter()
    observation = make_observation(["Participants: 3"])

    state = adapter.extract_state(observation)

    assert state.participant_count == 3


def test_no_useful_evidence_returns_lower_confidence_than_happy_path():
    adapter = RingCentralAdapter()
    happy_path = adapter.extract_state(
        make_observation(["Mute microphone", "Stop video", "Participants 3"])
    )
    no_signal = adapter.extract_state(make_observation(["RingCentral Video"]))

    assert no_signal.confidence < happy_path.confidence


def test_low_evidence_state_does_not_emit_runtime_events():
    adapter = RingCentralAdapter()
    detector = EventDetector(confidence_threshold=0.75)
    state = adapter.extract_state(make_observation(["RingCentral Video"]))

    events = detector.detect(previous=None, current=state)

    assert events == []


def test_happy_path_state_stays_above_runtime_threshold():
    adapter = RingCentralAdapter()
    detector = EventDetector(confidence_threshold=0.75)
    state = adapter.extract_state(make_observation(["Mute microphone", "Stop video"]))

    events = detector.detect(previous=None, current=state)

    assert state.confidence >= 0.75
    assert [event.type for event in events] == ["meeting_joined"]
