from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_presenter.cli import app
from ai_presenter.config.loader import load_profile
from ai_presenter.packages.loader import load_material_package
from ai_presenter.packages.models import MaterialPackage
from ai_presenter.runtime import diagnostics
from ai_presenter.runtime.voice import PresenterVoiceSettings
from ai_presenter.runtime.voice_assets import VoiceAssetAvailability


def _alias_package(*entries: tuple[str, dict[str, list[str]]]) -> MaterialPackage:
    entrypoints = [
        {
            "id": entrypoint_id,
            "title": entrypoint_id.rsplit(".", maxsplit=1)[-1].title(),
            "area": "Main",
            "purpose": f"Open {entrypoint_id}.",
            "questionAliases": aliases,
            "openSteps": [],
        }
        for entrypoint_id, aliases in entries
    ]
    return MaterialPackage.model_validate(
        {
            "appId": "demo",
            "appName": "Demo",
            "version": 1,
            "profileIds": ["ringcentral-video-bind-speaker"],
            "operationEntrypoints": entrypoints,
            "demoFlows": [],
            "explainers": {
                entrypoint["id"]: {
                    "shortScript": f"{entrypoint['id']}.",
                    "relatedEntrypointIds": [entrypoint["id"]],
                }
                for entrypoint in entrypoints
            },
            "manualControls": [],
        }
    )


def test_ringcentral_config_is_auto_discovered_from_running_process(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    exe_dir = tmp_path / "RingCentralVideo"
    exe_dir.mkdir()
    exe_path = exe_dir / "RingCentralVideo.exe"
    exe_path.write_text("", encoding="utf-8")
    config_path = exe_dir / "config.ini"
    config_path.write_text("DisableAffinityMask=true\n", encoding="utf-8")
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))

    monkeypatch.setattr(
        diagnostics,
        "_iter_process_executable_paths",
        lambda process_name: [exe_path],
        raising=False,
    )

    report = diagnostics.diagnose_configuration(profile=profile)

    ringcentral_check = next(
        check for check in report.checks if check.name == "RingCentral config"
    )
    assert ringcentral_check.status == "OK"
    assert str(config_path) in ringcentral_check.detail


def test_ringcentral_config_accepts_utf8_bom_ini(tmp_path: Path) -> None:
    config_path = tmp_path / "config.ini"
    config_path.write_bytes(b"\xef\xbb\xbfDisableAffinityMask=true\n")
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))

    report = diagnostics.diagnose_configuration(
        profile=profile,
        ringcentral_config=config_path,
    )

    ringcentral_check = next(
        check for check in report.checks if check.name == "RingCentral config"
    )
    assert ringcentral_check.status == "OK"


def test_diagnostics_accept_piper_provider() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-piper-speaker.yaml"))

    report = diagnostics.diagnose_configuration(profile=profile)

    providers_check = next(check for check in report.checks if check.name == "providers")
    assert providers_check.status == "OK"
    assert "speech=piper" in providers_check.detail


def test_diagnostics_reports_supported_voice(monkeypatch: pytest.MonkeyPatch) -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))
    monkeypatch.setattr(diagnostics, "check_voice_asset_availability", lambda *_args: None)

    report = diagnostics.diagnose_configuration(
        profile=profile,
        voice=PresenterVoiceSettings(language="zh-CN", tone="friendly"),
    )

    assert any(
        check.status == "OK"
        and check.name == "voice"
        and "Chinese / Friendly" in check.detail
        and "windows-sapi-zh" in check.detail
        for check in report.checks
    )


def test_diagnostics_reports_unsupported_voice() -> None:
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))

    report = diagnostics.diagnose_configuration(
        profile=profile,
        voice=PresenterVoiceSettings(language="zh-CN"),
    )

    assert report.failed_count == 1
    assert any(
        check.status == "FAIL"
        and check.name == "voice"
        and "speech provider fake" in check.detail
        for check in report.checks
    )


def test_diagnostics_reports_voice_assets_after_supported_voice(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))
    monkeypatch.setattr(
        diagnostics,
        "check_voice_asset_availability",
        lambda *_args, **_kwargs: VoiceAssetAvailability(
            status="OK",
            route="windows-sapi-zh",
            detail="speech=windows-sapi-zh found installed SAPI voice matching Huihui",
        ),
    )

    report = diagnostics.diagnose_configuration(
        profile=profile,
        voice=PresenterVoiceSettings(language="zh"),
    )

    assert any(check.status == "OK" and check.name == "voice assets" for check in report.checks)


def test_diagnostics_fails_for_missing_voice_assets(monkeypatch: pytest.MonkeyPatch) -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))
    monkeypatch.setattr(
        diagnostics,
        "check_voice_asset_availability",
        lambda *_args, **_kwargs: VoiceAssetAvailability(
            status="FAIL",
            route="windows-sapi-zh",
            detail="speech=windows-sapi-zh requires installed SAPI voice matching Huihui",
        ),
    )

    report = diagnostics.diagnose_configuration(
        profile=profile,
        voice=PresenterVoiceSettings(language="zh"),
    )

    assert report.failed_count == 1
    assert any("Huihui" in check.detail for check in report.checks if check.name == "voice assets")


def test_diagnostics_reports_piper_voice_assets(monkeypatch: pytest.MonkeyPatch) -> None:
    profile = load_profile(Path("profiles/ringcentral-video-piper-speaker.yaml"))
    monkeypatch.setattr(
        diagnostics,
        "check_voice_asset_availability",
        lambda *_args, **_kwargs: VoiceAssetAvailability(
            status="OK",
            route="piper",
            detail="speech=piper found local Piper voice assets for en_US-lessac-medium",
        ),
    )

    report = diagnostics.diagnose_configuration(
        profile=profile,
        voice=PresenterVoiceSettings(language="en"),
    )

    assert any(
        check.status == "OK"
        and check.name == "voice assets"
        and "en_US-lessac-medium" in check.detail
        for check in report.checks
    )


def test_diagnostics_fails_for_missing_piper_voice_assets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile = load_profile(Path("profiles/ringcentral-video-piper-speaker.yaml"))
    monkeypatch.setattr(
        diagnostics,
        "check_voice_asset_availability",
        lambda *_args, **_kwargs: VoiceAssetAvailability(
            status="FAIL",
            route="piper",
            detail="speech=piper requires local Piper voice assets for en_US-lessac-medium",
        ),
    )

    report = diagnostics.diagnose_configuration(
        profile=profile,
        voice=PresenterVoiceSettings(language="en"),
    )

    assert report.failed_count == 1
    assert any(
        "en_US-lessac-medium" in check.detail
        for check in report.checks
        if check.name == "voice assets"
    )


def test_diagnostics_require_localization_fails_without_package() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))

    report = diagnostics.diagnose_configuration(
        profile=profile,
        require_localization=True,
    )

    localization_check = next(
        check for check in report.checks if check.name == "localization"
    )
    assert localization_check.status == "FAIL"
    assert "--require-localization requires --package" in localization_check.detail


def test_diagnostics_require_localization_passes_for_ringcentral_chinese() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    report = diagnostics.diagnose_configuration(
        profile=profile,
        material_package=package,
        require_localization=True,
        localization_language="zh",
    )

    localization_check = next(
        check for check in report.checks if check.name == "localization"
    )
    assert localization_check.status == "OK"
    assert "required zh localization complete" in localization_check.detail
    assert "51/51 demo steps" in localization_check.detail
    assert "9/9 Q&A questions" in localization_check.detail
    assert "9/9 Q&A answers" in localization_check.detail


def test_diagnostics_require_localization_fails_for_incomplete_package() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))
    package = MaterialPackage.model_validate(
        {
            "appId": "demo",
            "appName": "Demo",
            "version": 1,
            "profileIds": ["ringcentral-video-bind-speaker"],
            "operationEntrypoints": [
                {
                    "id": "demo.panel",
                    "title": "Panel",
                    "area": "Main",
                    "purpose": "Open panel.",
                    "openSteps": [],
                }
            ],
            "demoFlows": [
                {
                    "id": "demo-flow",
                    "title": "Demo",
                    "goal": "Show the panel.",
                    "steps": [
                        {
                            "id": "intro",
                            "title": "Intro",
                            "action": {
                                "entrypointId": "demo.panel",
                                "operation": "explain",
                            },
                            "narration": {
                                "text": "Show the panel.",
                                "localizedText": {"zh": "Localized intro."},
                            },
                        },
                        {
                            "id": "missing",
                            "title": "Missing",
                            "action": {
                                "entrypointId": "demo.panel",
                                "operation": "explain",
                            },
                            "narration": {"text": "Missing localization."},
                        },
                    ],
                }
            ],
            "qa": [
                {
                    "question": "Where is the panel?",
                    "answer": "Open Panel.",
                    "localizedQuestions": {"zh": ["Panel?"]},
                    "localizedAnswers": {},
                    "relatedEntrypointIds": ["demo.panel"],
                }
            ],
            "manualControls": [],
        }
    )

    report = diagnostics.diagnose_configuration(
        profile=profile,
        material_package=package,
        require_localization=True,
        localization_language="zh",
    )

    localization_check = next(
        check for check in report.checks if check.name == "localization"
    )
    assert localization_check.status == "FAIL"
    assert "required zh localization incomplete" in localization_check.detail
    assert "1/2 demo steps" in localization_check.detail
    assert "1/1 Q&A questions" in localization_check.detail
    assert "0/1 Q&A answers" in localization_check.detail


def test_diagnostics_reports_question_aliases_ok_for_ringcentral_package() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    report = diagnostics.diagnose_configuration(
        profile=profile,
        material_package=package,
    )

    alias_check = next(check for check in report.checks if check.name == "question aliases")
    assert alias_check.status == "OK"
    assert alias_check.detail == (
        "49 package-owned aliases have no cross-entrypoint duplicates"
    )


def test_diagnostics_warns_for_duplicate_question_aliases() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))
    package = _alias_package(
        ("demo.alpha", {"en": [" Chat "]}),
        ("demo.bravo", {"en": ["chat"]}),
    )

    report = diagnostics.diagnose_configuration(
        profile=profile,
        material_package=package,
    )

    alias_check = next(check for check in report.checks if check.name == "question aliases")
    assert alias_check.status == "WARN"
    assert alias_check.detail == (
        "1 duplicate normalized package-owned question alias: "
        "'chat' (languages: en) maps to demo.alpha, demo.bravo; "
        "first match is demo.alpha"
    )


def test_diagnostics_warns_for_cross_language_question_alias_duplicates() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))
    package = _alias_package(
        ("demo.alpha", {"en": ["chat"]}),
        ("demo.bravo", {"zh": ["chat"]}),
    )

    report = diagnostics.diagnose_configuration(
        profile=profile,
        material_package=package,
    )

    alias_check = next(check for check in report.checks if check.name == "question aliases")
    assert alias_check.status == "WARN"
    assert alias_check.detail == (
        "1 duplicate normalized package-owned question alias: "
        "'chat' (languages: en, zh) maps to demo.alpha, demo.bravo; "
        "first match is demo.alpha"
    )


def test_diagnostics_ignores_same_entrypoint_question_alias_duplicates() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))
    package = _alias_package(("demo.alpha", {"en": ["Chat", " chat "]}))

    report = diagnostics.diagnose_configuration(
        profile=profile,
        material_package=package,
    )

    alias_check = next(check for check in report.checks if check.name == "question aliases")
    assert alias_check.status == "OK"
    assert alias_check.detail == (
        "2 package-owned aliases have no cross-entrypoint duplicates"
    )


def test_doctor_uses_unified_missing_flow_message(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(diagnostics, "_iter_process_executable_paths", lambda process_name: [])

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--profile",
            "ringcentral-video-bind-speaker",
            "--package",
            "ringcentral-video",
            "--flow",
            "missing-flow",
        ],
    )

    assert result.exit_code == 1
    assert (
        "[FAIL] demo flow: Unknown demo flow: missing-flow. Available flows:"
        in result.stdout
    )
