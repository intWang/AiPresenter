from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_presenter.cli import app
from ai_presenter.cli import REPO_PACKAGE_DIR
from ai_presenter.cli import PACKAGE_PROFILE_DIR
from ai_presenter.cli import REPO_PROFILE_DIR
from ai_presenter.cli import resolve_material_package
from ai_presenter.cli import resolve_profile
from ai_presenter.runtime import diagnostics


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


def test_demo_reports_available_flows_when_flow_is_missing() -> None:
    result = CliRunner().invoke(
        app,
        [
            "demo",
            "--profile",
            "ringcentral-video",
            "--package",
            "ringcentral-video",
            "--flow",
            "missing-flow",
            "--dry-run",
        ],
    )

    assert result.exit_code != 0
    assert "Unknown demo flow: missing-flow" in result.output
    assert "Available flows:" in result.output
    assert "meeting-control-map-demo" in result.output


def test_controller_dry_run_loads_profile_package_and_flow() -> None:
    result = CliRunner().invoke(
        app,
        [
            "controller",
            "--profile",
            "ringcentral-video-bind-speaker",
            "--package",
            "ringcentral-video",
            "--flow",
            "meeting-control-map-demo",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "Loaded profile: ringcentral-video-bind-speaker" in result.stdout
    assert "Loaded package: ringcentral-video" in result.stdout
    assert "Loaded flow: meeting-control-map-demo" in result.stdout
    assert "Controller dry run complete." in result.stdout


def test_flows_lists_material_package_demo_flows() -> None:
    result = CliRunner().invoke(app, ["flows", "--package", "ringcentral-video"])

    assert result.exit_code == 0
    assert "Package: ringcentral-video" in result.stdout
    assert "- meeting-control-map-demo: Meeting Control Map" in result.stdout
    assert "steps" in result.stdout


def test_entrypoints_lists_material_package_entrypoints_by_area() -> None:
    result = CliRunner().invoke(
        app,
        ["entrypoints", "--package", "ringcentral-video", "--area", "Meeting toolbar"],
    )

    assert result.exit_code == 0
    assert "Package: ringcentral-video" in result.stdout
    assert "ringcentral.video.toolbar.audio" in result.stdout
    assert "ringcentral.video.toolbar.leave" in result.stdout
    assert "ringcentral.video.top.meeting-info" not in result.stdout


def test_doctor_loads_profile_package_and_flow(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(diagnostics, "_iter_process_executable_paths", lambda process_name: [])

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--profile",
            "ringcentral-video-bind-speaker",
            "--package",
            "ringcentral-video",
            "--flow",
            "meeting-control-map-demo",
        ],
    )

    assert result.exit_code == 0
    assert "[OK] profile: loaded ringcentral-video-bind-speaker" in result.stdout
    assert "[OK] package: loaded ringcentral-video" in result.stdout
    assert "[OK] package profile support" in result.stdout
    assert "[OK] explainer coverage" in result.stdout
    assert "[OK] demo flow: meeting-control-map-demo" in result.stdout
    assert "[OK] presenter context" in result.stdout
    assert "[WARN] RingCentral config" in result.stdout
    assert "Doctor completed:" in result.stdout


def test_doctor_rejects_package_that_does_not_support_profile(tmp_path: Path) -> None:
    package_path = tmp_path / "demo-package.yaml"
    package_path.write_text(
        """
appId: demo
appName: Demo
version: 1
profileIds: [other-profile]
operationEntrypoints:
  - id: demo.overview
    title: Overview
    area: Main
    purpose: Explain the surface
    openSteps: []
demoFlows: []
manualControls: []
""",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        ["doctor", "--profile", "ringcentral-video-bind-speaker", "--package", str(package_path)],
    )

    assert result.exit_code == 1
    assert "[FAIL] package profile support" in result.stdout
    assert "does not list profile ringcentral-video-bind-speaker" in result.stdout


def test_doctor_accepts_ringcentral_config_with_disable_affinity_mask(tmp_path: Path) -> None:
    config_path = tmp_path / "config.ini"
    config_path.write_text("[General]\nDisableAffinityMask=true\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--profile",
            "ringcentral-video-bind-speaker",
            "--ringcentral-config",
            str(config_path),
        ],
    )

    assert result.exit_code == 0
    assert "[OK] RingCentral config" in result.stdout
    assert "DisableAffinityMask=true" in result.stdout


def test_doctor_rejects_ringcentral_config_without_disable_affinity_mask(tmp_path: Path) -> None:
    config_path = tmp_path / "config.ini"
    config_path.write_text("DisableAffinityMask=false\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--profile",
            "ringcentral-video-bind-speaker",
            "--ringcentral-config",
            str(config_path),
        ],
    )

    assert result.exit_code == 1
    assert "[FAIL] RingCentral config" in result.stdout
    assert "expected DisableAffinityMask=true" in result.stdout


def test_doctor_rejects_openai_profile_without_required_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("AI_PRESENTER_OPENAI_NARRATION_MODEL", raising=False)
    monkeypatch.setattr(diagnostics, "_iter_process_executable_paths", lambda process_name: [])

    result = CliRunner().invoke(
        app,
        ["doctor", "--profile", "profiles/ringcentral-video-openai.example.yaml"],
    )

    assert result.exit_code == 1
    assert "[FAIL] provider environment" in result.stdout
    assert "OPENAI_API_KEY" in result.stdout
    assert "AI_PRESENTER_OPENAI_NARRATION_MODEL" in result.stdout


def test_resolve_profile_id_from_non_repo_working_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    resolved = resolve_profile("ringcentral-video")

    assert resolved == REPO_PROFILE_DIR / "ringcentral-video.yaml"


def test_resolve_material_package_id_from_non_repo_working_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
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
