from __future__ import annotations

import logging
import time
from collections.abc import Callable
from time import perf_counter
from typing import Protocol

from ai_presenter.desktop.base import WindowHandle
from ai_presenter.packages.models import DemoStepAction, MaterialPackage, PackageOpenStep
from ai_presenter.runtime.logging import elapsed_ms, log_timed_event

logger = logging.getLogger("ai_presenter.runtime.package_demo")


class PackageActionExecutionError(RuntimeError):
    def __init__(
        self,
        *,
        entrypoint_id: str,
        operation: str,
        step_index: int,
        open_step: PackageOpenStep,
        cause: Exception,
    ) -> None:
        self.entrypoint_id = entrypoint_id
        self.operation = operation
        self.step_index = step_index
        self.open_step_action = open_step.action
        self.open_step_target = open_step.target
        target = open_step.target or "<none>"
        super().__init__(
            f"Package action failed for entrypoint {entrypoint_id}, operation {operation}, "
            f"open step {step_index} ({open_step.action}, target={target}): {cause}"
        )


class DemoWindowDriver(Protocol):
    def click_window_relative(self, handle: WindowHandle, x: int, y: int) -> None:
        ...

    def click_window_control(
        self,
        handle: WindowHandle,
        target: str,
        *,
        occurrence: int = 1,
        control_type: str | None = None,
    ) -> None:
        ...

    def window_bounds(self, handle: WindowHandle) -> tuple[int, int, int, int]:
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
        start = perf_counter()
        status = "ok"
        try:
            self._execute_action(entrypoint_id, operation=operation)
        except Exception:
            status = "error"
            raise
        finally:
            log_timed_event(
                logger,
                "package_action_executed",
                duration_ms=elapsed_ms(start, perf_counter()),
                status=status,
                package=self._package.app_id,
                entrypoint=entrypoint_id,
                operation=operation,
                deferred_cleanup=self._defer_cleanup,
                pending_cleanup=self._pending_cleanup is not None,
            )

    def _execute_action(self, entrypoint_id: str, *, operation: str) -> None:
        if operation in {"explain", "point", "verify"}:
            return

        entrypoint = self._package.entrypoint_by_id(entrypoint_id)
        if self._clear_before_action:
            self._clear_blockers()

        for index, step in enumerate(entrypoint.open_steps, start=1):
            try:
                self._execute_open_step(step)
            except Exception as exc:
                raise PackageActionExecutionError(
                    entrypoint_id=entrypoint_id,
                    operation=operation,
                    step_index=index,
                    open_step=step,
                    cause=exc,
                ) from exc

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
            x, y = _resolve_window_relative_point(step, self._driver, self._handle)
            self._driver.click_window_relative(self._handle, x, y)
            return
        if step.action == "clickWindowControl":
            if step.target is None:
                raise ValueError("clickWindowControl step requires target")
            occurrence = _optional_int_match(step, "occurrence", default=1)
            control_type = step.match.get("controlType")
            self._click_window_control_with_alternates(
                step,
                occurrence=occurrence,
                control_type=control_type,
            )
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
            self._click_close_control_if_available()
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
        self._click_control_if_available("Cancel")
        self._click_control_if_available("Close")
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

    def _click_close_control_if_available(self) -> None:
        self._click_control_if_available("Close")

    def _click_control_if_available(self, target: str) -> None:
        try:
            self._driver.click_window_control(
                self._handle,
                target,
                occurrence=1,
                control_type="button",
            )
        except Exception:
            return

    def _click_window_control_with_alternates(
        self,
        step: PackageOpenStep,
        *,
        occurrence: int,
        control_type: str | None,
    ) -> None:
        targets = [step.target or "", *_alternate_targets(step)]
        last_error: Exception | None = None
        for target in targets:
            if not target:
                continue
            try:
                self._driver.click_window_control(
                    self._handle,
                    target,
                    occurrence=occurrence,
                    control_type=control_type,
                )
                return
            except Exception as exc:
                last_error = exc
        if last_error is not None:
            raise last_error
        raise ValueError("clickWindowControl step requires target")


def _required_int_match(step: PackageOpenStep, key: str) -> int:
    raw_value = step.match.get(key)
    if raw_value is None:
        raise ValueError(f"{step.action} step requires match.{key}")
    return _parse_int_match(step, key, raw_value)


def _optional_int_match(step: PackageOpenStep, key: str, *, default: int) -> int:
    raw_value = step.match.get(key)
    if raw_value is None:
        return default
    return _parse_int_match(step, key, raw_value)


def _parse_int_match(step: PackageOpenStep, key: str, raw_value: str) -> int:
    try:
        return int(raw_value)
    except ValueError as exc:
        raise ValueError(f"{step.action} match.{key} must be an integer") from exc


def _alternate_targets(step: PackageOpenStep) -> list[str]:
    raw_targets = step.match.get("alternateTargets")
    if raw_targets is None:
        return []
    return [target.strip() for target in raw_targets.split(",") if target.strip()]


def _resolve_window_relative_point(
    step: PackageOpenStep,
    driver: DemoWindowDriver,
    handle: WindowHandle,
) -> tuple[int, int]:
    bounds: tuple[int, int, int, int] | None = None

    def size() -> tuple[int, int]:
        nonlocal bounds
        if bounds is None:
            bounds = driver.window_bounds(handle)
        left, top, right, bottom = bounds
        return right - left, bottom - top

    x = _resolve_axis_coordinate(
        step,
        absolute_key="x",
        inverse_key="xFromRight",
        axis_length=lambda: size()[0],
    )
    y = _resolve_axis_coordinate(
        step,
        absolute_key="y",
        inverse_key="yFromBottom",
        axis_length=lambda: size()[1],
    )
    return x, y


def _resolve_axis_coordinate(
    step: PackageOpenStep,
    *,
    absolute_key: str,
    inverse_key: str,
    axis_length: Callable[[], int],
) -> int:
    absolute_value = step.match.get(absolute_key)
    inverse_value = step.match.get(inverse_key)
    if absolute_value is not None and inverse_value is not None:
        raise ValueError(
            f"{step.action} step cannot combine match.{absolute_key} "
            f"and match.{inverse_key}"
        )
    if absolute_value is not None:
        return _parse_int_match(step, absolute_key, absolute_value)
    if inverse_value is not None:
        return axis_length() - _parse_int_match(step, inverse_key, inverse_value)
    raise ValueError(f"{step.action} step requires match.{absolute_key} or match.{inverse_key}")


def _cleanup_mode(steps: list[PackageOpenStep]) -> str:
    for step in reversed(steps):
        cleanup = step.match.get("cleanup")
        if cleanup is not None and cleanup.strip():
            return cleanup.strip()
    return "none"
