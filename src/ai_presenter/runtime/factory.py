import logging
import time
from collections.abc import Callable

from ai_presenter.adapters.base import AppAdapter
from ai_presenter.adapters.ringcentral import RingCentralAdapter
from ai_presenter.config.models import AppProfile
from ai_presenter.config.models import DesktopAppProfile
from ai_presenter.desktop.windows import WindowsDesktopDriver
from ai_presenter.desktop.base import WindowHandle
from ai_presenter.domain.state import MeetingState
from ai_presenter.media.output import MediaOutputFactory
from ai_presenter.media.output import MediaOutput
from ai_presenter.packages.models import DemoStep
from ai_presenter.packages.models import MaterialPackage
from ai_presenter.providers.base import ProviderRegistry
from ai_presenter.providers.codex_cli import CodexCliNarrationProvider
from ai_presenter.providers.fake import FakeNarrationProvider
from ai_presenter.providers.fake import FakeSpeechProvider
from ai_presenter.providers.fake import FakeVisionProvider
from ai_presenter.providers.openai_provider import OpenAINarrationProvider
from ai_presenter.providers.openai_provider import OpenAISpeechProvider
from ai_presenter.providers.piper_provider import PiperSpeechProvider
from ai_presenter.providers.windows_speech import WindowsSapiSpeechProvider
from ai_presenter.runtime.adaptive_demo import adjust_ringcentral_demo_step
from ai_presenter.runtime.control import DemoControl
from ai_presenter.runtime.events import EventDetector
from ai_presenter.runtime.material_runtime import MaterialDemoRuntime
from ai_presenter.runtime.narration import NarrationEngine
from ai_presenter.runtime.package_demo import PackageActionExecutor
from ai_presenter.runtime.package_demo import demo_flow_by_id
from ai_presenter.runtime.presenter_context import load_presenter_context
from ai_presenter.runtime.presenter import PresenterLoop
from ai_presenter.runtime.profile_runner import ProfileRunner
from ai_presenter.runtime.sync import SynchronizedTimelineRunner
from ai_presenter.runtime.voice import PresenterVoiceSettings
from ai_presenter.runtime.voice import render_presenter_text
from ai_presenter.runtime.voice import validate_profile_voice

logger = logging.getLogger("ai_presenter.runtime.factory")


def create_fake_provider_registry() -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register_vision("fake", FakeVisionProvider())
    registry.register_narration("fake", FakeNarrationProvider())
    registry.register_speech("fake", FakeSpeechProvider())
    return registry


def create_default_provider_registry() -> ProviderRegistry:
    return create_fake_provider_registry()


def create_provider_registry(profile: AppProfile) -> ProviderRegistry:
    registry = create_fake_provider_registry()
    presenter_context = load_presenter_context(profile.narration)
    if profile.providers.narration == "codex-cli":
        registry.register_narration(
            "codex-cli",
            CodexCliNarrationProvider(presenter_context=presenter_context),
        )
    if profile.providers.narration == "openai":
        registry.register_narration(
            "openai",
            OpenAINarrationProvider(presenter_context=presenter_context),
        )
    if profile.providers.speech == "openai":
        registry.register_speech("openai", OpenAISpeechProvider())
    if profile.providers.speech == "piper":
        registry.register_speech("piper", PiperSpeechProvider())
    if profile.providers.speech == "windows-sapi":
        registry.register_speech("windows-sapi", WindowsSapiSpeechProvider())
    if profile.providers.speech == "windows-sapi-en":
        registry.register_speech("windows-sapi-en", WindowsSapiSpeechProvider(voice="Zira"))
    if profile.providers.speech == "windows-sapi-zh":
        registry.register_speech("windows-sapi-zh", WindowsSapiSpeechProvider(voice="Huihui"))
    return registry


def create_adapter(profile: AppProfile) -> AppAdapter:
    if (
        isinstance(profile, DesktopAppProfile)
        and profile.bind.process == "RingCentralVideo"
        and profile.bind.window_class == "RingCentralVideoClass"
    ):
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


def run_material_demo(
    profile: DesktopAppProfile,
    material_package: MaterialPackage,
    flow_id: str,
    *,
    registry: ProviderRegistry | None = None,
    control: DemoControl | None = None,
    voice: PresenterVoiceSettings | None = None,
) -> None:
    desktop = WindowsDesktopDriver()
    providers = registry or create_provider_registry(profile)
    handle = create_profile_runner(profile, desktop).launch_and_bind()
    adapter = create_adapter(profile)
    _run_material_demo_on_handle(
        profile=profile,
        material_package=material_package,
        flow_id=flow_id,
        desktop=desktop,
        providers=providers,
        handle=handle,
        control=control,
        voice=voice,
        clear_blockers_before_start=True,
        clear_before_action=False,
        state_adjuster=lambda step: _adjust_demo_step(profile, desktop, adapter, handle, step),
    )


def run_existing_window_material_demo(
    profile: DesktopAppProfile,
    material_package: MaterialPackage,
    flow_id: str,
    *,
    handle: WindowHandle,
    registry: ProviderRegistry | None = None,
    control: DemoControl | None = None,
    voice: PresenterVoiceSettings | None = None,
) -> None:
    desktop = WindowsDesktopDriver()
    providers = registry or create_provider_registry(profile)
    _run_material_demo_on_handle(
        profile=profile,
        material_package=material_package,
        flow_id=flow_id,
        desktop=desktop,
        providers=providers,
        handle=handle,
        control=control,
        voice=voice,
        clear_blockers_before_start=False,
        clear_before_action=False,
        state_adjuster=lambda step: step,
    )


def _run_material_demo_on_handle(
    *,
    profile: DesktopAppProfile,
    material_package: MaterialPackage,
    flow_id: str,
    desktop: WindowsDesktopDriver,
    providers: ProviderRegistry,
    handle: WindowHandle,
    control: DemoControl | None,
    voice: PresenterVoiceSettings | None,
    clear_blockers_before_start: bool,
    clear_before_action: bool,
    state_adjuster: Callable[[DemoStep], DemoStep | None],
) -> None:
    voice_settings = voice or PresenterVoiceSettings()
    validate_profile_voice(profile, voice_settings)
    flow = demo_flow_by_id(material_package, flow_id)
    action_executor = PackageActionExecutor(
        package=material_package,
        driver=desktop,
        handle=handle,
        clear_before_action=clear_before_action,
        defer_cleanup=True,
        action_hold_seconds=0.2,
    )
    if clear_blockers_before_start:
        action_executor.clear_blockers()
    runner = SynchronizedTimelineRunner(
        speech_provider=providers.speech(profile.providers.speech),
        media_output=create_media_output(profile),
        action_executor=action_executor,
        control=control,
    )
    runtime = MaterialDemoRuntime(
        flow_steps=flow.steps,
        timeline=runner,
        state_adjuster=lambda step: _apply_voice_to_adjusted_step(
            state_adjuster(step),
            voice_settings,
        ),
        interrupt_source=None if control is None else control.pop_interrupt,
    )
    runtime.run_to_completion()


def _apply_voice_to_adjusted_step(
    step: DemoStep | None,
    voice: PresenterVoiceSettings,
) -> DemoStep | None:
    if step is None:
        return None
    return step.model_copy(
        update={
            "narration": step.narration.model_copy(
                update={"text": render_presenter_text(step.narration.text, voice)}
            )
        }
    )


def _adjust_demo_step(
    profile: DesktopAppProfile,
    desktop: WindowsDesktopDriver,
    adapter: AppAdapter,
    handle: WindowHandle,
    step: DemoStep,
) -> DemoStep | None:
    state = _capture_demo_state(profile, desktop, adapter, handle)
    adjusted_step = adjust_ringcentral_demo_step(step, state)
    if adjusted_step is None:
        logger.info(
            "demo_step_skipped_by_state step=%s participant_count=%s",
            step.id,
            None if state is None else state.participant_count,
        )
    return adjusted_step


def _capture_demo_state(
    profile: DesktopAppProfile,
    desktop: WindowsDesktopDriver,
    adapter: AppAdapter,
    handle: WindowHandle,
) -> MeetingState | None:
    try:
        observation = desktop.capture(handle, profile.observe.sources)
        return adapter.extract_state(observation)
    except Exception as exc:
        logger.warning("demo_state_capture_failed error=%s", exc)
        return None
