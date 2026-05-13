from typing import Protocol

from ai_presenter.config.models import AudioConfig, AudioOutputMode
from ai_presenter.providers.base import SpeechAudio


class AudioSink(Protocol):
    def play(self, audio: SpeechAudio) -> None:
        ...


class MediaOutput(Protocol):
    def play(self, audio: SpeechAudio) -> None:
        ...


class SingleOutput:
    def __init__(self, sink: AudioSink) -> None:
        self._sink = sink

    def play(self, audio: SpeechAudio) -> None:
        self._sink.play(audio)


class CombinedOutput:
    def __init__(self, sinks: list[AudioSink]) -> None:
        self._sinks = sinks

    def play(self, audio: SpeechAudio) -> None:
        errors: list[Exception] = []
        for sink in self._sinks:
            try:
                sink.play(audio)
            except Exception as exc:
                errors.append(exc)
        if len(errors) == len(self._sinks):
            raise RuntimeError("All audio outputs failed") from errors[0]


class MediaOutputFactory:
    def __init__(self, speaker_sink: AudioSink, virtual_mic_sink: AudioSink) -> None:
        self._speaker_sink = speaker_sink
        self._virtual_mic_sink = virtual_mic_sink

    def create(self, config: AudioConfig) -> MediaOutput:
        if config.output is AudioOutputMode.SPEAKER:
            return SingleOutput(self._speaker_sink)
        if config.output is AudioOutputMode.VIRTUAL_MIC:
            if not config.virtual_mic_device:
                raise ValueError("virtualMicDevice is required for virtual_mic output")
            return SingleOutput(self._virtual_mic_sink)
        if config.output is AudioOutputMode.BOTH:
            if not config.virtual_mic_device:
                raise ValueError("virtualMicDevice is required for both output")
            return CombinedOutput([self._speaker_sink, self._virtual_mic_sink])
        raise ValueError(f"Unsupported audio output mode: {config.output}")
