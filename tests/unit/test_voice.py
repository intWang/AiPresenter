from pathlib import Path

from ai_presenter.config.loader import load_profile
from ai_presenter.runtime.voice import PresenterVoiceSettings
from ai_presenter.runtime.voice import render_voice_instruction
from ai_presenter.runtime.voice import resolve_speech_provider_name
from ai_presenter.runtime.voice import validate_profile_voice


def test_default_voice_settings_are_english_professional() -> None:
    settings = PresenterVoiceSettings()

    assert settings.language == "en"
    assert settings.tone == "professional"


def test_voice_instruction_renders_chinese_conversational_style() -> None:
    settings = PresenterVoiceSettings(language="zh", tone="conversational")

    instruction = render_voice_instruction(settings)

    assert "Chinese" in instruction
    assert "natural" in instruction
    assert "conversational" in instruction


def test_voice_validation_allows_chinese_windows_sapi_profile() -> None:
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))
    profile.providers.speech = "windows-sapi-zh"

    validate_profile_voice(profile, PresenterVoiceSettings(language="zh"))


def test_voice_validation_allows_chinese_piper_profile_with_sapi_fallback() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-piper-speaker.yaml"))

    validate_profile_voice(profile, PresenterVoiceSettings(language="zh"))

    assert resolve_speech_provider_name(profile, PresenterVoiceSettings(language="zh")) == (
        "windows-sapi-zh"
    )
    assert resolve_speech_provider_name(profile, PresenterVoiceSettings(language="en")) == "piper"


def test_voice_validation_routes_english_from_chinese_sapi_to_english_sapi() -> None:
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))
    profile.providers.speech = "windows-sapi-zh"

    validate_profile_voice(profile, PresenterVoiceSettings(language="en"))

    assert resolve_speech_provider_name(profile, PresenterVoiceSettings(language="en")) == (
        "windows-sapi-en"
    )


def test_voice_validation_rejects_chinese_with_english_only_sapi_profile() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))

    validate_profile_voice(profile, PresenterVoiceSettings(language="zh"))

    assert resolve_speech_provider_name(profile, PresenterVoiceSettings(language="zh")) == (
        "windows-sapi-zh"
    )
