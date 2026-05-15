from dataclasses import dataclass
from typing import Literal

from ai_presenter.config.models import AppProfile
from ai_presenter.packages.models import DemoStepNarration

PresenterLanguage = Literal["en", "zh"]
PresenterTone = Literal["professional", "conversational", "concise"]

_TONE_DESCRIPTIONS: dict[PresenterTone, str] = {
    "professional": "professional, structured, and product-specialist",
    "conversational": "natural, conversational, warm, and easy to follow",
    "concise": "concise, brisk, and transition-focused",
}
_CHINESE_REPLACEMENTS = {
    "Chat": "聊天",
    "chat": "聊天",
    "Invite": "邀请",
    "Settings": "设置",
    "Leave": "离开会议",
    "Background": "背景",
}
_LOCAL_SAPI_FALLBACK_SPEECH = frozenset(
    {
        "piper",
        "windows-sapi",
        "windows-sapi-en",
        "windows-sapi-zh",
    }
)


@dataclass(frozen=True)
class PresenterVoiceSettings:
    language: PresenterLanguage = "en"
    tone: PresenterTone = "professional"


def render_voice_instruction(settings: PresenterVoiceSettings) -> str:
    language = "Chinese" if settings.language == "zh" else "English"
    tone = _TONE_DESCRIPTIONS[settings.tone]
    return f"Speak in {language}. Use a {tone} tone."


def render_presenter_text(text: str, settings: PresenterVoiceSettings) -> str:
    if settings.language == "zh":
        return _render_chinese(text, settings)
    if settings.tone == "conversational":
        return f"Sure. {text}"
    if settings.tone == "concise":
        return _first_sentence(text)
    return text


def render_narration_text(narration: DemoStepNarration, settings: PresenterVoiceSettings) -> str:
    localized = narration.localized_text.get(settings.language)
    if localized is not None and localized.strip():
        return _apply_tone_to_localized_text(localized.strip(), settings)
    return render_presenter_text(narration.text, settings)


def validate_profile_voice(profile: AppProfile, settings: PresenterVoiceSettings) -> None:
    speech = resolve_speech_provider_name(profile, settings)
    if settings.language == "zh" and speech not in {"openai", "windows-sapi-zh"}:
        raise ValueError("Chinese voice output requires speech provider openai or windows-sapi-zh.")
    if settings.language == "en" and speech == "windows-sapi-zh":
        raise ValueError(
            "English voice output requires speech provider openai, fake, piper, "
            "windows-sapi, or windows-sapi-en."
        )


def resolve_speech_provider_name(profile: AppProfile, settings: PresenterVoiceSettings) -> str:
    speech = profile.providers.speech
    if settings.language == "zh" and speech in _LOCAL_SAPI_FALLBACK_SPEECH:
        return "windows-sapi-zh"
    if settings.language == "en" and speech == "windows-sapi-zh":
        return "windows-sapi-en"
    return speech


def sapi_rate_for_voice(settings: PresenterVoiceSettings) -> int:
    if settings.language == "zh":
        if settings.tone == "conversational":
            return -1
        if settings.tone == "concise":
            return 1
    return 0


def _render_chinese(text: str, settings: PresenterVoiceSettings) -> str:
    rendered = text
    for source, target in _CHINESE_REPLACEMENTS.items():
        rendered = rendered.replace(source, target)
    prefix = "我来说明一下。" if settings.tone == "conversational" else ""
    return f"{prefix}{rendered}"


def _apply_tone_to_localized_text(text: str, settings: PresenterVoiceSettings) -> str:
    if settings.tone == "concise":
        return _first_sentence(text)
    return text


def _first_sentence(text: str) -> str:
    separators = (".", "。", "!", "！", "?", "？")
    first_end = min((index for sep in separators if (index := text.find(sep)) >= 0), default=-1)
    if first_end >= 0:
        return text[: first_end + 1].strip()
    first = text.split(".")[0].strip()
    if not first:
        return text
    return f"{first}."
