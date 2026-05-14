from __future__ import annotations

import time
from collections.abc import Callable
from typing import Protocol

from ai_presenter.desktop.base import WindowHandle
from ai_presenter.packages.models import DemoFlow, DemoStepAction, MaterialPackage, PackageOpenStep


class DemoWindowDriver(Protocol):
    def click_window_relative(self, handle: WindowHandle, x: int, y: int) -> None:
        ...

    def press_key(self, key: str) -> None:
        ...


class PackageActionExecutor:
    def __init__(
        self,
        *,
        package: MaterialPackage,
        driver: DemoWindowDriver,
        handle: WindowHandle,
        clear_before_action: bool = True,
        defer_cleanup: bool = False,
        action_hold_seconds: float = 0.8,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._package = package
        self._driver = driver
        self._handle = handle
        self._clear_before_action = clear_before_action
        self._defer_cleanup = defer_cleanup
        self._action_hold_seconds = action_hold_seconds
        self._sleep = sleep
        self._pending_cleanup: tuple[str, list[PackageOpenStep]] | None = None

    def execute(self, action: DemoStepAction) -> None:
        self.execute_action(action.entrypoint_id, operation=action.operation)

    def execute_action(self, entrypoint_id: str, *, operation: str) -> None:
        if operation in {"explain", "point", "verify"}:
            return

        entrypoint = self._package.entrypoint_by_id(entrypoint_id)
        if self._clear_before_action:
            self._clear_blockers()

        for step in entrypoint.open_steps:
            self._execute_open_step(step)

        if operation == "toggle":
            self._finish_or_defer_cleanup("toggle", entrypoint.open_steps)
            return

        cleanup = _cleanup_mode(entrypoint.open_steps)
        self._finish_or_defer_cleanup(cleanup, entrypoint.open_steps)

    def clear_blockers(self) -> None:
        self._clear_blockers()

    def cleanup_pending(self) -> None:
        if self._pending_cleanup is None:
            return
        cleanup, steps = self._pending_cleanup
        self._pending_cleanup = None
        self._cleanup(cleanup, steps)

    def _execute_open_step(self, step: PackageOpenStep) -> None:
        if step.action == "clickWindowRelative":
            x = _required_int_match(step, "x")
            y = _required_int_match(step, "y")
            self._driver.click_window_relative(self._handle, x, y)
            return
        if step.action == "pressKey":
            if step.target is None:
                raise ValueError("pressKey step requires target")
            self._driver.press_key(step.target)
            return
        raise ValueError(f"Unsupported package demo open step action: {step.action}")

    def _cleanup(self, cleanup: str, steps: list[PackageOpenStep]) -> None:
        if cleanup == "none":
            return
        if cleanup == "escape":
            self._driver.press_key("Escape")
            return
        if cleanup == "modal":
            self._clear_blockers()
            return
        if cleanup == "toggle":
            for step in steps:
                self._execute_open_step(step)
            return
        if cleanup == "settings":
            self._driver.click_window_relative(self._handle, 837, 47)
            self._driver.press_key("Escape")
            return
        if cleanup == "sidePanel":
            self._driver.click_window_relative(self._handle, 878, 75)
            self._driver.press_key("Escape")
            return
        raise ValueError(f"Unsupported package demo cleanup mode: {cleanup}")

    def _finish_or_defer_cleanup(self, cleanup: str, steps: list[PackageOpenStep]) -> None:
        if self._defer_cleanup:
            self._pending_cleanup = (cleanup, steps)
            return
        self._hold()
        self._cleanup(cleanup, steps)

    def _clear_blockers(self) -> None:
        for x, y in (
            (724, 139),
            (774, 254),
            (692, 195),
            (878, 75),
            (880, 86),
        ):
            self._driver.click_window_relative(self._handle, x, y)
        for _ in range(3):
            self._driver.press_key("Escape")

    def _hold(self) -> None:
        if self._action_hold_seconds > 0:
            self._sleep(self._action_hold_seconds)


def _required_int_match(step: PackageOpenStep, key: str) -> int:
    raw_value = step.match.get(key)
    if raw_value is None:
        raise ValueError(f"{step.action} step requires match.{key}")
    try:
        return int(raw_value)
    except ValueError as exc:
        raise ValueError(f"{step.action} match.{key} must be an integer") from exc


def _cleanup_mode(steps: list[PackageOpenStep]) -> str:
    for step in reversed(steps):
        cleanup = step.match.get("cleanup")
        if cleanup is not None and cleanup.strip():
            return cleanup.strip()
    return "none"


def demo_flow_by_id(package: MaterialPackage, flow_id: str) -> DemoFlow:
    for flow in package.demo_flows:
        if flow.id == flow_id:
            return flow
    raise KeyError(f"Unknown demo flow: {flow_id}")
