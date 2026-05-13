from pathlib import Path

import typer

from ai_presenter.config.loader import load_profile
from ai_presenter.config.models import DesktopAppProfile
from ai_presenter.runtime.factory import run_desktop_profile
from ai_presenter.runtime.logging import configure_logging

app = typer.Typer(help="AI presenter CLI for configured app profiles.")


@app.callback()
def main() -> None:
    """AI presenter CLI for configured app profiles."""


def resolve_profile(profile: str) -> Path:
    candidate = Path(profile)
    if candidate.exists():
        return candidate
    bundled = Path("profiles") / f"{profile}.yaml"
    if bundled.exists():
        return bundled
    raise typer.BadParameter(f"Profile not found: {profile}")


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
