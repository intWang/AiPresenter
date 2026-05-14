import pytest

from ai_presenter.desktop.base import WindowHandle
from ai_presenter.packages.models import MaterialPackage
from ai_presenter.runtime.package_demo import PackageActionExecutor
from ai_presenter.runtime.package_demo import PackageActionExecutionError


class RecordingDemoDriver:
    def __init__(self) -> None:
        self.log: list[str] = []
        self.bounds: tuple[int, int, int, int] = (10, 20, 930, 682)
        self.fail_controls: set[str] = set()

    def click_window_relative(self, handle: WindowHandle, x: int, y: int) -> None:
        self.log.append(f"click:{handle.pid}:{x}:{y}")

    def click_window_control(
        self,
        handle: WindowHandle,
        target: str,
        *,
        occurrence: int = 1,
        control_type: str | None = None,
    ) -> None:
        if target in self.fail_controls:
            self.log.append(f"control-fail:{handle.pid}:{target}:{occurrence}")
            raise RuntimeError(f"missing control: {target}")
        detail = f"control:{handle.pid}:{target}:{occurrence}"
        if control_type is not None:
            detail = f"{detail}:{control_type}"
        self.log.append(detail)

    def window_bounds(self, handle: WindowHandle) -> tuple[int, int, int, int]:
        self.log.append(f"bounds:{handle.pid}")
        return self.bounds

    def press_key(self, key: str) -> None:
        self.log.append(f"key:{key}")


def make_package() -> MaterialPackage:
    return MaterialPackage.model_validate(
        {
            "appId": "ringcentral-video",
            "appName": "RingCentral Video",
            "version": 1,
            "profileIds": ["ringcentral-video"],
            "operationEntrypoints": [
                {
                    "id": "ringcentral.video.toolbar.audio-menu",
                    "title": "Microphone and speaker menu",
                    "area": "Meeting toolbar",
                    "purpose": "Open microphone and speaker controls.",
                    "openSteps": [
                        {
                            "action": "clickWindowRelative",
                            "target": "Microphone caret",
                            "match": {"x": "143", "y": "604", "cleanup": "escape"},
                        }
                    ],
                },
                {
                    "id": "ringcentral.video.toolbar.raise-hand",
                    "title": "Raise hand",
                    "area": "Meeting toolbar",
                    "purpose": "Raise or lower hand.",
                    "openSteps": [
                        {
                            "action": "clickWindowRelative",
                            "target": "Raise hand",
                            "match": {"x": "645", "y": "613", "cleanup": "toggle"},
                        }
                    ],
                },
                {
                    "id": "ringcentral.video.toolbar.leave",
                    "title": "Leave",
                    "area": "Meeting toolbar",
                    "purpose": "Leave the meeting.",
                    "openSteps": [
                        {
                            "action": "clickWindowRelative",
                            "target": "Leave",
                            "match": {"x": "794", "y": "613"},
                        }
                    ],
                },
                {
                    "id": "ringcentral.video.toolbar.more-control",
                    "title": "More actions",
                    "area": "Meeting toolbar",
                    "purpose": "Open toolbar More by its UI Automation button.",
                    "openSteps": [
                        {
                            "action": "clickWindowControl",
                            "target": "More",
                            "match": {
                                "occurrence": "3",
                                "controlType": "button",
                                "cleanup": "escape",
                            },
                        }
                    ],
                },
                {
                    "id": "ringcentral.video.toolbar.raise-hand-alternate",
                    "title": "Raise hand",
                    "area": "Meeting toolbar",
                    "purpose": "Raise or lower hand with alternate active-state label.",
                    "openSteps": [
                        {
                            "action": "clickWindowControl",
                            "target": "Raise hand",
                            "match": {
                                "alternateTargets": "Lower hand",
                                "controlType": "button",
                                "cleanup": "escape",
                            },
                        }
                    ],
                },
                {
                    "id": "ringcentral.video.top.report-anchored",
                    "title": "Report",
                    "area": "Meeting top bar",
                    "purpose": "Open report issue from the top-right toolbar.",
                    "openSteps": [
                        {
                            "action": "clickWindowRelative",
                            "target": "Report",
                            "match": {"xFromRight": "168", "y": "21", "cleanup": "escape"},
                        }
                    ],
                },
                {
                    "id": "ringcentral.video.toolbar.audio-menu-anchored",
                    "title": "Audio menu",
                    "area": "Meeting toolbar",
                    "purpose": "Open audio menu using bottom-anchored coordinates.",
                    "openSteps": [
                        {
                            "action": "clickWindowRelative",
                            "target": "Microphone caret",
                            "match": {"x": "143", "yFromBottom": "58", "cleanup": "escape"},
                        }
                    ],
                },
                {
                    "id": "ringcentral.video.more.background",
                    "title": "Background",
                    "area": "More menu",
                    "purpose": "Open background settings.",
                    "openSteps": [
                        {
                            "action": "clickWindowRelative",
                            "target": "More",
                            "match": {"x": "719", "y": "613"},
                        },
                        {
                            "action": "clickWindowRelative",
                            "target": "Background",
                            "match": {"x": "714", "y": "505", "cleanup": "settings"},
                        },
                    ],
                },
                {
                    "id": "ringcentral.video.more.notes",
                    "title": "Notes and transcript",
                    "area": "More menu",
                    "purpose": "Open notes side panel.",
                    "openSteps": [
                        {
                            "action": "clickWindowRelative",
                            "target": "More",
                            "match": {"x": "719", "y": "613"},
                        },
                        {
                            "action": "clickWindowRelative",
                            "target": "Notes",
                            "match": {"x": "701", "y": "448", "cleanup": "sidePanel"},
                        },
                    ],
                },
            ],
            "demoFlows": [],
            "manualControls": [],
        }
    )


def make_handle() -> WindowHandle:
    return WindowHandle("RingCentralVideo", 123, "RingCentralVideoClass", "RingCentral Video")


def test_package_action_executor_clicks_coordinate_step_and_cleanup() -> None:
    driver = RecordingDemoDriver()
    executor = PackageActionExecutor(
        package=make_package(),
        driver=driver,
        handle=make_handle(),
        clear_before_action=False,
        action_hold_seconds=0,
    )

    executor.execute_action("ringcentral.video.toolbar.audio-menu", operation="open")

    assert driver.log == ["click:123:143:604", "key:Escape"]


def test_package_action_executor_restores_toggle_actions() -> None:
    driver = RecordingDemoDriver()
    executor = PackageActionExecutor(
        package=make_package(),
        driver=driver,
        handle=make_handle(),
        clear_before_action=False,
        action_hold_seconds=0,
    )

    executor.execute_action("ringcentral.video.toolbar.raise-hand", operation="toggle")

    assert driver.log == ["click:123:645:613", "click:123:645:613"]


def test_package_action_executor_uses_toggle_cleanup_for_open_panels() -> None:
    driver = RecordingDemoDriver()
    executor = PackageActionExecutor(
        package=make_package(),
        driver=driver,
        handle=make_handle(),
        clear_before_action=False,
        action_hold_seconds=0,
    )

    executor.execute_action("ringcentral.video.toolbar.raise-hand", operation="open")

    assert driver.log == ["click:123:645:613", "click:123:645:613"]


def test_package_action_executor_does_not_click_explain_only_actions() -> None:
    driver = RecordingDemoDriver()
    executor = PackageActionExecutor(
        package=make_package(),
        driver=driver,
        handle=make_handle(),
        clear_before_action=False,
    )

    executor.execute_action("ringcentral.video.toolbar.leave", operation="explain")

    assert driver.log == []


def test_package_action_executor_closes_settings_dialogs() -> None:
    driver = RecordingDemoDriver()
    executor = PackageActionExecutor(
        package=make_package(),
        driver=driver,
        handle=make_handle(),
        clear_before_action=False,
        action_hold_seconds=0,
    )

    executor.execute_action("ringcentral.video.more.background", operation="open")

    assert driver.log == [
        "click:123:719:613",
        "click:123:714:505",
        "control:123:Close:1:button",
        "key:Escape",
    ]


def test_package_action_executor_can_defer_cleanup_until_narration_finishes() -> None:
    driver = RecordingDemoDriver()
    executor = PackageActionExecutor(
        package=make_package(),
        driver=driver,
        handle=make_handle(),
        clear_before_action=False,
        defer_cleanup=True,
        action_hold_seconds=0,
    )

    executor.execute_action("ringcentral.video.more.background", operation="open")

    assert driver.log == [
        "click:123:719:613",
        "click:123:714:505",
    ]

    executor.cleanup_pending()

    assert driver.log == [
        "click:123:719:613",
        "click:123:714:505",
        "control:123:Close:1:button",
        "key:Escape",
    ]


def test_package_action_executor_closes_side_panels() -> None:
    driver = RecordingDemoDriver()
    executor = PackageActionExecutor(
        package=make_package(),
        driver=driver,
        handle=make_handle(),
        clear_before_action=False,
        action_hold_seconds=0,
    )

    executor.execute_action("ringcentral.video.more.notes", operation="open")

    assert driver.log == [
        "click:123:719:613",
        "click:123:701:448",
        "click:123:878:75",
        "key:Escape",
    ]


def test_package_action_executor_clear_blockers_includes_side_panel_close() -> None:
    driver = RecordingDemoDriver()
    executor = PackageActionExecutor(
        package=make_package(),
        driver=driver,
        handle=make_handle(),
        clear_before_action=False,
    )

    executor.clear_blockers()

    assert "control:123:Close:1:button" in driver.log
    assert "control:123:Cancel:1:button" in driver.log
    assert "click:123:878:75" in driver.log


def test_package_action_executor_clicks_window_control_occurrence() -> None:
    driver = RecordingDemoDriver()
    executor = PackageActionExecutor(
        package=make_package(),
        driver=driver,
        handle=make_handle(),
        clear_before_action=False,
        action_hold_seconds=0,
    )

    executor.execute_action("ringcentral.video.toolbar.more-control", operation="open")

    assert driver.log == ["control:123:More:3:button", "key:Escape"]


def test_package_action_executor_resolves_coordinates_from_window_edges() -> None:
    driver = RecordingDemoDriver()
    executor = PackageActionExecutor(
        package=make_package(),
        driver=driver,
        handle=make_handle(),
        clear_before_action=False,
        action_hold_seconds=0,
    )

    executor.execute_action("ringcentral.video.top.report-anchored", operation="open")
    executor.execute_action("ringcentral.video.toolbar.audio-menu-anchored", operation="open")

    assert driver.log == [
        "bounds:123",
        "click:123:752:21",
        "key:Escape",
        "bounds:123",
        "click:123:143:604",
        "key:Escape",
    ]


def test_package_action_executor_uses_alternate_window_control_targets() -> None:
    driver = RecordingDemoDriver()
    driver.fail_controls.add("Raise hand")
    executor = PackageActionExecutor(
        package=make_package(),
        driver=driver,
        handle=make_handle(),
        clear_before_action=False,
        action_hold_seconds=0,
    )

    executor.execute_action("ringcentral.video.toolbar.raise-hand-alternate", operation="open")

    assert driver.log == [
        "control-fail:123:Raise hand:1",
        "control:123:Lower hand:1:button",
        "key:Escape",
    ]


def test_package_action_executor_adds_context_to_open_step_failures() -> None:
    driver = RecordingDemoDriver()
    driver.fail_controls.update({"Raise hand", "Lower hand"})
    executor = PackageActionExecutor(
        package=make_package(),
        driver=driver,
        handle=make_handle(),
        clear_before_action=False,
        action_hold_seconds=0,
    )

    with pytest.raises(PackageActionExecutionError) as exc_info:
        executor.execute_action("ringcentral.video.toolbar.raise-hand-alternate", operation="open")

    error = exc_info.value
    assert error.entrypoint_id == "ringcentral.video.toolbar.raise-hand-alternate"
    assert error.operation == "open"
    assert error.step_index == 1
    assert error.open_step_action == "clickWindowControl"
    assert error.open_step_target == "Raise hand"
    assert "ringcentral.video.toolbar.raise-hand-alternate" in str(error)
    assert "clickWindowControl" in str(error)
    assert "Raise hand" in str(error)
