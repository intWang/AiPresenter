from dataclasses import dataclass
from typing import Literal

from ai_presenter.config.models import AppProfile
from ai_presenter.packages.models import DemoStepNarration

PresenterLanguage = Literal["en", "zh", "ja"]
PresenterTone = Literal[
    "professional",
    "conversational",
    "concise",
    "friendly",
    "coach",
    "formal",
    "support",
    "careful",
]
PRESENTER_LANGUAGE_CHOICES: tuple[tuple[str, PresenterLanguage], ...] = (
    ("English", "en"),
    ("Chinese", "zh"),
    ("Japanese", "ja"),
)
PRESENTER_TONE_CHOICES: tuple[tuple[str, PresenterTone], ...] = (
    ("Professional", "professional"),
    ("Conversational", "conversational"),
    ("Concise", "concise"),
    ("Friendly", "friendly"),
    ("Coach", "coach"),
    ("Formal", "formal"),
    ("Support", "support"),
    ("Careful", "careful"),
)

_TONE_DESCRIPTIONS: dict[PresenterTone, str] = {
    "professional": "professional, structured, and product-specialist",
    "conversational": "natural, conversational, warm, and easy to follow",
    "concise": "concise, brisk, and transition-focused",
    "friendly": "friendly, warm, reassuring, and approachable",
    "coach": "coach-like, step-by-step, and encouraging",
    "formal": "formal, polished, and restrained",
    "support": "calm, diagnostic, recovery-focused, and reassuring",
    "careful": "careful, privacy-aware, concise, and boundary-focused",
}
_LANGUAGE_LABELS: dict[PresenterLanguage, str] = {
    "en": "English",
    "zh": "Chinese",
    "ja": "Japanese",
}
_TONE_LABELS: dict[PresenterTone, str] = {
    "professional": "Professional",
    "conversational": "Conversational",
    "concise": "Concise",
    "friendly": "Friendly",
    "coach": "Coach",
    "formal": "Formal",
    "support": "Support",
    "careful": "Careful",
}
_LANGUAGE_ALIASES: dict[str, PresenterLanguage] = {
    "en": "en",
    "en-us": "en",
    "en-gb": "en",
    "english": "en",
    "zh": "zh",
    "zh-cn": "zh",
    "zh-hans": "zh",
    "zh-tw": "zh",
    "zh-hant": "zh",
    "chinese": "zh",
    "ja": "ja",
    "ja-jp": "ja",
    "japanese": "ja",
    "\u65e5\u672c\u8a9e": "ja",
    "中文": "zh",
}
_TONE_ALIASES: dict[str, PresenterTone] = {
    "professional": "professional",
    "pro": "professional",
    "conversational": "conversational",
    "conversation": "conversational",
    "casual": "conversational",
    "concise": "concise",
    "brief": "concise",
    "friendly": "friendly",
    "warm": "friendly",
    "coach": "coach",
    "coaching": "coach",
    "mentor": "coach",
    "formal": "formal",
    "structured": "formal",
    "support": "support",
    "supportive": "support",
    "helpdesk": "support",
    "troubleshooting": "support",
    "recovery": "support",
    "calm": "support",
    "steady": "support",
    "reassuring": "support",
    "careful": "careful",
    "safety": "careful",
    "safe": "careful",
    "privacy": "careful",
    "guarded": "careful",
    "compliance": "careful",
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


@dataclass(frozen=True, init=False)
class PresenterVoiceSettings:
    language: PresenterLanguage
    tone: PresenterTone

    def __init__(self, language: str = "en", tone: str = "professional") -> None:
        object.__setattr__(self, "language", normalize_presenter_language(language))
        object.__setattr__(self, "tone", normalize_presenter_tone(tone))


def normalize_presenter_language(language: str) -> PresenterLanguage:
    key = _normalize_voice_key(language)
    try:
        return _LANGUAGE_ALIASES[key]
    except KeyError:
        raise ValueError(f"Unsupported presenter language: {language}") from None


def normalize_presenter_tone(tone: str) -> PresenterTone:
    key = _normalize_voice_key(tone)
    try:
        return _TONE_ALIASES[key]
    except KeyError:
        raise ValueError(f"Unsupported presenter tone: {tone}") from None


def language_label(language: str) -> str:
    return _LANGUAGE_LABELS[normalize_presenter_language(language)]


def tone_label(tone: str) -> str:
    return _TONE_LABELS[normalize_presenter_tone(tone)]


def presenter_language_aliases(language: str) -> tuple[str, ...]:
    canonical = normalize_presenter_language(language)
    return tuple(alias for alias, value in _LANGUAGE_ALIASES.items() if value == canonical)


def presenter_tone_aliases(tone: str) -> tuple[str, ...]:
    canonical = normalize_presenter_tone(tone)
    return tuple(alias for alias, value in _TONE_ALIASES.items() if value == canonical)


def presenter_tone_description(tone: str) -> str:
    return _TONE_DESCRIPTIONS[normalize_presenter_tone(tone)]


def render_voice_instruction(settings: PresenterVoiceSettings) -> str:
    language = language_label(settings.language)
    tone = _TONE_DESCRIPTIONS[settings.tone]
    return f"Speak in {language}. Use a {tone} tone."


def render_presenter_text(text: str, settings: PresenterVoiceSettings) -> str:
    if settings.language == "zh":
        return _render_chinese(text, settings)
    if settings.language == "ja":
        return _apply_tone_to_localized_text(text, settings)
    if settings.tone == "conversational":
        return f"Sure. {text}"
    if settings.tone == "concise":
        return _first_sentence(text)
    if settings.tone == "friendly":
        return f"Happy to help. {text}"
    if settings.tone == "coach":
        return f"Let's walk through it. {text}"
    if settings.tone == "formal":
        return f"Certainly. {text}"
    if settings.tone == "support":
        return f"Let's troubleshoot this. {text}"
    if settings.tone == "careful":
        return f"Safety note. {text}"
    return text


def render_narration_text(narration: DemoStepNarration, settings: PresenterVoiceSettings) -> str:
    localized = narration.localized_text.get(settings.language)
    if localized is not None and localized.strip():
        return _apply_tone_to_localized_text(localized.strip(), settings)
    return render_presenter_text(narration.text, settings)


def validate_profile_voice(profile: AppProfile, settings: PresenterVoiceSettings) -> None:
    speech = resolve_speech_provider_name(profile, settings)
    context = _profile_voice_context(profile, settings)
    if settings.language == "zh" and speech not in {"openai", "windows-sapi-zh"}:
        raise ValueError(
            f"{context} Chinese voice output requires speech provider openai or windows-sapi-zh."
        )
    if settings.language == "ja" and speech != "openai":
        raise ValueError(
            f"{context} Japanese voice output requires speech provider openai."
        )
    if settings.language == "en" and speech == "windows-sapi-zh":
        raise ValueError(
            f"{context} English voice output requires speech provider openai, fake, piper, "
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
        if settings.tone in {"conversational", "friendly", "support"}:
            return -1
        if settings.tone == "concise":
            return 1
    return 0


def _profile_voice_context(profile: AppProfile, settings: PresenterVoiceSettings) -> str:
    voice = f"{language_label(settings.language)} / {tone_label(settings.tone)}"
    return f"Profile {profile.id} with speech provider {profile.providers.speech} cannot use {voice}."


def _render_chinese(text: str, settings: PresenterVoiceSettings) -> str:
    rendered = text
    for source, target in _CHINESE_REPLACEMENTS.items():
        rendered = rendered.replace(source, target)
    prefixes = {
        "conversational": "我来说明一下。",
        "friendly": "可以的，我来说明一下。",
        "coach": "我们一步步来看。",
        "formal": "请允许我说明。",
        "careful": "我会谨慎说明。",
    }
    prefix = prefixes.get(settings.tone, "")
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


def _normalize_voice_key(value: str) -> str:
    return value.strip().casefold().replace("_", "-")
