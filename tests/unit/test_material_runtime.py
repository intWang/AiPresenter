from ai_presenter.packages.models import DemoStep
from ai_presenter.packages.models import DemoStepAction
from ai_presenter.packages.models import DemoStepNarration
from ai_presenter.runtime.control import DemoControl
from ai_presenter.runtime.material_runtime import MaterialDemoRuntime


class TimelineResult:
    def __init__(self, *, stopped: bool = False, narration_text: str | None = None) -> None:
        self.stopped = stopped
        self.narration_text = narration_text


class FakeTimeline:
    def __init__(self, results: dict[str, TimelineResult] | None = None) -> None:
        self.results = results or {}
        self.steps: list[str] = []

    def run_step(self, step: DemoStep) -> object:
        self.steps.append(step.id)
        return self.results.get(step.id, TimelineResult())


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


def test_runtime_runs_queued_control_interrupt_before_next_flow_step() -> None:
    timeline = FakeTimeline()
    control = DemoControl()
    control.enqueue_interrupt(make_step("interrupt"))
    runtime = MaterialDemoRuntime(
        flow_steps=[make_step("one"), make_step("two")],
        timeline=timeline,
        state_adjuster=lambda step: step,
        interrupt_source=control.pop_interrupt,
    )

    runtime.run_next()
    runtime.run_next()

    assert timeline.steps == ["interrupt", "one"]


def test_runtime_resumes_main_flow_after_queued_interrupt_between_steps() -> None:
    timeline = FakeTimeline()
    control = DemoControl()
    runtime = MaterialDemoRuntime(
        flow_steps=[make_step("one"), make_step("two")],
        timeline=timeline,
        state_adjuster=lambda step: step,
        interrupt_source=control.pop_interrupt,
    )

    runtime.run_next()
    control.enqueue_interrupt(make_step("interrupt"))
    runtime.run_next()
    runtime.run_next()

    assert timeline.steps == ["one", "interrupt", "two"]
    assert runtime.is_complete is True


def test_runtime_skips_none_adjusted_step_and_continues_flow() -> None:
    timeline = FakeTimeline()
    runtime = MaterialDemoRuntime(
        flow_steps=[make_step("one"), make_step("two"), make_step("three")],
        timeline=timeline,
        state_adjuster=lambda step: None if step.id == "two" else step,
    )

    runtime.run_to_completion()

    assert timeline.steps == ["one", "three"]
    assert runtime.is_complete is True


def test_runtime_stopped_main_flow_result_halts_to_completion() -> None:
    timeline = FakeTimeline(results={"two": TimelineResult(stopped=True)})
    runtime = MaterialDemoRuntime(
        flow_steps=[make_step("one"), make_step("two"), make_step("three")],
        timeline=timeline,
        state_adjuster=lambda step: step,
    )

    runtime.run_to_completion()

    assert timeline.steps == ["one", "two"]
    assert runtime.is_complete is False


def test_runtime_interrupt_returns_stopped_result_without_advancing_flow() -> None:
    interrupt_result = TimelineResult(stopped=True, narration_text="answer")
    timeline = FakeTimeline(results={"interrupt": interrupt_result})
    runtime = MaterialDemoRuntime(
        flow_steps=[make_step("one"), make_step("two")],
        timeline=timeline,
        state_adjuster=lambda step: step,
    )

    result = runtime.run_interrupt(make_step("interrupt"))
    runtime.run_next()

    assert result is interrupt_result
    assert getattr(result, "stopped") is True
    assert getattr(result, "narration_text") == "answer"
    assert timeline.steps == ["interrupt", "one"]


def test_runtime_consumes_stopped_main_step_before_next_run() -> None:
    timeline = FakeTimeline(results={"one": TimelineResult(stopped=True)})
    runtime = MaterialDemoRuntime(
        flow_steps=[make_step("one"), make_step("two")],
        timeline=timeline,
        state_adjuster=lambda step: step,
    )

    should_continue = runtime.run_next()
    resumed = runtime.run_next()

    assert should_continue is False
    assert resumed is True
    assert timeline.steps == ["one", "two"]
