from ai_presenter.desktop.base import VisibleControl, VisibleWindow
from ai_presenter.runtime.temporary_package import build_temporary_package
from ai_presenter.runtime.temporary_package import classify_control_safety


def test_classifies_destructive_controls_as_risky() -> None:
    assert classify_control_safety("Delete", "Button").is_safe is False
    assert classify_control_safety("Send", "Button").is_safe is False


def test_classifies_settings_control_as_safe() -> None:
    assert classify_control_safety("Settings", "Button").is_safe is True


def test_builds_valid_temporary_package_from_visible_controls() -> None:
    window = VisibleWindow("Demo", 10, "DemoWindow", "Demo App", (0, 0, 800, 600))
    controls = (
        VisibleControl("Settings", "Button", (10, 10, 120, 40)),
        VisibleControl("Delete", "Button", (10, 60, 120, 90)),
    )

    package = build_temporary_package(window=window, controls=controls)

    assert package.app_id == "temp.demo.10"
    assert package.app_name == "Demo App"
    assert package.demo_flows[0].id == "temp-demo"
    settings = package.entrypoint_by_id("temp.demo.10.settings")
    delete = package.entrypoint_by_id("temp.demo.10.delete")
    assert settings.open_steps[0].action == "clickWindowControl"
    assert delete.open_steps == []
    assert "risky" in " ".join(delete.presenter_notes).casefold()
