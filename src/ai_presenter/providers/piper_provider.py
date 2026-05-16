import importlib.util
import subprocess
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from os import environ
from pathlib import Path

from ai_presenter.providers.base import SpeechAudio

PiperRunner = Callable[[list[str], float], subprocess.CompletedProcess[str]]


@dataclass(frozen=True)
class PiperVoiceAssets:
    voice: str
    data_dir: Path
    model_path: Path
    config_path: Path


class PiperSpeechProvider:
    def __init__(
        self,
        *,
        voice: str = "en_US-lessac-medium",
        data_dir: Path | None = None,
        download_dir: Path | None = None,
        timeout_seconds: float = 30,
        runner: PiperRunner | None = None,
        temp_dir: Path | None = None,
    ) -> None:
        self._voice = _require_nonblank(voice, "Piper voice cannot be blank.")
        self._data_dir = data_dir or _default_data_dir()
        self._download_dir = download_dir
        self._timeout_seconds = timeout_seconds
        self._runner = runner or _run_piper
        self._temp_dir = temp_dir

    def synthesize(self, text: str) -> SpeechAudio:
        speech_text = text.strip()
        if not speech_text:
            raise ValueError("Speech text cannot be blank.")

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav",
            dir=self._temp_dir,
        ) as output_file:
            output_path = Path(output_file.name)

        try:
            command = self._command(output_path, speech_text)
            result = self._runner(command, self._timeout_seconds)
            if result.returncode != 0:
                detail = result.stderr.strip() or result.stdout.strip() or "unknown error"
                raise RuntimeError(f"Piper TTS failed: {detail}")
            data = output_path.read_bytes()
            if len(data) <= 46:
                raise RuntimeError("Piper TTS returned empty audio.")
            return SpeechAudio(
                data=data,
                mime_type="audio/wav",
                sample_rate=0,
                channels=1,
            )
        finally:
            output_path.unlink(missing_ok=True)

    def _command(self, output_path: Path, text: str) -> list[str]:
        command = [sys.executable, "-m", "piper", "-m", self._voice, "-f", str(output_path)]
        if self._data_dir is not None:
            command.extend(["--data-dir", str(self._data_dir)])
        if self._download_dir is not None:
            command.extend(["--download-dir", str(self._download_dir)])
        command.extend(["--", text])
        return command


def _run_piper(command: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("Python executable was not found while running Piper TTS.") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Piper TTS timed out.") from exc


def default_piper_voice_assets(
    voice: str = "en_US-lessac-medium",
    data_dir: Path | None = None,
) -> PiperVoiceAssets:
    normalized_voice = _require_nonblank(voice, "Piper voice cannot be blank.")
    root = data_dir or _default_data_dir()
    return PiperVoiceAssets(
        voice=normalized_voice,
        data_dir=root,
        model_path=root / f"{normalized_voice}.onnx",
        config_path=root / f"{normalized_voice}.onnx.json",
    )


def piper_voice_assets_available(assets: PiperVoiceAssets) -> bool:
    return assets.model_path.is_file() and assets.config_path.is_file()


def piper_module_available(module_name: str = "piper") -> bool:
    return importlib.util.find_spec(module_name) is not None


def _require_nonblank(value: str, message: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(message)
    return normalized


def _default_data_dir() -> Path:
    configured = environ.get("AI_PRESENTER_PIPER_DATA_DIR")
    if configured is not None and configured.strip():
        return Path(configured.strip())
    return Path.home() / ".cache" / "ai-presenter" / "piper-voices"
