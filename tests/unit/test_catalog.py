from pathlib import Path

from ai_presenter.desktop.base import VisibleWindow
from ai_presenter.runtime.catalog import ControllerAppCatalog


class FakeDesktop:
    def list_visible_windows(self) -> tuple[VisibleWindow, ...]:
        return (
            VisibleWindow("Demo", 10, "DemoWindow", "Demo App", (0, 0, 800, 600)),
        )


def test_catalog_lists_material_packages() -> None:
    catalog = ControllerAppCatalog(
        package_dir=Path("packages"),
        desktop=FakeDesktop(),
    )

    packages = catalog.list_material_packages()

    assert packages[0].package_id == "ringcentral-video"
    assert packages[0].path.name == "ringcentral-video.yaml"


def test_catalog_lists_running_desktop_apps() -> None:
    catalog = ControllerAppCatalog(package_dir=Path("packages"), desktop=FakeDesktop())

    windows = catalog.list_running_apps()

    assert windows[0].process == "Demo"
    assert windows[0].title == "Demo App"
