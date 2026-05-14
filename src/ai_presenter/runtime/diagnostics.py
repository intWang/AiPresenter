import configparser
import importlib
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Literal

from ai_presenter.config.models import AppProfile
from ai_presenter.config.models import DesktopAppProfile
from ai_presenter.packages.models import MaterialPackage
from ai_presenter.runtime.package_demo import demo_flow_by_id

DiagnosticStatus = Literal["OK", "WARN", "FAIL"]

_SUPPORTED_VISION_PROVIDERS = frozenset({"fake"})
_SUPPORTED_NARRATION_PROVIDERS = frozenset({"fake", "codex-cli", "openai"})
_SUPPORTED_SPEECH_PROVIDERS = frozenset(
    {"fake", "openai", "windows-sapi", "windows-sapi-en", "windows-sapi-zh"}
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
) -> DiagnosticReport:
    checks = [
        DiagnosticCheck("OK", "profile", f"loaded {profile.id} ({profile.type.value})"),
        _diagnose_providers(profile),
        _diagnose_presenter_context(profile),
    ]

    if material_package is None:
        if flow_id is not None:
            checks.append(
                DiagnosticCheck("FAIL", "demo flow", "a flow id requires --package")
            )
    else:
        checks.extend(_diagnose_material_package(profile, material_package, flow_id))

    if _is_ringcentral_video_profile(profile):
        checks.append(_diagnose_ringcentral_config(ringcentral_config))

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
    checks.append(_diagnose_explainer_coverage(material_package))

    if flow_id is not None:
        try:
            flow = demo_flow_by_id(material_package, flow_id)
        except KeyError:
            checks.append(
                DiagnosticCheck(
                    "FAIL",
                    "demo flow",
                    f"{flow_id} was not found in package {material_package.app_id}",
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
