from __future__ import annotations

import logging
from typing import TYPE_CHECKING, cast

import pytest
from pydantic import ValidationError

from ai_presenter.config.models import AudioConfig, AudioOutputMode
from ai_presenter.media.output import AudioOutputError, AudioSink, MediaOutputFactory

if TYPE_CHECKING:
    from ai_presenter.providers.base import SpeechAudio


class RecordingSink(AudioSink):
    def __init__(self) -> None:
        self.calls: list[SpeechAudio] = []

    def play(self, audio: SpeechAudio) -> None:
        self.calls.append(audio)


class FailingSink(AudioSink):
    def __init__(self, name: str) -> None:
        self.name = name

    def play(self, audio: SpeechAudio) -> None:
        raise AudioOutputError(f"{self.name} unavailable")


class BuggySink(AudioSink):
    def play(self, audio: SpeechAudio) -> None:
        raise TypeError("programmer bug")


def make_audio() -> SpeechAudio:
    return cast("SpeechAudio", object())


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


def test_both_output_logs_and_continues_when_speaker_fails(
    caplog: pytest.LogCaptureFixture,
) -> None:
    virtual_mic = RecordingSink()
    config = AudioConfig(
        output=AudioOutputMode.BOTH,
        speakerDevice="default",
        virtualMicDevice="VB-CABLE Input",
    )

    output = MediaOutputFactory(FailingSink("speaker"), virtual_mic).create(config)
    with caplog.at_level(logging.WARNING, logger="ai_presenter.media.output"):
        output.play(make_audio())

    assert len(virtual_mic.calls) == 1
    assert "sink 0 (speaker)" in caplog.text
    assert "speaker unavailable" in caplog.text


def test_both_output_logs_and_continues_when_virtual_mic_fails(
    caplog: pytest.LogCaptureFixture,
) -> None:
    speaker = RecordingSink()
    config = AudioConfig(
        output=AudioOutputMode.BOTH,
        speakerDevice="default",
        virtualMicDevice="VB-CABLE Input",
    )

    output = MediaOutputFactory(speaker, FailingSink("virtual mic")).create(config)
    with caplog.at_level(logging.WARNING, logger="ai_presenter.media.output"):
        output.play(make_audio())

    assert len(speaker.calls) == 1
    assert "sink 1 (virtual mic)" in caplog.text
    assert "virtual mic unavailable" in caplog.text


def test_both_output_raises_when_all_sinks_fail() -> None:
    config = AudioConfig(
        output=AudioOutputMode.BOTH,
        speakerDevice="default",
        virtualMicDevice="VB-CABLE Input",
    )

    output = MediaOutputFactory(FailingSink("speaker"), FailingSink("virtual mic")).create(config)

    with pytest.raises(AudioOutputError, match="sink 0 \\(speaker\\).*sink 1 \\(virtual mic\\)") as exc_info:
        output.play(make_audio())

    assert set(exc_info.value.sink_failures) == {"sink 0 (speaker)", "sink 1 (virtual mic)"}


def test_both_output_does_not_mask_unexpected_sink_errors() -> None:
    config = AudioConfig(
        output=AudioOutputMode.BOTH,
        speakerDevice="default",
        virtualMicDevice="VB-CABLE Input",
    )

    output = MediaOutputFactory(BuggySink(), RecordingSink()).create(config)

    with pytest.raises(TypeError, match="programmer bug"):
        output.play(make_audio())


@pytest.mark.parametrize(
    ("output_mode", "virtual_mic_device", "message"),
    [
        (
            AudioOutputMode.VIRTUAL_MIC,
            None,
            "virtualMicDevice is required for virtual_mic output",
        ),
        (
            AudioOutputMode.VIRTUAL_MIC,
            "   ",
            "virtualMicDevice is required for virtual_mic output",
        ),
        (AudioOutputMode.BOTH, None, "virtualMicDevice is required for both output"),
        (AudioOutputMode.BOTH, "   ", "virtualMicDevice is required for both output"),
    ],
)
def test_factory_rejects_virtual_mic_outputs_without_device(
    output_mode: AudioOutputMode,
    virtual_mic_device: str | None,
    message: str,
) -> None:
    speaker = RecordingSink()
    virtual_mic = RecordingSink()
    config = AudioConfig.model_construct(
        output=output_mode,
        virtual_mic_device=virtual_mic_device,
    )

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
