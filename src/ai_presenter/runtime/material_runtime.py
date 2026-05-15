from collections.abc import Callable
from collections.abc import Sequence
from typing import Protocol

from ai_presenter.packages.models import DemoStep


class TimelineLike(Protocol):
    def run_step(self, step: DemoStep) -> object:
        ...


class MaterialDemoRuntime:
    def __init__(
        self,
        *,
        flow_steps: Sequence[DemoStep],
        timeline: TimelineLike,
        state_adjuster: Callable[[DemoStep], DemoStep | None],
    ) -> None:
        self._flow_steps = tuple(flow_steps)
        self._timeline = timeline
        self._state_adjuster = state_adjuster
        self._next_index = 0

    @property
    def is_complete(self) -> bool:
        return self._next_index >= len(self._flow_steps)

    def run_next(self) -> bool:
        if self.is_complete:
            return False
        step = self._flow_steps[self._next_index]
        self._next_index += 1
        adjusted = self._state_adjuster(step)
        if adjusted is None:
            return True
        result = self._timeline.run_step(adjusted)
        return not getattr(result, "stopped", False)

    def run_to_completion(self) -> None:
        while self.run_next():
            if self.is_complete:
                break

    def run_interrupt(self, step: DemoStep) -> None:
        self._timeline.run_step(step)
