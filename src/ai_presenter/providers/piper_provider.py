import subprocess
import tempfile
from collections.abc import Callable
from pathlib import Path

from ai_presenter.providers.base import SpeechAudio

PiperRunner = Callable[[list[str], float], subprocess.CompletedProcess[str]]


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
        self._data_dir = data_dir
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
        command = ["python", "-m", "piper", "-m", self._voice, "-f", str(output_path)]
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


def _require_nonblank(value: str, message: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(message)
    return normalized
