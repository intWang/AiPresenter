from collections.abc import Iterable
from pathlib import Path

import pytest

from ai_presenter.config.loader import load_profile
from ai_presenter.config.models import BrowserAppProfile, DesktopAppProfile, ObservationSource
from ai_presenter.domain.state import RawObservation, WindowMetadata
from ai_presenter.desktop.base import WindowHandle
from ai_presenter.packages.loader import load_material_package
from ai_presenter.packages.models import MaterialPackage
from ai_presenter.providers.base import SpeechAudio
from ai_presenter.runtime import factory as factory_module
from ai_presenter.runtime.factory import create_adapter
from ai_presenter.runtime.factory import create_fake_provider_registry
from ai_presenter.runtime.factory import create_provider_registry
from ai_presenter.runtime.factory import run_desktop_profile
from ai_presenter.runtime.factory import run_existing_window_material_demo
from ai_presenter.runtime.factory import run_material_demo
from ai_presenter.runtime.sync import StepRunResult
from ai_presenter.runtime.voice import PresenterVoiceSettings


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


def test_provider_registry_supports_piper_profile() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-piper-speaker.yaml"))

    registry = create_provider_registry(profile)

    assert profile.providers.speech == "piper"
    assert registry.speech(profile.providers.speech).__class__.__name__ == "PiperSpeechProvider"
    assert registry.speech("windows-sapi-zh").__class__.__name__ == "WindowsSapiSpeechProvider"


def test_provider_registry_uses_conversational_chinese_sapi_rate() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-piper-speaker.yaml"))

    registry = create_provider_registry(
        profile,
        voice=PresenterVoiceSettings(language="zh", tone="conversational"),
    )
    speech = registry.speech("windows-sapi-zh")

    assert speech.__class__.__name__ == "WindowsSapiSpeechProvider"
    assert getattr(speech, "_rate") == -1


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


def test_run_material_demo_validates_voice_before_desktop_driver(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))
    assert isinstance(profile, DesktopAppProfile)
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    calls: list[str] = []

    def fake_desktop_driver() -> object:
        calls.append("desktop")
        raise AssertionError("desktop should not start")

    monkeypatch.setattr(factory_module, "WindowsDesktopDriver", fake_desktop_driver)
    monkeypatch.setattr(
        factory_module,
        "create_provider_registry",
        lambda *_args, **_kwargs: calls.append("registry"),
    )

    with pytest.raises(ValueError, match="Chinese / Friendly"):
        run_material_demo(
            profile,
            package,
            "meeting-controls-tour",
            voice=PresenterVoiceSettings(language="zh-CN", tone="friendly"),
        )

    assert calls == []


def test_run_material_demo_validates_flow_before_desktop_driver(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))
    assert isinstance(profile, DesktopAppProfile)
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    calls: list[str] = []

    monkeypatch.setattr(factory_module, "WindowsDesktopDriver", lambda: calls.append("desktop"))

    with pytest.raises(KeyError, match="Unknown demo flow: missing-flow"):
        run_material_demo(profile, package, "missing-flow")

    assert calls == []


def test_existing_window_material_demo_validates_voice_before_desktop_driver(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))
    assert isinstance(profile, DesktopAppProfile)
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    handle = WindowHandle("RingCentralVideo", 1, "RingCentralVideoClass", "RingCentral Video")
    calls: list[str] = []

    monkeypatch.setattr(factory_module, "WindowsDesktopDriver", lambda: calls.append("desktop"))

    with pytest.raises(ValueError, match="speech provider fake"):
        run_existing_window_material_demo(
            profile,
            package,
            "meeting-controls-tour",
            handle=handle,
            voice=PresenterVoiceSettings(language="zh"),
        )

    assert calls == []


def test_existing_window_material_demo_validates_flow_before_desktop_driver(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))
    assert isinstance(profile, DesktopAppProfile)
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    handle = WindowHandle("RingCentralVideo", 1, "RingCentralVideoClass", "RingCentral Video")
    calls: list[str] = []

    monkeypatch.setattr(factory_module, "WindowsDesktopDriver", lambda: calls.append("desktop"))

    with pytest.raises(KeyError, match="Unknown demo flow: missing-flow"):
        run_existing_window_material_demo(
            profile,
            package,
            "missing-flow",
            handle=handle,
        )

    assert calls == []


def test_existing_window_material_demo_applies_voice_to_narration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))
    assert isinstance(profile, DesktopAppProfile)
    handle = WindowHandle("Demo", 123, "DemoWindow", "Demo App")
    run_texts: list[str] = []
    package = MaterialPackage.model_validate(
        {
            "appId": "temp.demo.123",
            "appName": "Demo App",
            "version": 1,
            "profileIds": ["temp.demo.123.profile"],
            "operationEntrypoints": [
                {
                    "id": "temp.demo.123.overview",
                    "title": "Overview",
                    "area": "Demo App",
                    "purpose": "Introduce the app.",
                    "openSteps": [],
                }
            ],
            "demoFlows": [
                {
                    "id": "temp-demo",
                    "title": "Temporary demo",
                    "goal": "Introduce a running app.",
                    "steps": [
                        {
                            "id": "overview",
                            "title": "Overview",
                            "action": {
                                "entrypointId": "temp.demo.123.overview",
                                "operation": "explain",
                            },
                            "narration": {
                                "text": "Open settings. Then review options.",
                                "placement": "before",
                            },
                        }
                    ],
                }
            ],
            "manualControls": [],
        }
    )

    class FakeDesktop:
        pass

    class FakeTimelineRunner:
        def __init__(self, **kwargs: object) -> None:
            return None

        def run_step(self, step: object) -> StepRunResult:
            narration = getattr(step, "narration")
            run_texts.append(getattr(narration, "text"))
            return StepRunResult(step_id=getattr(step, "id"), skipped=False)

    monkeypatch.setattr(factory_module, "WindowsDesktopDriver", FakeDesktop)
    monkeypatch.setattr(factory_module, "SynchronizedTimelineRunner", FakeTimelineRunner)

    run_existing_window_material_demo(
        profile,
        package,
        "temp-demo",
        handle=handle,
        registry=create_provider_registry(profile),
        voice=PresenterVoiceSettings(tone="concise"),
    )

    assert run_texts == ["Open settings."]


def test_existing_window_material_demo_applies_localized_chinese_narration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile = load_profile(Path("profiles/ringcentral-video-piper-speaker.yaml"))
    assert isinstance(profile, DesktopAppProfile)
    handle = WindowHandle("Demo", 123, "DemoWindow", "Demo App")
    run_texts: list[str] = []
    package = MaterialPackage.model_validate(
        {
            "appId": "temp.demo.123",
            "appName": "Demo App",
            "version": 1,
            "profileIds": ["temp.demo.123.profile"],
            "operationEntrypoints": [
                {
                    "id": "temp.demo.123.overview",
                    "title": "Overview",
                    "area": "Demo App",
                    "purpose": "Introduce the app.",
                    "openSteps": [],
                }
            ],
            "demoFlows": [
                {
                    "id": "temp-demo",
                    "title": "Temporary demo",
                    "goal": "Introduce a running app.",
                    "steps": [
                        {
                            "id": "overview",
                            "title": "Overview",
                            "action": {
                                "entrypointId": "temp.demo.123.overview",
                                "operation": "explain",
                            },
                            "narration": {
                                "text": "Open settings. Then review options.",
                                "localizedText": {
                                    "zh": "先看设置入口。这里集中管理会议选项。"
                                },
                                "placement": "before",
                            },
                        }
                    ],
                }
            ],
            "manualControls": [],
        }
    )

    class FakeDesktop:
        pass

    class FakeTimelineRunner:
        def __init__(self, **kwargs: object) -> None:
            return None

        def run_step(self, step: object) -> StepRunResult:
            narration = getattr(step, "narration")
            run_texts.append(getattr(narration, "text"))
            return StepRunResult(step_id=getattr(step, "id"), skipped=False)

    monkeypatch.setattr(factory_module, "WindowsDesktopDriver", FakeDesktop)
    monkeypatch.setattr(factory_module, "SynchronizedTimelineRunner", FakeTimelineRunner)

    run_existing_window_material_demo(
        profile,
        package,
        "temp-demo",
        handle=handle,
        registry=create_provider_registry(profile),
        voice=PresenterVoiceSettings(language="zh", tone="professional"),
    )

    assert run_texts == ["先看设置入口。这里集中管理会议选项。"]


def test_existing_window_material_demo_routes_piper_chinese_to_sapi_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile = load_profile(Path("profiles/ringcentral-video-piper-speaker.yaml"))
    assert isinstance(profile, DesktopAppProfile)
    handle = WindowHandle("Demo", 123, "DemoWindow", "Demo App")
    captured_speech_provider_classes: list[str] = []
    package = MaterialPackage.model_validate(
        {
            "appId": "temp.demo.123",
            "appName": "Demo App",
            "version": 1,
            "profileIds": ["temp.demo.123.profile"],
            "operationEntrypoints": [
                {
                    "id": "temp.demo.123.overview",
                    "title": "Overview",
                    "area": "Demo App",
                    "purpose": "Introduce the app.",
                    "openSteps": [],
                }
            ],
            "demoFlows": [
                {
                    "id": "temp-demo",
                    "title": "Temporary demo",
                    "goal": "Introduce a running app.",
                    "steps": [
                        {
                            "id": "overview",
                            "title": "Overview",
                            "action": {
                                "entrypointId": "temp.demo.123.overview",
                                "operation": "explain",
                            },
                            "narration": {"text": "Open settings.", "placement": "before"},
                        }
                    ],
                }
            ],
            "manualControls": [],
        }
    )

    class FakeDesktop:
        pass

    class FakeTimelineRunner:
        def __init__(self, **kwargs: object) -> None:
            captured_speech_provider_classes.append(
                kwargs["speech_provider"].__class__.__name__
            )

        def run_step(self, step: object) -> StepRunResult:
            return StepRunResult(step_id=getattr(step, "id"), skipped=False)

    monkeypatch.setattr(factory_module, "WindowsDesktopDriver", FakeDesktop)
    monkeypatch.setattr(factory_module, "SynchronizedTimelineRunner", FakeTimelineRunner)

    run_existing_window_material_demo(
        profile,
        package,
        "temp-demo",
        handle=handle,
        registry=create_provider_registry(profile),
        voice=PresenterVoiceSettings(language="zh"),
    )

    assert captured_speech_provider_classes == ["WindowsSapiSpeechProvider"]


def test_existing_window_material_demo_routes_openai_spanish_and_uses_localized_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile = load_profile(Path("profiles/ringcentral-video-openai.example.yaml"))
    assert isinstance(profile, DesktopAppProfile)
    profile.providers.narration = "fake"
    handle = WindowHandle("Demo", 123, "DemoWindow", "Demo App")
    captured_speech_provider_classes: list[str] = []
    run_texts: list[str] = []
    package = MaterialPackage.model_validate(
        {
            "appId": "temp.demo.123",
            "appName": "Demo App",
            "version": 1,
            "profileIds": ["temp.demo.123.profile"],
            "operationEntrypoints": [
                {
                    "id": "temp.demo.123.overview",
                    "title": "Overview",
                    "area": "Demo App",
                    "purpose": "Introduce the app.",
                    "openSteps": [],
                }
            ],
            "demoFlows": [
                {
                    "id": "temp-demo",
                    "title": "Temporary demo",
                    "goal": "Introduce a running app.",
                    "steps": [
                        {
                            "id": "overview",
                            "title": "Overview",
                            "action": {
                                "entrypointId": "temp.demo.123.overview",
                                "operation": "explain",
                            },
                            "narration": {
                                "text": "Open settings. Then review options.",
                                "localizedText": {
                                    "es": (
                                        "Abra configuracion. Revise las opciones "
                                        "antes de continuar."
                                    )
                                },
                                "placement": "before",
                            },
                        }
                    ],
                }
            ],
            "manualControls": [],
        }
    )

    class FakeDesktop:
        pass

    class FakeOpenAISpeechProvider:
        pass

    class FakeTimelineRunner:
        def __init__(self, **kwargs: object) -> None:
            captured_speech_provider_classes.append(
                kwargs["speech_provider"].__class__.__name__
            )

        def run_step(self, step: object) -> StepRunResult:
            narration = getattr(step, "narration")
            run_texts.append(getattr(narration, "text"))
            return StepRunResult(step_id=getattr(step, "id"), skipped=False)

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(factory_module, "WindowsDesktopDriver", FakeDesktop)
    monkeypatch.setattr(factory_module, "OpenAISpeechProvider", FakeOpenAISpeechProvider)
    monkeypatch.setattr(factory_module, "SynchronizedTimelineRunner", FakeTimelineRunner)

    run_existing_window_material_demo(
        profile,
        package,
        "temp-demo",
        handle=handle,
        voice=PresenterVoiceSettings(language="es", tone="concise"),
    )

    assert captured_speech_provider_classes == ["FakeOpenAISpeechProvider"]
    assert run_texts == ["Abra configuracion."]


def test_existing_window_material_demo_uses_injected_openai_registry_for_spanish(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile = load_profile(Path("profiles/ringcentral-video-openai.example.yaml"))
    assert isinstance(profile, DesktopAppProfile)
    profile.providers.narration = "fake"
    handle = WindowHandle("Demo", 123, "DemoWindow", "Demo App")
    captured_speech_provider_classes: list[str] = []
    run_texts: list[str] = []
    package = MaterialPackage.model_validate(
        {
            "appId": "temp.demo.123",
            "appName": "Demo App",
            "version": 1,
            "profileIds": ["ringcentral-video-openai"],
            "operationEntrypoints": [
                {
                    "id": "temp.demo.123.overview",
                    "title": "Overview",
                    "area": "Demo App",
                    "purpose": "Introduce the app.",
                    "openSteps": [],
                }
            ],
            "demoFlows": [
                {
                    "id": "temp-demo",
                    "title": "Temporary demo",
                    "goal": "Introduce a running app.",
                    "steps": [
                        {
                            "id": "overview",
                            "title": "Overview",
                            "action": {
                                "entrypointId": "temp.demo.123.overview",
                                "operation": "explain",
                            },
                            "narration": {
                                "text": "Open settings. Then review options.",
                                "localizedText": {
                                    "es": (
                                        "Abra configuracion. Revise las opciones "
                                        "antes de continuar."
                                    )
                                },
                                "placement": "before",
                            },
                        }
                    ],
                }
            ],
            "manualControls": [],
        }
    )

    class FakeDesktop:
        pass

    class InjectedOpenAISpeechProvider:
        def synthesize(self, text: str) -> SpeechAudio:
            raise AssertionError("speech synthesis should not run in this test")

    class FakeTimelineRunner:
        def __init__(self, **kwargs: object) -> None:
            captured_speech_provider_classes.append(
                kwargs["speech_provider"].__class__.__name__
            )

        def run_step(self, step: object) -> StepRunResult:
            narration = getattr(step, "narration")
            run_texts.append(getattr(narration, "text"))
            return StepRunResult(step_id=getattr(step, "id"), skipped=False)

    def fail_provider_construction(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("OpenAISpeechProvider should not be constructed")

    registry = create_fake_provider_registry()
    registry.register_speech("openai", InjectedOpenAISpeechProvider())

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(factory_module, "WindowsDesktopDriver", FakeDesktop)
    monkeypatch.setattr(factory_module, "OpenAISpeechProvider", fail_provider_construction)
    monkeypatch.setattr(factory_module, "SynchronizedTimelineRunner", FakeTimelineRunner)

    run_existing_window_material_demo(
        profile,
        package,
        "temp-demo",
        handle=handle,
        registry=registry,
        voice=PresenterVoiceSettings(language="es", tone="concise"),
    )

    assert captured_speech_provider_classes == ["InjectedOpenAISpeechProvider"]
    assert run_texts == ["Abra configuracion."]


def test_existing_window_material_demo_uses_tone_rate_when_creating_registry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile = load_profile(Path("profiles/ringcentral-video-piper-speaker.yaml"))
    assert isinstance(profile, DesktopAppProfile)
    handle = WindowHandle("Demo", 123, "DemoWindow", "Demo App")
    captured_rates: list[int] = []
    package = MaterialPackage.model_validate(
        {
            "appId": "temp.demo.123",
            "appName": "Demo App",
            "version": 1,
            "profileIds": ["temp.demo.123.profile"],
            "operationEntrypoints": [
                {
                    "id": "temp.demo.123.overview",
                    "title": "Overview",
                    "area": "Demo App",
                    "purpose": "Introduce the app.",
                    "openSteps": [],
                }
            ],
            "demoFlows": [
                {
                    "id": "temp-demo",
                    "title": "Temporary demo",
                    "goal": "Introduce a running app.",
                    "steps": [
                        {
                            "id": "overview",
                            "title": "Overview",
                            "action": {
                                "entrypointId": "temp.demo.123.overview",
                                "operation": "explain",
                            },
                            "narration": {
                                "text": "Open settings.",
                                "localizedText": {"zh": "先看设置。"},
                                "placement": "before",
                            },
                        }
                    ],
                }
            ],
            "manualControls": [],
        }
    )

    class FakeDesktop:
        pass

    class FakeTimelineRunner:
        def __init__(self, **kwargs: object) -> None:
            captured_rates.append(getattr(kwargs["speech_provider"], "_rate"))

        def run_step(self, step: object) -> StepRunResult:
            return StepRunResult(step_id=getattr(step, "id"), skipped=False)

    monkeypatch.setattr(factory_module, "WindowsDesktopDriver", FakeDesktop)
    monkeypatch.setattr(factory_module, "SynchronizedTimelineRunner", FakeTimelineRunner)

    run_existing_window_material_demo(
        profile,
        package,
        "temp-demo",
        handle=handle,
        voice=PresenterVoiceSettings(language="zh", tone="conversational"),
    )

    assert captured_rates == [-1]
