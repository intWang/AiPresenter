from ai_presenter.packages.models import DemoStep
from ai_presenter.packages.models import DemoStepAction
from ai_presenter.packages.models import DemoStepNarration
from ai_presenter.runtime.material_runtime import MaterialDemoRuntime


class FakeTimeline:
    def __init__(self) -> None:
        self.steps: list[str] = []

    def run_step(self, step: DemoStep) -> object:
        self.steps.append(step.id)
        return type("Result", (), {"stopped": False})()


def make_step(step_id: str, entrypoint_id: str = "entry") -> DemoStep:
    return DemoStep(
        id=step_id,
        title=step_id,
        action=DemoStepAction(entrypointId=entrypoint_id, operation="explain"),
        narration=DemoStepNarration(text=step_id, placement="before"),
    )


def test_runtime_runs_flow_steps_in_order() -> None:
    timeline = FakeTimeline()
    runtime = MaterialDemoRuntime(
        flow_steps=[make_step("one"), make_step("two")],
        timeline=timeline,
        state_adjuster=lambda step: step,
    )

    runtime.run_to_completion()

    assert timeline.steps == ["one", "two"]


def test_runtime_can_run_interrupt_step_without_advancing_flow() -> None:
    timeline = FakeTimeline()
    runtime = MaterialDemoRuntime(
        flow_steps=[make_step("one"), make_step("two")],
        timeline=timeline,
        state_adjuster=lambda step: step,
    )

    runtime.run_interrupt(make_step("interrupt"))
    runtime.run_next()

    assert timeline.steps == ["interrupt", "one"]
