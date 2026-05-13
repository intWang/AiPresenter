import time

from ai_presenter.adapters.base import AppAdapter
from ai_presenter.adapters.ringcentral import RingCentralAdapter
from ai_presenter.config.models import AppProfile
from ai_presenter.config.models import DesktopAppProfile
from ai_presenter.desktop.windows import WindowsDesktopDriver
from ai_presenter.domain.state import MeetingState
from ai_presenter.media.output import MediaOutputFactory
from ai_presenter.media.output import MediaOutput
from ai_presenter.providers.base import ProviderRegistry
from ai_presenter.providers.fake import FakeNarrationProvider
from ai_presenter.providers.fake import FakeSpeechProvider
from ai_presenter.providers.fake import FakeVisionProvider
from ai_presenter.providers.openai_provider import OpenAINarrationProvider
from ai_presenter.providers.openai_provider import OpenAISpeechProvider
from ai_presenter.runtime.events import EventDetector
from ai_presenter.runtime.narration import NarrationEngine
from ai_presenter.runtime.presenter import PresenterLoop
from ai_presenter.runtime.profile_runner import ProfileRunner


def create_fake_provider_registry() -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register_vision("fake", FakeVisionProvider(MeetingState(confidence=1.0)))
    registry.register_narration("fake", FakeNarrationProvider())
    registry.register_speech("fake", FakeSpeechProvider())
    return registry


def create_default_provider_registry() -> ProviderRegistry:
    return create_fake_provider_registry()


def create_provider_registry(profile: AppProfile) -> ProviderRegistry:
    registry = create_fake_provider_registry()
    if profile.providers.narration == "openai":
        registry.register_narration("openai", OpenAINarrationProvider())
    if profile.providers.speech == "openai":
        registry.register_speech("openai", OpenAISpeechProvider())
    return registry


def create_adapter(profile: AppProfile) -> AppAdapter:
    if profile.id == "ringcentral-video":
        return RingCentralAdapter()
    raise ValueError(f"No adapter registered for profile: {profile.id}")


def create_media_output(profile: AppProfile) -> MediaOutput:
    return MediaOutputFactory().create(profile.audio)


def create_presenter_loop(
    profile: AppProfile,
    desktop: WindowsDesktopDriver,
    registry: ProviderRegistry,
) -> PresenterLoop:
    return PresenterLoop(
        observation_driver=desktop,
        adapter=create_adapter(profile),
        event_detector=EventDetector(
            profile.narration.confidence_threshold,
            enabled_event_types=profile.events,
        ),
        narration_engine=NarrationEngine(
            profile.narration,
            registry.narration(profile.providers.narration),
        ),
        speech_provider=registry.speech(profile.providers.speech),
        media_output=create_media_output(profile),
        observation_sources=profile.observe.sources,
        vision_provider=registry.vision(profile.providers.vision),
    )


def create_profile_runner(profile: DesktopAppProfile, desktop: WindowsDesktopDriver) -> ProfileRunner:
    return ProfileRunner(profile, desktop)


def run_desktop_profile(
    profile: DesktopAppProfile,
    *,
    registry: ProviderRegistry | None = None,
    iterations: int = 1,
) -> None:
    if iterations < 1:
        raise ValueError("iterations must be at least 1")

    desktop = WindowsDesktopDriver()
    providers = registry or create_provider_registry(profile)
    handle = create_profile_runner(profile, desktop).launch_and_bind()
    presenter = create_presenter_loop(profile, desktop, providers)
    for index in range(iterations):
        presenter.run_once(handle)
        if index + 1 < iterations:
            time.sleep(profile.observe.interval_ms / 1000)
