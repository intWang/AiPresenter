from pathlib import Path

import typer

from ai_presenter.config.loader import load_profile
from ai_presenter.config.models import DesktopAppProfile
from ai_presenter.packages.loader import load_material_package
from ai_presenter.runtime.factory import run_desktop_profile
from ai_presenter.runtime.factory import run_material_demo
from ai_presenter.runtime.diagnostics import diagnose_configuration
from ai_presenter.runtime.diagnostics import format_diagnostic_report
from ai_presenter.runtime.logging import configure_logging
from ai_presenter.runtime.package_demo import demo_flow_by_id
from ai_presenter.runtime.controller import run_controller

app = typer.Typer(help="AI presenter CLI for configured app profiles.")

PACKAGE_PROFILE_DIR = Path(__file__).resolve().parent / "profiles"
REPO_PROFILE_DIR = Path(__file__).resolve().parents[2] / "profiles"
REPO_PACKAGE_DIR = Path(__file__).resolve().parents[2] / "packages"


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
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Load profile, package, and flow without app automation.",
    ),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logs."),
) -> None:
    """Run a synchronized material-package demo flow."""
    configure_logging(debug)
    loaded_profile = load_profile(resolve_profile(profile))
    loaded_package = load_material_package(resolve_material_package(package))
    try:
        loaded_flow = demo_flow_by_id(loaded_package, flow)
    except KeyError as exc:
        raise typer.BadParameter(str(exc.args[0])) from exc

    typer.echo(f"Loaded profile: {loaded_profile.id}")
    typer.echo(f"Loaded package: {loaded_package.app_id}")
    typer.echo(f"Loaded flow: {loaded_flow.id}")
    if dry_run:
        typer.echo("Dry run complete.")
        return
    if not isinstance(loaded_profile, DesktopAppProfile):
        raise typer.BadParameter(f"Only desktop profiles can run in this MVP: {loaded_profile.id}")
    run_material_demo(loaded_profile, loaded_package, loaded_flow.id)


@app.command()
def controller(
    profile: str = typer.Option(..., "--profile", help="Profile id or YAML path."),
    package: str = typer.Option(..., "--package", help="Material package id or YAML path."),
    flow: str = typer.Option(..., "--flow", help="Demo flow id from the material package."),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Load profile, package, and flow without opening the controller UI.",
    ),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logs."),
) -> None:
    """Open a small local controller for a synchronized demo flow."""
    configure_logging(debug)
    loaded_profile = load_profile(resolve_profile(profile))
    loaded_package = load_material_package(resolve_material_package(package))
    try:
        loaded_flow = demo_flow_by_id(loaded_package, flow)
    except KeyError as exc:
        raise typer.BadParameter(str(exc.args[0])) from exc

    typer.echo(f"Loaded profile: {loaded_profile.id}")
    typer.echo(f"Loaded package: {loaded_package.app_id}")
    typer.echo(f"Loaded flow: {loaded_flow.id}")
    if dry_run:
        typer.echo("Controller dry run complete.")
        return
    if not isinstance(loaded_profile, DesktopAppProfile):
        raise typer.BadParameter(f"Only desktop profiles can run in this MVP: {loaded_profile.id}")
    run_controller(loaded_profile, loaded_package, loaded_flow.id)


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
    debug: bool = typer.Option(False, "--debug", help="Enable debug logs."),
) -> None:
    """Check profile, package, flow, and local RingCentral prerequisites."""
    configure_logging(debug)
    loaded_profile = load_profile(resolve_profile(profile))
    loaded_package = None
    if package is not None:
        loaded_package = load_material_package(resolve_material_package(package))

    report = diagnose_configuration(
        profile=loaded_profile,
        material_package=loaded_package,
        flow_id=flow,
        ringcentral_config=ringcentral_config,
    )
    for line in format_diagnostic_report(report):
        typer.echo(line)
    if report.failed_count:
        raise typer.Exit(1)
