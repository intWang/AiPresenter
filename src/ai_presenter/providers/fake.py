import io
import wave

from ai_presenter.domain.state import MeetingState, PresenterEvent, RawObservation
from ai_presenter.providers.base import SpeechAudio


class FakeVisionProvider:
    def __init__(self, state: MeetingState | None = None) -> None:
        self._state = state or MeetingState(meeting_joined=True, confidence=1.0)

    def recognize(self, observation: RawObservation) -> MeetingState:
        return self._state


class FakeNarrationProvider:
    def narrate(self, state: MeetingState, events: list[PresenterEvent]) -> str:
        if not events:
            return ""
        event_names = ", ".join(event.type for event in events)
        return f"Detected meeting event: {event_names}."


class FakeSpeechProvider:
    def __init__(self) -> None:
        self.spoken_texts: list[str] = []

    def synthesize(self, text: str) -> SpeechAudio:
        self.spoken_texts.append(text)
        sample_rate = 16_000
        frames = b"\x00\x00" * int(sample_rate * 0.1)
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(frames)
        return SpeechAudio(
            data=buffer.getvalue(),
            mime_type="audio/wav",
            sample_rate=sample_rate,
            channels=1,
        )
