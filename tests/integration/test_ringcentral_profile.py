from pathlib import Path

from ai_presenter.adapters.ringcentral import RingCentralAdapter
from ai_presenter.config.loader import load_profile
from ai_presenter.config.models import DesktopAppProfile
from ai_presenter.domain.state import RawObservation, WindowMetadata


def test_ringcentral_profile_uses_expected_binding():
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))

    assert isinstance(profile, DesktopAppProfile)
    assert profile.bind.process == "RingCentralVideo"
    assert profile.bind.window_class == "RingCentralVideoClass"


def test_ringcentral_adapter_extracts_mic_and_camera_from_ui_text():
    adapter = RingCentralAdapter()
    observation = RawObservation(
        metadata=WindowMetadata(
            process="RingCentralVideo",
            pid=10,
            window_class="RingCentralVideoClass",
            title="RingCentral Video",
            bounds=(0, 0, 1000, 800),
        ),
        ui_text=["Mute microphone", "Stop video", "Participants 3"],
    )

    state = adapter.extract_state(observation)

    assert state.meeting_joined is True
    assert state.mic_muted is False
    assert state.camera_off is False
    assert state.participant_count == 3
