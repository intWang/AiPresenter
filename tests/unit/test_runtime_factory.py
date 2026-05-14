from collections.abc import Iterable
from pathlib import Path

import pytest

from ai_presenter.config.loader import load_profile
from ai_presenter.config.models import BrowserAppProfile, DesktopAppProfile, ObservationSource
from ai_presenter.domain.state import RawObservation, WindowMetadata
from ai_presenter.desktop.base import WindowHandle
from ai_presenter.packages.models import MaterialPackage
from ai_presenter.runtime import factory as factory_module
from ai_presenter.runtime.factory import create_adapter
from ai_presenter.runtime.factory import create_fake_provider_registry
from ai_presenter.runtime.factory import create_provider_registry
from ai_presenter.runtime.factory import run_desktop_profile
from ai_presenter.runtime.factory import run_material_demo
from ai_presenter.runtime.sync import StepRunResult


def test_fake_provider_registry_satisfies_ringcentral_profile() -> None:
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))
    registry = create_fake_provider_registry()

    assert registry.vision(profile.providers.vision)
    assert registry.narration(profile.providers.narration)
    assert registry.speech(profile.providers.speech)


def test_fake_provider_registry_reports_joined_meeting_for_smoke_runs() -> None:
    registry = create_fake_provider_registry()
    observation = RawObservation(
        metadata=WindowMetadata(
            process="RingCentralVideo",
            pid=10,
            window_class="RingCentralVideoClass",
            title="RingCentral Video",
            bounds=(0, 0, 1000, 800),
        )
    )

    state = registry.vision("fake").recognize(observation)

    assert state.meeting_joined is True


def test_provider_registry_does_not_require_openai_for_fake_profile(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))

    registry = create_provider_registry(profile)

    assert registry.narration(profile.providers.narration)
    assert registry.speech(profile.providers.speech)


def test_provider_registry_supports_codex_cli_speaker_profile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    profile = load_profile(Path("profiles/ringcentral-video-codex-cli-speaker.yaml"))

    registry = create_provider_registry(profile)

    assert registry.narration(profile.providers.narration).__class__.__name__ == (
        "CodexCliNarrationProvider"
    )
    assert registry.speech(profile.providers.speech).__class__.__name__ == (
        "WindowsSapiSpeechProvider"
    )


def test_provider_registry_supports_english_windows_sapi_profile() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))

    registry = create_provider_registry(profile)

    assert profile.providers.speech == "windows-sapi-en"
    assert registry.speech(profile.providers.speech).__class__.__name__ == (
        "WindowsSapiSpeechProvider"
    )


def test_create_adapter_returns_ringcentral_adapter_for_reference_profile() -> None:
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))
    adapter = create_adapter(profile)

    assert adapter.__class__.__name__ == "RingCentralAdapter"


def test_create_adapter_returns_ringcentral_adapter_for_openai_profile() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-openai.example.yaml"))
    adapter = create_adapter(profile)

    assert adapter.__class__.__name__ == "RingCentralAdapter"


def test_create_adapter_rejects_unknown_profile() -> None:
    profile = BrowserAppProfile.model_validate(
        {
            "id": "browser-demo",
            "type": "browser",
            "launch": {"url": "https://example.com", "steps": []},
            "bind": {"title": "Example"},
            "observe": {"intervalMs": 1000, "sources": ["screenshot"]},
            "events": [],
            "narration": {
                "style": "concise_presenter",
                "maxSentences": 2,
                "minSecondsBetweenUtterances": 4,
                "repeatCooldownSeconds": 30,
                "confidenceThreshold": 0.75,
                "forbidSharedScreenInterpretation": True,
            },
            "audio": {"output": "speaker"},
            "providers": {"vision": "fake", "narration": "fake", "speech": "fake"},
        }
    )

    with pytest.raises(ValueError, match="No adapter"):
        create_adapter(profile)


def test_ringcentral_profile_is_desktop_for_runtime() -> None:
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))

    assert isinstance(profile, DesktopAppProfile)


def test_run_desktop_profile_launches_and_runs_presenter_iterations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))
    assert isinstance(profile, DesktopAppProfile)
    handle = object()
    calls: list[object] = []
    sleeps: list[float] = []

    class FakeRunner:
        def launch_and_bind(self) -> object:
            return handle

    class FakePresenter:
        def run_once(self, captured_handle: object) -> None:
            calls.append(captured_handle)

    monkeypatch.setattr(factory_module, "WindowsDesktopDriver", object)
    monkeypatch.setattr(factory_module, "create_profile_runner", lambda _profile, _desktop: FakeRunner())
    monkeypatch.setattr(factory_module, "create_presenter_loop", lambda *_args: FakePresenter())
    monkeypatch.setattr("ai_presenter.runtime.factory.time.sleep", sleeps.append)

    run_desktop_profile(profile, registry=create_fake_provider_registry(), iterations=2)

    assert calls == [handle, handle]
    assert sleeps == [profile.observe.interval_ms / 1000]


def test_run_material_demo_captures_state_before_steps_and_rewrites_empty_room_invite(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))
    assert isinstance(profile, DesktopAppProfile)
    handle = WindowHandle("RingCentralVideo", 123, "RingCentralVideoClass", "RingCentral Video")
    captures: list[tuple[str, ...]] = []
    run_steps: list[tuple[str, str]] = []

    package = MaterialPackage.model_validate(
        {
            "appId": "ringcentral-video",
            "appName": "RingCentral Video",
            "version": 1,
            "profileIds": ["ringcentral-video-bind-speaker"],
            "operationEntrypoints": [
                {
                    "id": "ringcentral.video.main.add-coworkers",
                    "title": "Add coworkers",
                    "area": "Meeting canvas",
                    "purpose": "Invite from an empty meeting.",
                    "openSteps": [
                        {
                            "action": "clickWindowRelative",
                            "target": "Add coworkers",
                            "match": {"x": "1", "y": "2", "cleanup": "modal"},
                        }
                    ],
                },
                {
                    "id": "ringcentral.video.toolbar.participants",
                    "title": "Participants",
                    "area": "Meeting toolbar",
                    "purpose": "Open participants.",
                    "openSteps": [
                        {
                            "action": "clickWindowRelative",
                            "target": "Participants",
                            "match": {"x": "3", "y": "4", "cleanup": "toggle"},
                        }
                    ],
                },
                {
                    "id": "ringcentral.video.toolbar.invite",
                    "title": "Invite",
                    "area": "Meeting toolbar",
                    "purpose": "Invite more people.",
                    "openSteps": [
                        {
                            "action": "clickWindowRelative",
                            "target": "Invite",
                            "match": {"x": "5", "y": "6", "cleanup": "modal"},
                        }
                    ],
                },
            ],
            "demoFlows": [
                {
                    "id": "adaptive-demo",
                    "title": "Adaptive Demo",
                    "goal": "Verify state-aware execution.",
                    "steps": [
                        {
                            "id": "add-coworkers",
                            "title": "Add coworkers",
                            "action": {
                                "entrypointId": "ringcentral.video.main.add-coworkers",
                                "operation": "open",
                            },
                            "narration": {"text": "Empty-room invite.", "placement": "before"},
                        },
                        {
                            "id": "participants",
                            "title": "Participants",
                            "action": {
                                "entrypointId": "ringcentral.video.toolbar.participants",
                                "operation": "open",
                            },
                            "narration": {"text": "Open participants.", "placement": "before"},
                        },
                    ],
                }
            ],
            "manualControls": [],
        }
    )

    class FakeDesktop:
        def capture(
            self,
            captured_handle: WindowHandle,
            sources: Iterable[ObservationSource],
        ) -> RawObservation:
            captures.append(tuple(str(source) for source in sources))
            return RawObservation(
                metadata=WindowMetadata(
                    process="RingCentralVideo",
                    pid=captured_handle.pid,
                    window_class="RingCentralVideoClass",
                    title="RingCentral Video",
                    bounds=(0, 0, 1000, 800),
                ),
                ui_text=["Participants (2)", "Mute microphone", "Start video"],
                screenshot_png=b"png",
            )

        def click_window_relative(self, captured_handle: WindowHandle, x: int, y: int) -> None:
            return None

        def press_key(self, key: str) -> None:
            return None

    class FakeRunner:
        def launch_and_bind(self) -> WindowHandle:
            return handle

    class FakeTimelineRunner:
        def __init__(self, **kwargs: object) -> None:
            return None

        def run_step(self, step: object) -> StepRunResult:
            action = getattr(step, "action")
            run_steps.append((getattr(step, "id"), getattr(action, "entrypoint_id")))
            return StepRunResult(step_id=getattr(step, "id"), skipped=False)

    monkeypatch.setattr(factory_module, "WindowsDesktopDriver", FakeDesktop)
    monkeypatch.setattr(
        factory_module,
        "create_profile_runner",
        lambda _profile, _desktop: FakeRunner(),
    )
    monkeypatch.setattr(factory_module, "SynchronizedTimelineRunner", FakeTimelineRunner)

    run_material_demo(profile, package, "adaptive-demo", registry=create_provider_registry(profile))

    assert len(captures) == 2
    assert run_steps == [
        ("add-coworkers", "ringcentral.video.toolbar.invite"),
        ("participants", "ringcentral.video.toolbar.participants"),
    ]
