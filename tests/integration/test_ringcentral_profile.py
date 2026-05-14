from pathlib import Path

import pytest

from ai_presenter.adapters.ringcentral import RingCentralAdapter
from ai_presenter.config.loader import load_profile
from ai_presenter.config.models import DesktopAppProfile
from ai_presenter.domain.state import RawObservation, WindowMetadata
from ai_presenter.runtime.events import EventDetector


def make_observation(
    ui_text: list[str],
    *,
    process: str = "RingCentralVideo",
    window_class: str = "RingCentralVideoClass",
) -> RawObservation:
    return RawObservation(
        metadata=WindowMetadata(
            process=process,
            pid=10,
            window_class=window_class,
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


def test_ringcentral_adapter_treats_first_one_here_as_joined_meeting():
    adapter = RingCentralAdapter()
    observation = make_observation(["You're the first one here"])

    state = adapter.extract_state(observation)

    assert state.meeting_joined is True
    assert state.confidence >= 0.75


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


def test_permission_settings_does_not_create_active_dialog():
    adapter = RingCentralAdapter()
    observation = make_observation(["Permission settings"])

    state = adapter.extract_state(observation)

    assert state.active_dialog is None


def test_waiting_room_settings_does_not_create_active_dialog():
    adapter = RingCentralAdapter()
    observation = make_observation(["Waiting room settings"])

    state = adapter.extract_state(observation)

    assert state.active_dialog is None


def test_reconnecting_help_does_not_create_connection_warning():
    adapter = RingCentralAdapter()
    observation = make_observation(["Reconnecting help"])

    state = adapter.extract_state(observation)

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


@pytest.mark.parametrize("label", ["Participant 3", "Participant 3 of 10"])
def test_singular_participant_labels_do_not_create_in_meeting_evidence(label: str):
    adapter = RingCentralAdapter()
    detector = EventDetector(confidence_threshold=0.75)
    state = adapter.extract_state(make_observation([label]))

    events = detector.detect(previous=None, current=state)

    assert state.participant_count is None
    assert state.meeting_joined is False
    assert state.confidence < 0.75
    assert events == []


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


def test_ambiguous_dialog_and_warning_text_does_not_emit_runtime_events():
    adapter = RingCentralAdapter()
    detector = EventDetector(confidence_threshold=0.75)
    state = adapter.extract_state(
        make_observation(["Permission settings", "Waiting room settings", "Reconnecting help"])
    )

    events = detector.detect(previous=None, current=state)

    assert state.active_dialog is None
    assert state.connection_warning is None
    assert state.confidence < 0.75
    assert events == []


@pytest.mark.parametrize(
    ("label", "active_dialog"),
    [
        ("Waiting room", "waiting room"),
        ("Waiting for host", "waiting room"),
        ("Permission required", "permission"),
        ("Permissions required", "permission"),
    ],
)
def test_prejoin_dialogs_do_not_emit_initial_meeting_joined_event(
    label: str,
    active_dialog: str,
):
    adapter = RingCentralAdapter()
    detector = EventDetector(confidence_threshold=0.75)
    state = adapter.extract_state(make_observation([label]))

    events = detector.detect(previous=None, current=state)

    assert state.meeting_joined is False
    assert state.active_dialog == active_dialog
    assert state.confidence >= 0.75
    assert [event.type for event in events] == ["dialog_appeared"]


@pytest.mark.parametrize(
    ("label", "active_dialog"),
    [
        ("Waiting room", "waiting room"),
        ("Waiting for host", "waiting room"),
        ("Permission required", "permission"),
        ("Permissions required", "permission"),
    ],
)
def test_prejoin_dialogs_suppress_meeting_joined_with_other_evidence(
    label: str,
    active_dialog: str,
):
    adapter = RingCentralAdapter()
    detector = EventDetector(confidence_threshold=0.75)
    state = adapter.extract_state(make_observation([label, "Participants 3"]))

    events = detector.detect(previous=None, current=state)

    assert state.meeting_joined is False
    assert state.active_dialog == active_dialog
    assert state.participant_count == 3
    assert [event.type for event in events] == ["dialog_appeared"]


def test_happy_path_state_stays_above_runtime_threshold():
    adapter = RingCentralAdapter()
    detector = EventDetector(confidence_threshold=0.75)
    state = adapter.extract_state(make_observation(["Mute microphone", "Stop video"]))

    events = detector.detect(previous=None, current=state)

    assert state.confidence >= 0.75
    assert [event.type for event in events] == ["meeting_joined"]


def test_right_window_class_with_wrong_process_does_not_mark_joined():
    adapter = RingCentralAdapter()
    observation = make_observation(
        ["Mute microphone", "Stop video"],
        process="OtherProcess",
    )

    state = adapter.extract_state(observation)

    assert state.meeting_joined is False


def test_right_process_with_wrong_window_class_does_not_mark_joined():
    adapter = RingCentralAdapter()
    observation = make_observation(
        ["Mute microphone", "Stop video"],
        window_class="OtherWindowClass",
    )

    state = adapter.extract_state(observation)

    assert state.meeting_joined is False
