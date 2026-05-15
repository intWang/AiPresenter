from dataclasses import dataclass

from ai_presenter.packages.models import MaterialPackage, OperationEntrypoint
from ai_presenter.runtime.voice import PresenterVoiceSettings

_RISKY_ENTRYPOINT_WORDS = {"leave", "recording", "record", "share", "delete", "send", "pay"}


@dataclass(frozen=True)
class QuestionResponse:
    answer_text: str
    entrypoint_id: str | None = None
    can_operate: bool = False


def answer_question(
    *,
    package: MaterialPackage,
    question: str,
    voice: PresenterVoiceSettings,
) -> QuestionResponse:
    normalized = question.casefold().strip()
    qa_match = _match_qa(package, normalized)
    if qa_match is not None:
        entrypoint_id = qa_match.related_entrypoint_ids[0] if qa_match.related_entrypoint_ids else None
        return QuestionResponse(
            answer_text=_render_text(qa_match.answer, voice),
            entrypoint_id=entrypoint_id,
            can_operate=_can_operate(package, entrypoint_id),
        )

    entrypoint = _match_entrypoint(package, normalized)
    if entrypoint is None:
        return QuestionResponse(
            answer_text=_render_text("I could not find a matching control in the active app context.", voice)
        )
    return QuestionResponse(
        answer_text=_render_entrypoint_answer(entrypoint, voice),
        entrypoint_id=entrypoint.id,
        can_operate=_can_operate(package, entrypoint.id),
    )


def _match_qa(package: MaterialPackage, normalized_question: str):
    for item in package.qa:
        if normalized_question and normalized_question in item.question.casefold():
            return item
        if item.question.casefold() in normalized_question:
            return item
    return None


def _match_entrypoint(package: MaterialPackage, normalized_question: str) -> OperationEntrypoint | None:
    best: OperationEntrypoint | None = None
    for entrypoint in package.operation_entrypoints:
        haystack = " ".join([entrypoint.id, entrypoint.title, entrypoint.area, entrypoint.purpose]).casefold()
        if normalized_question and normalized_question in haystack:
            return entrypoint
        for token in normalized_question.split():
            if len(token) >= 3 and token in haystack:
                best = entrypoint
    return best


def _render_entrypoint_answer(entrypoint: OperationEntrypoint, voice: PresenterVoiceSettings) -> str:
    base = f"{entrypoint.title}: {entrypoint.purpose}"
    return _render_text(base, voice)


def _render_text(text: str, voice: PresenterVoiceSettings) -> str:
    if voice.language == "zh":
        return _render_chinese(text, voice)
    if voice.tone == "conversational":
        return f"Sure. {text}"
    if voice.tone == "concise":
        return text.split(".")[0].strip() + "."
    return text


def _render_chinese(text: str, voice: PresenterVoiceSettings) -> str:
    replacements = {
        "Chat": "聊天",
        "chat": "聊天",
        "Invite": "邀请",
        "Settings": "设置",
        "Leave": "离开会议",
        "Background": "背景",
    }
    rendered = text
    for source, target in replacements.items():
        rendered = rendered.replace(source, target)
    prefix = "我来说明一下。" if voice.tone == "conversational" else ""
    return f"{prefix}{rendered}"


def _can_operate(package: MaterialPackage, entrypoint_id: str | None) -> bool:
    if entrypoint_id is None:
        return False
    entrypoint = package.entrypoint_by_id(entrypoint_id)
    if not entrypoint.open_steps:
        return False
    lowered = " ".join([entrypoint.id, entrypoint.title, entrypoint.purpose]).casefold()
    return not any(word in lowered for word in _RISKY_ENTRYPOINT_WORDS)
