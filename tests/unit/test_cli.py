from pathlib import Path

from typer.testing import CliRunner

from ai_presenter.cli import app
from ai_presenter.cli import REPO_PACKAGE_DIR
from ai_presenter.cli import PACKAGE_PROFILE_DIR
from ai_presenter.cli import REPO_PROFILE_DIR
from ai_presenter.cli import resolve_material_package
from ai_presenter.cli import resolve_profile


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


def test_demo_dry_run_loads_profile_package_and_flow() -> None:
    result = CliRunner().invoke(
        app,
        [
            "demo",
            "--profile",
            "ringcentral-video",
            "--package",
            "ringcentral-video",
            "--flow",
            "meeting-controls-tour",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "Loaded profile: ringcentral-video" in result.stdout
    assert "Loaded package: ringcentral-video" in result.stdout
    assert "Loaded flow: meeting-controls-tour" in result.stdout


def test_resolve_profile_id_from_non_repo_working_directory(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    resolved = resolve_profile("ringcentral-video")

    assert resolved == REPO_PROFILE_DIR / "ringcentral-video.yaml"


def test_resolve_material_package_id_from_non_repo_working_directory(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    resolved = resolve_material_package("ringcentral-video")

    assert resolved == REPO_PACKAGE_DIR / "ringcentral-video.yaml"


def test_packaged_profile_copy_matches_repo_profile() -> None:
    assert (PACKAGE_PROFILE_DIR / "ringcentral-video.yaml").read_text(encoding="utf-8") == (
        REPO_PROFILE_DIR / "ringcentral-video.yaml"
    ).read_text(encoding="utf-8")


def test_cli_run_requires_profile() -> None:
    result = CliRunner().invoke(app, ["run"])

    assert result.exit_code != 0
    assert "--profile" in result.output


def test_run_rejects_missing_profile() -> None:
    result = CliRunner().invoke(app, ["run", "--profile", "missing", "--dry-run"])

    assert result.exit_code != 0
    assert "Profile not found: missing" in result.output
