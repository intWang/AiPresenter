import pytest

from ai_presenter.domain.state import MeetingState, PresenterEvent, RawObservation, WindowMetadata
from ai_presenter.providers.base import ProviderLookupError, ProviderRegistrationError, ProviderRegistry
from ai_presenter.providers.fake import FakeNarrationProvider, FakeSpeechProvider, FakeVisionProvider


def make_observation() -> RawObservation:
    return RawObservation(
        metadata=WindowMetadata(
            process="meet",
            pid=123,
            window_class="Chrome_WidgetWin_1",
            title="Meeting",
            bounds=(0, 0, 1280, 720),
        )
    )


def test_registry_returns_registered_provider() -> None:
    registry = ProviderRegistry()
    vision = FakeVisionProvider(MeetingState(meeting_joined=True, confidence=0.9))

    registry.register_vision("fake", vision)

    assert registry.vision("fake") is vision


def test_registry_returns_registered_narration_provider() -> None:
    registry = ProviderRegistry()
    narration = FakeNarrationProvider()

    registry.register_narration("fake", narration)

    assert registry.narration("fake") is narration


def test_registry_returns_registered_speech_provider() -> None:
    registry = ProviderRegistry()
    speech = FakeSpeechProvider()

    registry.register_speech("fake", speech)

    assert registry.speech("fake") is speech


def test_registry_rejects_duplicate_vision_provider_name() -> None:
    registry = ProviderRegistry()
    registry.register_vision("fake", FakeVisionProvider())

    with pytest.raises(ProviderRegistrationError, match="vision.*fake"):
        registry.register_vision("fake", FakeVisionProvider())


def test_registry_rejects_duplicate_narration_provider_name() -> None:
    registry = ProviderRegistry()
    registry.register_narration("fake", FakeNarrationProvider())

    with pytest.raises(ProviderRegistrationError, match="narration.*fake"):
        registry.register_narration("fake", FakeNarrationProvider())


def test_registry_rejects_duplicate_speech_provider_name() -> None:
    registry = ProviderRegistry()
    registry.register_speech("fake", FakeSpeechProvider())

    with pytest.raises(ProviderRegistrationError, match="speech.*fake"):
        registry.register_speech("fake", FakeSpeechProvider())


def test_registry_rejects_missing_provider() -> None:
    registry = ProviderRegistry()
    registry.register_speech("available", FakeSpeechProvider())

    with pytest.raises(ProviderLookupError, match="speech.*missing.*available"):
        registry.speech("missing")


def test_missing_provider_message_reports_empty_available_names() -> None:
    registry = ProviderRegistry()

    with pytest.raises(ProviderLookupError, match="vision.*missing.*none"):
        registry.vision("missing")


def test_fake_vision_returns_configured_state() -> None:
    state = MeetingState(meeting_joined=False, mic_muted=True, confidence=0.42)
    vision = FakeVisionProvider(state)

    assert vision.recognize(make_observation()) == state


def test_fake_narration_returns_empty_text_without_events() -> None:
    assert FakeNarrationProvider().narrate(MeetingState(), []) == ""


def test_fake_narration_describes_event_types() -> None:
    events = [
        PresenterEvent(type="meeting_joined", payload={}, confidence=0.9),
        PresenterEvent(type="mic_muted", payload={"muted": True}, confidence=0.8),
    ]

    narration = FakeNarrationProvider().narrate(MeetingState(), events)

    assert narration == "Detected meeting event: meeting_joined, mic_muted."


def test_fake_speech_returns_wav_bytes() -> None:
    audio = FakeSpeechProvider().synthesize("Meeting joined.")

    assert audio.mime_type == "audio/wav"
    assert audio.data.startswith(b"RIFF")


def test_fake_speech_records_synthesized_text() -> None:
    speech = FakeSpeechProvider()

    speech.synthesize("Meeting joined.")
    speech.synthesize("Microphone muted.")

    assert speech.spoken_texts == ["Meeting joined.", "Microphone muted."]
