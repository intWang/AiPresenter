from pathlib import Path

import pytest

from ai_presenter.providers.windows_speech import WindowsSapiSpeechProvider


def test_windows_sapi_speech_provider_returns_wav_audio() -> None:
    calls: list[tuple[str, str | None, int, int]] = []

    def synthesizer(
        text: str,
        output_path: Path,
        voice: str | None,
        rate: int,
        volume: int,
    ) -> None:
        calls.append((text, voice, rate, volume))
        output_path.write_bytes(b"RIFF" + b"x" * 64)

    provider = WindowsSapiSpeechProvider(
        voice="Test Voice",
        rate=1,
        volume=90,
        synthesizer=synthesizer,
    )

    audio = provider.synthesize("Meeting started.")

    assert audio.data == b"RIFF" + b"x" * 64
    assert audio.mime_type == "audio/wav"
    assert calls == [("Meeting started.", "Test Voice", 1, 90)]


def test_windows_sapi_speech_provider_rejects_blank_text() -> None:
    provider = WindowsSapiSpeechProvider(synthesizer=lambda *_args: None)

    with pytest.raises(ValueError, match="Speech text"):
        provider.synthesize("  ")


def test_windows_sapi_speech_provider_raises_on_empty_audio() -> None:
    def synthesizer(
        text: str,
        output_path: Path,
        voice: str | None,
        rate: int,
        volume: int,
    ) -> None:
        output_path.write_bytes(b"RIFF")

    provider = WindowsSapiSpeechProvider(synthesizer=synthesizer)

    with pytest.raises(RuntimeError, match="empty audio"):
        provider.synthesize("Meeting started.")


def test_windows_sapi_speech_provider_validates_rate_and_volume() -> None:
    with pytest.raises(ValueError, match="rate"):
        WindowsSapiSpeechProvider(rate=11)

    with pytest.raises(ValueError, match="volume"):
        WindowsSapiSpeechProvider(volume=101)
