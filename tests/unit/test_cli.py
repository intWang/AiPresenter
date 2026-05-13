from typer.testing import CliRunner

from ai_presenter.cli import app


def test_cli_help_renders() -> None:
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "AI presenter" in result.stdout


def test_cli_run_profile_renders_requested_profile() -> None:
    result = CliRunner().invoke(app, ["run", "--profile", "ringcentral-video"])

    assert result.exit_code == 0
    assert "Profile requested: ringcentral-video" in result.stdout


def test_cli_run_requires_profile() -> None:
    result = CliRunner().invoke(app, ["run"])

    assert result.exit_code != 0
    assert "--profile" in result.output
