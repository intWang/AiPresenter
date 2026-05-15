from dataclasses import dataclass
import re

from ai_presenter.packages.models import MaterialPackage, OperationEntrypoint, QuestionAnswer
from ai_presenter.runtime.voice import PresenterVoiceSettings, render_presenter_text

_RISKY_ENTRYPOINT_WORDS = {
    "delete",
    "end",
    "invite",
    "leave",
    "lock",
    "lower hand",
    "mute",
    "pay",
    "raise hand",
    "reaction",
    "record",
    "recording",
    "send",
    "share",
    "start",
    "stop",
    "submit",
    "toggle",
    "transfer",
    "turn",
    "unlock",
    "unmute",
}
_STOPWORDS = {
    "a",
    "can",
    "control",
    "could",
    "do",
    "how",
    "i",
    "in",
    "meeting",
    "open",
    "please",
    "show",
    "the",
    "to",
    "where",
}
_GENERIC_ENTRYPOINT_TOKENS = {"people"}
_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


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


def _match_qa(package: MaterialPackage, normalized_question: str) -> QuestionAnswer | None:
    for item in package.qa:
        if normalized_question and normalized_question in item.question.casefold():
            return item
        if item.question.casefold() in normalized_question:
            return item
    query_tokens = _meaningful_tokens(normalized_question)
    if not query_tokens:
        return None

    best_match: QuestionAnswer | None = None
    best_score = 0
    for item in package.qa:
        question_tokens = _meaningful_tokens(item.question)
        overlap = query_tokens & question_tokens
        if not overlap:
            continue
        score = len(overlap)
        if score > best_score:
            best_match = item
            best_score = score
    if best_score >= 2:
        return best_match
    return None


def _match_entrypoint(package: MaterialPackage, normalized_question: str) -> OperationEntrypoint | None:
    query_tokens = _meaningful_tokens(normalized_question)
    if not query_tokens:
        return None

    best_entrypoint: OperationEntrypoint | None = None
    best_score = 0
    for entrypoint in package.operation_entrypoints:
        score = _score_entrypoint_match(entrypoint, query_tokens)
        if score > best_score:
            best_entrypoint = entrypoint
            best_score = score
    return best_entrypoint


def _score_entrypoint_match(entrypoint: OperationEntrypoint, query_tokens: set[str]) -> int:
    title_tokens = _field_tokens(entrypoint.title)
    id_tokens = _field_tokens(entrypoint.id)
    area_tokens = _field_tokens(entrypoint.area)
    purpose_tokens = _field_tokens(entrypoint.purpose)

    title_or_id_matches = query_tokens & (title_tokens | id_tokens)
    area_matches = query_tokens & area_tokens
    purpose_matches = query_tokens & purpose_tokens
    all_matches = title_or_id_matches | area_matches | purpose_matches
    if not all_matches or all_matches <= _GENERIC_ENTRYPOINT_TOKENS:
        return 0

    score = 0
    score += len(query_tokens & id_tokens) * 6
    score += len(query_tokens & title_tokens) * 5
    score += len(area_matches) * 2
    score += len(purpose_matches)
    if query_tokens <= (title_tokens | id_tokens):
        score += 3
    return score


def _meaningful_tokens(text: str) -> set[str]:
    return {token for token in _field_tokens(text) if token not in _STOPWORDS and len(token) >= 3}


def _field_tokens(text: str) -> set[str]:
    return set(_TOKEN_PATTERN.findall(text.casefold()))


def _render_entrypoint_answer(entrypoint: OperationEntrypoint, voice: PresenterVoiceSettings) -> str:
    base = f"{entrypoint.title}: {entrypoint.purpose}"
    return _render_text(base, voice)


def _render_text(text: str, voice: PresenterVoiceSettings) -> str:
    return render_presenter_text(text, voice)


def _can_operate(package: MaterialPackage, entrypoint_id: str | None) -> bool:
    if entrypoint_id is None:
        return False
    entrypoint = package.entrypoint_by_id(entrypoint_id)
    if not entrypoint.open_steps:
        return False
    lowered = " ".join([entrypoint.id, entrypoint.title, entrypoint.purpose]).casefold()
    return not any(word in lowered for word in _RISKY_ENTRYPOINT_WORDS)
