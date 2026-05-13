import json
import os
from collections.abc import Callable
from typing import Any
from typing import cast

from openai import OpenAI

from ai_presenter.domain.state import MeetingState, PresenterEvent
from ai_presenter.providers.base import SpeechAudio

_NARRATION_MODEL_ENV = "AI_PRESENTER_OPENAI_NARRATION_MODEL"
_SPEECH_MODEL_ENV = "AI_PRESENTER_OPENAI_TTS_MODEL"

_NARRATION_INSTRUCTIONS = (
    "You are the narration voice for an AI presenter observing RingCentral meeting UI. "
    "Speak only about verified RingCentral meeting UI state and verified events supplied in "
    "the input. Do not infer shared-screen content, participant identity, meeting purpose, "
    "or private content. Use only the provided state/events, and return concise output."
)


class OpenAINarrationProvider:
    def __init__(self, client: Any | None = None, model: str | None = None) -> None:
        self._client = _resolve_client(client)
        model_value = model if model is not None else os.getenv(_NARRATION_MODEL_ENV)
        self._model = _require_nonblank(
            model_value,
            f"OpenAI narration model is required. Pass model or set {_NARRATION_MODEL_ENV}.",
        )

    def narrate(self, state: MeetingState, events: list[PresenterEvent]) -> str:
        response = self._client.responses.create(
            model=self._model,
            instructions=_NARRATION_INSTRUCTIONS,
            input=_build_narration_input(state, events),
        )
        output_text: object = getattr(response, "output_text", None)
        if not isinstance(output_text, str):
            raise TypeError("OpenAI Responses API response must expose string output_text.")
        return output_text.strip()


class OpenAISpeechProvider:
    def __init__(
        self,
        client: Any | None = None,
        model: str | None = None,
        voice: str = "verse",
    ) -> None:
        self._client = _resolve_client(client)
        model_value = model if model is not None else os.getenv(_SPEECH_MODEL_ENV, "gpt-4o-mini-tts")
        self._model = _require_nonblank(model_value, "OpenAI speech model cannot be blank.")
        self._voice = _require_nonblank(voice, "OpenAI speech voice cannot be blank.")

    def synthesize(self, text: str) -> SpeechAudio:
        speech_text = text.strip()
        if not speech_text:
            raise ValueError("Speech text cannot be blank.")

        response = self._client.audio.speech.create(
            model=self._model,
            voice=self._voice,
            input=speech_text,
            response_format="wav",
        )
        return SpeechAudio(
            data=_read_binary_response(response),
            mime_type="audio/wav",
            sample_rate=24_000,
            channels=1,
        )


def _resolve_client(client: Any | None) -> Any:
    if client is not None:
        return client

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("OPENAI_API_KEY is required to create an OpenAI client.")
    return OpenAI(api_key=api_key)


def _require_nonblank(value: str | None, message: str) -> str:
    normalized = (value or "").strip()
    if not normalized:
        raise ValueError(message)
    return normalized


def _build_narration_input(state: MeetingState, events: list[PresenterEvent]) -> str:
    payload: dict[str, object] = {
        "meeting_ui_state": {
            "meeting_joined": state.meeting_joined,
            "mic_muted": state.mic_muted,
            "camera_off": state.camera_off,
            "active_dialog": state.active_dialog,
            "participant_count": state.participant_count,
            "connection_warning": state.connection_warning,
            "confidence": state.confidence,
        },
        "verified_events": [
            {
                "type": event.type,
                "payload": dict(event.payload),
                "confidence": event.confidence,
                "occurred_at": event.occurred_at.isoformat(),
            }
            for event in events
        ],
    }
    return json.dumps(payload, default=str, sort_keys=True)


def _read_binary_response(response: object) -> bytes:
    content: object = getattr(response, "content", None)
    data = _coerce_bytes(content)
    if data is not None:
        return data

    reader: object = getattr(response, "read", None)
    if callable(reader):
        read = cast(Callable[[], object], reader)
        read_data = read()
        data = _coerce_bytes(read_data)
        if data is not None:
            return data

    raise TypeError("OpenAI Speech API response must expose bytes via content or read().")


def _coerce_bytes(value: object) -> bytes | None:
    if isinstance(value, bytes):
        return value
    if isinstance(value, bytearray):
        return bytes(value)
    if isinstance(value, memoryview):
        return value.tobytes()
    return None
