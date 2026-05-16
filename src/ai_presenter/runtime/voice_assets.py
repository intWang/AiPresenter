from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from ai_presenter.config.models import AppProfile
from ai_presenter.providers.piper_provider import PiperVoiceAssets
from ai_presenter.providers.piper_provider import default_piper_voice_assets
from ai_presenter.providers.piper_provider import piper_module_available
from ai_presenter.providers.piper_provider import piper_voice_assets_available
from ai_presenter.providers.windows_speech import InstalledSapiVoice
from ai_presenter.providers.windows_speech import list_installed_sapi_voices
from ai_presenter.providers.windows_speech import sapi_voice_available
from ai_presenter.runtime.voice import PresenterVoiceSettings
from ai_presenter.runtime.voice import resolve_speech_provider_name

VoiceAssetStatus = Literal["OK", "FAIL"]
SapiVoiceLister = Callable[[], tuple[InstalledSapiVoice, ...]]
PiperAssetResolver = Callable[[], PiperVoiceAssets]
PiperModuleChecker = Callable[[], bool]


@dataclass(frozen=True)
class VoiceAssetAvailability:
    status: VoiceAssetStatus
    route: str
    detail: str


def check_voice_asset_availability(
    profile: AppProfile,
    voice: PresenterVoiceSettings,
    *,
    sapi_voice_lister: SapiVoiceLister = list_installed_sapi_voices,
    piper_asset_resolver: PiperAssetResolver = default_piper_voice_assets,
    piper_module_checker: PiperModuleChecker = piper_module_available,
) -> VoiceAssetAvailability | None:
    route = resolve_speech_provider_name(profile, voice)
    if route == "windows-sapi-en":
        return _check_sapi_voice(route, "Zira", sapi_voice_lister)
    if route == "windows-sapi-zh":
        return _check_sapi_voice(route, "Huihui", sapi_voice_lister)
    if route == "windows-sapi":
        return _check_any_sapi_voice(route, sapi_voice_lister)
    if route == "piper":
        return _check_piper_assets(route, piper_asset_resolver, piper_module_checker)
    return None


def _check_sapi_voice(
    route: str,
    voice_name: str,
    sapi_voice_lister: SapiVoiceLister,
) -> VoiceAssetAvailability:
    try:
        voices = sapi_voice_lister()
    except Exception as exc:
        return VoiceAssetAvailability(
            "FAIL",
            route,
            f"speech={route} requires installed SAPI voice matching {voice_name}: {exc}",
        )
    if sapi_voice_available(voice_name, voices):
        return VoiceAssetAvailability(
            "OK",
            route,
            f"speech={route} found installed SAPI voice matching {voice_name}",
        )
    return VoiceAssetAvailability(
        "FAIL",
        route,
        f"speech={route} requires installed SAPI voice matching {voice_name}",
    )


def _check_any_sapi_voice(
    route: str,
    sapi_voice_lister: SapiVoiceLister,
) -> VoiceAssetAvailability:
    try:
        voices = sapi_voice_lister()
    except Exception as exc:
        return VoiceAssetAvailability(
            "FAIL",
            route,
            f"speech={route} requires at least one installed SAPI voice: {exc}",
        )
    if voices:
        return VoiceAssetAvailability(
            "OK",
            route,
            f"speech={route} found {len(voices)} installed SAPI voice(s)",
        )
    return VoiceAssetAvailability(
        "FAIL",
        route,
        f"speech={route} requires at least one installed SAPI voice",
    )


def _check_piper_assets(
    route: str,
    piper_asset_resolver: PiperAssetResolver,
    piper_module_checker: PiperModuleChecker,
) -> VoiceAssetAvailability:
    if not piper_module_checker():
        return VoiceAssetAvailability(
            "FAIL",
            route,
            f"speech={route} requires Python module piper",
        )

    assets = piper_asset_resolver()
    if piper_voice_assets_available(assets):
        return VoiceAssetAvailability(
            "OK",
            route,
            f"speech={route} found local Piper voice assets for {assets.voice}",
        )
    return VoiceAssetAvailability(
        "FAIL",
        route,
        f"speech={route} requires local Piper voice assets for {assets.voice}",
    )
