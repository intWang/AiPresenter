import subprocess
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pytest

from ai_presenter.config.loader import load_profile
from ai_presenter.domain.state import MeetingState, PresenterEvent
from ai_presenter.providers.codex_cli import CodexCliNarrationProvider
from ai_presenter.runtime.presenter_context import PresenterContext
from ai_presenter.runtime.presenter_context import PresenterSkill
from ai_presenter.runtime.presenter_context import load_presenter_context


def test_codex_cli_narration_reads_last_message_file() -> None:
    calls: list[dict[str, Any]] = []

    def runner(command: Sequence[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        calls.append({"command": command, **kwargs})
        output_path = Path(command[-2])
        output_path.write_text("会议已经开始，当前麦克风已静音。", encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, stdout="noise", stderr="")

    provider = CodexCliNarrationProvider(executable="codex-test", runner=runner)

    narration = provider.narrate(
        MeetingState(meeting_joined=True, mic_muted=True, confidence=0.9),
        [PresenterEvent("meeting_joined", {}, 0.9)],
    )

    assert narration == "会议已经开始，当前麦克风已静音。"
    assert calls[0]["command"][:5] == [
        "codex-test",
        "exec",
        "--ephemeral",
        "--sandbox",
        "read-only",
    ]
    assert calls[0]["command"][-1] == "-"
    assert "meeting_joined" in calls[0]["input"]


def test_codex_cli_prompt_includes_presenter_soul_and_memory() -> None:
    calls: list[dict[str, Any]] = []

    def runner(command: Sequence[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        calls.append({"command": command, **kwargs})
        output_path = Path(command[-2])
        output_path.write_text("Meeting joined.", encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    provider = CodexCliNarrationProvider(
        runner=runner,
        presenter_context=PresenterContext(
            soul="Soul marker: professional presenter identity.",
            memory="Memory marker: speak in English with tighter transitions.",
            skills=(
                PresenterSkill(name="live-explainer", content="Skill marker: recover gracefully."),
                PresenterSkill(
                    name="ringcentral-safety",
                    content="Skill marker: never read chat or participant names by default.",
                ),
            ),
        ),
    )

    provider.narrate(MeetingState(confidence=0.9), [PresenterEvent("meeting_joined", {}, 0.9)])

    assert "Soul marker: professional presenter identity." in calls[0]["input"]
    assert "Memory marker: speak in English with tighter transitions." in calls[0]["input"]
    assert "Skill marker: recover gracefully." in calls[0]["input"]
    assert "Presenter skill - ringcentral-safety:" in calls[0]["input"]
    assert "Skill marker: never read chat or participant names by default." in calls[0]["input"]


def test_codex_cli_prompt_includes_loaded_ringcentral_safety_skill() -> None:
    calls: list[dict[str, Any]] = []

    def runner(command: Sequence[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        calls.append({"command": command, **kwargs})
        output_path = Path(command[-2])
        output_path.write_text("Meeting joined.", encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    profile = load_profile(Path("profiles/ringcentral-video.yaml"))
    provider = CodexCliNarrationProvider(
        runner=runner,
        presenter_context=load_presenter_context(profile.narration),
    )

    provider.narrate(MeetingState(confidence=0.9), [PresenterEvent("meeting_joined", {}, 0.9)])

    assert "Presenter skill - ringcentral-safety:" in calls[0]["input"]
    assert "RingCentral Video safety guardian" in calls[0]["input"]


def test_codex_cli_narration_raises_on_failure() -> None:
    def runner(command: Sequence[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 1, stdout="", stderr="auth failed")

    provider = CodexCliNarrationProvider(runner=runner)

    with pytest.raises(RuntimeError, match="auth failed"):
        provider.narrate(MeetingState(confidence=0.9), [PresenterEvent("meeting_joined", {}, 0.9)])


def test_codex_cli_narration_rejects_blank_executable() -> None:
    with pytest.raises(ValueError, match="executable"):
        CodexCliNarrationProvider(executable=" ")
