from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_presenter.cli import app
from ai_presenter.config.loader import load_profile
from ai_presenter.runtime import diagnostics
from ai_presenter.runtime.voice import PresenterVoiceSettings
from ai_presenter.runtime.voice_assets import VoiceAssetAvailability


def test_ringcentral_config_is_auto_discovered_from_running_process(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    exe_dir = tmp_path / "RingCentralVideo"
    exe_dir.mkdir()
    exe_path = exe_dir / "RingCentralVideo.exe"
    exe_path.write_text("", encoding="utf-8")
    config_path = exe_dir / "config.ini"
    config_path.write_text("DisableAffinityMask=true\n", encoding="utf-8")
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))

    monkeypatch.setattr(
        diagnostics,
        "_iter_process_executable_paths",
        lambda process_name: [exe_path],
        raising=False,
    )

    report = diagnostics.diagnose_configuration(profile=profile)

    ringcentral_check = next(
        check for check in report.checks if check.name == "RingCentral config"
    )
    assert ringcentral_check.status == "OK"
    assert str(config_path) in ringcentral_check.detail


def test_ringcentral_config_accepts_utf8_bom_ini(tmp_path: Path) -> None:
    config_path = tmp_path / "config.ini"
    config_path.write_bytes(b"\xef\xbb\xbfDisableAffinityMask=true\n")
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))

    report = diagnostics.diagnose_configuration(
        profile=profile,
        ringcentral_config=config_path,
    )

    ringcentral_check = next(
        check for check in report.checks if check.name == "RingCentral config"
    )
    assert ringcentral_check.status == "OK"


def test_diagnostics_accept_piper_provider() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-piper-speaker.yaml"))

    report = diagnostics.diagnose_configuration(profile=profile)

    providers_check = next(check for check in report.checks if check.name == "providers")
    assert providers_check.status == "OK"
    assert "speech=piper" in providers_check.detail


def test_diagnostics_reports_supported_voice(monkeypatch: pytest.MonkeyPatch) -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))
    monkeypatch.setattr(diagnostics, "check_voice_asset_availability", lambda *_args: None)

    report = diagnostics.diagnose_configuration(
        profile=profile,
        voice=PresenterVoiceSettings(language="zh-CN", tone="friendly"),
    )

    assert any(
        check.status == "OK"
        and check.name == "voice"
        and "Chinese / Friendly" in check.detail
        and "windows-sapi-zh" in check.detail
        for check in report.checks
    )


def test_diagnostics_reports_unsupported_voice() -> None:
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))

    report = diagnostics.diagnose_configuration(
        profile=profile,
        voice=PresenterVoiceSettings(language="zh-CN"),
    )

    assert report.failed_count == 1
    assert any(
        check.status == "FAIL"
        and check.name == "voice"
        and "speech provider fake" in check.detail
        for check in report.checks
    )


def test_diagnostics_reports_voice_assets_after_supported_voice(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))
    monkeypatch.setattr(
        diagnostics,
        "check_voice_asset_availability",
        lambda *_args, **_kwargs: VoiceAssetAvailability(
            status="OK",
            route="windows-sapi-zh",
            detail="speech=windows-sapi-zh found installed SAPI voice matching Huihui",
        ),
    )

    report = diagnostics.diagnose_configuration(
        profile=profile,
        voice=PresenterVoiceSettings(language="zh"),
    )

    assert any(check.status == "OK" and check.name == "voice assets" for check in report.checks)


def test_diagnostics_fails_for_missing_voice_assets(monkeypatch: pytest.MonkeyPatch) -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))
    monkeypatch.setattr(
        diagnostics,
        "check_voice_asset_availability",
        lambda *_args, **_kwargs: VoiceAssetAvailability(
            status="FAIL",
            route="windows-sapi-zh",
            detail="speech=windows-sapi-zh requires installed SAPI voice matching Huihui",
        ),
    )

    report = diagnostics.diagnose_configuration(
        profile=profile,
        voice=PresenterVoiceSettings(language="zh"),
    )

    assert report.failed_count == 1
    assert any("Huihui" in check.detail for check in report.checks if check.name == "voice assets")


def test_diagnostics_reports_piper_voice_assets(monkeypatch: pytest.MonkeyPatch) -> None:
    profile = load_profile(Path("profiles/ringcentral-video-piper-speaker.yaml"))
    monkeypatch.setattr(
        diagnostics,
        "check_voice_asset_availability",
        lambda *_args, **_kwargs: VoiceAssetAvailability(
            status="OK",
            route="piper",
            detail="speech=piper found local Piper voice assets for en_US-lessac-medium",
        ),
    )

    report = diagnostics.diagnose_configuration(
        profile=profile,
        voice=PresenterVoiceSettings(language="en"),
    )

    assert any(
        check.status == "OK"
        and check.name == "voice assets"
        and "en_US-lessac-medium" in check.detail
        for check in report.checks
    )


def test_diagnostics_fails_for_missing_piper_voice_assets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile = load_profile(Path("profiles/ringcentral-video-piper-speaker.yaml"))
    monkeypatch.setattr(
        diagnostics,
        "check_voice_asset_availability",
        lambda *_args, **_kwargs: VoiceAssetAvailability(
            status="FAIL",
            route="piper",
            detail="speech=piper requires local Piper voice assets for en_US-lessac-medium",
        ),
    )

    report = diagnostics.diagnose_configuration(
        profile=profile,
        voice=PresenterVoiceSettings(language="en"),
    )

    assert report.failed_count == 1
    assert any(
        "en_US-lessac-medium" in check.detail
        for check in report.checks
        if check.name == "voice assets"
    )


def test_doctor_uses_unified_missing_flow_message(monkeypatch: pytest.MonkeyPatch) -> None:
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
            "missing-flow",
        ],
    )

    assert result.exit_code == 1
    assert (
        "[FAIL] demo flow: Unknown demo flow: missing-flow. Available flows:"
        in result.stdout
    )
