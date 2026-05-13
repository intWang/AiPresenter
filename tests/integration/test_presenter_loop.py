from pathlib import Path

import pytest

from ai_presenter.adapters.ringcentral import RingCentralAdapter
from ai_presenter.config.loader import load_profile
from ai_presenter.config.models import DesktopAppProfile
from ai_presenter.desktop.base import WindowHandle
from ai_presenter.domain.state import MeetingState, PresenterEvent, RawObservation, WindowMetadata
from ai_presenter.providers.base import SpeechAudio
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


class FailingOnceSink:
    def __init__(self) -> None:
        self.failures_remaining = 1
        self.audio: list[object] = []

    def play(self, audio: object) -> None:
        if self.failures_remaining > 0:
            self.failures_remaining -= 1
            raise RuntimeError("speaker unavailable")
        self.audio.append(audio)


class FailingOnceSpeechProvider:
    def __init__(self) -> None:
        self.failures_remaining = 1
        self.spoken_texts: list[str] = []
        self._delegate = FakeSpeechProvider()

    def synthesize(self, text: str) -> SpeechAudio:
        self.spoken_texts.append(text)
        if self.failures_remaining > 0:
            self.failures_remaining -= 1
            raise RuntimeError("tts unavailable")
        return self._delegate.synthesize(text)


class MutableClock:
    def __init__(self, value: float) -> None:
        self.value = value

    def __call__(self) -> float:
        return self.value


class SequenceNarrationProvider:
    def __init__(self, responses: list[str]) -> None:
        self._responses = list(responses)
        self.calls: list[list[str]] = []

    def narrate(self, state: MeetingState, events: list[PresenterEvent]) -> str:
        self.calls.append([event.type for event in events])
        if not self._responses:
            raise AssertionError("narration called more times than expected")
        return self._responses.pop(0)


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
    narration_provider: FakeNarrationProvider | SequenceNarrationProvider | None = None,
    speech_provider: FakeSpeechProvider | FailingOnceSpeechProvider | None = None,
    media_output: RecordingSink | FailingOnceSink | None = None,
) -> tuple[
    PresenterLoop,
    FakeSpeechProvider | FailingOnceSpeechProvider,
    RecordingSink | FailingOnceSink,
]:
    profile = load_desktop_profile()
    speech = speech_provider or FakeSpeechProvider()
    sink = media_output or RecordingSink()
    narration = NarrationEngine(
        profile.narration,
        narration_provider or FakeNarrationProvider(),
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


def test_blank_narration_does_not_commit_state_so_event_retries() -> None:
    provider = SequenceNarrationProvider(["   ", "Meeting joined."])
    observation = make_observation(["Mute microphone", "Stop video", "Participants 2"])
    loop, speech, sink = make_loop(
        [observation, observation],
        narration_provider=provider,
    )

    loop.run_once(make_handle())
    loop.run_once(make_handle())

    assert provider.calls == [["meeting_joined"], ["meeting_joined"]]
    assert speech.spoken_texts == ["Meeting joined."]
    assert len(sink.audio) == 1


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


def test_cooldown_suppressed_event_retries_after_cooldown_clears() -> None:
    clock = MutableClock(100.0)
    loop, speech, sink = make_loop(
        [
            make_observation(["Mute microphone", "Stop video", "Participants 2"]),
            make_observation(["Unmute microphone", "Stop video", "Participants 2"]),
            make_observation(["Unmute microphone", "Stop video", "Participants 2"]),
        ],
        clock=clock,
    )

    loop.run_once(make_handle())
    clock.value = 101.0
    loop.run_once(make_handle())
    clock.value = 105.0
    loop.run_once(make_handle())

    assert speech.spoken_texts == [
        "Detected meeting event: meeting_joined.",
        "Detected meeting event: mic_state_changed.",
    ]
    assert len(sink.audio) == 2


def test_speech_failure_does_not_commit_cooldown_or_state() -> None:
    observation = make_observation(["Mute microphone", "Stop video", "Participants 2"])
    speech = FailingOnceSpeechProvider()
    loop, _, sink = make_loop(
        [observation, observation],
        speech_provider=speech,
    )

    with pytest.raises(RuntimeError, match="tts unavailable"):
        loop.run_once(make_handle())
    loop.run_once(make_handle())

    assert speech.spoken_texts == [
        "Detected meeting event: meeting_joined.",
        "Detected meeting event: meeting_joined.",
    ]
    assert len(sink.audio) == 1


def test_media_output_failure_does_not_commit_cooldown_or_state() -> None:
    observation = make_observation(["Mute microphone", "Stop video", "Participants 2"])
    sink = FailingOnceSink()
    loop, speech, _ = make_loop(
        [observation, observation],
        media_output=sink,
    )

    with pytest.raises(RuntimeError, match="speaker unavailable"):
        loop.run_once(make_handle())
    loop.run_once(make_handle())

    assert speech.spoken_texts == [
        "Detected meeting event: meeting_joined.",
        "Detected meeting event: meeting_joined.",
    ]
    assert len(sink.audio) == 1
