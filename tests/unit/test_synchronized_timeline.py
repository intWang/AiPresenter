from typing import Literal
import threading

from ai_presenter.media.output import AudioSink
from ai_presenter.packages.models import DemoStep, DemoStepAction, DemoStepNarration
from ai_presenter.providers.base import SpeechAudio
from ai_presenter.runtime.control import DemoControl
from ai_presenter.runtime.manual import ManualDirectiveQueue
from ai_presenter.runtime.sync import SynchronizedTimelineRunner


class RecordingSpeechProvider:
    def __init__(self, log: list[str]) -> None:
        self._log = log
        self.spoken_texts: list[str] = []

    def synthesize(self, text: str) -> SpeechAudio:
        self._log.append(f"synthesize:{text}")
        self.spoken_texts.append(text)
        return SpeechAudio(data=f"wav:{text}".encode(), mime_type="audio/wav", sample_rate=1, channels=1)


class RecordingOutput(AudioSink):
    def __init__(self, log: list[str]) -> None:
        self._log = log

    def play(self, audio: SpeechAudio) -> None:
        self._log.append(audio.data.decode().replace("wav:", "play:"))


class BlockingStoppableOutput(AudioSink):
    def __init__(self, log: list[str]) -> None:
        self._log = log
        self.started = threading.Event()
        self.released = threading.Event()

    def play(self, audio: SpeechAudio) -> None:
        self._log.append("play:start")
        self.started.set()
        self.released.wait(timeout=2)
        self._log.append("play:end")

    def stop(self) -> None:
        self._log.append("stop")
        self.released.set()


class RecordingActionExecutor:
    def __init__(self, log: list[str]) -> None:
        self._log = log
        self.actions: list[DemoStepAction] = []

    def execute(self, action: DemoStepAction) -> None:
        self.actions.append(action)
        self._log.append(f"action:{action.entrypoint_id}:{action.operation}:{action.target}")


class CleanupRecordingActionExecutor(RecordingActionExecutor):
    def cleanup_pending(self) -> None:
        self._log.append("cleanup")


def make_step(
    *,
    placement: Literal["before", "during", "after"],
    step_id: str = "step-one",
    title: str = "Step One",
    entrypoint_id: str = "ringcentral.video.toolbar.video",
    target: str = "Start video",
    text: str = "Scripted narration.",
    action_offset_ms: int = 0,
) -> DemoStep:
    return DemoStep(
        id=step_id,
        title=title,
        action=DemoStepAction(
            entrypointId=entrypoint_id,
            operation="click",
            target=target,
        ),
        narration=DemoStepNarration(
            text=text,
            placement=placement,
            actionOffsetMs=action_offset_ms,
        ),
    )


def make_runner(
    log: list[str],
    *,
    manual_directives: ManualDirectiveQueue | None = None,
) -> tuple[SynchronizedTimelineRunner, RecordingActionExecutor]:
    action_executor = RecordingActionExecutor(log)
    runner = SynchronizedTimelineRunner(
        speech_provider=RecordingSpeechProvider(log),
        media_output=RecordingOutput(log),
        action_executor=action_executor,
        manual_directives=manual_directives,
        sleep=lambda seconds: log.append(f"sleep:{seconds:.1f}"),
    )
    return runner, action_executor


def test_before_narration_plays_audio_before_action() -> None:
    log: list[str] = []
    runner, _ = make_runner(log)

    result = runner.run_step(make_step(placement="before"))

    assert result.skipped is False
    assert log == [
        "synthesize:Scripted narration.",
        "play:Scripted narration.",
        "action:ringcentral.video.toolbar.video:click:Start video",
    ]


def test_before_narration_stops_blocking_audio_when_control_stops() -> None:
    log: list[str] = []
    control = DemoControl()
    media_output = BlockingStoppableOutput(log)
    action_executor = RecordingActionExecutor(log)
    runner = SynchronizedTimelineRunner(
        speech_provider=RecordingSpeechProvider(log),
        media_output=media_output,
        action_executor=action_executor,
        control=control,
    )
    result_holder: list[object] = []
    worker = threading.Thread(
        target=lambda: result_holder.append(runner.run_step(make_step(placement="before"))),
        daemon=True,
    )

    worker.start()
    assert media_output.started.wait(timeout=1)
    control.request_stop()
    worker.join(timeout=1)

    assert len(result_holder) == 1
    result = result_holder[0]
    assert getattr(result, "stopped") is True
    assert action_executor.actions == []
    assert log == ["synthesize:Scripted narration.", "play:start", "stop", "play:end"]


def test_after_narration_runs_action_before_audio() -> None:
    log: list[str] = []
    runner, _ = make_runner(log)

    runner.run_step(make_step(placement="after"))

    assert log == [
        "action:ringcentral.video.toolbar.video:click:Start video",
        "synthesize:Scripted narration.",
        "play:Scripted narration.",
    ]


def test_during_narration_starts_audio_then_offsets_action() -> None:
    log: list[str] = []
    runner, _ = make_runner(log)

    runner.run_step(make_step(placement="during", action_offset_ms=300))

    assert log == [
        "synthesize:Scripted narration.",
        "play:Scripted narration.",
        "sleep:0.3",
        "action:ringcentral.video.toolbar.video:click:Start video",
    ]


def test_during_narration_keeps_open_action_until_audio_finishes_before_cleanup() -> None:
    log: list[str] = []
    action_executor = CleanupRecordingActionExecutor(log)
    runner = SynchronizedTimelineRunner(
        speech_provider=RecordingSpeechProvider(log),
        media_output=RecordingOutput(log),
        action_executor=action_executor,
        sleep=lambda seconds: log.append(f"sleep:{seconds:.1f}"),
    )

    runner.run_step(make_step(placement="during", action_offset_ms=300))

    assert log == [
        "synthesize:Scripted narration.",
        "play:Scripted narration.",
        "sleep:0.3",
        "action:ringcentral.video.toolbar.video:click:Start video",
        "cleanup",
    ]


def test_say_directive_replaces_next_scripted_narration() -> None:
    log: list[str] = []
    manual_directives = ManualDirectiveQueue()
    manual_directives.submit("say: Explain that blur protects the room.")
    runner, _ = make_runner(log, manual_directives=manual_directives)

    result = runner.run_step(make_step(placement="before"))

    assert result.narration_text == "Explain that blur protects the room."
    assert log[:2] == [
        "synthesize:Explain that blur protects the room.",
        "play:Explain that blur protects the room.",
    ]


def test_skip_directive_skips_next_step_without_action_or_audio() -> None:
    log: list[str] = []
    manual_directives = ManualDirectiveQueue()
    manual_directives.submit("skip")
    runner, action_executor = make_runner(log, manual_directives=manual_directives)

    result = runner.run_step(make_step(placement="before"))

    assert result.skipped is True
    assert action_executor.actions == []
    assert log == []


def test_targeted_skip_waits_for_matching_step() -> None:
    log: list[str] = []
    manual_directives = ManualDirectiveQueue()
    manual_directives.submit("skip: participants")
    runner, action_executor = make_runner(log, manual_directives=manual_directives)

    first_result = runner.run_step(
        make_step(
            placement="before",
            step_id="chat",
            title="Chat panel",
            entrypoint_id="ringcentral.video.toolbar.chat",
            target="Chat",
        )
    )
    second_result = runner.run_step(
        make_step(
            placement="before",
            step_id="participants",
            title="Participants panel",
            entrypoint_id="ringcentral.video.toolbar.participants",
            target="Participants",
        )
    )

    assert first_result.skipped is False
    assert second_result.skipped is True
    assert [action.entrypoint_id for action in action_executor.actions] == [
        "ringcentral.video.toolbar.chat"
    ]


def test_focus_directive_skips_until_matching_step() -> None:
    log: list[str] = []
    manual_directives = ManualDirectiveQueue()
    manual_directives.submit("focus: chat")
    runner, action_executor = make_runner(log, manual_directives=manual_directives)

    first_result = runner.run_step(
        make_step(
            placement="before",
            step_id="participants",
            title="Participants panel",
            entrypoint_id="ringcentral.video.toolbar.participants",
            target="Participants",
        )
    )
    second_result = runner.run_step(
        make_step(
            placement="before",
            step_id="chat",
            title="Chat panel",
            entrypoint_id="ringcentral.video.toolbar.chat",
            target="Chat",
        )
    )

    assert first_result.skipped is True
    assert second_result.skipped is False
    assert [action.entrypoint_id for action in action_executor.actions] == [
        "ringcentral.video.toolbar.chat"
    ]
