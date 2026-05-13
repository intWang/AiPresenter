import pytest
from pydantic import ValidationError

from ai_presenter.config.models import AudioConfig, AudioOutputMode
from ai_presenter.media.output import AudioSink, MediaOutputFactory
from ai_presenter.providers.base import (
    ProviderLookupError,
    ProviderRegistrationError,
    ProviderRegistry,
    SpeechAudio,
)


class RecordingSink(AudioSink):
    def __init__(self) -> None:
        self.calls: list[SpeechAudio] = []

    def play(self, audio: SpeechAudio) -> None:
        self.calls.append(audio)


class FailingSink(AudioSink):
    def play(self, audio: SpeechAudio) -> None:
        raise OSError("audio device unavailable")


class StubSpeechProvider:
    def synthesize(self, text: str) -> SpeechAudio:
        return make_audio()


def make_audio() -> SpeechAudio:
    return SpeechAudio(b"RIFFdata", "audio/wav", 16000, 1)


def test_speaker_output_routes_only_to_speaker() -> None:
    speaker = RecordingSink()
    virtual_mic = RecordingSink()
    config = AudioConfig(output=AudioOutputMode.SPEAKER, speakerDevice="default")

    output = MediaOutputFactory(speaker, virtual_mic).create(config)
    output.play(make_audio())

    assert len(speaker.calls) == 1
    assert len(virtual_mic.calls) == 0


def test_virtual_mic_output_routes_only_to_virtual_mic() -> None:
    speaker = RecordingSink()
    virtual_mic = RecordingSink()
    config = AudioConfig(
        output=AudioOutputMode.VIRTUAL_MIC,
        speakerDevice="default",
        virtualMicDevice="VB-CABLE Input",
    )

    output = MediaOutputFactory(speaker, virtual_mic).create(config)
    output.play(make_audio())

    assert len(speaker.calls) == 0
    assert len(virtual_mic.calls) == 1


def test_both_output_routes_to_speaker_and_virtual_mic() -> None:
    speaker = RecordingSink()
    virtual_mic = RecordingSink()
    config = AudioConfig(
        output=AudioOutputMode.BOTH,
        speakerDevice="default",
        virtualMicDevice="VB-CABLE Input",
    )

    output = MediaOutputFactory(speaker, virtual_mic).create(config)
    output.play(make_audio())

    assert len(speaker.calls) == 1
    assert len(virtual_mic.calls) == 1


def test_both_output_continues_when_one_sink_fails() -> None:
    virtual_mic = RecordingSink()
    config = AudioConfig(
        output=AudioOutputMode.BOTH,
        speakerDevice="default",
        virtualMicDevice="VB-CABLE Input",
    )

    output = MediaOutputFactory(FailingSink(), virtual_mic).create(config)
    output.play(make_audio())

    assert len(virtual_mic.calls) == 1


def test_both_output_raises_when_all_sinks_fail() -> None:
    config = AudioConfig(
        output=AudioOutputMode.BOTH,
        speakerDevice="default",
        virtualMicDevice="VB-CABLE Input",
    )

    output = MediaOutputFactory(FailingSink(), FailingSink()).create(config)

    with pytest.raises(RuntimeError, match="All audio outputs failed"):
        output.play(make_audio())


@pytest.mark.parametrize(
    ("output_mode", "message"),
    [
        (AudioOutputMode.VIRTUAL_MIC, "virtualMicDevice is required for virtual_mic output"),
        (AudioOutputMode.BOTH, "virtualMicDevice is required for both output"),
    ],
)
def test_factory_rejects_virtual_mic_outputs_without_device(
    output_mode: AudioOutputMode,
    message: str,
) -> None:
    speaker = RecordingSink()
    virtual_mic = RecordingSink()
    config = AudioConfig.model_construct(output=output_mode, virtual_mic_device=None)

    with pytest.raises(ValueError, match=message):
        MediaOutputFactory(speaker, virtual_mic).create(config)


def test_factory_rejects_unsupported_output_mode() -> None:
    speaker = RecordingSink()
    virtual_mic = RecordingSink()
    config = AudioConfig.model_construct(output="unsupported", virtual_mic_device=None)

    with pytest.raises(ValueError, match="Unsupported audio output mode"):
        MediaOutputFactory(speaker, virtual_mic).create(config)


@pytest.mark.parametrize("virtual_mic_device", [None, "", "   "])
def test_virtual_mic_requires_device_name(virtual_mic_device: str | None) -> None:
    with pytest.raises(ValidationError, match="virtualMicDevice"):
        AudioConfig(
            output=AudioOutputMode.VIRTUAL_MIC,
            speakerDevice="default",
            virtualMicDevice=virtual_mic_device,
        )


def test_provider_registry_normalizes_names_and_reports_lookup_errors() -> None:
    registry = ProviderRegistry()
    speech_provider = StubSpeechProvider()

    registry.register_speech(" fake ", speech_provider)

    assert registry.speech("fake") is speech_provider
    with pytest.raises(ProviderRegistrationError, match="already registered"):
        registry.register_speech("fake", StubSpeechProvider())
    with pytest.raises(ProviderLookupError, match="Available speech providers: fake"):
        registry.speech("missing")
