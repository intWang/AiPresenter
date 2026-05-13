from pathlib import Path

import pytest

from ai_presenter.config.loader import load_profile
from ai_presenter.config.models import BrowserAppProfile, DesktopAppProfile
from ai_presenter.runtime import factory as factory_module
from ai_presenter.runtime.factory import create_adapter
from ai_presenter.runtime.factory import create_fake_provider_registry
from ai_presenter.runtime.factory import create_provider_registry
from ai_presenter.runtime.factory import run_desktop_profile


def test_fake_provider_registry_satisfies_ringcentral_profile() -> None:
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))
    registry = create_fake_provider_registry()

    assert registry.vision(profile.providers.vision)
    assert registry.narration(profile.providers.narration)
    assert registry.speech(profile.providers.speech)


def test_provider_registry_does_not_require_openai_for_fake_profile(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))

    registry = create_provider_registry(profile)

    assert registry.narration(profile.providers.narration)
    assert registry.speech(profile.providers.speech)


def test_create_adapter_returns_ringcentral_adapter_for_reference_profile() -> None:
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))
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
    monkeypatch.setattr(factory_module.time, "sleep", sleeps.append)

    run_desktop_profile(profile, registry=create_fake_provider_registry(), iterations=2)

    assert calls == [handle, handle]
    assert sleeps == [profile.observe.interval_ms / 1000]
