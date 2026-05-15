from dataclasses import dataclass
from typing import Literal

from ai_presenter.config.models import AppProfile

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


def validate_profile_voice(profile: AppProfile, settings: PresenterVoiceSettings) -> None:
    speech = profile.providers.speech
    if settings.language == "zh" and speech not in {"openai", "windows-sapi-zh"}:
        raise ValueError("Chinese voice output requires speech provider openai or windows-sapi-zh.")
    if settings.language == "en" and speech == "windows-sapi-zh":
        raise ValueError("English voice output requires speech provider openai, fake, windows-sapi, or windows-sapi-en.")


def _render_chinese(text: str, settings: PresenterVoiceSettings) -> str:
    rendered = text
    for source, target in _CHINESE_REPLACEMENTS.items():
        rendered = rendered.replace(source, target)
    prefix = "我来说明一下。" if settings.tone == "conversational" else ""
    return f"{prefix}{rendered}"


def _first_sentence(text: str) -> str:
    first = text.split(".")[0].strip()
    if not first:
        return text
    return f"{first}."
