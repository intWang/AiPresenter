from __future__ import annotations

import io
import logging
from typing import TYPE_CHECKING, Any, Protocol, cast

import numpy as np
import sounddevice  # type: ignore[import-untyped]
import soundfile  # type: ignore[import-untyped]

from ai_presenter.config.models import AudioConfig, AudioOutputMode

if TYPE_CHECKING:
    from ai_presenter.providers.base import SpeechAudio

logger = logging.getLogger(__name__)

_Float32Samples = np.ndarray[Any, np.dtype[np.float32]]


class AudioSink(Protocol):
    def play(self, audio: SpeechAudio) -> None:
        ...


class MediaOutput(Protocol):
    def play(self, audio: SpeechAudio) -> None:
        ...


class AudioOutputError(RuntimeError):
    def __init__(self, message: str, *, sink_failures: dict[str, Exception] | None = None) -> None:
        self.sink_failures = sink_failures or {}
        super().__init__(message)


def decode_wav(audio: SpeechAudio) -> tuple[_Float32Samples, int]:
    try:
        raw_samples, sample_rate = soundfile.read(
            io.BytesIO(audio.data),
            dtype="float32",
            always_2d=True,
        )
    except soundfile.SoundFileError as exc:
        raise AudioOutputError("Failed to decode WAV audio.") from exc
    samples = cast(_Float32Samples, raw_samples)
    return samples, int(sample_rate)


class SoundDeviceSink:
    def __init__(self, device: str | int | None = None) -> None:
        self._device = device
        self.name = "sounddevice" if device is None else f"sounddevice: {device}"

    def play(self, audio: SpeechAudio) -> None:
        samples, sample_rate = decode_wav(audio)
        try:
            sounddevice.play(
                samples,
                samplerate=sample_rate,
                device=self._device,
                blocking=True,
            )
        except sounddevice.PortAudioError as exc:
            raise AudioOutputError(f"Audio playback failed for {self.name}.") from exc


class SingleOutput:
    def __init__(self, sink: AudioSink) -> None:
        self._sink = sink

    def play(self, audio: SpeechAudio) -> None:
        self._sink.play(audio)


class CombinedOutput:
    def __init__(self, sinks: list[AudioSink]) -> None:
        self._sinks = sinks

    def play(self, audio: SpeechAudio) -> None:
        errors: dict[str, Exception] = {}
        for index, sink in enumerate(self._sinks):
            sink_name = self._sink_name(index, sink)
            try:
                sink.play(audio)
            except AudioOutputError as exc:
                errors[sink_name] = exc
                logger.warning("Audio output failed for %s: %s", sink_name, exc)
        if len(errors) == len(self._sinks):
            failed_sinks = ", ".join(errors)
            raise AudioOutputError(
                f"All audio outputs failed: {failed_sinks}",
                sink_failures=errors,
            ) from next(iter(errors.values()))

    def _sink_name(self, index: int, sink: AudioSink) -> str:
        name = getattr(sink, "name", None)
        if isinstance(name, str) and name.strip():
            return f"sink {index} ({name.strip()})"
        return f"sink {index} ({sink.__class__.__name__})"


class MediaOutputFactory:
    def __init__(self, speaker_sink: AudioSink, virtual_mic_sink: AudioSink) -> None:
        self._speaker_sink = speaker_sink
        self._virtual_mic_sink = virtual_mic_sink

    def create(self, config: AudioConfig) -> MediaOutput:
        if config.output is AudioOutputMode.SPEAKER:
            return SingleOutput(self._speaker_sink)
        if config.output is AudioOutputMode.VIRTUAL_MIC:
            if not config.virtual_mic_device or not config.virtual_mic_device.strip():
                raise ValueError("virtualMicDevice is required for virtual_mic output")
            return SingleOutput(self._virtual_mic_sink)
        if config.output is AudioOutputMode.BOTH:
            if not config.virtual_mic_device or not config.virtual_mic_device.strip():
                raise ValueError("virtualMicDevice is required for both output")
            return CombinedOutput([self._speaker_sink, self._virtual_mic_sink])
        raise ValueError(f"Unsupported audio output mode: {config.output}")
