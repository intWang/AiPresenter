import logging
import threading
from pathlib import Path

import pytest

from ai_presenter.config.loader import load_profile
from ai_presenter.config.models import DesktopAppProfile
from ai_presenter.desktop.base import VisibleControl
from ai_presenter.packages.loader import load_material_package
from ai_presenter.packages.models import MaterialPackage
from ai_presenter.desktop.base import VisibleWindow, WindowHandle
from ai_presenter.runtime import controller as controller_module
from ai_presenter.runtime.control import DemoControl
from ai_presenter.runtime.controller import NO_RUNNING_APPS_LABEL
from ai_presenter.runtime.controller import ChatTurn
from ai_presenter.runtime.controller import ControllerAppliedStatusState
from ai_presenter.runtime.controller import ControllerStatusSnapshot
from ai_presenter.runtime.controller import ControllerStatusUpdate
from ai_presenter.runtime.controller import PresenterController
from ai_presenter.runtime.controller import _RunningAppScanState
from ai_presenter.runtime.controller import _apply_operator_summary_wraplength
from ai_presenter.runtime.controller import _apply_button_state
from ai_presenter.runtime.controller import _check_controller_voice_readiness
from ai_presenter.runtime.controller import _configure_operator_summary_label
from ai_presenter.runtime.controller import _ControllerVoiceReadinessCache
from ai_presenter.runtime.controller import _voice_readiness_failure_message
from ai_presenter.runtime.controller import describe_controller_action_error
from ai_presenter.runtime.controller import describe_controller_error
from ai_presenter.runtime.controller import describe_question_error
from ai_presenter.runtime.controller import describe_question_result
from ai_presenter.runtime.controller import format_chat_turns
from ai_presenter.runtime.controller import plan_controller_status_application
from ai_presenter.runtime.controller import QuestionSubmitResult
from ai_presenter.runtime.controller import render_operator_summary_text
from ai_presenter.runtime.controller import render_voice_label
from ai_presenter.runtime.controller import resolve_controller_status
from ai_presenter.runtime.session import ControllerSession, RunningAppTarget
from ai_presenter.runtime.controller_view_model import ControllerOperatorSnapshot
from ai_presenter.runtime.controller_view_model import build_controller_operator_view_model
from ai_presenter.runtime.temporary_package import build_temporary_package
from ai_presenter.runtime.voice import PresenterVoiceSettings
from ai_presenter.runtime.voice_assets import VoiceAssetAvailability


def _controller_inputs() -> tuple[DesktopAppProfile, MaterialPackage]:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))
    assert isinstance(profile, DesktopAppProfile)
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    return profile, package


def test_controller_voice_readiness_adapts_available_assets() -> None:
    profile, _package = _controller_inputs()

    readiness = _check_controller_voice_readiness(
        profile,
        PresenterVoiceSettings(language="zh"),
        checker=lambda *_args: VoiceAssetAvailability(
            status="OK",
            route="windows-sapi-zh",
            detail="speech=windows-sapi-zh found installed SAPI voice matching Huihui",
        ),
    )

    assert readiness is not None
    assert readiness.status == "OK"
    assert readiness.label == "OK"


def test_controller_voice_readiness_converts_checker_exception_to_failure() -> None:
    profile, _package = _controller_inputs()

    def checker(*_args: object) -> VoiceAssetAvailability | None:
        raise RuntimeError("private voice path")

    readiness = _check_controller_voice_readiness(
        profile,
        PresenterVoiceSettings(language="zh"),
        checker=checker,
    )

    assert readiness is not None
    assert readiness.status == "FAIL"
    assert readiness.detail == "voice asset check failed; retry or check local voice setup."
    assert "private voice path" not in readiness.detail
    failure = _voice_readiness_failure_message(readiness)
    assert failure is not None
    assert "voice asset check failed" in failure
    assert "private voice path" not in failure


def test_controller_voice_readiness_rejects_incompatible_voice_before_asset_check() -> None:
    profile, _package = _controller_inputs()
    calls: list[str] = []

    def checker(
        _profile: object,
        _voice: PresenterVoiceSettings,
    ) -> VoiceAssetAvailability | None:
        calls.append("asset-check")
        return VoiceAssetAvailability(
            status="OK",
            route="windows-sapi-en",
            detail="speech=windows-sapi-en found installed SAPI voice matching Zira",
        )

    readiness = _check_controller_voice_readiness(
        profile,
        PresenterVoiceSettings(language="es"),
        checker=checker,
    )

    assert readiness is not None
    assert readiness.status == "FAIL"
    assert "Spanish / Professional" in readiness.detail
    assert "requires speech provider openai" in readiness.detail
    assert calls == []


def test_controller_voice_readiness_cache_reuses_selected_voice_until_it_changes() -> None:
    profile, _package = _controller_inputs()
    calls: list[PresenterVoiceSettings] = []

    def checker(
        _profile: object,
        voice: PresenterVoiceSettings,
    ) -> VoiceAssetAvailability | None:
        calls.append(voice)
        return VoiceAssetAvailability(
            status="OK",
            route="windows-sapi-zh",
            detail="speech=windows-sapi-zh found installed SAPI voice matching Huihui",
        )

    cache = _ControllerVoiceReadinessCache(profile=profile, checker=checker)

    first = cache.get(PresenterVoiceSettings(language="zh", tone="friendly"))
    second = cache.get(PresenterVoiceSettings(language="zh-CN", tone="friendly"))
    third = cache.get(PresenterVoiceSettings(language="zh", tone="coach"))

    assert first == second
    assert third is not None
    assert len(calls) == 2
    assert calls == [
        PresenterVoiceSettings(language="zh", tone="friendly"),
        PresenterVoiceSettings(language="zh", tone="coach"),
    ]


def test_controller_voice_readiness_cache_reuses_prior_voice_after_switching_back() -> None:
    profile, _package = _controller_inputs()
    calls: list[PresenterVoiceSettings] = []

    def checker(
        _profile: object,
        voice: PresenterVoiceSettings,
    ) -> VoiceAssetAvailability | None:
        calls.append(voice)
        return VoiceAssetAvailability(
            status="OK",
            route="windows-sapi-zh",
            detail=f"ready for {voice.language}/{voice.tone}",
        )

    cache = _ControllerVoiceReadinessCache(profile=profile, checker=checker)

    first = cache.get(PresenterVoiceSettings(language="zh", tone="friendly"))
    second = cache.get(PresenterVoiceSettings(language="zh", tone="coach"))
    third = cache.get(PresenterVoiceSettings(language="zh-CN", tone="friendly"))

    assert first == third
    assert second is not None
    assert calls == [
        PresenterVoiceSettings(language="zh", tone="friendly"),
        PresenterVoiceSettings(language="zh", tone="coach"),
    ]


def test_controller_voice_readiness_refresh_invalidates_only_selected_voice() -> None:
    profile, _package = _controller_inputs()
    calls: list[PresenterVoiceSettings] = []

    def checker(
        _profile: object,
        voice: PresenterVoiceSettings,
    ) -> VoiceAssetAvailability | None:
        calls.append(voice)
        return VoiceAssetAvailability(
            status="OK",
            route="windows-sapi-zh",
            detail=f"ready call {len(calls)} for {voice.language}/{voice.tone}",
        )

    cache = _ControllerVoiceReadinessCache(profile=profile, checker=checker)

    first = cache.get(PresenterVoiceSettings(language="zh", tone="friendly"))
    coach = cache.get(PresenterVoiceSettings(language="zh", tone="coach"))
    refreshed = cache.refresh(PresenterVoiceSettings(language="zh-CN", tone="friendly"))
    reused_coach = cache.get(PresenterVoiceSettings(language="zh", tone="coach"))

    assert refreshed != first
    assert reused_coach == coach
    assert calls == [
        PresenterVoiceSettings(language="zh", tone="friendly"),
        PresenterVoiceSettings(language="zh", tone="coach"),
        PresenterVoiceSettings(language="zh", tone="friendly"),
    ]


def test_controller_voice_readiness_cache_preserves_none_results() -> None:
    profile, _package = _controller_inputs()
    calls: list[PresenterVoiceSettings] = []

    def checker(
        _profile: object,
        voice: PresenterVoiceSettings,
    ) -> VoiceAssetAvailability | None:
        calls.append(voice)
        return None

    cache = _ControllerVoiceReadinessCache(profile=profile, checker=checker)

    assert cache.get(PresenterVoiceSettings(language="en")) is None
    assert cache.get(PresenterVoiceSettings(language="en-US")) is None

    assert calls == [PresenterVoiceSettings(language="en")]


def test_presenter_controller_exposes_running_state_and_runner_inputs() -> None:
    profile, package = _controller_inputs()
    control = DemoControl()
    calls: list[tuple[str, str, str, DemoControl, PresenterVoiceSettings | None]] = []

    def runner(
        captured_profile: DesktopAppProfile,
        captured_package: MaterialPackage,
        captured_flow_id: str,
        *,
        control: DemoControl,
        voice: PresenterVoiceSettings | None = None,
    ) -> None:
        calls.append(
            (
                captured_profile.id,
                captured_package.app_id,
                captured_flow_id,
                control,
                voice,
            )
        )

    controller = PresenterController(
        profile=profile,
        material_package=package,
        flow_id="meeting-control-map-demo",
        control=control,
        runner=runner,
    )
    controller.set_voice(PresenterVoiceSettings(tone="conversational"))

    controller.start()
    controller.join(timeout=1)

    assert controller.is_running is False
    assert controller.last_error is None
    assert calls == [
        (
            "ringcentral-video-bind-speaker",
            "ringcentral-video",
            "meeting-control-map-demo",
            control,
            PresenterVoiceSettings(tone="conversational"),
        )
    ]


def test_presenter_controller_forwards_initial_voice_without_setter() -> None:
    profile, package = _controller_inputs()
    calls: list[PresenterVoiceSettings] = []

    def runner(*_args: object, voice: PresenterVoiceSettings | None = None, **_kwargs: object) -> None:
        assert voice is not None
        calls.append(voice)

    controller = PresenterController(
        profile=profile,
        material_package=package,
        flow_id="meeting-control-map-demo",
        runner=runner,
        voice=PresenterVoiceSettings(language="zh-CN", tone="friendly"),
    )

    controller.start()
    controller.join(timeout=1)

    assert calls == [PresenterVoiceSettings(language="zh", tone="friendly")]


def test_presenter_controller_validates_voice_before_runner_thread() -> None:
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))
    assert isinstance(profile, DesktopAppProfile)
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    called = False

    def runner(*_args: object, **_kwargs: object) -> None:
        nonlocal called
        called = True

    controller = PresenterController(
        profile=profile,
        material_package=package,
        flow_id="meeting-control-map-demo",
        runner=runner,
        voice=PresenterVoiceSettings(language="zh-CN", tone="friendly"),
    )

    with pytest.raises(ValueError, match="Chinese / Friendly"):
        controller.start()

    assert called is False
    assert controller.is_running is False


def test_presenter_controller_records_runner_errors() -> None:
    profile, package = _controller_inputs()

    def runner(
        captured_profile: DesktopAppProfile,
        captured_package: MaterialPackage,
        captured_flow_id: str,
        *,
        control: DemoControl,
        voice: PresenterVoiceSettings | None = None,
    ) -> None:
        raise RuntimeError("demo exploded")

    controller = PresenterController(
        profile=profile,
        material_package=package,
        flow_id="meeting-control-map-demo",
        runner=runner,
    )

    controller.start()
    controller.join(timeout=1)

    assert controller.is_running is False
    assert isinstance(controller.last_error, RuntimeError)
    assert str(controller.last_error) == "demo exploded"


def test_presenter_controller_runs_existing_window_target() -> None:
    profile, package = _controller_inputs()
    window = VisibleWindow("Demo", 10, "DemoWindow", "Demo App", (0, 0, 800, 600))
    handle = WindowHandle(window.process, window.pid, window.window_class, window.title)
    temporary_package = build_temporary_package(
        window=window,
        controls=(VisibleControl("Settings", "Button", (10, 10, 120, 40)),),
    )
    calls: list[tuple[str, str, str, WindowHandle]] = []

    def window_runner(
        captured_profile: DesktopAppProfile,
        captured_package: MaterialPackage,
        captured_flow_id: str,
        *,
        handle: WindowHandle,
        control: DemoControl,
        voice: PresenterVoiceSettings | None = None,
    ) -> None:
        calls.append((captured_profile.id, captured_package.app_id, captured_flow_id, handle))

    controller = PresenterController(
        profile=profile,
        material_package=package,
        flow_id="meeting-control-map-demo",
        window_runner=window_runner,
    )
    controller.set_target(
        material_package=temporary_package,
        flow_id="temp-demo",
        handle=handle,
    )

    controller.start()
    controller.join(timeout=1)

    assert calls == [("ringcentral-video-bind-speaker", "temp.demo.10", "temp-demo", handle)]


def test_presenter_controller_queues_safe_question_without_stopping_running_demo() -> None:
    profile, package = _controller_inputs()
    control = DemoControl()
    started = threading.Event()
    interrupt_seen = threading.Event()
    release = threading.Event()
    calls: list[str] = []
    queued_steps: list[str] = []

    def runner(
        captured_profile: DesktopAppProfile,
        captured_package: MaterialPackage,
        captured_flow_id: str,
        *,
        control: DemoControl,
        voice: PresenterVoiceSettings | None = None,
    ) -> None:
        calls.append(captured_flow_id)
        started.set()
        while not release.is_set():
            interrupt = control.pop_interrupt()
            if interrupt is not None:
                queued_steps.append(interrupt.id)
                interrupt_seen.set()
            release.wait(timeout=0.01)

    controller = PresenterController(
        profile=profile,
        material_package=package,
        flow_id="meeting-control-map-demo",
        control=control,
        runner=runner,
    )

    controller.start()
    assert started.wait(timeout=1)

    result = controller.submit_question("chat")
    assert interrupt_seen.wait(timeout=1)
    release.set()
    controller.join(timeout=1)

    assert "Chat" in result.answer_text or "chat" in result.answer_text
    assert result.demonstration_status == "queued"
    assert result.entrypoint_id == "ringcentral.video.toolbar.chat"
    assert result.can_operate is True
    assert control.is_stop_requested is False
    assert calls == ["meeting-control-map-demo"]
    assert queued_steps == ["question-ringcentral.video.toolbar.chat"]


def test_presenter_controller_end_clears_queued_question_before_next_run() -> None:
    profile, package = _controller_inputs()
    control = DemoControl()
    started = threading.Event()
    release = threading.Event()
    calls: list[str] = []

    def runner(
        captured_profile: DesktopAppProfile,
        captured_package: MaterialPackage,
        captured_flow_id: str,
        *,
        control: DemoControl,
        voice: PresenterVoiceSettings | None = None,
    ) -> None:
        calls.append(captured_flow_id)
        started.set()
        release.wait(timeout=1)

    controller = PresenterController(
        profile=profile,
        material_package=package,
        flow_id="meeting-control-map-demo",
        control=control,
        runner=runner,
    )

    controller.start()
    assert started.wait(timeout=1)
    result = controller.submit_question("chat")
    assert result.demonstration_status == "queued"

    controller.end()
    release.set()
    controller.join(timeout=1)

    control.reset()
    assert control.pop_interrupt() is None
    assert calls == ["meeting-control-map-demo"]


def test_presenter_controller_starts_safe_question_demo_when_idle() -> None:
    profile, package = _controller_inputs()
    control = DemoControl()
    calls: list[tuple[str, str, str, DemoControl, PresenterVoiceSettings | None]] = []

    def runner(
        captured_profile: DesktopAppProfile,
        captured_package: MaterialPackage,
        captured_flow_id: str,
        *,
        control: DemoControl,
        voice: PresenterVoiceSettings | None = None,
    ) -> None:
        calls.append(
            (
                captured_profile.id,
                captured_package.app_id,
                captured_flow_id,
                control,
                voice,
            )
        )

    controller = PresenterController(
        profile=profile,
        material_package=package,
        flow_id="meeting-control-map-demo",
        control=control,
        runner=runner,
    )
    controller.set_voice(PresenterVoiceSettings(language="en", tone="conversational"))

    result = controller.submit_question("chat")
    controller.join(timeout=1)

    assert result.demonstration_status == "started"
    assert "Chat" in result.answer_text or "chat" in result.answer_text
    assert calls == [
        (
            "ringcentral-video-bind-speaker",
            "ringcentral-video",
            "question-answer-demo",
            control,
            PresenterVoiceSettings(language="en", tone="conversational"),
        )
    ]


def test_presenter_controller_starts_spanish_openai_question_demo_when_idle() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-openai.example.yaml"))
    assert isinstance(profile, DesktopAppProfile)
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    control = DemoControl()
    calls: list[tuple[str, str, str, DemoControl, PresenterVoiceSettings | None]] = []

    def runner(
        captured_profile: DesktopAppProfile,
        captured_package: MaterialPackage,
        captured_flow_id: str,
        *,
        control: DemoControl,
        voice: PresenterVoiceSettings | None = None,
    ) -> None:
        calls.append(
            (
                captured_profile.id,
                captured_package.app_id,
                captured_flow_id,
                control,
                voice,
            )
        )

    controller = PresenterController(
        profile=profile,
        material_package=package,
        flow_id="meeting-control-map-demo",
        control=control,
        runner=runner,
        voice=PresenterVoiceSettings(language="es"),
    )

    result = controller.submit_question("panel de participantes")
    controller.join(timeout=1)

    assert result.demonstration_status == "started"
    assert result.entrypoint_id == "ringcentral.video.toolbar.participants"
    assert result.can_operate is True
    assert result.answer_text.startswith("panel de participantes:")
    assert "Participants panel:" not in result.answer_text
    assert calls == [
        (
            "ringcentral-video-openai",
            "ringcentral-video",
            "question-answer-demo",
            control,
            PresenterVoiceSettings(language="es"),
        )
    ]


@pytest.mark.parametrize(
    ("question", "voice"),
    [
        ("Please be brief", PresenterVoiceSettings(language="en")),
        ("\u8bf7\u7528\u4e2d\u6587\u56de\u7b54", PresenterVoiceSettings(language="zh")),
    ],
)
def test_presenter_controller_answers_meta_prompt_without_question_demo_when_idle(
    question: str,
    voice: PresenterVoiceSettings,
) -> None:
    profile, package = _controller_inputs()
    control = DemoControl()
    calls: list[str] = []

    def runner(
        _profile: DesktopAppProfile,
        _package: MaterialPackage,
        captured_flow_id: str,
        *,
        control: DemoControl,
        voice: PresenterVoiceSettings | None = None,
    ) -> None:
        calls.append(captured_flow_id)

    controller = PresenterController(
        profile=profile,
        material_package=package,
        flow_id="meeting-control-map-demo",
        control=control,
        runner=runner,
        voice=voice,
    )

    result = controller.submit_question(question)
    controller.join(timeout=1)

    assert result.demonstration_status == "text_only"
    assert result.demonstration_message == ""
    assert result.entrypoint_id is None
    assert result.can_operate is False
    assert result.answer_source == "presenter_meta"
    assert result.answer_text.startswith("Presenter settings:")
    assert (
        describe_question_result(result)
        == "Answered only: presenter settings response; no demo was started"
    )
    assert controller.is_running is False
    assert controller.last_error is None
    assert calls == []
    assert control.pop_interrupt() is None
    assert control.is_stop_requested is False


@pytest.mark.parametrize(
    ("question", "voice"),
    [
        ("Please be brief", PresenterVoiceSettings(language="en")),
        ("\u8bf7\u7528\u4e2d\u6587\u56de\u7b54", PresenterVoiceSettings(language="zh")),
    ],
)
def test_presenter_controller_answers_meta_prompt_without_queuing_running_demo(
    question: str,
    voice: PresenterVoiceSettings,
) -> None:
    profile, package = _controller_inputs()
    control = DemoControl()
    started = threading.Event()
    release = threading.Event()
    calls: list[str] = []

    def runner(
        _profile: DesktopAppProfile,
        _package: MaterialPackage,
        captured_flow_id: str,
        *,
        control: DemoControl,
        voice: PresenterVoiceSettings | None = None,
    ) -> None:
        calls.append(captured_flow_id)
        started.set()
        release.wait(timeout=1)

    controller = PresenterController(
        profile=profile,
        material_package=package,
        flow_id="meeting-control-map-demo",
        control=control,
        runner=runner,
    )

    controller.start()
    assert started.wait(timeout=1)
    controller.set_voice(voice)

    result = controller.submit_question(question)
    release.set()
    controller.join(timeout=1)

    assert result.demonstration_status == "text_only"
    assert result.demonstration_message == ""
    assert result.entrypoint_id is None
    assert result.can_operate is False
    assert result.answer_source == "presenter_meta"
    assert result.answer_text.startswith("Presenter settings:")
    assert (
        describe_question_result(result)
        == "Answered only: presenter settings response; no demo was started"
    )
    assert control.pop_interrupt() is None
    assert control.is_stop_requested is False
    assert calls == ["meeting-control-map-demo"]
    assert "question-answer-demo" not in calls


@pytest.mark.parametrize(
    ("question", "voice", "expected_entrypoint_id", "expected_answer"),
    [
        (
            "Please be brief and open chat",
            PresenterVoiceSettings(language="en"),
            "ringcentral.video.toolbar.chat",
            "Chat panel:",
        ),
        (
            "\u8bf7\u7528\u4e2d\u6587\u56de\u7b54\uff0c\u804a\u5929\u5728\u54ea\u91cc",
            PresenterVoiceSettings(language="zh"),
            "ringcentral.video.toolbar.chat",
            "\u804a\u5929",
        ),
        (
            "Please be brief and show network quality",
            PresenterVoiceSettings(language="en"),
            "ringcentral.video.top.network-quality",
            "Network quality:",
        ),
        (
            "Please be brief and open participants panel",
            PresenterVoiceSettings(language="en"),
            "ringcentral.video.toolbar.participants",
            "Participants panel:",
        ),
        (
            "请简洁一点，参会者在哪里",
            PresenterVoiceSettings(language="zh"),
            "ringcentral.video.toolbar.participants",
            "Participants",
        ),
    ],
)
def test_presenter_controller_queues_safe_mixed_meta_question_for_running_demo(
    question: str,
    voice: PresenterVoiceSettings,
    expected_entrypoint_id: str,
    expected_answer: str,
) -> None:
    profile, package = _controller_inputs()
    control = DemoControl()
    started = threading.Event()
    release = threading.Event()
    calls: list[str] = []

    def runner(
        _profile: DesktopAppProfile,
        _package: MaterialPackage,
        captured_flow_id: str,
        *,
        control: DemoControl,
        voice: PresenterVoiceSettings | None = None,
    ) -> None:
        calls.append(captured_flow_id)
        started.set()
        release.wait(timeout=1)

    controller = PresenterController(
        profile=profile,
        material_package=package,
        flow_id="meeting-control-map-demo",
        control=control,
        runner=runner,
    )

    controller.start()
    assert started.wait(timeout=1)
    controller.set_voice(voice)

    result = controller.submit_question(question)
    interrupt = control.pop_interrupt()
    release.set()
    controller.join(timeout=1)

    assert result.demonstration_status == "queued"
    assert result.demonstration_message == "I queued that for the next safe step."
    assert result.entrypoint_id == expected_entrypoint_id
    assert result.can_operate is True
    assert expected_answer in result.answer_text
    assert not result.answer_text.startswith("Presenter settings:")
    assert interrupt is not None
    assert interrupt.action.entrypoint_id == expected_entrypoint_id
    assert control.is_stop_requested is False
    assert calls == ["meeting-control-map-demo"]
    assert "question-answer-demo" not in calls


@pytest.mark.parametrize(
    ("question", "voice", "expected_entrypoint_id", "expected_answer"),
    [
        (
            "Please be brief and read meeting information aloud",
            PresenterVoiceSettings(language="en"),
            "ringcentral.video.top.meeting-info",
            "Meeting IDs and links are private meeting details",
        ),
        (
            "\u8bf7\u7b80\u6d01\u4e00\u70b9\uff0c\u590d\u5236\u4f1a\u8bae\u94fe\u63a5",
            PresenterVoiceSettings(language="zh"),
            "ringcentral.video.top.meeting-info",
            "\u79c1\u4eba\u4f1a\u8bae\u8be6\u60c5",
        ),
        (
            "Please be brief and open notes and transcript",
            PresenterVoiceSettings(language="en"),
            "ringcentral.video.more.notes",
            "Starting notes can change",
        ),
        (
            "Please be brief and show participants",
            PresenterVoiceSettings(language="en"),
            None,
            "participant names",
        ),
        (
            "请简洁一点，列出参会者",
            PresenterVoiceSettings(language="zh"),
            None,
            "参会人姓名",
        ),
        (
            "参加者名を読んで",
            PresenterVoiceSettings(language="ja"),
            None,
            "参加者名",
        ),
    ],
)
def test_presenter_controller_keeps_sensitive_mixed_meta_question_text_only_while_running(
    question: str,
    voice: PresenterVoiceSettings,
    expected_entrypoint_id: str,
    expected_answer: str,
) -> None:
    profile, package = _controller_inputs()
    control = DemoControl()
    started = threading.Event()
    release = threading.Event()
    calls: list[str] = []

    def runner(
        _profile: DesktopAppProfile,
        _package: MaterialPackage,
        captured_flow_id: str,
        *,
        control: DemoControl,
        voice: PresenterVoiceSettings | None = None,
    ) -> None:
        calls.append(captured_flow_id)
        started.set()
        release.wait(timeout=1)

    controller = PresenterController(
        profile=profile,
        material_package=package,
        flow_id="meeting-control-map-demo",
        control=control,
        runner=runner,
    )

    controller.start()
    assert started.wait(timeout=1)
    controller.set_voice(voice)

    result = controller.submit_question(question)
    release.set()
    controller.join(timeout=1)

    assert result.demonstration_status == "text_only"
    assert result.demonstration_message == ""
    assert result.entrypoint_id == expected_entrypoint_id
    assert result.can_operate is False
    assert result.answer_source == "qa"
    assert expected_answer in result.answer_text
    assert not result.answer_text.startswith("Presenter settings:")
    assert (
        describe_question_result(result)
        == "Answered only: matched text guidance; no demo was started"
    )
    assert control.pop_interrupt() is None
    assert control.is_stop_requested is False
    assert calls == ["meeting-control-map-demo"]
    assert "question-answer-demo" not in calls


def test_presenter_controller_starts_safe_question_demo_with_indexed_flow_lookup() -> None:
    profile, package = _controller_inputs()
    calls: list[str] = []

    def runner(
        _profile: DesktopAppProfile,
        captured_package: MaterialPackage,
        captured_flow_id: str,
        *,
        control: DemoControl,
        voice: PresenterVoiceSettings | None = None,
    ) -> None:
        calls.append(captured_package.demo_flow_by_id(captured_flow_id).id)

    controller = PresenterController(
        profile=profile,
        material_package=package,
        flow_id="meeting-control-map-demo",
        runner=runner,
    )

    result = controller.submit_question("chat")
    controller.join(timeout=1)

    assert result.demonstration_status == "started"
    assert calls == ["question-answer-demo"]


def test_presenter_controller_answers_risky_question_without_demo() -> None:
    profile, package = _controller_inputs()
    calls: list[str] = []

    def runner(
        captured_profile: DesktopAppProfile,
        captured_package: MaterialPackage,
        captured_flow_id: str,
        *,
        control: DemoControl,
        voice: PresenterVoiceSettings | None = None,
    ) -> None:
        calls.append(captured_flow_id)

    controller = PresenterController(
        profile=profile,
        material_package=package,
        flow_id="meeting-control-map-demo",
        runner=runner,
    )

    result = controller.submit_question("invite people")

    assert result.demonstration_status == "text_only"
    assert result.entrypoint_id == "ringcentral.video.toolbar.invite"
    assert result.can_operate is False
    assert result.answer_source == "entrypoint"
    assert (
        describe_question_result(result)
        == "Answered only: ringcentral.video.toolbar.invite is not safe to operate automatically"
    )
    assert result.answer_text
    assert calls == []


def test_presenter_controller_answers_no_match_without_demo() -> None:
    profile, package = _controller_inputs()
    control = DemoControl()
    calls: list[str] = []

    def runner(
        _profile: DesktopAppProfile,
        _package: MaterialPackage,
        captured_flow_id: str,
        *,
        control: DemoControl,
        voice: PresenterVoiceSettings | None = None,
    ) -> None:
        calls.append(captured_flow_id)

    controller = PresenterController(
        profile=profile,
        material_package=package,
        flow_id="meeting-control-map-demo",
        control=control,
        runner=runner,
    )

    result = controller.submit_question("definitely unknown control")

    assert result.demonstration_status == "text_only"
    assert result.demonstration_message == ""
    assert result.entrypoint_id is None
    assert result.can_operate is False
    assert result.answer_source == "no_match"
    assert describe_question_result(result) == "Answered only: no matching safe control"
    assert calls == []
    assert control.pop_interrupt() is None


@pytest.mark.parametrize(
    ("question", "voice", "expected_entrypoint_id", "expected_answer"),
    [
        (
            "Please be brief and open chat",
            PresenterVoiceSettings(language="en"),
            "ringcentral.video.toolbar.chat",
            "Chat panel:",
        ),
        (
            "\u8bf7\u7528\u4e2d\u6587\u56de\u7b54\uff0c\u804a\u5929\u5728\u54ea\u91cc",
            PresenterVoiceSettings(language="zh"),
            "ringcentral.video.toolbar.chat",
            "\u804a\u5929",
        ),
        (
            "Please be brief and show network quality",
            PresenterVoiceSettings(language="en"),
            "ringcentral.video.top.network-quality",
            "Network quality:",
        ),
        (
            "Please be brief and open participants panel",
            PresenterVoiceSettings(language="en"),
            "ringcentral.video.toolbar.participants",
            "Participants panel:",
        ),
        (
            "请简洁一点，参会者在哪里",
            PresenterVoiceSettings(language="zh"),
            "ringcentral.video.toolbar.participants",
            "Participants",
        ),
    ],
)
def test_presenter_controller_starts_safe_mixed_meta_question_demo_when_idle(
    question: str,
    voice: PresenterVoiceSettings,
    expected_entrypoint_id: str,
    expected_answer: str,
) -> None:
    profile, package = _controller_inputs()
    calls: list[str] = []

    def runner(
        _profile: DesktopAppProfile,
        _package: MaterialPackage,
        captured_flow_id: str,
        *,
        control: DemoControl,
        voice: PresenterVoiceSettings | None = None,
    ) -> None:
        calls.append(captured_flow_id)

    controller = PresenterController(
        profile=profile,
        material_package=package,
        flow_id="meeting-control-map-demo",
        runner=runner,
        voice=voice,
    )

    result = controller.submit_question(question)
    controller.join(timeout=1)

    assert result.demonstration_status == "started"
    assert result.demonstration_message == "Demonstrating it now."
    assert result.entrypoint_id == expected_entrypoint_id
    assert result.can_operate is True
    assert expected_answer in result.answer_text
    assert not result.answer_text.startswith("Presenter settings:")
    assert calls == ["question-answer-demo"]


@pytest.mark.parametrize(
    ("question", "voice", "expected_entrypoint_id", "expected_answer"),
    [
        (
            "Please be brief and read meeting information aloud",
            PresenterVoiceSettings(language="en"),
            "ringcentral.video.top.meeting-info",
            "Meeting IDs and links are private meeting details",
        ),
        (
            "\u8bf7\u7b80\u6d01\u4e00\u70b9\uff0c\u590d\u5236\u4f1a\u8bae\u94fe\u63a5",
            PresenterVoiceSettings(language="zh"),
            "ringcentral.video.top.meeting-info",
            "\u79c1\u4eba\u4f1a\u8bae\u8be6\u60c5",
        ),
        (
            "Please be brief and open notes and transcript",
            PresenterVoiceSettings(language="en"),
            "ringcentral.video.more.notes",
            "Starting notes can change",
        ),
        (
            "Please be brief and show participants",
            PresenterVoiceSettings(language="en"),
            None,
            "participant names",
        ),
        (
            "请简洁一点，列出参会者",
            PresenterVoiceSettings(language="zh"),
            None,
            "参会人姓名",
        ),
        (
            "参加者名を読んで",
            PresenterVoiceSettings(language="ja"),
            None,
            "参加者名",
        ),
    ],
)
def test_presenter_controller_keeps_sensitive_mixed_meta_question_text_only_when_idle(
    question: str,
    voice: PresenterVoiceSettings,
    expected_entrypoint_id: str,
    expected_answer: str,
) -> None:
    profile, package = _controller_inputs()
    control = DemoControl()
    calls: list[str] = []

    def runner(
        _profile: DesktopAppProfile,
        _package: MaterialPackage,
        captured_flow_id: str,
        *,
        control: DemoControl,
        voice: PresenterVoiceSettings | None = None,
    ) -> None:
        calls.append(captured_flow_id)

    controller = PresenterController(
        profile=profile,
        material_package=package,
        flow_id="meeting-control-map-demo",
        control=control,
        runner=runner,
        voice=voice,
    )

    result = controller.submit_question(question)
    controller.join(timeout=1)

    assert result.demonstration_status == "text_only"
    assert result.demonstration_message == ""
    assert result.entrypoint_id == expected_entrypoint_id
    assert result.can_operate is False
    assert result.answer_source == "qa"
    assert expected_answer in result.answer_text
    assert not result.answer_text.startswith("Presenter settings:")
    assert (
        describe_question_result(result)
        == "Answered only: matched text guidance; no demo was started"
    )
    assert calls == []
    assert control.pop_interrupt() is None


def test_controller_session_answers_question_text() -> None:
    profile, package = _controller_inputs()

    def runner(
        captured_profile: DesktopAppProfile,
        captured_package: MaterialPackage,
        captured_flow_id: str,
        *,
        control: DemoControl,
        voice: PresenterVoiceSettings | None = None,
    ) -> None:
        return

    controller = PresenterController(
        profile=profile,
        material_package=package,
        flow_id="meeting-control-map-demo",
        runner=runner,
    )

    result = controller.submit_question("chat")

    assert "Chat" in result.answer_text or "chat" in result.answer_text


def test_run_controller_validates_initial_voice_before_desktop_driver(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))
    assert isinstance(profile, DesktopAppProfile)
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    calls: list[str] = []

    monkeypatch.setattr(controller_module, "WindowsDesktopDriver", lambda: calls.append("desktop"))

    with pytest.raises(ValueError, match="Chinese / Friendly"):
        controller_module.run_controller(
            profile,
            package,
            "meeting-control-map-demo",
            voice=PresenterVoiceSettings(language="zh-CN", tone="friendly"),
        )

    assert calls == []


def test_run_controller_validates_flow_before_desktop_driver(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile, package = _controller_inputs()

    def fail_desktop_setup() -> object:
        raise AssertionError("desktop should not start")

    monkeypatch.setattr(controller_module, "WindowsDesktopDriver", fail_desktop_setup)

    with pytest.raises(KeyError, match="Unknown demo flow: missing-flow"):
        controller_module.run_controller(profile, package, "missing-flow")


def test_describe_question_result_distinguishes_queued_started_and_risky() -> None:
    queued = QuestionSubmitResult(
        answer_text="Chat: Open chat.",
        demonstration_status="queued",
        demonstration_message="I queued that for the next safe step.",
        entrypoint_id="ringcentral.video.toolbar.chat",
        can_operate=True,
    )
    started = QuestionSubmitResult(
        answer_text="Chat: Open chat.",
        demonstration_status="started",
        demonstration_message="Demonstrating it now.",
        entrypoint_id="ringcentral.video.toolbar.chat",
        can_operate=True,
    )
    risky = QuestionSubmitResult(
        answer_text="Leave meeting: Leave or end the meeting.",
        entrypoint_id="ringcentral.video.toolbar.leave",
        can_operate=False,
        answer_source="entrypoint",
    )
    privacy_guidance = QuestionSubmitResult(
        answer_text="Participant privacy guidance.",
        answer_source="qa",
    )
    policy_guidance = QuestionSubmitResult(
        answer_text="Meeting information privacy guidance.",
        entrypoint_id="ringcentral.video.top.meeting-info",
        can_operate=False,
        answer_source="qa",
    )
    no_match = QuestionSubmitResult(
        answer_text="I could not find a matching control.",
        answer_source="no_match",
    )
    presenter_meta = QuestionSubmitResult(
        answer_text="Presenter settings: I will keep the answer brief.",
        answer_source="presenter_meta",
    )

    assert describe_question_result(queued) == "Queued safe demo: ringcentral.video.toolbar.chat"
    assert describe_question_result(started) == "Demonstrating: ringcentral.video.toolbar.chat"
    assert (
        describe_question_result(risky)
        == "Answered only: ringcentral.video.toolbar.leave is not safe to operate automatically"
    )
    assert (
        describe_question_result(privacy_guidance)
        == "Answered only: matched text guidance; no demo was started"
    )
    assert (
        describe_question_result(policy_guidance)
        == "Answered only: matched text guidance; no demo was started"
    )
    assert (
        describe_question_result(presenter_meta)
        == "Answered only: presenter settings response; no demo was started"
    )
    assert describe_question_result(no_match) == "Answered only: no matching safe control"


def test_describe_question_error_hides_exception_text() -> None:
    message = describe_question_error(RuntimeError("private board agenda"))

    assert message == "Question error: question could not be answered safely."
    assert "private board agenda" not in message


def test_describe_controller_error_hides_private_runtime_exception_text() -> None:
    message = describe_controller_error(RuntimeError("private board agenda"))

    assert message == "Controller error: action could not continue safely."
    assert "private board agenda" not in message


def test_describe_controller_error_preserves_known_public_flow_error() -> None:
    message = describe_controller_error(
        KeyError("Unknown demo flow: missing-flow. Available flows: demo")
    )

    assert message == "Unknown demo flow: missing-flow. Available flows: demo"


def test_describe_controller_error_rejects_spoofed_private_flow_error() -> None:
    message = describe_controller_error(KeyError("Unknown demo flow: private board agenda"))

    assert message == "Controller error: action could not continue safely."
    assert "private board agenda" not in message


def test_describe_controller_action_error_hides_exception_text() -> None:
    message = describe_controller_action_error("Scan", RuntimeError("private board agenda"))

    assert message == "Scan error: action could not continue safely."
    assert "private board agenda" not in message


def test_render_voice_label_uses_controller_labels() -> None:
    assert render_voice_label(PresenterVoiceSettings()) == "English / Professional"
    assert (
        render_voice_label(PresenterVoiceSettings(language="zh", tone="conversational"))
        == "Chinese / Conversational"
    )
    assert (
        render_voice_label(PresenterVoiceSettings(language="zh-CN", tone="friendly"))
        == "Chinese / Friendly"
    )
    assert render_voice_label(PresenterVoiceSettings(tone="calm")) == "English / Support"
    assert render_voice_label(PresenterVoiceSettings(tone="safety")) == "English / Careful"


def test_format_chat_turns_keeps_history_in_order() -> None:
    transcript = format_chat_turns(
        [
            ChatTurn("You", "How do I open chat?"),
            ChatTurn("AiPresenter", "Open Chat from the meeting toolbar."),
            ChatTurn("AiPresenter", "Demonstrating it now."),
        ]
    )

    assert transcript == (
        "You: How do I open chat?\n\n"
        "AiPresenter: Open Chat from the meeting toolbar.\n\n"
        "AiPresenter: Demonstrating it now."
    )


def test_resolve_controller_status_keeps_stopping_visible_while_thread_is_alive() -> None:
    update = resolve_controller_status(
        ControllerStatusSnapshot(
            current_status="Ending",
            last_error=None,
            is_running=True,
            is_paused=False,
            is_stopping=True,
            is_switching_targets=False,
            session_is_running=True,
        )
    )

    assert update.status == "Ending"
    assert update.pause_label == "Pause"
    assert update.mark_session_stopped is False


def test_resolve_controller_status_reports_switching_before_running() -> None:
    update = resolve_controller_status(
        ControllerStatusSnapshot(
            current_status="Question queued",
            last_error=None,
            is_running=True,
            is_paused=False,
            is_stopping=True,
            is_switching_targets=True,
            session_is_running=True,
        )
    )

    assert update.status == "Switching to answer"
    assert update.pause_label == "Pause"
    assert update.mark_session_stopped is False


def test_resolve_controller_status_uses_unquoted_key_error_message() -> None:
    update = resolve_controller_status(
        ControllerStatusSnapshot(
            current_status="Ready",
            last_error=KeyError("Unknown demo flow: missing-flow. Available flows: demo"),
            is_running=False,
            is_paused=False,
            is_stopping=False,
            is_switching_targets=False,
            session_is_running=True,
        )
    )

    assert update.status == "Error: Unknown demo flow: missing-flow. Available flows: demo"
    assert update.mark_session_stopped is True


def test_resolve_controller_status_hides_private_runtime_error_text() -> None:
    update = resolve_controller_status(
        ControllerStatusSnapshot(
            current_status="Ready",
            last_error=RuntimeError("private board agenda"),
            is_running=False,
            is_paused=False,
            is_stopping=False,
            is_switching_targets=False,
            session_is_running=True,
        )
    )

    assert update.status == "Error: Controller error: action could not continue safely."
    assert "private board agenda" not in update.status
    assert update.mark_session_stopped is True


def test_resolve_controller_status_does_not_repeat_error_stop_after_session_stopped() -> None:
    update = resolve_controller_status(
        ControllerStatusSnapshot(
            current_status="Error: boom",
            last_error=RuntimeError("boom"),
            is_running=False,
            is_paused=False,
            is_stopping=False,
            is_switching_targets=False,
            session_is_running=False,
        )
    )

    assert update.status == "Error: Controller error: action could not continue safely."
    assert "boom" not in update.status
    assert update.mark_session_stopped is False


def test_controller_status_application_skips_operator_refresh_when_unchanged() -> None:
    application = plan_controller_status_application(
        ControllerAppliedStatusState(status="Ready", pause_label="Pause"),
        ControllerStatusUpdate(status="Ready", pause_label="Pause"),
    )

    assert application.status_changed is False
    assert application.pause_label_changed is False
    assert application.mark_session_stopped is False
    assert application.refresh_operator_view is False
    assert application.state == ControllerAppliedStatusState(status="Ready", pause_label="Pause")


def test_controller_status_application_refreshes_when_status_or_pause_changes() -> None:
    application = plan_controller_status_application(
        ControllerAppliedStatusState(status="Running", pause_label="Pause"),
        ControllerStatusUpdate(status="Paused", pause_label="Resume"),
    )

    assert application.status_changed is True
    assert application.pause_label_changed is True
    assert application.refresh_operator_view is True
    assert application.state == ControllerAppliedStatusState(status="Paused", pause_label="Resume")


def test_controller_status_application_refreshes_for_session_stop_side_effect() -> None:
    application = plan_controller_status_application(
        ControllerAppliedStatusState(status="Ended", pause_label="Pause"),
        ControllerStatusUpdate(status="Ended", pause_label="Pause", mark_session_stopped=True),
    )

    assert application.status_changed is False
    assert application.pause_label_changed is False
    assert application.mark_session_stopped is True
    assert application.refresh_operator_view is True


def test_render_operator_summary_text_uses_multiline_rows() -> None:
    view_model = build_controller_operator_view_model(
        ControllerOperatorSnapshot(
            source_mode="material_package",
            material_package_id="ringcentral-video",
            material_flow_id="meeting-control-map-demo",
            running_app_label="",
            has_running_app_selection=False,
            has_scanned_running_app=False,
            scanned_package_id="",
            scanned_flow_id="",
            voice=PresenterVoiceSettings(),
            voice_readiness=None,
            run_status="Ready",
            is_running=False,
            is_stopping=False,
            question_text="",
            last_question_outcome="",
        )
    )

    text = render_operator_summary_text(view_model)

    assert text.splitlines() == [
        "Target: Material package: ringcentral-video",
        "Flow: meeting-control-map-demo",
        "Voice: English / Professional | assets: Not required",
        "State: Ready | scan: Package target ready",
        "Question: No question yet",
        "Actions: Submit blocked: Type a question to enable Submit.",
    ]


class _FakeButton:
    def __init__(self, state: str) -> None:
        self.state = state
        self.configure_calls: list[str] = []

    def cget(self, key: str) -> str:
        assert key == "state"
        return self.state

    def configure(self, *, state: str) -> None:
        self.configure_calls.append(state)
        self.state = state


class _FakeLabel:
    def __init__(self, **options: object) -> None:
        self.options = dict(options)
        self.configure_calls: list[dict[str, object]] = []
        self.bindings: dict[str, object] = {}

    def cget(self, key: str) -> object:
        return self.options.get(key, "")

    def configure(self, **kwargs: object) -> None:
        self.configure_calls.append(kwargs)
        self.options.update(kwargs)

    def bind(self, sequence: str, callback: object) -> None:
        self.bindings[sequence] = callback


def test_configure_operator_summary_label_sets_multiline_alignment_and_resize_binding() -> None:
    label = _FakeLabel()

    _configure_operator_summary_label(label)

    assert label.options["anchor"] == "nw"
    assert label.options["justify"] == "left"
    callback = label.bindings["<Configure>"]
    assert callable(callback)
    callback(type("Event", (), {"width": 640})())
    assert label.options["wraplength"] == 640


def test_apply_operator_summary_wraplength_skips_unchanged_width() -> None:
    label = _FakeLabel(wraplength=640)

    changed = _apply_operator_summary_wraplength(label, 640)

    assert changed is False
    assert label.configure_calls == []


@pytest.mark.parametrize("width", [0, -12])
def test_apply_operator_summary_wraplength_clamps_non_positive_width(width: int) -> None:
    label = _FakeLabel()

    changed = _apply_operator_summary_wraplength(label, width)

    assert changed is True
    assert label.options["wraplength"] == 1


def test_apply_button_state_skips_configure_when_state_matches() -> None:
    button = _FakeButton("normal")

    changed = _apply_button_state(button, enabled=True)

    assert changed is False
    assert button.configure_calls == []


def test_apply_button_state_configures_only_on_state_change() -> None:
    button = _FakeButton("disabled")

    changed = _apply_button_state(button, enabled=True)

    assert changed is True
    assert button.configure_calls == ["normal"]
    assert button.state == "normal"


def test_running_app_scan_state_starts_unscanned() -> None:
    state = _RunningAppScanState()

    assert state.has_scanned_selection is False


def test_running_app_scan_state_clears_scan_when_selection_changes() -> None:
    state = _RunningAppScanState()
    app_a = VisibleWindow("DemoA", 10, "WindowA", "Demo A", (0, 0, 800, 600))
    app_b = VisibleWindow("DemoB", 20, "WindowB", "Demo B", (0, 0, 800, 600))
    state.replace_windows({"Demo A (DemoA:10)": app_a, "Demo B (DemoB:20)": app_b})
    state.choose("Demo A (DemoA:10)")
    state.mark_selected_scanned()

    state.choose("Demo B (DemoB:20)")

    assert state.has_scanned_selection is False
    assert state.selected_label == "Demo B (DemoB:20)"


def test_running_app_scan_state_clears_scan_when_refresh_removes_all_windows() -> None:
    state = _RunningAppScanState()
    app_a = VisibleWindow("DemoA", 10, "WindowA", "Demo A", (0, 0, 800, 600))
    state.replace_windows({"Demo A (DemoA:10)": app_a})
    state.choose("Demo A (DemoA:10)")
    state.mark_selected_scanned()

    state.replace_windows({})

    assert state.has_scanned_selection is False
    assert state.selected_label == NO_RUNNING_APPS_LABEL
    assert state.selected_window is None


def test_running_app_scan_state_clears_scan_when_refresh_removes_window() -> None:
    state = _RunningAppScanState()
    app_a = VisibleWindow("DemoA", 10, "WindowA", "Demo A", (0, 0, 800, 600))
    app_b = VisibleWindow("DemoB", 20, "WindowB", "Demo B", (0, 0, 800, 600))
    state.replace_windows({"Demo A (DemoA:10)": app_a, "Demo B (DemoB:20)": app_b})
    state.choose("Demo A (DemoA:10)")
    state.mark_selected_scanned()

    state.replace_windows({"Demo B (DemoB:20)": app_b})

    assert state.has_scanned_selection is False
    assert state.selected_label == "Demo B (DemoB:20)"


def test_running_app_scan_telemetry_logs_bounded_success_metadata(
    caplog: pytest.LogCaptureFixture,
) -> None:
    session = ControllerSession()
    window = VisibleWindow(
        "DemoProcess",
        42,
        "DemoClass",
        "Private Board Agenda",
        (0, 0, 800, 600),
    )
    handle = WindowHandle("DemoProcess", 42, "DemoClass", "Private Board Agenda")
    controls = (
        VisibleControl("Settings", "Button", (1, 1, 2, 2)),
        VisibleControl("Secret Launch", "Button", (3, 3, 4, 4)),
    )
    times = iter([10.0, 10.05])

    with caplog.at_level(logging.INFO, logger="ai_presenter.runtime.controller"):
        result = controller_module._scan_running_app_for_controller(
            session,
            RunningAppTarget(window=window),
            handle_from_window=lambda selected: handle,
            list_visible_controls=lambda selected_handle: controls,
            now=lambda: next(times),
        )

    message = caplog.records[-1].getMessage()
    assert "running_app_scanned status=ok duration_ms=50.00" in message
    assert "process=DemoProcess" in message
    assert "window_class=DemoClass" in message
    assert "pid=42" in message
    assert "control_count=2" in message
    assert "entrypoint_count=3" in message
    assert "openable_count=1" in message
    assert "explain_only_count=2" in message
    assert "package=temp.demoprocess.42" in message
    assert "flow=temp-demo" in message
    assert "Private Board Agenda" not in message
    assert "Settings" not in message
    assert "Secret Launch" not in message
    assert result.status_message == (
        "Scanned temp.demoprocess.42: 2 controls, 3 entrypoints, 50 ms"
    )


def test_running_app_scan_telemetry_logs_bounded_error_metadata(
    caplog: pytest.LogCaptureFixture,
) -> None:
    session = ControllerSession()
    session.mark_running_for_test()
    window = VisibleWindow(
        "DemoProcess",
        42,
        "DemoClass",
        "Private Board Agenda",
        (0, 0, 800, 600),
    )
    handle = WindowHandle("DemoProcess", 42, "DemoClass", "Private Board Agenda")
    controls = (VisibleControl("Secret Launch", "Button", (3, 3, 4, 4)),)
    times = iter([20.0, 20.025])

    with caplog.at_level(logging.INFO, logger="ai_presenter.runtime.controller"):
        with pytest.raises(RuntimeError, match="Cannot scan while a demo is running"):
            controller_module._scan_running_app_for_controller(
                session,
                RunningAppTarget(window=window),
                handle_from_window=lambda selected: handle,
                list_visible_controls=lambda selected_handle: controls,
                now=lambda: next(times),
            )

    message = caplog.records[-1].getMessage()
    assert "running_app_scanned status=error duration_ms=25.00" in message
    assert "process=DemoProcess" in message
    assert "window_class=DemoClass" in message
    assert "pid=42" in message
    assert "control_count=1" in message
    assert "entrypoint_count" not in message
    assert "package=" not in message
    assert "flow=" not in message
    assert "Private Board Agenda" not in message
    assert "Secret Launch" not in message
    assert "Cannot scan while a demo is running" not in message
