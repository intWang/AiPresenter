import importlib
import tempfile
from collections.abc import Callable
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ai_presenter.providers.base import SpeechAudio

Synthesizer = Callable[[str, Path, str | None, int, int], None]
SapiDispatcher = Callable[[str], Any]


@dataclass(frozen=True)
class InstalledSapiVoice:
    name: str
    token_id: str | None = None


class WindowsSapiSpeechProvider:
    def __init__(
        self,
        *,
        voice: str | None = None,
        rate: int = 0,
        volume: int = 100,
        synthesizer: Synthesizer | None = None,
    ) -> None:
        if not -10 <= rate <= 10:
            raise ValueError("Windows SAPI speech rate must be between -10 and 10.")
        if not 0 <= volume <= 100:
            raise ValueError("Windows SAPI speech volume must be between 0 and 100.")
        self._voice = _normalize_optional(voice)
        self._rate = rate
        self._volume = volume
        self._synthesizer = synthesizer or _synthesize_with_sapi

    def synthesize(self, text: str) -> SpeechAudio:
        speech_text = text.strip()
        if not speech_text:
            raise ValueError("Speech text cannot be blank.")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as output_file:
            output_path = Path(output_file.name)

        try:
            self._synthesizer(speech_text, output_path, self._voice, self._rate, self._volume)
            data = output_path.read_bytes()
            if len(data) <= 46:
                raise RuntimeError(
                    "Windows SAPI speech synthesis returned empty audio. "
                    "Check that an installed SAPI voice supports the narration language."
                )
            return SpeechAudio(
                data=data,
                mime_type="audio/wav",
                sample_rate=0,
                channels=1,
            )
        finally:
            output_path.unlink(missing_ok=True)


def _synthesize_with_sapi(
    text: str,
    output_path: Path,
    voice_name: str | None,
    rate: int,
    volume: int,
) -> None:
    win32com_client = importlib.import_module("win32com.client")
    voice = win32com_client.Dispatch("SAPI.SpVoice")
    _select_voice(voice, voice_name)
    voice.Rate = rate
    voice.Volume = volume

    stream = win32com_client.Dispatch("SAPI.SpFileStream")
    stream.Open(str(output_path), 3, False)
    try:
        voice.AudioOutputStream = stream
        voice.Speak(text)
    finally:
        stream.Close()


def list_installed_sapi_voices(
    *,
    dispatcher: SapiDispatcher | None = None,
) -> tuple[InstalledSapiVoice, ...]:
    if dispatcher is None:
        win32com_client = importlib.import_module("win32com.client")
        dispatcher = win32com_client.Dispatch

    voice = dispatcher("SAPI.SpVoice")
    installed: list[InstalledSapiVoice] = []
    for token in voice.GetVoices():
        description = token.GetDescription()
        if not isinstance(description, str) or not description.strip():
            continue
        token_id = getattr(token, "Id", None)
        installed.append(
            InstalledSapiVoice(
                name=description.strip(),
                token_id=token_id if isinstance(token_id, str) and token_id.strip() else None,
            )
        )
    return tuple(installed)


def sapi_voice_available(voice_name: str, voices: Iterable[InstalledSapiVoice]) -> bool:
    expected = voice_name.strip().casefold()
    if not expected:
        return False
    return any(expected in voice.name.casefold() for voice in voices)


def _select_voice(voice: Any, voice_name: str | None) -> None:
    if voice_name is None:
        return
    for token in voice.GetVoices():
        description = token.GetDescription()
        if isinstance(description, str) and voice_name.casefold() in description.casefold():
            voice.Voice = token
            return
    raise ValueError(f"Windows SAPI voice not found: {voice_name}")


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None
