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


@dataclass(frozen=True)
class PresenterVoiceSettings:
    language: PresenterLanguage = "en"
    tone: PresenterTone = "professional"


def render_voice_instruction(settings: PresenterVoiceSettings) -> str:
    language = "Chinese" if settings.language == "zh" else "English"
    tone = _TONE_DESCRIPTIONS[settings.tone]
    return f"Speak in {language}. Use a {tone} tone."


def validate_profile_voice(profile: AppProfile, settings: PresenterVoiceSettings) -> None:
    speech = profile.providers.speech
    if settings.language == "zh" and speech not in {"openai", "windows-sapi-zh"}:
        raise ValueError("Chinese voice output requires speech provider openai or windows-sapi-zh.")
    if settings.language == "en" and speech == "windows-sapi-zh":
        raise ValueError("English voice output requires speech provider openai, fake, windows-sapi, or windows-sapi-en.")
