import pytest

from ai_presenter.domain.state import MeetingState
from ai_presenter.providers.base import ProviderRegistry
from ai_presenter.providers.fake import FakeSpeechProvider, FakeVisionProvider


def test_registry_returns_registered_provider() -> None:
    registry = ProviderRegistry()
    vision = FakeVisionProvider(MeetingState(meeting_joined=True, confidence=0.9))

    registry.register_vision("fake", vision)

    assert registry.vision("fake") is vision


def test_registry_rejects_missing_provider() -> None:
    registry = ProviderRegistry()

    with pytest.raises(KeyError):
        registry.speech("missing")


def test_fake_speech_returns_wav_bytes() -> None:
    audio = FakeSpeechProvider().synthesize("Meeting joined.")

    assert audio.mime_type == "audio/wav"
    assert audio.data.startswith(b"RIFF")
