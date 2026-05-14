import json
import subprocess
import tempfile
from collections.abc import Callable, Sequence
from pathlib import Path

from ai_presenter.domain.state import MeetingState, PresenterEvent

Runner = Callable[..., subprocess.CompletedProcess[str]]


class CodexCliNarrationProvider:
    def __init__(
        self,
        *,
        executable: str = "codex",
        model: str | None = None,
        timeout_seconds: float = 120,
        runner: Runner = subprocess.run,
    ) -> None:
        self._executable = _require_nonblank(executable, "Codex executable cannot be blank.")
        self._model = _normalize_optional(model)
        self._timeout_seconds = timeout_seconds
        self._runner = runner

    def narrate(self, state: MeetingState, events: list[PresenterEvent]) -> str:
        prompt = _build_codex_prompt(state, events)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as output_file:
            output_path = Path(output_file.name)

        try:
            completed = self._runner(
                self._command(output_path),
                input=prompt,
                text=True,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=self._timeout_seconds,
            )
            if completed.returncode != 0:
                stderr = (completed.stderr or completed.stdout or "").strip()
                raise RuntimeError(f"Codex CLI narration failed: {stderr}")

            narration = output_path.read_text(encoding="utf-8").strip()
            if not narration:
                raise RuntimeError("Codex CLI narration returned blank output.")
            return narration
        finally:
            output_path.unlink(missing_ok=True)

    def _command(self, output_path: Path) -> Sequence[str]:
        command = [
            self._executable,
            "exec",
            "--ephemeral",
            "--sandbox",
            "read-only",
            "--color",
            "never",
            "--output-last-message",
            str(output_path),
        ]
        if self._model is not None:
            command.extend(["--model", self._model])
        command.append("-")
        return command


def _build_codex_prompt(state: MeetingState, events: list[PresenterEvent]) -> str:
    payload: dict[str, object] = {
        "meeting_ui_state": {
            "meeting_joined": state.meeting_joined,
            "mic_muted": state.mic_muted,
            "camera_off": state.camera_off,
            "active_dialog": state.active_dialog,
            "participant_count": state.participant_count,
            "connection_warning": state.connection_warning,
            "confidence": state.confidence,
        },
        "verified_events": [
            {
                "type": event.type,
                "payload": dict(event.payload),
                "confidence": event.confidence,
                "occurred_at": event.occurred_at.isoformat(),
            }
            for event in events
        ],
    }
    return (
        "You are the narration voice for an AI presenter observing RingCentral meeting UI.\n"
        "Use only the verified UI state/events in the JSON payload. Do not infer shared-screen "
        "content, participant identity, meeting purpose, or private content. Return one concise "
        "English narration sentence only, with no Markdown or explanation.\n\n"
        f"{json.dumps(payload, default=str, ensure_ascii=False, sort_keys=True)}"
    )


def _require_nonblank(value: str, message: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(message)
    return normalized


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None
