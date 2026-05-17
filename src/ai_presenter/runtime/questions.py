from dataclasses import dataclass
import logging
from time import perf_counter
from typing import Literal

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

QuestionAnswerSource = Literal["entrypoint", "no_match", "presenter_meta", "qa"]

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
_BROAD_QA_FRAGMENT_TOKENS = {
    "secure",
    "security",
    "status",
    "verify",
    "\u5b89\u5168",
    "\u72b6\u6001",
    "\u786e\u8ba4",
    "\u9690\u79c1",
}
_MEETING_INFO_ENTRYPOINT_ID = "ringcentral.video.top.meeting-info"
_MEETING_INFO_PRIVACY_QUESTION = (
    "How should AiPresenter handle meeting IDs and links safely?"
)
_PRIVATE_MEETING_INFO_ACTION_TOKENS = {
    "copy",
    "paste",
    "read",
    "share",
    "\u590d\u5236",
    "\u7c98\u8d34",
    "\u8d34\u4e0a",
    "\u5206\u4eab",
    "\u8bfb",
    "\u8bfb\u51fa",
    "\u6717\u8bfb",
    "\u30b3\u30d4\u30fc",
    "\u5171\u6709",
    "\u8cbc\u308a\u4ed8\u3051",
    "\u8aad",
    "copia",
    "copiar",
    "comparte",
    "compartir",
    "lee",
    "leer",
    "pega",
    "pegar",
}
_PRIVATE_MEETING_INFO_ALIAS_FRAGMENTS = {
    "meeting id",
    "meeting link",
    "\u4f1a\u8bae\u53f7",
    "\u4f1a\u8bae\u94fe\u63a5",
}
_PRIVATE_MEETING_INFO_CONTENT_FRAGMENTS = _PRIVATE_MEETING_INFO_ALIAS_FRAGMENTS | {
    "dial in",
    "dial-in",
    "host",
    "meeting details",
    "meeting information",
    "meeting url",
    "datos de marcacion",
    "detalles de la reunion",
    "detalles de reunion",
    "enlace de la reunion",
    "enlace de reunion",
    "id de la reunion",
    "id de reunion",
    "informacion de la reunion",
    "informacion de reunion",
    "informacion del host",
    "url de la reunion",
    "url de reunion",
    "\u4f1a\u8b70 id",
    "\u4f1a\u8b70id",
    "\u4f1a\u8b70\u30ea\u30f3\u30af",
    "\u4f1a\u8b70\u60c5\u5831",
    "\u4f1a\u8b70\u8a73\u7d30",
    "\u30c0\u30a4\u30e4\u30eb\u30a4\u30f3",
    "\u30db\u30b9\u30c8",
    "\u30df\u30fc\u30c6\u30a3\u30f3\u30b0 id",
    "\u30df\u30fc\u30c6\u30a3\u30f3\u30b0id",
    "\u30df\u30fc\u30c6\u30a3\u30f3\u30b0\u30ea\u30f3\u30af",
}
_PRIVATE_MEETING_INFO_LOCATION_FRAGMENTS = (
    _PRIVATE_MEETING_INFO_ALIAS_FRAGMENTS
    | (_PRIVATE_MEETING_INFO_CONTENT_FRAGMENTS - {"host", "\u30db\u30b9\u30c8"})
    | {"host information", "informacion del host", "\u30db\u30b9\u30c8\u60c5\u5831"}
)
_RECORDING_SAFETY_ENTRYPOINT_ID = "ringcentral.video.more.recording"
_NOTES_TRANSCRIPT_SAFETY_QUESTION = (
    "Where are captions, live transcription, and translation controls?"
)
_CHAT_CONTENT_PRIVACY_QUESTION = (
    "Can the presenter read meeting messages or participant names?"
)
_CHAT_CONTENT_TERMS = (
    "chat content",
    "chat message",
    "chat messages",
    "chat text",
    "meeting message",
    "meeting messages",
    "messages in chat",
    "private chat",
)
_CHAT_CONTENT_ACTION_TERMS = (
    "copy",
    "display",
    "export",
    "open",
    "quote",
    "read",
    "show",
    "summarize",
    "summary",
    "tell me",
    "what did",
)
_PARTICIPANT_PRIVACY_QUESTION = (
    "Can the presenter read meeting messages or participant names?"
)
_PARTICIPANT_PANEL_LOCATION_TERMS = (
    "participant panel",
    "participant button",
    "participants panel",
    "participants button",
    "panel de participantes",
    "lista de participantes",
    "controles de participantes",
    "参会人列表",
    "参会者面板",
    "参加者パネル",
    "参加者一覧",
)
_PARTICIPANT_DISCLOSURE_TERMS = (
    "show participants",
    "list participants",
    "participant names",
    "participant roles",
    "which participants",
    "who is host",
    "who is in",
    "host or moderator",
    "who is in the meeting",
    "who joined the meeting",
    "muestrame los participantes",
    "muéstrame los participantes",
    "muestra los participantes",
    "lista los participantes",
    "lee los nombres de participantes",
    "nombres de participantes",
    "roles de participantes",
    "participantes con nombres",
    "participantes con roles",
    "quien esta en la reunion",
    "quién está en la reunión",
    "quienes estan en la reunion",
    "quiénes están en la reunión",
    "quien esta en el panel de participantes",
    "quién está en el panel de participantes",
    "quienes estan en el panel de participantes",
    "quiénes están en el panel de participantes",
    "quienes estan en la lista de participantes",
    "quiénes están en la lista de participantes",
    "quien esta en la lista de participantes",
    "quién está en la lista de participantes",
    "host o moderador",
    "列出参会者",
    "列出参会人",
    "显示参会者",
    "显示参会人",
    "读参会人名字",
    "读出参会人名字",
    "参会人名字",
    "参会人姓名",
    "参会者角色",
    "参会人角色",
    "谁在会议",
    "谁是主持人",
    "主持人或协管员",
    "参加者名",
    "参加者の名前",
    "参加者を表示",
    "参加者を一覧表示",
    "参加者一覧に誰",
    "参加者一覧の役割",
    "会議には誰",
    "ホストまたはモデレーター",
)
_PARTICIPANT_IDENTITY_TERMS = (
    "names",
    "roles",
    "which participants",
    "who is",
    "who joined",
    "nombres",
    "roles",
    "quien",
    "quién",
    "quienes",
    "quiénes",
    "host",
    "moderador",
    "名字",
    "姓名",
    "角色",
    "谁在",
    "谁是",
    "主持人",
    "协管员",
    "参加者名",
    "名前",
    "役割",
    "誰",
    "ホスト",
    "モデレーター",
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
    "donde",
    "ubicacion",
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
_PRESENTER_META_REQUEST_ANSWER = (
    "Presenter settings: I can adjust language, tone, pacing, and guidance depth "
    "through AiPresenter voice settings. This is separate from RingCentral Video "
    "controls, so I will not open or operate the meeting UI for it."
)
_PRESENTER_META_REQUEST_FRAGMENTS = (
    "answer in chinese",
    "answer in english",
    "answer in japanese",
    "answer in spanish",
    "be brief",
    "be concise",
    "beginner guidance",
    "can you speak chinese",
    "can you speak english",
    "can you speak japanese",
    "can you speak spanish",
    "careful tone",
    "change language",
    "coach tone",
    "conversational tone",
    "executive tone",
    "explain more slowly",
    "formal tone",
    "friendly tone",
    "guidance depth",
    "language to",
    "make the presenter friendlier",
    "more concise",
    "more slowly",
    "new to ringcentral",
    "new to ringcentral video",
    "please be brief",
    "presenter friendlier",
    "privacy tone",
    "speak chinese",
    "speak english",
    "speak japanese",
    "speak spanish",
    "support tone",
    "\u53ef\u4ee5\u7528\u4e2d\u6587\u8bf4\u5417",
    "\u80fd\u7528\u4e2d\u6587\u8bf4\u5417",
    "\u6211\u662f\u521d\u5b66\u8005",
    "\u6211\u662f\u65b0\u624b",
    "\u7528\u4e2d\u6587\u56de\u7b54",
    "\u7528\u53cb\u597d\u7684\u8bed\u6c14\u56de\u7b54",
    "\u7528\u8c28\u614e\u7684\u8bed\u6c14\u56de\u7b54",
    "\u8bf7\u8bb2\u4e2d\u6587",
    "\u8bf7\u8bb2\u6162\u4e00\u70b9",
    "\u8bf7\u8bb2\u7b80\u5355\u4e00\u70b9",
    "\u8bf7\u8bf4\u4e2d\u6587",
    "\u8bf7\u8bf4\u6162\u4e00\u70b9",
    "\u8bf7\u7528\u4e2d\u6587\u56de\u7b54",
    "\u8bf7\u7528\u66f4\u53cb\u597d\u7684\u8bed\u6c14\u56de\u7b54",
    "\u8bf7\u7528\u8c28\u614e\u7684\u8bed\u6c14\u56de\u7b54",
    "\u8bf7\u7b80\u6d01\u4e00\u70b9",
    "\u89e3\u91ca\u6162\u4e00\u70b9",
    "\u4ece\u57fa\u7840\u8bb2\u8d77",
    "\u56de\u7b54\u7b80\u6d01\u4e00\u70b9",
)
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
    answer_source: QuestionAnswerSource = "no_match"


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
        answer_source=response.answer_source,
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
            answer_source="qa",
        )

    is_presenter_meta_request = _is_presenter_meta_request(normalized)
    entrypoint = (
        _match_explicit_entrypoint(package, normalized)
        if is_presenter_meta_request
        else _match_entrypoint(package, normalized)
    )
    if entrypoint is None:
        if is_presenter_meta_request:
            return QuestionResponse(
                answer_text=_render_text(_PRESENTER_META_REQUEST_ANSWER, voice),
                answer_source="presenter_meta",
            )
        return QuestionResponse(
            answer_text=_render_text(_NO_MATCH_ANSWERS[voice.language], voice)
        )
    return QuestionResponse(
        answer_text=_render_entrypoint_answer(entrypoint, voice),
        entrypoint_id=entrypoint.id,
        can_operate=_can_operate(package, entrypoint.id),
        answer_source="entrypoint",
    )


def _match_explicit_entrypoint(
    package: MaterialPackage,
    normalized_question: str,
) -> OperationEntrypoint | None:
    alias_match = _match_entrypoint_alias(package, normalized_question)
    if alias_match is not None:
        return alias_match
    location_match = _match_meeting_info_location_entrypoint(package, normalized_question)
    if location_match is not None:
        return location_match

    for entrypoint in package.operation_entrypoints:
        titles = (entrypoint.title, *entrypoint.localized_titles.values())
        if any(
            normalized_title
            and normalized_title in normalized_question
            for title in titles
            if (normalized_title := normalize_question_prompt(title))
        ):
            return entrypoint
    return None


def _is_presenter_meta_request(normalized_question: str) -> bool:
    if not normalized_question:
        return False
    return any(
        fragment in normalized_question
        for fragment in _PRESENTER_META_REQUEST_FRAGMENTS
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
    meeting_info_privacy_match = _match_meeting_info_privacy_qa(
        package,
        normalized_question,
    )
    if meeting_info_privacy_match is not None:
        return meeting_info_privacy_match
    chat_content_privacy_match = _match_chat_content_privacy_qa(
        package,
        normalized_question,
    )
    if chat_content_privacy_match is not None:
        return chat_content_privacy_match
    participant_privacy_match = _match_participant_privacy_qa(
        package,
        normalized_question,
    )
    if participant_privacy_match is not None:
        return participant_privacy_match
    contained_match = _match_contained_qa_question(package, normalized_question)
    if contained_match is not None:
        return contained_match
    if _is_meeting_info_location_lookup(normalized_question):
        return None

    if _is_entrypoint_title_lookup(package, normalized_question):
        return None
    if _is_package_entrypoint_alias_lookup(package, normalized_question):
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


def _match_contained_qa_question(
    package: MaterialPackage,
    normalized_question: str,
) -> QuestionAnswer | None:
    for candidate in package.qa_question_candidates:
        if (
            candidate.normalized_question in normalized_question
            and candidate.normalized_question != normalized_question
            and _is_specific_question_fragment(candidate.normalized_question)
        ):
            return candidate.item
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


def _match_chat_content_privacy_qa(
    package: MaterialPackage,
    normalized_question: str,
) -> QuestionAnswer | None:
    if not any(term in normalized_question for term in _CHAT_CONTENT_TERMS):
        return None
    if not any(term in normalized_question for term in _CHAT_CONTENT_ACTION_TERMS):
        return None
    return package.qa_questions_by_normalized.get(
        normalize_question_prompt(_CHAT_CONTENT_PRIVACY_QUESTION)
    )


def _match_participant_privacy_qa(
    package: MaterialPackage,
    normalized_question: str,
) -> QuestionAnswer | None:
    if not any(term in normalized_question for term in _PARTICIPANT_DISCLOSURE_TERMS):
        return None
    has_panel_location = any(
        term in normalized_question for term in _PARTICIPANT_PANEL_LOCATION_TERMS
    )
    has_identity_intent = any(
        term in normalized_question for term in _PARTICIPANT_IDENTITY_TERMS
    )
    if has_panel_location and not has_identity_intent:
        return None
    return _participant_privacy_qa(package)


def _participant_privacy_qa(package: MaterialPackage) -> QuestionAnswer | None:
    return package.qa_questions_by_normalized.get(
        normalize_question_prompt(_PARTICIPANT_PRIVACY_QUESTION)
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


def _match_meeting_info_privacy_qa(
    package: MaterialPackage,
    normalized_question: str,
) -> QuestionAnswer | None:
    if any(term in normalized_question for term in _LOCATION_LOOKUP_TERMS):
        return None
    has_private_content = any(
        fragment in normalized_question
        for fragment in _PRIVATE_MEETING_INFO_CONTENT_FRAGMENTS
    )
    if not has_private_content:
        return None
    has_private_action = any(
        token in normalized_question
        for token in _PRIVATE_MEETING_INFO_ACTION_TOKENS
    )
    if (
        not has_private_action
        and normalized_question not in _PRIVATE_MEETING_INFO_ALIAS_FRAGMENTS
    ):
        return None
    return package.qa_questions_by_normalized.get(
        normalize_question_prompt(_MEETING_INFO_PRIVACY_QUESTION)
    )


def _is_entrypoint_title_lookup(package: MaterialPackage, normalized_question: str) -> bool:
    if not normalized_question.startswith(("where is ", "where are ")):
        return False
    return any(
        normalize_question_prompt(entrypoint.title) in normalized_question
        for entrypoint in package.operation_entrypoints
    )


def _is_package_entrypoint_alias_lookup(
    package: MaterialPackage,
    normalized_question: str,
) -> bool:
    entrypoint = _match_package_entrypoint_alias(package, normalized_question)
    if entrypoint is None:
        return False
    if entrypoint.id != _MEETING_INFO_ENTRYPOINT_ID:
        return True
    if any(term in normalized_question for term in _LOCATION_LOOKUP_TERMS):
        return True
    if any(term in normalized_question for term in _PRIVATE_MEETING_INFO_ACTION_TOKENS):
        return False
    if normalized_question in _PRIVATE_MEETING_INFO_ALIAS_FRAGMENTS:
        return False
    return True


def _qa_answer_text(item: QuestionAnswer, voice: PresenterVoiceSettings) -> str:
    localized = item.localized_answers.get(voice.language)
    if localized is not None and localized.strip():
        return localized.strip()
    return _render_text(item.answer, voice)


def _match_entrypoint(package: MaterialPackage, normalized_question: str) -> OperationEntrypoint | None:
    alias_match = _match_entrypoint_alias(package, normalized_question)
    if alias_match is not None:
        return alias_match
    meeting_info_location_match = _match_meeting_info_location_entrypoint(
        package,
        normalized_question,
    )
    if meeting_info_location_match is not None:
        return meeting_info_location_match

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


def _match_meeting_info_location_entrypoint(
    package: MaterialPackage,
    normalized_question: str,
) -> OperationEntrypoint | None:
    if not _is_meeting_info_location_lookup(normalized_question):
        return None
    try:
        return package.entrypoint_by_id(_MEETING_INFO_ENTRYPOINT_ID)
    except KeyError:
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
    if normalized_question in _BROAD_QA_FRAGMENT_TOKENS:
        return False
    if _is_specific_question_fragment(normalized_question):
        return True
    entrypoint_match = _match_entrypoint(package, normalized_question)
    if entrypoint_match is None:
        return True
    return entrypoint_match.id in item.related_entrypoint_ids


def _is_meeting_info_location_lookup(normalized_question: str) -> bool:
    return any(
        term in normalized_question for term in _LOCATION_LOOKUP_TERMS
    ) and any(
        fragment in normalized_question
        for fragment in _PRIVATE_MEETING_INFO_LOCATION_FRAGMENTS
    )


def _contains_cjk(text: str) -> bool:
    return any("\u4e00" <= character <= "\u9fff" for character in text)


def _field_tokens(text: str) -> set[str]:
    return set(match_field_tokens(text))


def _render_entrypoint_answer(entrypoint: OperationEntrypoint, voice: PresenterVoiceSettings) -> str:
    base = (
        f"{_entrypoint_answer_label(entrypoint, voice)}: "
        f"{entrypoint.purpose_for_language(voice.language)}"
    )
    return _render_text(base, voice)


def _entrypoint_answer_label(
    entrypoint: OperationEntrypoint,
    voice: PresenterVoiceSettings,
) -> str:
    localized_title = entrypoint.localized_titles.get(voice.language, "").strip()
    if localized_title:
        return localized_title
    if voice.language == "es":
        aliases = entrypoint.question_aliases.get(voice.language, ())
        for alias in aliases:
            label = alias.strip()
            if label:
                return label
    return entrypoint.title_for_language(voice.language)


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
