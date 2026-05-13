from pathlib import Path

from typer.testing import CliRunner

from ai_presenter.cli import app


def test_cli_help_renders() -> None:
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "AI presenter" in result.stdout


def test_run_dry_run_loads_profile() -> None:
    result = CliRunner().invoke(app, ["run", "--profile", "ringcentral-video", "--dry-run"])

    assert result.exit_code == 0
    assert "Loaded profile: ringcentral-video" in result.stdout
    assert "Dry run complete." in result.stdout


def test_run_dry_run_loads_profile_path() -> None:
    profile_path = Path("profiles/ringcentral-video.yaml")

    result = CliRunner().invoke(app, ["run", "--profile", str(profile_path), "--dry-run"])

    assert result.exit_code == 0
    assert "Loaded profile: ringcentral-video" in result.stdout


def test_cli_run_requires_profile() -> None:
    result = CliRunner().invoke(app, ["run"])

    assert result.exit_code != 0
    assert "--profile" in result.output


def test_run_rejects_missing_profile() -> None:
    result = CliRunner().invoke(app, ["run", "--profile", "missing", "--dry-run"])

    assert result.exit_code != 0
    assert "Profile not found: missing" in result.output
