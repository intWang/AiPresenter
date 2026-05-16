import configparser
import importlib
import os
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Literal

from ai_presenter.config.models import AppProfile
from ai_presenter.config.models import DesktopAppProfile
from ai_presenter.packages.localization_status import LocalizationStatusReport
from ai_presenter.packages.localization_status import build_localization_status
from ai_presenter.packages.models import EntrypointQuestionAlias
from ai_presenter.packages.models import MaterialPackage
from ai_presenter.packages.models import QuestionAnswer
from ai_presenter.packages.models import QuestionAnswerMatchCandidate
from ai_presenter.runtime.voice import PresenterVoiceSettings
from ai_presenter.runtime.voice import language_label
from ai_presenter.runtime.voice import resolve_speech_provider_name
from ai_presenter.runtime.voice import tone_label
from ai_presenter.runtime.voice import validate_profile_voice
from ai_presenter.runtime.voice_assets import check_voice_asset_availability

DiagnosticStatus = Literal["OK", "WARN", "FAIL"]

_SUPPORTED_VISION_PROVIDERS = frozenset({"fake"})
_SUPPORTED_NARRATION_PROVIDERS = frozenset({"fake", "codex-cli", "openai"})
_SUPPORTED_SPEECH_PROVIDERS = frozenset(
    {"fake", "openai", "piper", "windows-sapi", "windows-sapi-en", "windows-sapi-zh"}
)
_SECTION_HEADER_PATTERN = re.compile(r"^\s*\[[^\]]+\]", re.MULTILINE)

psutil: Any = None
try:
    psutil = importlib.import_module("psutil")
except ImportError:
    pass


@dataclass(frozen=True)
class DiagnosticCheck:
    status: DiagnosticStatus
    name: str
    detail: str


@dataclass(frozen=True)
class DiagnosticReport:
    checks: tuple[DiagnosticCheck, ...]

    @property
    def failed_count(self) -> int:
        return sum(1 for check in self.checks if check.status == "FAIL")

    @property
    def warning_count(self) -> int:
        return sum(1 for check in self.checks if check.status == "WARN")

    @property
    def ok_count(self) -> int:
        return sum(1 for check in self.checks if check.status == "OK")


def diagnose_configuration(
    *,
    profile: AppProfile,
    material_package: MaterialPackage | None = None,
    flow_id: str | None = None,
    ringcentral_config: Path | None = None,
    voice: PresenterVoiceSettings | None = None,
    require_localization: bool = False,
    localization_language: str | None = None,
) -> DiagnosticReport:
    checks = [
        DiagnosticCheck("OK", "profile", f"loaded {profile.id} ({profile.type.value})"),
        _diagnose_providers(profile),
        _diagnose_presenter_context(profile),
    ]
    provider_environment = _diagnose_provider_environment(profile)
    if provider_environment is not None:
        checks.append(provider_environment)

    if material_package is None:
        if flow_id is not None:
            checks.append(
                DiagnosticCheck("FAIL", "demo flow", "a flow id requires --package")
            )
    else:
        checks.extend(_diagnose_material_package(profile, material_package, flow_id))

    if require_localization:
        language = localization_language or (voice.language if voice is not None else "zh")
        checks.append(
            _diagnose_required_localization(
                material_package,
                language=language,
            )
        )

    if _is_ringcentral_video_profile(profile):
        checks.append(_diagnose_ringcentral_config(ringcentral_config))

    if voice is not None:
        voice_check = _diagnose_voice(profile, voice)
        checks.append(voice_check)
        if voice_check.status == "OK":
            voice_assets_check = _diagnose_voice_assets(profile, voice)
            if voice_assets_check is not None:
                checks.append(voice_assets_check)

    return DiagnosticReport(tuple(checks))


def format_diagnostic_report(report: DiagnosticReport) -> list[str]:
    lines = [
        f"[{check.status}] {check.name}: {check.detail}"
        for check in report.checks
    ]
    failed_word = "failed" if report.failed_count == 1 else "failed"
    warning_word = "warning" if report.warning_count == 1 else "warnings"
    lines.append(
        "Doctor completed: "
        f"{report.ok_count} ok, {report.warning_count} {warning_word}, "
        f"{report.failed_count} {failed_word}."
    )
    return lines


def _diagnose_providers(profile: AppProfile) -> DiagnosticCheck:
    unsupported: list[str] = []
    if profile.providers.vision not in _SUPPORTED_VISION_PROVIDERS:
        unsupported.append(f"vision={profile.providers.vision}")
    if profile.providers.narration not in _SUPPORTED_NARRATION_PROVIDERS:
        unsupported.append(f"narration={profile.providers.narration}")
    if profile.providers.speech not in _SUPPORTED_SPEECH_PROVIDERS:
        unsupported.append(f"speech={profile.providers.speech}")

    if unsupported:
        return DiagnosticCheck(
            "FAIL",
            "providers",
            f"unsupported provider names: {', '.join(unsupported)}",
        )
    return DiagnosticCheck(
        "OK",
        "providers",
        "configured "
        f"vision={profile.providers.vision}, narration={profile.providers.narration}, "
        f"speech={profile.providers.speech}",
    )


def _diagnose_provider_environment(profile: AppProfile) -> DiagnosticCheck | None:
    required_env_vars: list[str] = []
    if profile.providers.narration == "openai" or profile.providers.speech == "openai":
        required_env_vars.append("OPENAI_API_KEY")
    if profile.providers.narration == "openai":
        required_env_vars.append("AI_PRESENTER_OPENAI_NARRATION_MODEL")

    if not required_env_vars:
        return None

    missing = [name for name in required_env_vars if not os.getenv(name, "").strip()]
    if missing:
        return DiagnosticCheck(
            "FAIL",
            "provider environment",
            f"missing required environment variables: {', '.join(missing)}",
        )
    return DiagnosticCheck(
        "OK",
        "provider environment",
        f"required environment variables are set: {', '.join(required_env_vars)}",
    )


def _diagnose_presenter_context(profile: AppProfile) -> DiagnosticCheck:
    parts: list[str] = []
    if profile.narration.soul_path is not None:
        parts.append(f"soul={profile.narration.soul_path.name}")
    if profile.narration.memory_path is not None:
        parts.append(f"memory={profile.narration.memory_path.name}")
    if profile.narration.skill_paths:
        parts.append(f"skills={len(profile.narration.skill_paths)}")

    if not parts:
        return DiagnosticCheck("WARN", "presenter context", "no soul, memory, or skills configured")
    return DiagnosticCheck("OK", "presenter context", ", ".join(parts))


def _diagnose_voice(profile: AppProfile, voice: PresenterVoiceSettings) -> DiagnosticCheck:
    label = f"{language_label(voice.language)} / {tone_label(voice.tone)}"
    try:
        validate_profile_voice(profile, voice)
    except ValueError as exc:
        return DiagnosticCheck("FAIL", "voice", str(exc))
    route = resolve_speech_provider_name(profile, voice)
    return DiagnosticCheck(
        "OK",
        "voice",
        f"{label} supported via speech={route} (configured {profile.providers.speech})",
    )


def _diagnose_voice_assets(
    profile: AppProfile,
    voice: PresenterVoiceSettings,
) -> DiagnosticCheck | None:
    result = check_voice_asset_availability(profile, voice)
    if result is None:
        return None
    return DiagnosticCheck(result.status, "voice assets", result.detail)


def _diagnose_material_package(
    profile: AppProfile,
    material_package: MaterialPackage,
    flow_id: str | None,
) -> list[DiagnosticCheck]:
    checks = [
        DiagnosticCheck("OK", "package", f"loaded {material_package.app_id}"),
    ]
    if profile.id in material_package.profile_ids:
        checks.append(
            DiagnosticCheck(
                "OK",
                "package profile support",
                f"package lists profile {profile.id}",
            )
        )
    else:
        checks.append(
            DiagnosticCheck(
                "FAIL",
                "package profile support",
                f"package {material_package.app_id} does not list profile {profile.id}",
            )
        )
    checks.append(_diagnose_question_aliases(material_package))
    checks.append(_diagnose_qa_questions(material_package))
    checks.append(_diagnose_qa_alias_overlaps(material_package))
    checks.append(_diagnose_explainer_coverage(material_package))

    if flow_id is not None:
        try:
            flow = material_package.demo_flow_by_id(flow_id)
        except KeyError as exc:
            checks.append(
                DiagnosticCheck(
                    "FAIL",
                    "demo flow",
                    str(exc.args[0]),
                )
            )
        else:
            checks.append(
                DiagnosticCheck(
                    "OK",
                    "demo flow",
                    f"{flow.id} ({len(flow.steps)} steps)",
                )
            )
    return checks


def _diagnose_required_localization(
    material_package: MaterialPackage | None,
    *,
    language: str,
) -> DiagnosticCheck:
    if material_package is None:
        return DiagnosticCheck(
            "FAIL",
            "localization",
            "--require-localization requires --package",
        )
    report = build_localization_status(material_package, language=language)
    status: DiagnosticStatus = "OK" if report.required_localization_complete else "FAIL"
    state = "complete" if status == "OK" else "incomplete"
    return DiagnosticCheck(
        status,
        "localization",
        f"required {report.language} localization {state}: "
        f"{_format_localization_counts(report)}",
    )


def _format_localization_counts(report: LocalizationStatusReport) -> str:
    return (
        f"{report.demo_localized_steps}/{report.demo_total_steps} demo steps, "
        f"{report.qa_localized_questions}/{report.qa_total} Q&A questions, "
        f"{report.qa_localized_answers}/{report.qa_total} Q&A answers"
    )


def _diagnose_explainer_coverage(material_package: MaterialPackage) -> DiagnosticCheck:
    entrypoint_ids = {entrypoint.id for entrypoint in material_package.operation_entrypoints}
    explained_ids = {
        related_id
        for explainer in material_package.explainers.values()
        for related_id in explainer.related_entrypoint_ids
    }
    missing = sorted(entrypoint_ids - explained_ids)
    if missing:
        preview = ", ".join(missing[:5])
        suffix = "" if len(missing) <= 5 else f", and {len(missing) - 5} more"
        return DiagnosticCheck(
            "WARN",
            "explainer coverage",
            f"{len(missing)} entrypoints lack explainers: {preview}{suffix}",
        )
    return DiagnosticCheck(
        "OK",
        "explainer coverage",
        f"{len(entrypoint_ids)}/{len(entrypoint_ids)} entrypoints covered",
    )


def _diagnose_question_aliases(material_package: MaterialPackage) -> DiagnosticCheck:
    aliases_by_normalized: dict[str, list[EntrypointQuestionAlias]] = {}
    for alias in material_package.entrypoint_question_aliases:
        aliases_by_normalized.setdefault(alias.normalized_alias, []).append(alias)

    conflicts = [
        (normalized_alias, aliases)
        for normalized_alias, aliases in aliases_by_normalized.items()
        if len(_unique_alias_entrypoint_ids(aliases)) > 1
    ]
    if not conflicts:
        return DiagnosticCheck(
            "OK",
            "question aliases",
            f"{len(material_package.entrypoint_question_aliases)} package-owned aliases "
            "have no cross-entrypoint duplicates",
        )

    normalized_alias, aliases = conflicts[0]
    alias_word = "alias" if len(conflicts) == 1 else "aliases"
    suffix = "" if len(conflicts) == 1 else f"; and {len(conflicts) - 1} more"
    return DiagnosticCheck(
        "WARN",
        "question aliases",
        f"{len(conflicts)} duplicate normalized package-owned question {alias_word}: "
        f"{_format_question_alias_conflict(normalized_alias, aliases)}{suffix}",
    )


def _diagnose_qa_questions(material_package: MaterialPackage) -> DiagnosticCheck:
    candidates_by_normalized: dict[str, list[QuestionAnswerMatchCandidate]] = {}
    for candidate in material_package.qa_question_candidates:
        candidates_by_normalized.setdefault(candidate.normalized_question, []).append(candidate)

    conflicts = [
        (normalized_question, candidates)
        for normalized_question, candidates in candidates_by_normalized.items()
        if len(_unique_qa_items(candidates)) > 1
    ]
    if not conflicts:
        return DiagnosticCheck(
            "OK",
            "qa questions",
            f"{len(material_package.qa_question_candidates)} Q&A question prompts "
            "have no cross-item duplicates",
        )

    normalized_question, candidates = conflicts[0]
    prompt_word = "prompt" if len(conflicts) == 1 else "prompts"
    suffix = "" if len(conflicts) == 1 else f"; and {len(conflicts) - 1} more"
    return DiagnosticCheck(
        "WARN",
        "qa questions",
        f"{len(conflicts)} duplicate normalized Q&A question {prompt_word}: "
        f"{_format_qa_question_conflict(material_package, normalized_question, candidates)}{suffix}",
    )


def _diagnose_qa_alias_overlaps(material_package: MaterialPackage) -> DiagnosticCheck:
    aliases_by_normalized: dict[str, list[EntrypointQuestionAlias]] = {}
    for alias in material_package.entrypoint_question_aliases:
        aliases_by_normalized.setdefault(alias.normalized_alias, []).append(alias)

    candidates_by_item: dict[
        tuple[str, int],
        list[QuestionAnswerMatchCandidate],
    ] = {}
    for candidate in material_package.qa_question_candidates:
        key = (_normalize_user_question(candidate.question), id(candidate.item))
        candidates_by_item.setdefault(key, []).append(candidate)

    conflicts: list[
        tuple[
            str,
            list[QuestionAnswerMatchCandidate],
            list[EntrypointQuestionAlias],
        ]
    ] = []
    for (normalized_question, _item_id), candidates in candidates_by_item.items():
        aliases = aliases_by_normalized.get(normalized_question, [])
        if not aliases:
            continue
        related_ids = set(candidates[0].item.related_entrypoint_ids)
        unsafe_aliases = [
            alias for alias in aliases if alias.entrypoint_id not in related_ids
        ]
        if unsafe_aliases:
            conflicts.append((normalized_question, candidates, unsafe_aliases))

    if not conflicts:
        return DiagnosticCheck(
            "OK",
            "qa alias overlap",
            f"{len(material_package.qa_question_candidates)} Q&A question prompts "
            "have no unsafe package-owned alias overlaps",
        )

    normalized_question, candidates, aliases = conflicts[0]
    prompt_word = "prompt" if len(conflicts) == 1 else "prompts"
    shadow_phrase = (
        "shadows a package-owned alias"
        if len(conflicts) == 1
        else "shadow package-owned aliases"
    )
    suffix = "" if len(conflicts) == 1 else f"; and {len(conflicts) - 1} more"
    return DiagnosticCheck(
        "WARN",
        "qa alias overlap",
        f"{len(conflicts)} Q&A question {prompt_word} {shadow_phrase}: "
        f"{_format_qa_alias_overlap_conflict(material_package, normalized_question, candidates, aliases)}"
        f"{suffix}",
    )


def _format_qa_alias_overlap_conflict(
    material_package: MaterialPackage,
    normalized_question: str,
    candidates: list[QuestionAnswerMatchCandidate],
    aliases: list[EntrypointQuestionAlias],
) -> str:
    item = candidates[0].item
    label = _format_qa_item_label(material_package, item)
    qa_languages = _ordered_unique(_qa_question_language(candidate) for candidate in candidates)
    alias_languages = _ordered_unique(alias.language for alias in aliases)
    alias_entrypoint_ids = _unique_alias_entrypoint_ids(aliases)
    return (
        f"{normalized_question!r} (Q&A languages: {', '.join(qa_languages)}; "
        f"alias languages: {', '.join(alias_languages)}) appears in {label} "
        f"and shadows {', '.join(alias_entrypoint_ids)}; first match is Q&A {label}"
    )


def _normalize_user_question(question: str) -> str:
    return question.casefold().strip()


def _format_qa_question_conflict(
    material_package: MaterialPackage,
    normalized_question: str,
    candidates: list[QuestionAnswerMatchCandidate],
) -> str:
    items = _unique_qa_items(candidates)
    labels = [_format_qa_item_label(material_package, item) for item in items]
    languages = _ordered_unique(_qa_question_language(candidate) for candidate in candidates)
    return (
        f"{normalized_question!r} (languages: {', '.join(languages)}) appears in "
        f"{', '.join(labels)}; first match is {labels[0]}"
    )


def _unique_qa_items(
    candidates: list[QuestionAnswerMatchCandidate],
) -> list[QuestionAnswer]:
    seen: set[int] = set()
    ordered: list[QuestionAnswer] = []
    for candidate in candidates:
        item_id = id(candidate.item)
        if item_id in seen:
            continue
        seen.add(item_id)
        ordered.append(candidate.item)
    return ordered


def _format_qa_item_label(
    material_package: MaterialPackage,
    item: QuestionAnswer,
) -> str:
    for index, candidate in enumerate(material_package.qa, start=1):
        if candidate is item:
            return f"#{index} {item.question}"
    return item.question


def _qa_question_language(candidate: QuestionAnswerMatchCandidate) -> str:
    for language, questions in candidate.item.localized_questions.items():
        if candidate.question in questions:
            return language
    return "en"


def _format_question_alias_conflict(
    normalized_alias: str,
    aliases: list[EntrypointQuestionAlias],
) -> str:
    entrypoint_ids = _unique_alias_entrypoint_ids(aliases)
    languages = _ordered_unique(alias.language for alias in aliases)
    return (
        f"{normalized_alias!r} (languages: {', '.join(languages)}) maps to "
        f"{', '.join(entrypoint_ids)}; first match is {entrypoint_ids[0]}"
    )


def _unique_alias_entrypoint_ids(aliases: list[EntrypointQuestionAlias]) -> list[str]:
    return _ordered_unique(alias.entrypoint_id for alias in aliases)


def _ordered_unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def _is_ringcentral_video_profile(profile: AppProfile) -> bool:
    return (
        isinstance(profile, DesktopAppProfile)
        and profile.bind.process == "RingCentralVideo"
        and profile.bind.window_class == "RingCentralVideoClass"
    )


def _diagnose_ringcentral_config(path: Path | None) -> DiagnosticCheck:
    if path is None:
        discovered = _discover_ringcentral_video_config()
        if discovered is None:
            return DiagnosticCheck(
                "WARN",
                "RingCentral config",
                "not checked; pass --ringcentral-config <RingCentralVideo config.ini>",
            )
        path = discovered

    config_path = path.expanduser()
    if not config_path.is_file():
        return DiagnosticCheck("FAIL", "RingCentral config", f"file not found: {config_path}")

    try:
        value = _read_disable_affinity_mask(config_path)
    except (OSError, configparser.Error, ValueError) as exc:
        return DiagnosticCheck("FAIL", "RingCentral config", str(exc))

    if value is True:
        return DiagnosticCheck(
            "OK",
            "RingCentral config",
            f"{config_path} has DisableAffinityMask=true",
        )
    if value is False:
        return DiagnosticCheck(
            "FAIL",
            "RingCentral config",
            f"{config_path} has DisableAffinityMask=false; expected DisableAffinityMask=true",
        )
    return DiagnosticCheck(
        "FAIL",
        "RingCentral config",
        f"{config_path} does not define DisableAffinityMask; expected DisableAffinityMask=true",
    )


def _read_disable_affinity_mask(path: Path) -> bool | None:
    content = path.read_text(encoding="utf-8-sig")
    parser = configparser.ConfigParser()
    parser.read_string(_ensure_ini_section(content))

    for section in parser.sections():
        if parser.has_option(section, "DisableAffinityMask"):
            return parser.getboolean(section, "DisableAffinityMask")
    return None


def _ensure_ini_section(content: str) -> str:
    if _SECTION_HEADER_PATTERN.search(content):
        return content
    return f"[root]\n{content}"


def _discover_ringcentral_video_config() -> Path | None:
    for exe_path in _iter_process_executable_paths("RingCentralVideo"):
        candidate = exe_path.parent / "config.ini"
        if candidate.is_file():
            return candidate
    return None


def _iter_process_executable_paths(process_name: str) -> Iterable[Path]:
    if psutil is None:
        return []

    executable_paths: list[Path] = []
    for process in psutil.process_iter(["name", "exe"]):
        try:
            info = process.info
            name = info.get("name")
            exe = info.get("exe")
        except Exception:
            continue
        if not isinstance(name, str) or not _process_name_matches(name, process_name):
            continue
        if isinstance(exe, str) and exe.strip():
            executable_paths.append(Path(exe))
    return executable_paths


def _process_name_matches(actual: str, expected: str) -> bool:
    return Path(actual).stem.lower() == expected.lower()
