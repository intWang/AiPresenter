from dataclasses import dataclass
import logging
from time import perf_counter

from ai_presenter.packages.models import EntrypointMatchCandidate
from ai_presenter.packages.models import MaterialPackage
from ai_presenter.packages.models import OperationEntrypoint
from ai_presenter.packages.models import QuestionAnswer
from ai_presenter.packages.models import match_field_tokens
from ai_presenter.packages.models import match_meaningful_tokens
from ai_presenter.packages.models import normalize_question_prompt
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
_RECORDING_SAFETY_ENTRYPOINT_ID = "ringcentral.video.more.recording"
_NOTES_TRANSCRIPT_SAFETY_QUESTION = (
    "Where are captions, live transcription, and translation controls?"
)
_JAPANESE_RECORDING_TERMS = ("録画",)
_JAPANESE_RECORDING_ACTION_TERMS = (
    "して",
    "開始",
    "止め",
    "停止",
    "クリック",
    "今すぐ",
    "知らせず",
    "同意なし",
    "ホスト",
    "中ですか",
    "されていますか",
    "状態",
    "見る",
    "開いて",
    "再生",
    "ダウンロード",
    "内容",
    "要約",
)
_NOTES_TRANSCRIPT_TERMS = (
    "start notes",
    "transcript",
    "notes and transcript",
    "笔记",
    "转录",
    "字幕",
    "ノート",
    "文字起こし",
    "議事録",
    "会議メモ",
)
_NOTES_TRANSCRIPT_ACTION_OR_CONTENT_TERMS = (
    "click",
    "start",
    "summarize",
    "read",
    "content",
    "copy",
    "save",
    "export",
    "create",
    "show",
    "点击",
    "打开",
    "开启",
    "开始",
    "启动",
    "读取",
    "读",
    "朗读",
    "总结",
    "摘要",
    "内容",
    "复制",
    "保存",
    "导出",
    "创建",
    "生成",
    "クリック",
    "押して",
    "開始",
    "始め",
    "オン",
    "読ん",
    "読み上げ",
    "要約",
    "内容",
    "コピー",
    "保存",
    "エクスポート",
    "作って",
    "作成",
    "見せて",
)
_LOCATION_LOOKUP_TERMS = (
    "where",
    "location",
    "哪里",
    "哪儿",
    "在哪",
    "位置",
    "場所",
    "どこ",
    "入口",
)
_NO_MATCH_ANSWERS = {
    "en": "I could not find a matching control in the active app context.",
    "zh": "\u6211\u6ca1\u6709\u5728\u5f53\u524d\u5e94\u7528\u4e0a\u4e0b\u6587\u4e2d\u627e\u5230\u5339\u914d\u7684\u63a7\u4ef6\u3002",
    "ja": (
        "\u73fe\u5728\u306e\u30a2\u30d7\u30ea\u306e\u72b6\u6cc1\u3067\u306f"
        "\u4e00\u81f4\u3059\u308b\u30b3\u30f3\u30c8\u30ed\u30fc\u30eb\u304c\u898b\u3064\u304b\u308a\u307e\u305b\u3093\u3002"
    ),
    "es": "No encontre un control que coincida en el contexto activo de la app.",
}
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
_LEGACY_ENTRYPOINT_ALIAS_SIGNATURE: tuple[tuple[str, tuple[str, ...]], ...] = ()
_LEGACY_ENTRYPOINT_ALIAS_MATCHES: tuple[tuple[str, str], ...] = ()


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
    normalized = normalize_question_prompt(question)
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
            answer_text=_render_text(_NO_MATCH_ANSWERS[voice.language], voice)
        )
    return QuestionResponse(
        answer_text=_render_entrypoint_answer(entrypoint, voice),
        entrypoint_id=entrypoint.id,
        can_operate=_can_operate(package, entrypoint.id),
    )


def _match_qa(package: MaterialPackage, normalized_question: str) -> QuestionAnswer | None:
    if not normalized_question:
        return None
    exact_match = package.qa_questions_by_normalized.get(normalized_question)
    if exact_match is not None:
        return exact_match
    safety_match = _match_recording_safety_qa(package, normalized_question)
    if safety_match is not None:
        return safety_match
    notes_safety_match = _match_notes_transcript_safety_qa(
        package,
        normalized_question,
    )
    if notes_safety_match is not None:
        return notes_safety_match

    if _is_entrypoint_title_lookup(package, normalized_question):
        return None

    for candidate in package.qa_question_candidates:
        if (
            normalized_question
            and normalized_question in candidate.normalized_question
            and _can_match_qa_fragment(package, candidate.item, normalized_question)
        ):
            return candidate.item
        if candidate.normalized_question in normalized_question:
            return candidate.item
    if _match_package_entrypoint_alias(package, normalized_question) is not None:
        return None
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


def _match_recording_safety_qa(
    package: MaterialPackage,
    normalized_question: str,
) -> QuestionAnswer | None:
    if not any(term in normalized_question for term in _JAPANESE_RECORDING_TERMS):
        return None
    if not any(term in normalized_question for term in _JAPANESE_RECORDING_ACTION_TERMS):
        return None
    return _qa_by_related_entrypoint(package, _RECORDING_SAFETY_ENTRYPOINT_ID)


def _match_notes_transcript_safety_qa(
    package: MaterialPackage,
    normalized_question: str,
) -> QuestionAnswer | None:
    if not any(term in normalized_question for term in _NOTES_TRANSCRIPT_TERMS):
        return None
    if any(term in normalized_question for term in _LOCATION_LOOKUP_TERMS):
        return None
    if not any(
        term in normalized_question
        for term in _NOTES_TRANSCRIPT_ACTION_OR_CONTENT_TERMS
    ):
        return None
    return package.qa_questions_by_normalized.get(
        normalize_question_prompt(_NOTES_TRANSCRIPT_SAFETY_QUESTION)
    )


def _qa_by_related_entrypoint(
    package: MaterialPackage,
    entrypoint_id: str,
) -> QuestionAnswer | None:
    return next(
        (
            item
            for item in package.qa
            if entrypoint_id in item.related_entrypoint_ids
        ),
        None,
    )


def _is_entrypoint_title_lookup(package: MaterialPackage, normalized_question: str) -> bool:
    if not normalized_question.startswith(("where is ", "where are ")):
        return False
    return any(
        normalize_question_prompt(entrypoint.title) in normalized_question
        for entrypoint in package.operation_entrypoints
    )


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

    for entrypoint_id, normalized_alias in _legacy_entrypoint_alias_matches():
        if normalized_alias not in normalized_question:
            continue
        try:
            return package.entrypoint_by_id(entrypoint_id)
        except KeyError:
            return None
    return None


def _match_package_entrypoint_alias(
    package: MaterialPackage,
    normalized_question: str,
) -> OperationEntrypoint | None:
    for alias in package.entrypoint_question_aliases_by_match_order:
        if alias.normalized_alias in normalized_question:
            return package.entrypoint_by_id(alias.entrypoint_id)
    return None


def _legacy_entrypoint_alias_matches() -> tuple[tuple[str, str], ...]:
    global _LEGACY_ENTRYPOINT_ALIAS_MATCHES
    global _LEGACY_ENTRYPOINT_ALIAS_SIGNATURE
    signature = tuple(
        (entrypoint_id, aliases)
        for entrypoint_id, aliases in _ENTRYPOINT_ALIASES.items()
    )
    if _LEGACY_ENTRYPOINT_ALIAS_SIGNATURE == signature:
        return _LEGACY_ENTRYPOINT_ALIAS_MATCHES

    matches = [
        (entrypoint_id, normalized_alias)
        for entrypoint_id, aliases in _ENTRYPOINT_ALIASES.items()
        for alias in aliases
        if (normalized_alias := normalize_question_prompt(alias))
    ]
    _LEGACY_ENTRYPOINT_ALIAS_MATCHES = tuple(
        sorted(matches, key=lambda match: len(match[1]), reverse=True)
    )
    _LEGACY_ENTRYPOINT_ALIAS_SIGNATURE = signature
    return _LEGACY_ENTRYPOINT_ALIAS_MATCHES


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


def _is_specific_question_fragment(text: str) -> bool:
    if len(_meaningful_tokens(text)) >= 2:
        return True
    return _contains_cjk(text) and len(text) >= 6


def _can_match_qa_fragment(
    package: MaterialPackage,
    item: QuestionAnswer,
    normalized_question: str,
) -> bool:
    if item.related_entrypoint_ids:
        return True
    if _is_specific_question_fragment(normalized_question):
        return True
    return _match_entrypoint(package, normalized_question) is None


def _contains_cjk(text: str) -> bool:
    return any("\u4e00" <= character <= "\u9fff" for character in text)


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
    if entrypoint.question_policy == "answerOnly":
        return False
    if not entrypoint.open_steps:
        return False
    lowered = " ".join([entrypoint.id, entrypoint.title, entrypoint.purpose]).casefold()
    return not any(word in lowered for word in _RISKY_ENTRYPOINT_WORDS)
