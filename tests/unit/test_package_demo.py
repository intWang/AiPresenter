from ai_presenter.desktop.base import WindowHandle
from ai_presenter.packages.models import MaterialPackage
from ai_presenter.runtime.package_demo import PackageActionExecutor


class RecordingDemoDriver:
    def __init__(self) -> None:
        self.log: list[str] = []

    def click_window_relative(self, handle: WindowHandle, x: int, y: int) -> None:
        self.log.append(f"click:{handle.pid}:{x}:{y}")

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
        "click:123:837:47",
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
        "click:123:837:47",
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

    assert "click:123:878:75" in driver.log
