from pathlib import Path

from ai_presenter.config.loader import load_profile
from ai_presenter.config.models import DesktopAppProfile
from ai_presenter.packages.loader import load_material_package
from ai_presenter.packages.models import MaterialPackage
from ai_presenter.runtime.control import DemoControl
from ai_presenter.runtime.controller import PresenterController


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
