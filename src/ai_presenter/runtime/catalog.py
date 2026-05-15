from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from ai_presenter.desktop.base import VisibleWindow


class WindowCatalogDriver(Protocol):
    def list_visible_windows(self) -> tuple[VisibleWindow, ...]:
        ...


@dataclass(frozen=True)
class MaterialPackageOption:
    package_id: str
    path: Path


class ControllerAppCatalog:
    def __init__(self, *, package_dir: Path, desktop: WindowCatalogDriver) -> None:
        self._package_dir = package_dir
        self._desktop = desktop

    def list_material_packages(self) -> tuple[MaterialPackageOption, ...]:
        options = [
            MaterialPackageOption(package_id=path.stem, path=path)
            for path in sorted(self._package_dir.glob("*.yaml"))
            if path.is_file()
        ]
        return tuple(options)

    def list_running_apps(self) -> tuple[VisibleWindow, ...]:
        return self._desktop.list_visible_windows()
