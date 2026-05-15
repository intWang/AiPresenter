from pathlib import Path

from ai_presenter.config.loader import load_profile
from ai_presenter.config.models import DesktopAppProfile
from ai_presenter.packages.loader import load_material_package
from ai_presenter.packages.models import MaterialPackage
from ai_presenter.desktop.base import VisibleWindow
from ai_presenter.runtime.control import DemoControl
from ai_presenter.runtime.controller import NO_RUNNING_APPS_LABEL
from ai_presenter.runtime.controller import PresenterController
from ai_presenter.runtime.controller import _RunningAppScanState


def _controller_inputs() -> tuple[DesktopAppProfile, MaterialPackage]:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))
    assert isinstance(profile, DesktopAppProfile)
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    return profile, package


def test_presenter_controller_exposes_running_state_and_runner_inputs() -> None:
    profile, package = _controller_inputs()
    control = DemoControl()
    calls: list[tuple[str, str, str, DemoControl]] = []

    def runner(
        captured_profile: DesktopAppProfile,
        captured_package: MaterialPackage,
        captured_flow_id: str,
        *,
        control: DemoControl,
    ) -> None:
        calls.append(
            (
                captured_profile.id,
                captured_package.app_id,
                captured_flow_id,
                control,
            )
        )

    controller = PresenterController(
        profile=profile,
        material_package=package,
        flow_id="meeting-control-map-demo",
        control=control,
        runner=runner,
    )

    controller.start()
    controller.join(timeout=1)

    assert controller.is_running is False
    assert controller.last_error is None
    assert calls == [("ringcentral-video-bind-speaker", "ringcentral-video", "meeting-control-map-demo", control)]


def test_presenter_controller_records_runner_errors() -> None:
    profile, package = _controller_inputs()

    def runner(
        captured_profile: DesktopAppProfile,
        captured_package: MaterialPackage,
        captured_flow_id: str,
        *,
        control: DemoControl,
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


def test_controller_session_answers_question_text() -> None:
    profile, package = _controller_inputs()
    controller = PresenterController(
        profile=profile,
        material_package=package,
        flow_id="meeting-control-map-demo",
    )

    answer = controller.submit_question("chat")

    assert "Chat" in answer or "chat" in answer


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
