import subprocess
import sys
import wave
from pathlib import Path

import pytest

from ai_presenter.providers.piper_provider import default_piper_voice_assets
from ai_presenter.providers.piper_provider import piper_voice_assets_available
from ai_presenter.providers.piper_provider import PiperSpeechProvider


def write_wav(path: Path) -> None:
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16_000)
        wav.writeframes(b"\x00\x00" * 1600)


def test_piper_provider_returns_wav_audio(tmp_path: Path) -> None:
    calls: list[list[str]] = []

    def runner(command: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        output_path = Path(command[command.index("-f") + 1])
        write_wav(output_path)
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    provider = PiperSpeechProvider(
        voice="en_US-lessac-medium",
        data_dir=tmp_path / "voices",
        runner=runner,
        temp_dir=tmp_path,
    )

    audio = provider.synthesize("Hello from Piper.")

    assert audio.mime_type == "audio/wav"
    assert len(audio.data) > 46
    assert calls[0][0:3] == [sys.executable, "-m", "piper"]
    assert "en_US-lessac-medium" in calls[0]
    assert "--data-dir" in calls[0]
    assert str(tmp_path / "voices") in calls[0]
    assert calls[0][-1] == "Hello from Piper."


def test_piper_provider_rejects_blank_text(tmp_path: Path) -> None:
    provider = PiperSpeechProvider(temp_dir=tmp_path)

    with pytest.raises(ValueError, match="Speech text cannot be blank"):
        provider.synthesize("   ")


def test_piper_provider_reports_failed_command(tmp_path: Path) -> None:
    def runner(command: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 2, stdout="", stderr="missing model")

    provider = PiperSpeechProvider(runner=runner, temp_dir=tmp_path)

    with pytest.raises(RuntimeError, match="missing model"):
        provider.synthesize("Hello.")


def test_default_piper_voice_assets_use_provider_data_dir(tmp_path: Path) -> None:
    assets = default_piper_voice_assets(data_dir=tmp_path)

    assert assets.voice == "en_US-lessac-medium"
    assert assets.model_path == tmp_path / "en_US-lessac-medium.onnx"
    assert assets.config_path == tmp_path / "en_US-lessac-medium.onnx.json"


def test_piper_voice_assets_available_requires_model_and_config(tmp_path: Path) -> None:
    assets = default_piper_voice_assets(data_dir=tmp_path)
    assert piper_voice_assets_available(assets) is False

    assets.model_path.write_text("model", encoding="utf-8")
    assert piper_voice_assets_available(assets) is False

    assets.config_path.write_text("{}", encoding="utf-8")
    assert piper_voice_assets_available(assets) is True
