from pathlib import Path
from typing import Any

import typer

from ai_presenter.acceptance.manual_record import AcceptanceDraftRequest
from ai_presenter.acceptance.manual_record import render_manual_acceptance_draft
from ai_presenter.acceptance.validation_targets import discover_validation_targets
from ai_presenter.acceptance.validation_targets import render_validation_target_lines
from ai_presenter.config.loader import load_profile
from ai_presenter.config.models import DesktopAppProfile
from ai_presenter.packages.localization_status import build_localization_status
from ai_presenter.packages.localization_status import render_localization_status_lines
from ai_presenter.packages.loader import load_material_package
from ai_presenter.runtime.controller_view_model import render_voice_label
from ai_presenter.runtime.logging import configure_logging
from ai_presenter.runtime.voice import PRESENTER_LANGUAGE_CHOICES
from ai_presenter.runtime.voice import PRESENTER_TONE_CHOICES
from ai_presenter.runtime.voice import PresenterVoiceSettings
from ai_presenter.runtime.voice import language_label
from ai_presenter.runtime.voice import presenter_language_aliases
from ai_presenter.runtime.voice import presenter_tone_aliases
from ai_presenter.runtime.voice import presenter_tone_description
from ai_presenter.runtime.voice import resolve_speech_provider_name
from ai_presenter.runtime.voice import tone_label
from ai_presenter.runtime.voice import validate_profile_voice

app = typer.Typer(help="AI presenter CLI for configured app profiles.")

PACKAGE_PROFILE_DIR = Path(__file__).resolve().parent / "profiles"
REPO_PROFILE_DIR = Path(__file__).resolve().parents[2] / "profiles"
REPO_PACKAGE_DIR = Path(__file__).resolve().parents[2] / "packages"
RINGCENTRAL_KNOWLEDGE_DIR = (
    Path(__file__).resolve().parents[2] / "docs" / "knowledge" / "ringcentral-video"
)
DEFAULT_VALIDATION_CHECKLIST = RINGCENTRAL_KNOWLEDGE_DIR / "validation-checklist-index.md"
DEFAULT_EVIDENCE_INDEX = RINGCENTRAL_KNOWLEDGE_DIR / "evidence-index.md"


@app.callback()
def main() -> None:
    """AI presenter CLI for configured app profiles."""


def resolve_profile(profile: str) -> Path:
    candidate = Path(profile).expanduser()
    if candidate.exists():
        return candidate
    for profile_dir in (Path.cwd() / "profiles", REPO_PROFILE_DIR, PACKAGE_PROFILE_DIR):
        bundled = profile_dir / f"{profile}.yaml"
        if bundled.exists():
            return bundled
    raise typer.BadParameter(f"Profile not found: {profile}")


def resolve_material_package(package: str) -> Path:
    candidate = Path(package).expanduser()
    if candidate.exists():
        return candidate
    for package_dir in (Path.cwd() / "packages", REPO_PACKAGE_DIR):
        bundled = package_dir / f"{package}.yaml"
        if bundled.exists():
            return bundled
    raise typer.BadParameter(f"Material package not found: {package}")


def resolve_voice_settings(language: str, tone: str) -> PresenterVoiceSettings:
    try:
        return PresenterVoiceSettings(language=language, tone=tone)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc


def validate_cli_voice_profile(
    profile: DesktopAppProfile,
    voice: PresenterVoiceSettings,
) -> None:
    try:
        validate_profile_voice(profile, voice)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc


def run_desktop_profile(*args: Any, **kwargs: Any) -> None:
    from ai_presenter.runtime.factory import run_desktop_profile as _run_desktop_profile

    _run_desktop_profile(*args, **kwargs)


def run_material_demo(*args: Any, **kwargs: Any) -> None:
    from ai_presenter.runtime.factory import run_material_demo as _run_material_demo

    _run_material_demo(*args, **kwargs)


def run_controller(*args: Any, **kwargs: Any) -> None:
    from ai_presenter.runtime.controller import run_controller as _run_controller

    _run_controller(*args, **kwargs)


def diagnose_configuration(*args: Any, **kwargs: Any) -> Any:
    from ai_presenter.runtime.diagnostics import diagnose_configuration as _diagnose_configuration

    return _diagnose_configuration(*args, **kwargs)


def format_diagnostic_report(*args: Any, **kwargs: Any) -> Any:
    from ai_presenter.runtime.diagnostics import format_diagnostic_report as _format_diagnostic_report

    return _format_diagnostic_report(*args, **kwargs)


def check_voice_asset_availability(*args: Any, **kwargs: Any) -> Any:
    from ai_presenter.runtime.voice_assets import (
        check_voice_asset_availability as _check_voice_asset_availability,
    )

    return _check_voice_asset_availability(*args, **kwargs)


@app.command()
def run(
    profile: str = typer.Option(..., "--profile", help="Profile id or YAML path."),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Load configuration without app automation.",
    ),
    iterations: int = typer.Option(
        1,
        "--iterations",
        min=1,
        help="Presenter loop iterations after launch and binding.",
    ),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logs."),
) -> None:
    """Run an AI presenter profile."""
    configure_logging(debug)
    loaded = load_profile(resolve_profile(profile))
    typer.echo(f"Loaded profile: {loaded.id}")
    if dry_run:
        typer.echo("Dry run complete.")
        return
    if not isinstance(loaded, DesktopAppProfile):
        raise typer.BadParameter(f"Only desktop profiles can run in this MVP: {loaded.id}")
    run_desktop_profile(loaded, iterations=iterations)


@app.command()
def demo(
    profile: str = typer.Option(..., "--profile", help="Profile id or YAML path."),
    package: str = typer.Option(..., "--package", help="Material package id or YAML path."),
    flow: str = typer.Option(..., "--flow", help="Demo flow id from the material package."),
    language: str = typer.Option(
        "en",
        "--language",
        help="Presenter language, such as English or zh-CN.",
    ),
    tone: str = typer.Option(
        "professional",
        "--tone",
        help="Presenter tone, such as professional, friendly, or coach.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Load profile, package, and flow without app automation.",
    ),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logs."),
) -> None:
    """Run a synchronized material-package demo flow."""
    configure_logging(debug)
    voice_settings = resolve_voice_settings(language, tone)
    loaded_profile = load_profile(resolve_profile(profile))
    loaded_package = load_material_package(resolve_material_package(package))
    try:
        loaded_flow = loaded_package.demo_flow_by_id(flow)
    except KeyError as exc:
        raise typer.BadParameter(str(exc.args[0])) from exc

    typer.echo(f"Loaded profile: {loaded_profile.id}")
    typer.echo(f"Loaded package: {loaded_package.app_id}")
    typer.echo(f"Loaded flow: {loaded_flow.id}")
    typer.echo(f"Loaded voice: {render_voice_label(voice_settings)}")
    if not isinstance(loaded_profile, DesktopAppProfile):
        raise typer.BadParameter(f"Only desktop profiles can run in this MVP: {loaded_profile.id}")
    validate_cli_voice_profile(loaded_profile, voice_settings)
    if dry_run:
        typer.echo("Dry run complete.")
        return
    run_material_demo(loaded_profile, loaded_package, loaded_flow.id, voice=voice_settings)


@app.command()
def controller(
    profile: str = typer.Option(..., "--profile", help="Profile id or YAML path."),
    package: str = typer.Option(..., "--package", help="Material package id or YAML path."),
    flow: str = typer.Option(..., "--flow", help="Demo flow id from the material package."),
    language: str = typer.Option(
        "en",
        "--language",
        help="Presenter language, such as English or zh-CN.",
    ),
    tone: str = typer.Option(
        "professional",
        "--tone",
        help="Presenter tone, such as professional, friendly, or coach.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Load profile, package, and flow without opening the controller UI.",
    ),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logs."),
) -> None:
    """Open a small local controller for a synchronized demo flow."""
    configure_logging(debug)
    voice_settings = resolve_voice_settings(language, tone)
    loaded_profile = load_profile(resolve_profile(profile))
    loaded_package = load_material_package(resolve_material_package(package))
    try:
        loaded_flow = loaded_package.demo_flow_by_id(flow)
    except KeyError as exc:
        raise typer.BadParameter(str(exc.args[0])) from exc

    typer.echo(f"Loaded profile: {loaded_profile.id}")
    typer.echo(f"Loaded package: {loaded_package.app_id}")
    typer.echo(f"Loaded flow: {loaded_flow.id}")
    typer.echo(f"Loaded voice: {render_voice_label(voice_settings)}")
    if not isinstance(loaded_profile, DesktopAppProfile):
        raise typer.BadParameter(f"Only desktop profiles can run in this MVP: {loaded_profile.id}")
    validate_cli_voice_profile(loaded_profile, voice_settings)
    if dry_run:
        typer.echo("Controller dry run complete.")
        return
    run_controller(loaded_profile, loaded_package, loaded_flow.id, voice=voice_settings)


@app.command()
def flows(
    package: str = typer.Option(..., "--package", help="Material package id or YAML path."),
) -> None:
    """List demo flows available in a material package."""
    loaded_package = load_material_package(resolve_material_package(package))
    typer.echo(f"Package: {loaded_package.app_id}")
    for flow in loaded_package.demo_flows:
        typer.echo(f"- {flow.id}: {flow.title} ({len(flow.steps)} steps)")


@app.command()
def entrypoints(
    package: str = typer.Option(..., "--package", help="Material package id or YAML path."),
    area: str | None = typer.Option(
        None,
        "--area",
        help="Optional case-insensitive area filter.",
    ),
) -> None:
    """List operation entrypoints available in a material package."""
    loaded_package = load_material_package(resolve_material_package(package))
    typer.echo(f"Package: {loaded_package.app_id}")
    area_filter = None if area is None else area.strip().lower()
    for entrypoint in loaded_package.operation_entrypoints:
        if area_filter and area_filter not in entrypoint.area.lower():
            continue
        typer.echo(f"- {entrypoint.id}: {entrypoint.title} [{entrypoint.area}]")


@app.command("localization-report")
def localization_report(
    package: str = typer.Option(..., "--package", help="Material package id or YAML path."),
    language: str = typer.Option("zh", "--language", help="Localization language to report."),
    require_complete: bool = typer.Option(
        False,
        "--require-complete",
        help="Exit nonzero if required demo narration or Q&A localization is incomplete.",
    ),
) -> None:
    """Report material-package localization coverage without running automation."""
    loaded_package = load_material_package(resolve_material_package(package))
    report = build_localization_status(loaded_package, language=language)
    typer.echo("\n".join(render_localization_status_lines(report)))
    if require_complete and not report.required_localization_complete:
        typer.echo(f"Localization coverage incomplete for {report.language}.")
        raise typer.Exit(1)


@app.command("validation-targets")
def validation_targets(
    package: str = typer.Option(..., "--package", help="Material package id or YAML path."),
    priority: str | None = typer.Option(None, "--priority", help="Optional priority filter such as P0."),
    target: str | None = typer.Option(None, "--target", help="Optional discovered validation target id."),
    checklist: Path = typer.Option(
        DEFAULT_VALIDATION_CHECKLIST,
        "--checklist",
        help="Validation checklist markdown path.",
    ),
    evidence: Path = typer.Option(
        DEFAULT_EVIDENCE_INDEX,
        "--evidence",
        help="Evidence index markdown path.",
    ),
    include_blocked: bool = typer.Option(
        False,
        "--include-blocked",
        help="Include Do Not Execute Yet targets.",
    ),
) -> None:
    """List offline RingCentral validation targets without running automation."""
    loaded_package = load_material_package(resolve_material_package(package))
    try:
        checklist_text = checklist.read_text(encoding="utf-8")
        evidence_text = evidence.read_text(encoding="utf-8")
        catalog = discover_validation_targets(
            loaded_package,
            checklist_text=checklist_text,
            checklist_path=checklist,
            evidence_text=evidence_text,
            evidence_path=evidence,
            include_blocked=include_blocked,
        )
        lines = render_validation_target_lines(catalog, priority=priority, target_id=target)
    except OSError as exc:
        raise typer.BadParameter(str(exc)) from exc
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo("\n".join(lines))


@app.command("acceptance-draft")
def acceptance_draft(
    package: str = typer.Option(..., "--package", help="Material package id or YAML path."),
    flow: str | None = typer.Option(None, "--flow", help="Optional demo flow id."),
    entrypoint: str | None = typer.Option(
        None,
        "--entrypoint",
        help="Optional operation entrypoint id.",
    ),
    checklist_target: str | None = typer.Option(
        None,
        "--checklist-target",
        help="Optional validation checklist target label.",
    ),
    profile: str | None = typer.Option(None, "--profile", help="Optional profile text prefill."),
    tester: str | None = typer.Option(None, "--tester", help="Optional tester name prefill."),
    local_time: str | None = typer.Option(
        None,
        "--local-time",
        help="Optional local timestamp text for the draft header.",
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        help="Optional path to write the draft instead of printing it.",
    ),
) -> None:
    """Render a manual RingCentral acceptance markdown draft without automation."""
    loaded_package = load_material_package(resolve_material_package(package))
    request = AcceptanceDraftRequest(
        profile_id=profile,
        flow_id=flow,
        entrypoint_id=entrypoint,
        checklist_target=checklist_target,
        tester=tester,
        local_time=local_time,
    )
    try:
        draft = render_manual_acceptance_draft(loaded_package, request)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    if output is not None:
        _write_acceptance_draft_output(output, draft)
        typer.echo(f"Wrote acceptance draft: {output}")
        return

    typer.echo(draft, nl=False)


def _write_acceptance_draft_output(output: Path, draft: str) -> None:
    if output.name.casefold() == "acceptance-runs.md":
        raise typer.BadParameter(
            "Refusing to write acceptance draft to acceptance-runs.md; "
            "write to a separate draft file and append completed evidence manually."
        )
    if output.exists():
        raise typer.BadParameter(f"Output file already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(draft, encoding="utf-8")


@app.command()
def voices(
    profile: str | None = typer.Option(
        None,
        "--profile",
        help="Optional profile id or YAML path for compatibility checks.",
    ),
    language: str | None = typer.Option(
        None,
        "--language",
        help="Optional presenter language to check.",
    ),
    tone: str | None = typer.Option(
        None,
        "--tone",
        help="Optional presenter tone to check.",
    ),
) -> None:
    """List presenter voice choices and optionally check profile compatibility."""
    _print_voice_catalog()

    loaded_profile = None
    if profile is not None:
        loaded_profile = load_profile(resolve_profile(profile))
        typer.echo("")
        typer.echo(f"Profile: {loaded_profile.id}")
        typer.echo(f"Configured speech provider: {loaded_profile.providers.speech}")
        for _, canonical_language in PRESENTER_LANGUAGE_CHOICES:
            voice = PresenterVoiceSettings(language=canonical_language)
            label = f"{language_label(voice.language)} / {tone_label(voice.tone)}"
            try:
                validate_profile_voice(loaded_profile, voice)
            except ValueError as exc:
                typer.echo(f"- {label}: unsupported ({exc})")
            else:
                route = resolve_speech_provider_name(loaded_profile, voice)
                asset = check_voice_asset_availability(loaded_profile, voice)
                asset_detail = "" if asset is None else f"; assets {asset.status}: {asset.detail}"
                typer.echo(f"- {label}: supported via {route}{asset_detail}")

    if language is None and tone is None:
        return

    selected_voice = resolve_voice_settings(language or "en", tone or "professional")
    typer.echo("")
    typer.echo(
        f"Selected voice: {language_label(selected_voice.language)} / {tone_label(selected_voice.tone)}"
    )
    if loaded_profile is None:
        return
    try:
        validate_profile_voice(loaded_profile, selected_voice)
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(1) from exc
    route = resolve_speech_provider_name(loaded_profile, selected_voice)
    typer.echo(f"Selected voice supported via {route}.")
    asset = check_voice_asset_availability(loaded_profile, selected_voice)
    if asset is None:
        return
    if asset.status == "FAIL":
        typer.echo(f"Selected voice assets unavailable: {asset.detail}")
        raise typer.Exit(1)
    typer.echo(f"Selected voice assets available: {asset.detail}")


@app.command()
def doctor(
    profile: str = typer.Option(..., "--profile", help="Profile id or YAML path."),
    package: str | None = typer.Option(
        None,
        "--package",
        help="Optional material package id or YAML path.",
    ),
    flow: str | None = typer.Option(
        None,
        "--flow",
        help="Optional demo flow id to validate inside the material package.",
    ),
    ringcentral_config: Path | None = typer.Option(
        None,
        "--ringcentral-config",
        help="Optional RingCentralVideo config.ini path to validate DisableAffinityMask.",
    ),
    language: str | None = typer.Option(
        None,
        "--language",
        help="Optional presenter language voice check.",
    ),
    tone: str | None = typer.Option(
        None,
        "--tone",
        help="Optional presenter tone voice check.",
    ),
    require_localization: bool = typer.Option(
        False,
        "--require-localization",
        help=(
            "Fail if the selected package language lacks required demo narration "
            "or Q&A localization."
        ),
    ),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logs."),
) -> None:
    """Check profile, package, flow, and local RingCentral prerequisites."""
    configure_logging(debug)
    loaded_profile = load_profile(resolve_profile(profile))
    loaded_package = None
    if package is not None:
        loaded_package = load_material_package(resolve_material_package(package))
    voice = None
    if language is not None or tone is not None:
        voice = resolve_voice_settings(language or "en", tone or "professional")

    report = diagnose_configuration(
        profile=loaded_profile,
        material_package=loaded_package,
        flow_id=flow,
        ringcentral_config=ringcentral_config,
        voice=voice,
        require_localization=require_localization,
        localization_language=voice.language if voice is not None else None,
    )
    for line in format_diagnostic_report(report):
        typer.echo(line)
    if report.failed_count:
        raise typer.Exit(1)


def _print_voice_catalog() -> None:
    typer.echo("Languages:")
    for label, language_value in PRESENTER_LANGUAGE_CHOICES:
        aliases = _format_voice_aliases(presenter_language_aliases(language_value))
        typer.echo(f"- {label} aliases: {aliases}")

    typer.echo("Tones:")
    for label, tone_value in PRESENTER_TONE_CHOICES:
        aliases = _format_voice_aliases(presenter_tone_aliases(tone_value))
        description = presenter_tone_description(tone_value)
        typer.echo(f"- {label} aliases: {aliases} ({description})")


def _format_voice_aliases(aliases: tuple[str, ...]) -> str:
    return ", ".join(alias.encode("ascii", "backslashreplace").decode("ascii") for alias in aliases)
