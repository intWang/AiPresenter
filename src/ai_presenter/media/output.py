from __future__ import annotations

import io
import logging
from collections.abc import Callable
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


class StoppableOutput(Protocol):
    def stop(self) -> None:
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

    def stop(self) -> None:
        sounddevice.stop()


class SingleOutput:
    def __init__(self, sink: AudioSink) -> None:
        self._sink = sink

    def play(self, audio: SpeechAudio) -> None:
        self._sink.play(audio)

    def stop(self) -> None:
        _stop_if_supported(self._sink)


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

    def stop(self) -> None:
        for sink in self._sinks:
            try:
                _stop_if_supported(sink)
            except Exception as exc:
                logger.warning("Audio stop failed for %s: %s", sink.__class__.__name__, exc)

    def _sink_name(self, index: int, sink: AudioSink) -> str:
        name = getattr(sink, "name", None)
        if isinstance(name, str) and name.strip():
            return f"sink {index} ({name.strip()})"
        return f"sink {index} ({sink.__class__.__name__})"


class MediaOutputFactory:
    def __init__(
        self,
        speaker_sink: AudioSink | None = None,
        virtual_mic_sink: AudioSink | None = None,
        sink_factory: Callable[[str | int | None], AudioSink] = SoundDeviceSink,
    ) -> None:
        self._speaker_sink = speaker_sink
        self._virtual_mic_sink = virtual_mic_sink
        self._sink_factory = sink_factory

    def create(self, config: AudioConfig) -> MediaOutput:
        if config.output is AudioOutputMode.SPEAKER:
            return SingleOutput(self._create_speaker_sink(config))
        if config.output is AudioOutputMode.VIRTUAL_MIC:
            return SingleOutput(self._create_virtual_mic_sink(config, "virtual_mic"))
        if config.output is AudioOutputMode.BOTH:
            return CombinedOutput(
                [
                    self._create_speaker_sink(config),
                    self._create_virtual_mic_sink(config, "both"),
                ]
            )
        raise ValueError(f"Unsupported audio output mode: {config.output}")

    def _create_speaker_sink(self, config: AudioConfig) -> AudioSink:
        if self._speaker_sink is not None:
            return self._speaker_sink
        return self._sink_factory(_speaker_device(config.speaker_device))

    def _create_virtual_mic_sink(self, config: AudioConfig, output_name: str) -> AudioSink:
        if not config.virtual_mic_device or not config.virtual_mic_device.strip():
            raise ValueError(f"virtualMicDevice is required for {output_name} output")
        if self._virtual_mic_sink is not None:
            return self._virtual_mic_sink
        return self._sink_factory(config.virtual_mic_device.strip())


def _speaker_device(device: str | None) -> str | None:
    if device is None:
        return None
    normalized = device.strip()
    if not normalized or normalized.casefold() == "default":
        return None
    return normalized


def _stop_if_supported(output: object) -> None:
    stop = getattr(output, "stop", None)
    if callable(stop):
        stop()
