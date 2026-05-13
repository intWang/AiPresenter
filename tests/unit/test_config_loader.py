from pathlib import Path

import pytest
from pydantic import ValidationError

from ai_presenter.config.loader import load_profile
from ai_presenter.config.models import AudioOutputMode, ProfileType


def test_load_ringcentral_profile() -> None:
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))

    assert profile.id == "ringcentral-video"
    assert profile.type is ProfileType.DESKTOP
    assert profile.launch.app_process == "RingCentralDevelop"
    assert profile.bind.process == "RingCentralVideo"
    assert profile.bind.window_class == "RingCentralVideoClass"
    assert profile.audio.output is AudioOutputMode.BOTH


def test_rejects_unknown_audio_mode(tmp_path: Path) -> None:
    profile_path = tmp_path / "bad.yaml"
    profile_path.write_text(
        """
id: bad
type: desktop
launch:
  appProcess: App
  requireAlreadyLoggedIn: true
  steps: []
bind:
  process: Proc
  windowClass: Class
observe:
  intervalMs: 1000
  sources: [screenshot]
events: []
narration:
  style: concise_presenter
  maxSentences: 2
  minSecondsBetweenUtterances: 4
  repeatCooldownSeconds: 30
  confidenceThreshold: 0.75
  forbidSharedScreenInterpretation: true
audio:
  output: invalid
providers:
  vision: fake
  narration: fake
  speech: fake
""",
        encoding="utf-8",
    )

    with pytest.raises(ValidationError):
        load_profile(profile_path)
