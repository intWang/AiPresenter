from dataclasses import dataclass
import logging
from time import perf_counter

from ai_presenter.packages.models import EntrypointMatchCandidate
from ai_presenter.packages.models import MaterialPackage
from ai_presenter.packages.models import OperationEntrypoint
from ai_presenter.packages.models import QuestionAnswer
from ai_presenter.packages.models import match_field_tokens
from ai_presenter.packages.models import match_meaningful_tokens
from ai_presenter.runtime.logging import elapsed_ms, log_timed_event
from ai_presenter.runtime.voice import PresenterVoiceSettings, render_presenter_text

logger = logging.getLogger("ai_presenter.runtime.questions")

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
_GENERIC_ENTRYPOINT_TOKENS = {"people"}
_ENTRYPOINT_ALIASES: dict[str, tuple[str, ...]] = {
    "ringcentral.video.toolbar.chat": (
        "聊天",
        "聊天室",
        "消息",
    ),
    "ringcentral.video.toolbar.participants": (
        "参会者",
        "参与者",
        "成员",
        "人员",
        "谁在会议",
    ),
    "ringcentral.video.toolbar.invite": (
        "邀请",
        "邀请别人",
        "拉人",
        "加人",
    ),
    "ringcentral.video.toolbar.share": (
        "共享屏幕",
        "分享屏幕",
        "屏幕共享",
        "共享",
    ),
    "ringcentral.video.toolbar.audio": (
        "麦克风",
        "静音",
        "取消静音",
        "声音",
    ),
    "ringcentral.video.toolbar.video": (
        "摄像头",
        "相机",
        "视频开关",
        "开启视频",
    ),
    "ringcentral.video.more.settings": (
        "设置",
        "会议设置",
    ),
    "ringcentral.video.settings.background": (
        "背景",
        "虚拟背景",
        "模糊背景",
        "设置背景",
    ),
    "ringcentral.video.more.recording": (
        "录制",
        "录像",
        "记录会议",
    ),
    "ringcentral.video.more.notes": (
        "笔记",
        "转录",
        "字幕记录",
    ),
    "ringcentral.video.toolbar.react": (
        "回应",
        "表情",
        "反应",
        "点赞",
    ),
    "ringcentral.video.toolbar.raise-hand": (
        "举手",
        "举手发言",
    ),
    "ringcentral.video.top.network-quality": (
        "网络",
        "网络质量",
        "连接质量",
    ),
    "ringcentral.video.top.meeting-info": (
        "会议信息",
        "会议号",
        "会议链接",
    ),
    "ringcentral.video.toolbar.leave": (
        "离开会议",
        "退出会议",
        "结束会议",
    ),
}


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
    start = perf_counter()
    try:
        response = _answer_question(package=package, question=question, voice=voice)
    except Exception:
        log_timed_event(
            logger,
            "question_answered",
            duration_ms=elapsed_ms(start, perf_counter()),
            status="error",
            package=package.app_id,
            language=voice.language,
            tone=voice.tone,
        )
        raise

    log_timed_event(
        logger,
        "question_answered",
        duration_ms=elapsed_ms(start, perf_counter()),
        status="ok",
        package=package.app_id,
        language=voice.language,
        tone=voice.tone,
        entrypoint=response.entrypoint_id,
        can_operate=response.can_operate,
    )
    return response


def _answer_question(
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
            answer_text=_qa_answer_text(qa_match, voice),
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
    for candidate in package.qa_question_candidates:
        if normalized_question and normalized_question in candidate.normalized_question:
            return candidate.item
        if candidate.normalized_question in normalized_question:
            return candidate.item
    query_tokens = _meaningful_tokens(normalized_question)
    if not query_tokens:
        return None

    best_match: QuestionAnswer | None = None
    best_score = 0
    for candidate in package.qa_question_candidates:
        overlap = query_tokens & candidate.meaningful_tokens
        if not overlap:
            continue
        score = len(overlap)
        if score > best_score:
            best_match = candidate.item
            best_score = score
    if best_score >= 2:
        return best_match
    return None


def _qa_answer_text(item: QuestionAnswer, voice: PresenterVoiceSettings) -> str:
    localized = item.localized_answers.get(voice.language)
    if localized is not None and localized.strip():
        return localized.strip()
    return _render_text(item.answer, voice)


def _match_entrypoint(package: MaterialPackage, normalized_question: str) -> OperationEntrypoint | None:
    alias_match = _match_entrypoint_alias(package, normalized_question)
    if alias_match is not None:
        return alias_match

    query_tokens = _meaningful_tokens(normalized_question)
    if not query_tokens:
        return None

    best_entrypoint: OperationEntrypoint | None = None
    best_score = 0
    for candidate in package.entrypoint_match_candidates:
        score = _score_entrypoint_match(candidate, query_tokens)
        if score > best_score:
            best_entrypoint = candidate.entrypoint
            best_score = score
    return best_entrypoint


def _match_entrypoint_alias(
    package: MaterialPackage,
    normalized_question: str,
) -> OperationEntrypoint | None:
    if not normalized_question:
        return None
    package_match = _match_package_entrypoint_alias(package, normalized_question)
    if package_match is not None:
        return package_match

    best_entrypoint_id: str | None = None
    best_alias_length = 0
    for entrypoint_id, aliases in _ENTRYPOINT_ALIASES.items():
        for alias in aliases:
            normalized_alias = alias.casefold()
            if normalized_alias in normalized_question and len(normalized_alias) > best_alias_length:
                best_entrypoint_id = entrypoint_id
                best_alias_length = len(normalized_alias)
    if best_entrypoint_id is None:
        return None
    try:
        return package.entrypoint_by_id(best_entrypoint_id)
    except KeyError:
        return None


def _match_package_entrypoint_alias(
    package: MaterialPackage,
    normalized_question: str,
) -> OperationEntrypoint | None:
    best_entrypoint_id: str | None = None
    best_alias_length = 0
    for alias in package.entrypoint_question_aliases:
        if alias.normalized_alias in normalized_question and len(alias.normalized_alias) > best_alias_length:
            best_entrypoint_id = alias.entrypoint_id
            best_alias_length = len(alias.normalized_alias)
    if best_entrypoint_id is None:
        return None
    return package.entrypoint_by_id(best_entrypoint_id)


def _score_entrypoint_match(candidate: EntrypointMatchCandidate, query_tokens: set[str]) -> int:
    title_or_id_matches = query_tokens & candidate.title_or_id_tokens
    area_matches = query_tokens & candidate.area_tokens
    purpose_matches = query_tokens & candidate.purpose_tokens
    all_matches = title_or_id_matches | area_matches | purpose_matches
    if not all_matches or all_matches <= _GENERIC_ENTRYPOINT_TOKENS:
        return 0

    score = 0
    score += len(query_tokens & candidate.id_tokens) * 6
    score += len(query_tokens & candidate.title_tokens) * 5
    score += len(area_matches) * 2
    score += len(purpose_matches)
    if query_tokens <= candidate.title_or_id_tokens:
        score += 3
    return score


def _meaningful_tokens(text: str) -> set[str]:
    return set(match_meaningful_tokens(text))


def _field_tokens(text: str) -> set[str]:
    return set(match_field_tokens(text))


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
