from ai_presenter.desktop.base import VisibleControl, VisibleWindow
from ai_presenter.runtime.temporary_package import build_temporary_package
from ai_presenter.runtime.temporary_package import classify_control_safety


def test_classifies_destructive_controls_as_risky() -> None:
    assert classify_control_safety("Delete", "Button").is_safe is False
    assert classify_control_safety("Send", "Button").is_safe is False
    assert classify_control_safety("Start recording", "Button").is_safe is False


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


def test_duplicate_safe_controls_get_unique_ids_and_occurrence() -> None:
    window = VisibleWindow("Demo", 10, "DemoWindow", "Demo App", (0, 0, 800, 600))
    controls = (
        VisibleControl("Settings", "Button", (10, 10, 120, 40)),
        VisibleControl("Settings", "Button", (10, 60, 120, 90)),
    )

    package = build_temporary_package(window=window, controls=controls)

    first = package.entrypoint_by_id("temp.demo.10.settings")
    second = package.entrypoint_by_id("temp.demo.10.settings-2")
    assert package.demo_flows[0].steps[1].id == "settings"
    assert package.demo_flows[0].steps[2].id == "settings-2"
    assert "occurrence" not in first.open_steps[0].match
    assert second.open_steps[0].match["occurrence"] == "2"


def test_slug_collision_gets_unique_ids() -> None:
    window = VisibleWindow("Demo", 10, "DemoWindow", "Demo App", (0, 0, 800, 600))
    controls = (
        VisibleControl("A/B", "Button", (10, 10, 120, 40)),
        VisibleControl("A B", "Button", (10, 60, 120, 90)),
    )

    package = build_temporary_package(window=window, controls=controls)

    assert package.entrypoint_by_id("temp.demo.10.a-b").title == "A/B"
    assert package.entrypoint_by_id("temp.demo.10.a-b-2").title == "A B"
    assert package.demo_flows[0].steps[1].id == "a-b"
    assert package.demo_flows[0].steps[2].id == "a-b-2"


def test_non_allowlisted_menuitem_is_explain_only() -> None:
    window = VisibleWindow("Demo", 10, "DemoWindow", "Demo App", (0, 0, 800, 600))
    controls = (VisibleControl("Open", "MenuItem", (10, 10, 120, 40)),)

    package = build_temporary_package(window=window, controls=controls)

    open_item = package.entrypoint_by_id("temp.demo.10.open")
    assert open_item.open_steps == []
    assert package.demo_flows[0].steps[1].action.operation == "explain"


def test_punctuation_only_labels_get_unique_fallback_ids() -> None:
    window = VisibleWindow("Demo", 10, "DemoWindow", "Demo App", (0, 0, 800, 600))
    controls = (
        VisibleControl("!!!", "Button", (10, 10, 120, 40)),
        VisibleControl("???", "Button", (10, 60, 120, 90)),
    )

    package = build_temporary_package(window=window, controls=controls)

    assert package.entrypoint_by_id("temp.demo.10.item").title == "!!!"
    assert package.entrypoint_by_id("temp.demo.10.item-2").title == "???"
    assert package.demo_flows[0].steps[1].id == "item"
    assert package.demo_flows[0].steps[2].id == "item-2"
