from pathlib import Path

import pytest

from ai_presenter.config.loader import load_profile
from ai_presenter.packages.models import DemoStepNarration
from ai_presenter.runtime import voice
from ai_presenter.runtime.voice import PresenterVoiceSettings
from ai_presenter.runtime.voice import render_narration_text
from ai_presenter.runtime.voice import render_presenter_text
from ai_presenter.runtime.voice import render_voice_instruction
from ai_presenter.runtime.voice import resolve_speech_provider_name
from ai_presenter.runtime.voice import sapi_rate_for_voice
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


def test_voice_instruction_renders_japanese_style() -> None:
    settings = PresenterVoiceSettings(language="ja-JP", tone="friendly")

    instruction = render_voice_instruction(settings)

    assert settings.language == "ja"
    assert "Japanese" in instruction
    assert "warm" in instruction


def test_voice_settings_normalize_language_aliases() -> None:
    assert PresenterVoiceSettings(language="zh-CN").language == "zh"
    assert PresenterVoiceSettings(language="zh-Hans").language == "zh"
    assert PresenterVoiceSettings(language="Chinese").language == "zh"
    assert PresenterVoiceSettings(language="中文").language == "zh"
    assert PresenterVoiceSettings(language="English").language == "en"
    assert PresenterVoiceSettings(language="en-US").language == "en"
    assert PresenterVoiceSettings(language="Japanese").language == "ja"
    assert PresenterVoiceSettings(language="\u65e5\u672c\u8a9e").language == "ja"


def test_presenter_language_aliases_are_public_and_canonical() -> None:
    assert voice.presenter_language_aliases("zh-CN") == (
        "zh",
        "zh-cn",
        "zh-hans",
        "zh-tw",
        "zh-hant",
        "chinese",
        "中文",
    )


def test_presenter_japanese_language_aliases_are_public_and_canonical() -> None:
    assert voice.presenter_language_aliases("ja-JP") == (
        "ja",
        "ja-jp",
        "japanese",
        "\u65e5\u672c\u8a9e",
    )


def test_voice_settings_normalize_expanded_tones() -> None:
    assert PresenterVoiceSettings(tone="friendly").tone == "friendly"
    assert PresenterVoiceSettings(tone="warm").tone == "friendly"
    assert PresenterVoiceSettings(tone="mentor").tone == "coach"
    assert PresenterVoiceSettings(tone="structured").tone == "formal"
    assert PresenterVoiceSettings(tone="executive").tone == "formal"
    assert PresenterVoiceSettings(tone="briefing").tone == "formal"
    assert PresenterVoiceSettings(tone="boardroom").tone == "formal"
    assert PresenterVoiceSettings(tone="support").tone == "support"
    assert PresenterVoiceSettings(tone="calm").tone == "support"
    assert PresenterVoiceSettings(tone="steady").tone == "support"
    assert PresenterVoiceSettings(tone="reassuring").tone == "support"
    assert PresenterVoiceSettings(tone="careful").tone == "careful"
    assert PresenterVoiceSettings(tone="safety").tone == "careful"
    assert PresenterVoiceSettings(tone="safe").tone == "careful"
    assert PresenterVoiceSettings(tone="privacy").tone == "careful"
    assert PresenterVoiceSettings(tone="guarded").tone == "careful"
    assert PresenterVoiceSettings(tone="compliance").tone == "careful"


def test_presenter_tone_aliases_and_description_are_public() -> None:
    assert voice.presenter_tone_aliases("mentor") == ("coach", "coaching", "mentor")
    assert "step-by-step" in voice.presenter_tone_description("coach")
    assert voice.presenter_tone_aliases("executive") == (
        "formal",
        "structured",
        "executive",
        "briefing",
        "boardroom",
    )
    assert "polished" in voice.presenter_tone_description("executive")
    assert voice.presenter_tone_aliases("calm") == (
        "support",
        "supportive",
        "helpdesk",
        "troubleshooting",
        "recovery",
        "calm",
        "steady",
        "reassuring",
    )
    assert "recovery-focused" in voice.presenter_tone_description("support")
    assert voice.presenter_tone_aliases("privacy") == (
        "careful",
        "safety",
        "safe",
        "privacy",
        "guarded",
        "compliance",
    )
    assert "privacy-aware" in voice.presenter_tone_description("careful")


def test_voice_settings_reject_unknown_language_and_tone() -> None:
    with pytest.raises(ValueError, match="Unsupported presenter language"):
        PresenterVoiceSettings(language="es")
    with pytest.raises(ValueError, match="Unsupported presenter tone"):
        PresenterVoiceSettings(tone="shouty")


def test_voice_instruction_describes_expanded_tones() -> None:
    assert "warm" in render_voice_instruction(PresenterVoiceSettings(tone="friendly"))
    assert "step-by-step" in render_voice_instruction(PresenterVoiceSettings(tone="coach"))
    assert "formal" in render_voice_instruction(PresenterVoiceSettings(tone="formal"))
    assert "recovery-focused" in render_voice_instruction(PresenterVoiceSettings(tone="support"))
    assert "boundary-focused" in render_voice_instruction(PresenterVoiceSettings(tone="privacy"))


def test_render_presenter_text_applies_expanded_english_tones() -> None:
    assert render_presenter_text(
        "Open Chat.",
        PresenterVoiceSettings(tone="friendly"),
    ).startswith("Happy to help.")
    assert render_presenter_text(
        "Open Chat.",
        PresenterVoiceSettings(tone="coach"),
    ).startswith("Let's walk through it.")
    assert render_presenter_text(
        "Open Chat.",
        PresenterVoiceSettings(tone="formal"),
    ).startswith("Certainly.")
    assert render_presenter_text(
        "Open audio settings.",
        PresenterVoiceSettings(tone="support"),
    ).startswith("Let's troubleshoot this.")
    assert render_presenter_text(
        "Recording requires consent.",
        PresenterVoiceSettings(tone="privacy"),
    ).startswith("Safety note.")


def test_render_presenter_text_applies_chinese_careful_tone_without_english_prefix() -> None:
    rendered = render_presenter_text(
        "Recording requires consent.",
        PresenterVoiceSettings(language="zh", tone="safety"),
    )

    assert rendered.startswith("\u6211\u4f1a\u8c28\u614e\u8bf4\u660e\u3002")
    assert "Safety note" not in rendered


def test_render_presenter_text_keeps_japanese_text_without_english_prefix() -> None:
    rendered = render_presenter_text(
        "\u73fe\u5728\u306e\u30a2\u30d7\u30ea\u3067\u4e00\u81f4\u3059\u308b\u64cd\u4f5c\u304c\u898b\u3064\u304b\u308a\u307e\u305b\u3093\u3002",
        PresenterVoiceSettings(language="ja", tone="friendly"),
    )

    assert rendered.startswith("\u73fe\u5728\u306e\u30a2\u30d7\u30ea")
    assert "Happy to help" not in rendered


def test_render_presenter_text_keeps_existing_chinese_concise_behavior() -> None:
    rendered = render_presenter_text(
        "Chat opens the panel. Settings stays available.",
        PresenterVoiceSettings(language="zh", tone="concise"),
    )

    assert "stays available" in rendered


def test_language_aliases_use_existing_provider_routing() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-piper-speaker.yaml"))

    assert resolve_speech_provider_name(profile, PresenterVoiceSettings(language="zh-CN")) == (
        "windows-sapi-zh"
    )


def test_language_alias_prefers_canonical_localized_narration_key() -> None:
    narration = DemoStepNarration(
        text="Share opens the picker for your screen.",
        localizedText={"zh": "接下来，看共享屏幕。"},
    )

    rendered = render_narration_text(
        narration,
        PresenterVoiceSettings(language="zh-CN", tone="professional"),
    )

    assert rendered == "接下来，看共享屏幕。"


def test_voice_validation_allows_chinese_windows_sapi_profile() -> None:
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))
    profile.providers.speech = "windows-sapi-zh"

    validate_profile_voice(profile, PresenterVoiceSettings(language="zh"))


def test_voice_validation_allows_japanese_openai_profile() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-openai.example.yaml"))

    validate_profile_voice(profile, PresenterVoiceSettings(language="ja-JP"))


def test_voice_validation_rejects_japanese_local_sapi_profile() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))

    with pytest.raises(ValueError) as exc_info:
        validate_profile_voice(profile, PresenterVoiceSettings(language="ja"))

    message = str(exc_info.value)
    assert "Japanese / Professional" in message
    assert "speech provider windows-sapi-en" in message
    assert "openai" in message


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


def test_voice_validation_error_includes_profile_provider_and_voice() -> None:
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))

    with pytest.raises(ValueError) as exc_info:
        validate_profile_voice(
            profile,
            PresenterVoiceSettings(language="zh-CN", tone="friendly"),
        )

    message = str(exc_info.value)
    assert "ringcentral-video" in message
    assert "speech provider fake" in message
    assert "Chinese / Friendly" in message
    assert "openai or windows-sapi-zh" in message


def test_voice_validation_rejects_chinese_with_english_only_sapi_profile() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))

    validate_profile_voice(profile, PresenterVoiceSettings(language="zh"))

    assert resolve_speech_provider_name(profile, PresenterVoiceSettings(language="zh")) == (
        "windows-sapi-zh"
    )


def test_render_narration_text_prefers_localized_chinese_script() -> None:
    narration = DemoStepNarration(
        text="Share opens the picker for your screen.",
        localizedText={"zh": "接下来，看共享屏幕。这里会打开屏幕和窗口选择器。"},
    )

    rendered = render_narration_text(
        narration,
        PresenterVoiceSettings(language="zh", tone="professional"),
    )

    assert rendered == "接下来，看共享屏幕。这里会打开屏幕和窗口选择器。"


def test_render_narration_text_concise_chinese_uses_first_sentence() -> None:
    narration = DemoStepNarration(
        text="Share opens the picker for your screen.",
        localizedText={"zh": "接下来，看共享屏幕。这里会打开屏幕和窗口选择器。"},
    )

    rendered = render_narration_text(
        narration,
        PresenterVoiceSettings(language="zh", tone="concise"),
    )

    assert rendered == "接下来，看共享屏幕。"


def test_sapi_rate_for_voice_maps_chinese_tones_to_practical_rates() -> None:
    assert sapi_rate_for_voice(PresenterVoiceSettings(language="zh", tone="professional")) == 0
    assert sapi_rate_for_voice(PresenterVoiceSettings(language="zh", tone="conversational")) == -1
    assert sapi_rate_for_voice(PresenterVoiceSettings(language="zh", tone="concise")) == 1
    assert sapi_rate_for_voice(PresenterVoiceSettings(language="zh", tone="friendly")) == -1
    assert sapi_rate_for_voice(PresenterVoiceSettings(language="zh", tone="coach")) == 0
    assert sapi_rate_for_voice(PresenterVoiceSettings(language="zh", tone="formal")) == 0
    assert sapi_rate_for_voice(PresenterVoiceSettings(language="zh", tone="support")) == -1
    assert sapi_rate_for_voice(PresenterVoiceSettings(language="zh", tone="careful")) == 0
