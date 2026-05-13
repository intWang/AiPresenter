from pathlib import Path

import pytest
from pydantic import ValidationError

from ai_presenter.config.loader import load_profile, profile_to_public_dict
from ai_presenter.config.models import AudioOutputMode, ProfileType


def test_load_ringcentral_profile() -> None:
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))

    assert profile.id == "ringcentral-video"
    assert profile.type is ProfileType.DESKTOP
    assert profile.launch.app_process == "RingCentralDevelop"
    assert profile.bind.process == "RingCentralVideo"
    assert profile.bind.window_class == "RingCentralVideoClass"
    assert profile.audio.output is AudioOutputMode.BOTH


def test_load_ringcentral_openai_example_profile() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-openai.example.yaml"))

    assert profile.id == "ringcentral-video-openai"
    assert profile.providers.narration == "openai"
    assert profile.providers.speech == "openai"


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


@pytest.mark.parametrize("output", ["virtual_mic", "both"])
@pytest.mark.parametrize("virtual_mic_device", [None, "", "   "])
def test_requires_virtual_mic_device_for_virtual_mic_output(
    tmp_path: Path,
    output: str,
    virtual_mic_device: str | None,
) -> None:
    profile_path = tmp_path / "bad-audio.yaml"
    virtual_mic_line = (
        ""
        if virtual_mic_device is None
        else f'  virtualMicDevice: "{virtual_mic_device}"\n'
    )
    profile_path.write_text(
        f"""
id: bad-audio
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
  output: {output}
{virtual_mic_line}providers:
  vision: fake
  narration: fake
  speech: fake
""",
        encoding="utf-8",
    )

    with pytest.raises(ValidationError):
        load_profile(profile_path)


def test_loads_browser_profile_with_browser_launch_and_bind(tmp_path: Path) -> None:
    profile_path = tmp_path / "browser.yaml"
    profile_path.write_text(
        """
id: browser-demo
type: browser
launch:
  url: https://example.test/meeting
bind:
  urlPattern: https://example.test/*
  title: Example Meeting
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
  output: speaker
providers:
  vision: fake
  narration: fake
  speech: fake
""",
        encoding="utf-8",
    )

    profile = load_profile(profile_path)

    assert profile.type is ProfileType.BROWSER
    assert profile.launch.url == "https://example.test/meeting"
    assert profile.launch.steps == []
    assert profile.bind.url_pattern == "https://example.test/*"
    assert profile.bind.title == "Example Meeting"


def test_launch_step_action_and_target_are_trimmed(tmp_path: Path) -> None:
    profile_path = tmp_path / "trimmed-launch-step.yaml"
    profile_path.write_text(
        """
id: launch-step-demo
type: browser
launch:
  url: https://example.test/meeting
  steps:
    - action: " clickTab "
      target: " Video "
bind:
  title: Example Meeting
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
  output: speaker
providers:
  vision: fake
  narration: fake
  speech: fake
""",
        encoding="utf-8",
    )

    profile = load_profile(profile_path)

    assert profile.launch.steps[0].action == "clickTab"
    assert profile.launch.steps[0].target == "Video"


def test_rejects_blank_launch_action(tmp_path: Path) -> None:
    profile_path = tmp_path / "blank-launch-action.yaml"
    profile_path.write_text(
        """
id: launch-step-demo
type: browser
launch:
  url: https://example.test/meeting
  steps:
    - action: "   "
bind:
  title: Example Meeting
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
  output: speaker
providers:
  vision: fake
  narration: fake
  speech: fake
""",
        encoding="utf-8",
    )

    with pytest.raises(ValidationError, match="launch action cannot be blank"):
        load_profile(profile_path)


def test_rejects_blank_launch_target(tmp_path: Path) -> None:
    profile_path = tmp_path / "blank-launch-target.yaml"
    profile_path.write_text(
        """
id: launch-step-demo
type: browser
launch:
  url: https://example.test/meeting
  steps:
    - action: clickTab
      target: "   "
bind:
  title: Example Meeting
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
  output: speaker
providers:
  vision: fake
  narration: fake
  speech: fake
""",
        encoding="utf-8",
    )

    with pytest.raises(ValidationError, match="launch target cannot be blank"):
        load_profile(profile_path)


def test_profile_provider_fields_are_trimmed(tmp_path: Path) -> None:
    profile_path = tmp_path / "providers-trimmed.yaml"
    profile_path.write_text(
        """
id: provider-demo
type: browser
launch:
  url: https://example.test/meeting
bind:
  title: Example Meeting
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
  output: speaker
providers:
  vision: " fake-vision "
  narration: " fake-narration "
  speech: " fake-speech "
""",
        encoding="utf-8",
    )

    profile = load_profile(profile_path)

    assert profile.providers.vision == "fake-vision"
    assert profile.providers.narration == "fake-narration"
    assert profile.providers.speech == "fake-speech"


@pytest.mark.parametrize("provider_field", ["vision", "narration", "speech"])
def test_rejects_blank_profile_provider_field(tmp_path: Path, provider_field: str) -> None:
    profile_path = tmp_path / "blank-provider.yaml"
    providers = {
        "vision": "fake",
        "narration": "fake",
        "speech": "fake",
        provider_field: "   ",
    }
    profile_path.write_text(
        f"""
id: provider-demo
type: browser
launch:
  url: https://example.test/meeting
bind:
  title: Example Meeting
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
  output: speaker
providers:
  vision: "{providers["vision"]}"
  narration: "{providers["narration"]}"
  speech: "{providers["speech"]}"
""",
        encoding="utf-8",
    )

    with pytest.raises(ValidationError, match=provider_field):
        load_profile(profile_path)


def test_rejects_browser_profile_without_bind_target(tmp_path: Path) -> None:
    profile_path = tmp_path / "browser-without-bind-target.yaml"
    profile_path.write_text(
        """
id: browser-demo
type: browser
launch:
  url: https://example.test/meeting
bind: {}
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
  output: speaker
providers:
  vision: fake
  narration: fake
  speech: fake
""",
        encoding="utf-8",
    )

    with pytest.raises(ValidationError):
        load_profile(profile_path)


def test_profile_to_public_dict_uses_aliases() -> None:
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))

    public = profile_to_public_dict(profile)

    assert public["launch"]["appProcess"] == "RingCentralDevelop"
    assert "app_process" not in public["launch"]
    assert public["bind"]["windowClass"] == "RingCentralVideoClass"
    assert "window_class" not in public["bind"]
    assert public["audio"]["virtualMicDevice"] == "VB-CABLE Input"
    assert public["audio"]["output"] == "both"


def test_rejects_non_mapping_yaml(tmp_path: Path) -> None:
    profile_path = tmp_path / "list.yaml"
    profile_path.write_text("- not\n- a\n- mapping\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Profile must be a YAML mapping"):
        load_profile(profile_path)
