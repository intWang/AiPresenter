from pathlib import Path

import pytest

from ai_presenter.config.loader import load_profile
from ai_presenter.runtime import diagnostics


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
