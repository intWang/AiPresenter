from pathlib import Path

from ai_presenter.config.loader import load_profile
from ai_presenter.providers.piper_provider import PiperVoiceAssets
from ai_presenter.providers.windows_speech import InstalledSapiVoice
from ai_presenter.runtime.voice import PresenterVoiceSettings
from ai_presenter.runtime.voice_assets import check_voice_asset_availability


def test_voice_asset_check_finds_chinese_sapi_voice() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))

    result = check_voice_asset_availability(
        profile,
        PresenterVoiceSettings(language="zh"),
        sapi_voice_lister=lambda: (InstalledSapiVoice("Microsoft Huihui Desktop"),),
    )

    assert result is not None
    assert result.status == "OK"
    assert "windows-sapi-zh" in result.detail


def test_voice_asset_check_reports_missing_chinese_sapi_voice() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))

    result = check_voice_asset_availability(
        profile,
        PresenterVoiceSettings(language="zh"),
        sapi_voice_lister=lambda: (InstalledSapiVoice("Microsoft Zira Desktop"),),
    )

    assert result is not None
    assert result.status == "FAIL"
    assert "Huihui" in result.detail


def test_voice_asset_check_reports_missing_piper_model(tmp_path: Path) -> None:
    profile = load_profile(Path("profiles/ringcentral-video-piper-speaker.yaml"))
    assets = PiperVoiceAssets(
        voice="en_US-lessac-medium",
        data_dir=tmp_path,
        model_path=tmp_path / "en_US-lessac-medium.onnx",
        config_path=tmp_path / "en_US-lessac-medium.onnx.json",
    )

    result = check_voice_asset_availability(
        profile,
        PresenterVoiceSettings(language="en"),
        piper_asset_resolver=lambda: assets,
        piper_module_checker=lambda: True,
    )

    assert result is not None
    assert result.status == "FAIL"
    assert "en_US-lessac-medium" in result.detail


def test_voice_asset_check_skips_fake_and_openai_routes() -> None:
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))

    assert check_voice_asset_availability(profile, PresenterVoiceSettings()) is None
