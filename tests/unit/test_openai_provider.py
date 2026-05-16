from pathlib import Path
from typing import Any

import pytest

from ai_presenter.config.loader import load_profile
from ai_presenter.domain.state import MeetingState, PresenterEvent
from ai_presenter.providers.base import ProviderLookupError, ProviderRegistrationError, ProviderRegistry
from ai_presenter.providers.openai_provider import OpenAINarrationProvider, OpenAISpeechProvider
from ai_presenter.runtime.presenter_context import PresenterContext
from ai_presenter.runtime.presenter_context import PresenterSkill
from ai_presenter.runtime.presenter_context import load_presenter_context


class FakeResponsesClient:
    def __init__(self, output_text: str = " Meeting joined. \n") -> None:
        self.calls: list[dict[str, Any]] = []
        self._output_text = output_text

    def create(self, **kwargs: Any) -> object:
        self.calls.append(kwargs)
        return type("Response", (), {"output_text": self._output_text})()


class FakeInvalidNarrationResponseClient:
    def create(self, **kwargs: Any) -> object:
        return type("Response", (), {"output_text": None})()


class FakeSpeechResponse:
    def __init__(self, content: bytes | bytearray | memoryview) -> None:
        self.content = content


class FakeReadableSpeechResponse:
    def __init__(self, content: bytes) -> None:
        self._content = content

    def read(self) -> bytes:
        return self._content


class FakeSpeechClient:
    def __init__(self, response: object | None = None) -> None:
        self.calls: list[dict[str, Any]] = []
        self._response = response or FakeSpeechResponse(b"RIFFfake-wav")

    def create(self, **kwargs: Any) -> object:
        self.calls.append(kwargs)
        return self._response


class FakeOpenAIClient:
    def __init__(
        self,
        responses: FakeResponsesClient | FakeInvalidNarrationResponseClient | None = None,
        speech: FakeSpeechClient | None = None,
    ) -> None:
        self.responses = responses or FakeResponsesClient()
        self.audio = type("AudioClient", (), {"speech": speech or FakeSpeechClient()})()


class FakeOpenAIClientFactory:
    def __init__(self) -> None:
        self.api_keys: list[str] = []

    def __call__(self, *, api_key: str) -> FakeOpenAIClient:
        self.api_keys.append(api_key)
        return FakeOpenAIClient()


def test_narration_calls_responses_api_with_constrained_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    responses = FakeResponsesClient(output_text="\n The microphone is muted.  ")
    provider = OpenAINarrationProvider(client=FakeOpenAIClient(responses=responses), model="gpt-4.1")

    text = provider.narrate(
        MeetingState(
            meeting_joined=True,
            mic_muted=True,
            camera_off=False,
            participant_count=3,
            confidence=0.91,
        ),
        [
            PresenterEvent(
                type="mic_state_changed",
                payload={"micMuted": True},
                confidence=0.88,
            )
        ],
    )

    assert text == "The microphone is muted."
    assert responses.calls == [
        {
            "model": "gpt-4.1",
            "instructions": responses.calls[0]["instructions"],
            "input": responses.calls[0]["input"],
        }
    ]
    instructions = responses.calls[0]["instructions"].lower()
    assert "verified ringcentral meeting ui state" in instructions
    assert "do not infer shared-screen content" in instructions
    assert "participant identity" in instructions
    assert "meeting purpose" in instructions
    assert "private content" in instructions
    assert "concise" in instructions
    request_input = responses.calls[0]["input"]
    assert "mic_state_changed" in request_input
    assert "micMuted" in request_input
    assert "participant_count" in request_input


def test_narration_instructions_include_presenter_soul_and_memory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    responses = FakeResponsesClient()
    provider = OpenAINarrationProvider(
        client=FakeOpenAIClient(responses=responses),
        model="gpt-4.1",
        presenter_context=PresenterContext(
            soul="Soul marker: professional presenter identity.",
            memory="Memory marker: speak in English with tighter transitions.",
            skills=(
                PresenterSkill(name="app-director", content="Skill marker: plan app slices."),
                PresenterSkill(
                    name="ringcentral-safety",
                    content="Skill marker: recording and leave/end stay explain-only.",
                ),
            ),
        ),
    )

    provider.narrate(MeetingState(confidence=0.9), [PresenterEvent("meeting_joined", {}, 0.9)])

    instructions = responses.calls[0]["instructions"]
    assert "Soul marker: professional presenter identity." in instructions
    assert "Memory marker: speak in English with tighter transitions." in instructions
    assert "Skill marker: plan app slices." in instructions
    assert "Presenter skill - ringcentral-safety:" in instructions
    assert "Skill marker: recording and leave/end stay explain-only." in instructions


def test_narration_instructions_include_loaded_ringcentral_safety_skill(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    responses = FakeResponsesClient()
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))
    provider = OpenAINarrationProvider(
        client=FakeOpenAIClient(responses=responses),
        model="gpt-4.1",
        presenter_context=load_presenter_context(profile.narration),
    )

    provider.narrate(MeetingState(confidence=0.9), [PresenterEvent("meeting_joined", {}, 0.9)])

    instructions = responses.calls[0]["instructions"]
    assert "Presenter skill - ringcentral-safety:" in instructions
    assert "RingCentral Video safety guardian" in instructions


def test_narration_uses_env_model_with_fake_client_without_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("AI_PRESENTER_OPENAI_NARRATION_MODEL", "  gpt-4.1-mini  ")
    responses = FakeResponsesClient()

    provider = OpenAINarrationProvider(client=FakeOpenAIClient(responses=responses))
    provider.narrate(MeetingState(confidence=0.9), [PresenterEvent("meeting_joined", {}, 0.9)])

    assert responses.calls[0]["model"] == "gpt-4.1-mini"


def test_narration_requires_model_with_fake_client(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("AI_PRESENTER_OPENAI_NARRATION_MODEL", raising=False)

    with pytest.raises(ValueError, match="narration model"):
        OpenAINarrationProvider(client=FakeOpenAIClient())


def test_narration_rejects_blank_model_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("AI_PRESENTER_OPENAI_NARRATION_MODEL", "   ")

    with pytest.raises(ValueError, match="narration model"):
        OpenAINarrationProvider(client=FakeOpenAIClient())


def test_narration_requires_api_key_when_creating_real_client(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        OpenAINarrationProvider(model="gpt-4.1")


def test_narration_creates_default_client_with_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    factory = FakeOpenAIClientFactory()
    monkeypatch.setenv("OPENAI_API_KEY", " test-key ")
    monkeypatch.setattr("ai_presenter.providers.openai_provider.OpenAI", factory)

    OpenAINarrationProvider(model="gpt-4.1")

    assert factory.api_keys == ["test-key"]


def test_narration_rejects_missing_output_text(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = FakeOpenAIClient(responses=FakeInvalidNarrationResponseClient())
    provider = OpenAINarrationProvider(client=client, model="gpt-4.1")

    with pytest.raises(TypeError, match="output_text"):
        provider.narrate(MeetingState(confidence=0.9), [PresenterEvent("meeting_joined", {}, 0.9)])


def test_speech_calls_audio_api_and_returns_wav_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    speech = FakeSpeechClient(FakeSpeechResponse(b"RIFFspeech-bytes"))
    provider = OpenAISpeechProvider(
        client=FakeOpenAIClient(speech=speech),
        model="tts-test",
        voice="alloy",
    )

    audio = provider.synthesize("Meeting joined.")

    assert speech.calls == [
        {
            "model": "tts-test",
            "voice": "alloy",
            "input": "Meeting joined.",
            "response_format": "wav",
        }
    ]
    assert audio.data == b"RIFFspeech-bytes"
    assert audio.mime_type == "audio/wav"
    assert audio.sample_rate == 24_000
    assert audio.channels == 1


def test_speech_uses_env_model_when_constructor_model_is_omitted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("AI_PRESENTER_OPENAI_TTS_MODEL", "  tts-env-model  ")
    speech = FakeSpeechClient()
    provider = OpenAISpeechProvider(client=FakeOpenAIClient(speech=speech))

    provider.synthesize("Meeting joined.")

    assert speech.calls[0]["model"] == "tts-env-model"


def test_speech_supports_readable_binary_response(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    speech = FakeSpeechClient(FakeReadableSpeechResponse(b"RIFFreadable"))
    provider = OpenAISpeechProvider(client=FakeOpenAIClient(speech=speech))

    audio = provider.synthesize("Camera is off.")

    assert audio.data == b"RIFFreadable"


def test_speech_supports_bytearray_and_memoryview_responses(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    bytearray_provider = OpenAISpeechProvider(
        client=FakeOpenAIClient(speech=FakeSpeechClient(FakeSpeechResponse(bytearray(b"RIFFarray"))))
    )
    memoryview_provider = OpenAISpeechProvider(
        client=FakeOpenAIClient(
            speech=FakeSpeechClient(FakeSpeechResponse(memoryview(b"RIFFmemory")))
        )
    )

    assert bytearray_provider.synthesize("Meeting joined.").data == b"RIFFarray"
    assert memoryview_provider.synthesize("Meeting joined.").data == b"RIFFmemory"


def test_speech_rejects_response_without_binary_content(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    speech = FakeSpeechClient(response=object())
    provider = OpenAISpeechProvider(client=FakeOpenAIClient(speech=speech))

    with pytest.raises(TypeError, match="bytes"):
        provider.synthesize("Meeting joined.")


def test_speech_rejects_blank_text_before_api_call(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    speech = FakeSpeechClient()
    provider = OpenAISpeechProvider(client=FakeOpenAIClient(speech=speech))

    with pytest.raises(ValueError, match="Speech text"):
        provider.synthesize(" \t\n ")

    assert speech.calls == []


def test_speech_validates_constructor_inputs(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = FakeOpenAIClient()

    with pytest.raises(ValueError, match="speech model"):
        OpenAISpeechProvider(client=client, model=" ")

    monkeypatch.setenv("AI_PRESENTER_OPENAI_TTS_MODEL", " ")
    with pytest.raises(ValueError, match="speech model"):
        OpenAISpeechProvider(client=client)
    monkeypatch.delenv("AI_PRESENTER_OPENAI_TTS_MODEL", raising=False)

    with pytest.raises(ValueError, match="speech voice"):
        OpenAISpeechProvider(client=client, voice="\t")


def test_speech_requires_api_key_when_creating_real_client(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        OpenAISpeechProvider()


def test_openai_providers_can_be_registered_and_resolved(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    narration = OpenAINarrationProvider(client=FakeOpenAIClient(), model="gpt-4.1")
    speech = OpenAISpeechProvider(client=FakeOpenAIClient())
    registry = ProviderRegistry()

    registry.register_narration(" openai ", narration)
    registry.register_speech("openai-tts", speech)

    assert registry.narration("openai") is narration
    assert registry.speech(" openai-tts ") is speech

    with pytest.raises(ProviderRegistrationError, match="openai-tts"):
        registry.register_speech("openai-tts", speech)

    with pytest.raises(ProviderLookupError, match="missing"):
        registry.narration("missing")

    with pytest.raises(ProviderLookupError, match="blank"):
        registry.speech(" ")
