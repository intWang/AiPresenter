from pathlib import Path

import pytest

from ai_presenter.providers.windows_speech import InstalledSapiVoice
from ai_presenter.providers.windows_speech import WindowsSapiSpeechProvider
from ai_presenter.providers.windows_speech import list_installed_sapi_voices
from ai_presenter.providers.windows_speech import sapi_voice_available


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


def test_list_installed_sapi_voices_uses_injected_dispatcher() -> None:
    class FakeToken:
        Id = "token-id"

        def GetDescription(self) -> str:
            return "Microsoft Huihui Desktop"

    class FakeVoice:
        def GetVoices(self) -> list[FakeToken]:
            return [FakeToken()]

    def dispatch(name: str) -> FakeVoice:
        assert name == "SAPI.SpVoice"
        return FakeVoice()

    voices = list_installed_sapi_voices(dispatcher=dispatch)

    assert voices == (InstalledSapiVoice(name="Microsoft Huihui Desktop", token_id="token-id"),)


def test_sapi_voice_available_matches_case_insensitive_substrings() -> None:
    voices = (
        InstalledSapiVoice(name="Microsoft Zira Desktop"),
        InstalledSapiVoice(name="Microsoft Huihui Desktop"),
    )

    assert sapi_voice_available("zira", voices) is True
    assert sapi_voice_available("Huihui", voices) is True
    assert sapi_voice_available("Jenny", voices) is False
