from __future__ import annotations

from typing import Any, cast

import numpy as np
import pytest

from ai_presenter.media import output
from ai_presenter.providers.base import ProviderRegistry, SpeechAudio
from ai_presenter.providers.fake import FakeSpeechProvider


def test_decode_wav_returns_float32_samples_from_fake_speech_provider() -> None:
    speech = FakeSpeechProvider()
    registry = ProviderRegistry()
    registry.register_speech(" fake ", speech)
    audio = registry.speech("fake").synthesize("Meeting joined.")

    samples, sample_rate = output.decode_wav(audio)

    assert sample_rate == 16_000
    assert samples.dtype == np.float32
    assert samples.shape == (1_600, 1)
    assert np.allclose(samples, 0.0)
    assert speech.spoken_texts == ["Meeting joined."]


def test_sounddevice_sink_plays_decoded_wav_with_blocking_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[np.ndarray, int, str | int | None, bool]] = []

    def fake_play(
        samples: np.ndarray,
        *,
        samplerate: int,
        device: str | int | None,
        blocking: bool,
    ) -> None:
        calls.append((samples, samplerate, device, blocking))

    sounddevice = cast(Any, getattr(output, "sounddevice"))
    monkeypatch.setattr(sounddevice, "play", fake_play)

    audio = FakeSpeechProvider().synthesize("Meeting joined.")
    output.SoundDeviceSink(device="VB-CABLE Input").play(audio)

    assert len(calls) == 1
    samples, sample_rate, device, blocking = calls[0]
    assert samples.dtype == np.float32
    assert samples.shape == (1_600, 1)
    assert sample_rate == 16_000
    assert device == "VB-CABLE Input"
    assert blocking is True


def test_sounddevice_sink_name_describes_selected_device() -> None:
    assert output.SoundDeviceSink().name == "sounddevice"
    assert output.SoundDeviceSink(device="VB-CABLE Input").name == "sounddevice: VB-CABLE Input"
    assert output.SoundDeviceSink(device=3).name == "sounddevice: 3"


def test_decode_wav_wraps_soundfile_decode_errors() -> None:
    audio = SpeechAudio(
        data=b"not a wav",
        mime_type="audio/wav",
        sample_rate=16_000,
        channels=1,
    )

    with pytest.raises(output.AudioOutputError, match="Failed to decode WAV audio") as exc_info:
        output.decode_wav(audio)

    soundfile = cast(Any, getattr(output, "soundfile"))
    assert isinstance(exc_info.value.__cause__, soundfile.SoundFileError)


def test_sounddevice_sink_wraps_portaudio_playback_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_play(
        samples: np.ndarray,
        *,
        samplerate: int,
        device: str | int | None,
        blocking: bool,
    ) -> None:
        sounddevice = cast(Any, getattr(output, "sounddevice"))
        raise sounddevice.PortAudioError("device unavailable")

    sounddevice = cast(Any, getattr(output, "sounddevice"))
    monkeypatch.setattr(sounddevice, "play", fail_play)

    audio = FakeSpeechProvider().synthesize("Meeting joined.")
    with pytest.raises(output.AudioOutputError, match="Audio playback failed") as exc_info:
        output.SoundDeviceSink(device=3).play(audio)

    assert isinstance(exc_info.value.__cause__, sounddevice.PortAudioError)


def test_sounddevice_sink_does_not_wrap_programmer_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_play(
        samples: np.ndarray,
        *,
        samplerate: int,
        device: str | int | None,
        blocking: bool,
    ) -> None:
        raise TypeError("programmer bug")

    sounddevice = cast(Any, getattr(output, "sounddevice"))
    monkeypatch.setattr(sounddevice, "play", fail_play)

    audio = FakeSpeechProvider().synthesize("Meeting joined.")
    with pytest.raises(TypeError, match="programmer bug"):
        output.SoundDeviceSink().play(audio)
