import threading
import time

from ai_presenter.media.output import AudioSink
from ai_presenter.packages.models import DemoStep, DemoStepAction, DemoStepNarration
from ai_presenter.providers.base import SpeechAudio
from ai_presenter.runtime.control import DemoControl
from ai_presenter.runtime.sync import SynchronizedTimelineRunner


class RecordingSpeechProvider:
    def __init__(self, log: list[str]) -> None:
        self._log = log

    def synthesize(self, text: str) -> SpeechAudio:
        self._log.append(f"synthesize:{text}")
        return SpeechAudio(data=b"wav", mime_type="audio/wav", sample_rate=1, channels=1)


class RecordingOutput(AudioSink):
    def __init__(self, log: list[str]) -> None:
        self._log = log

    def play(self, audio: SpeechAudio) -> None:
        self._log.append("play")


class RecordingActionExecutor:
    def __init__(self, log: list[str]) -> None:
        self._log = log

    def execute(self, action: DemoStepAction) -> None:
        self._log.append(f"action:{action.entrypoint_id}")


def make_step() -> DemoStep:
    return DemoStep(
        id="step-one",
        title="Step One",
        action=DemoStepAction(entrypointId="entrypoint", operation="open"),
        narration=DemoStepNarration(text="Narration.", placement="before"),
    )


def test_demo_control_blocks_at_step_boundary_until_resumed() -> None:
    control = DemoControl()
    control.pause()
    results: list[bool] = []
    worker = threading.Thread(target=lambda: results.append(control.wait_before_step()), daemon=True)

    worker.start()
    time.sleep(0.05)

    assert results == []

    control.resume()
    worker.join(timeout=1)

    assert results == [True]


def test_demo_control_stop_request_returns_false_at_step_boundary() -> None:
    control = DemoControl()

    control.request_stop()

    assert control.wait_before_step() is False


def test_timeline_runner_skips_step_when_control_requests_stop() -> None:
    log: list[str] = []
    control = DemoControl()
    control.request_stop()
    runner = SynchronizedTimelineRunner(
        speech_provider=RecordingSpeechProvider(log),
        media_output=RecordingOutput(log),
        action_executor=RecordingActionExecutor(log),
        control=control,
    )

    result = runner.run_step(make_step())

    assert result.skipped is True
    assert result.stopped is True
    assert log == []
