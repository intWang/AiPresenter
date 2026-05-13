from pathlib import Path

from ai_presenter.adapters.ringcentral import RingCentralAdapter
from ai_presenter.config.loader import load_profile
from ai_presenter.config.models import DesktopAppProfile
from ai_presenter.desktop.base import WindowHandle
from ai_presenter.domain.state import RawObservation, WindowMetadata
from ai_presenter.providers.fake import FakeNarrationProvider, FakeSpeechProvider
from ai_presenter.runtime.events import EventDetector
from ai_presenter.runtime.narration import NarrationEngine
from ai_presenter.runtime.presenter import PresenterLoop


class FakeObservationDriver:
    def __init__(self, observations: list[RawObservation]) -> None:
        self._observations = list(observations)
        self.handles: list[WindowHandle] = []

    def capture(self, handle: WindowHandle) -> RawObservation:
        self.handles.append(handle)
        if not self._observations:
            raise AssertionError("capture called more times than expected")
        return self._observations.pop(0)


class RecordingSink:
    def __init__(self) -> None:
        self.audio: list[object] = []

    def play(self, audio: object) -> None:
        self.audio.append(audio)


class MutableClock:
    def __init__(self, value: float) -> None:
        self.value = value

    def __call__(self) -> float:
        return self.value


def make_handle() -> WindowHandle:
    return WindowHandle(
        process="RingCentralVideo",
        pid=10,
        window_class="RingCentralVideoClass",
        title="RingCentral Video",
    )


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


def load_desktop_profile() -> DesktopAppProfile:
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))
    assert isinstance(profile, DesktopAppProfile)
    return profile


def make_loop(
    observations: list[RawObservation],
    *,
    clock: MutableClock | None = None,
) -> tuple[PresenterLoop, FakeSpeechProvider, RecordingSink]:
    profile = load_desktop_profile()
    speech = FakeSpeechProvider()
    sink = RecordingSink()
    narration = NarrationEngine(
        profile.narration,
        FakeNarrationProvider(),
        now=clock or (lambda: 100.0),
    )
    loop = PresenterLoop(
        observation_driver=FakeObservationDriver(observations),
        adapter=RingCentralAdapter(),
        event_detector=EventDetector(confidence_threshold=profile.narration.confidence_threshold),
        narration_engine=narration,
        speech_provider=speech,
        media_output=sink,
    )
    return loop, speech, sink


def test_first_ringcentral_happy_path_observation_speaks_once_and_outputs_audio() -> None:
    loop, speech, sink = make_loop(
        [make_observation(["Mute microphone", "Stop video", "Participants 2"])]
    )

    loop.run_once(make_handle())

    assert speech.spoken_texts == ["Detected meeting event: meeting_joined."]
    assert len(sink.audio) == 1
    assert sink.audio[0].mime_type == "audio/wav"


def test_second_identical_observation_does_not_speak_or_output_again() -> None:
    observation = make_observation(["Mute microphone", "Stop video", "Participants 2"])
    loop, speech, sink = make_loop([observation, observation])

    loop.run_once(make_handle())
    loop.run_once(make_handle())

    assert speech.spoken_texts == ["Detected meeting event: meeting_joined."]
    assert len(sink.audio) == 1


def test_low_confidence_prejoin_only_observation_does_not_speak_or_output() -> None:
    loop, speech, sink = make_loop([make_observation(["RingCentral Video"])])

    loop.run_once(make_handle())

    assert speech.spoken_texts == []
    assert sink.audio == []


def test_later_changed_meeting_state_speaks_for_event_changes() -> None:
    clock = MutableClock(100.0)
    loop, speech, sink = make_loop(
        [
            make_observation(["Mute microphone", "Stop video", "Participants 2"]),
            make_observation(["Unmute microphone", "Start video", "Participants 3"]),
        ],
        clock=clock,
    )

    loop.run_once(make_handle())
    clock.value = 105.0
    loop.run_once(make_handle())

    assert speech.spoken_texts == [
        "Detected meeting event: meeting_joined.",
        "Detected meeting event: "
        "mic_state_changed, camera_state_changed, participant_count_changed.",
    ]
    assert len(sink.audio) == 2
