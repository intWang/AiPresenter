from __future__ import annotations

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from ai_presenter.media.output import MediaOutput
from ai_presenter.packages.models import DemoStep, DemoStepAction
from ai_presenter.providers.base import SpeechAudio, SpeechProvider
from ai_presenter.runtime.control import DemoControl
from ai_presenter.runtime.manual import ManualDirective
from ai_presenter.runtime.manual import ManualDirectiveQueue


class ActionExecutor(Protocol):
    def execute(self, action: DemoStepAction) -> None:
        ...


@dataclass(frozen=True)
class StepRunResult:
    step_id: str
    skipped: bool
    stopped: bool = False
    narration_text: str | None = None


class SynchronizedTimelineRunner:
    def __init__(
        self,
        *,
        speech_provider: SpeechProvider,
        media_output: MediaOutput,
        action_executor: ActionExecutor,
        manual_directives: ManualDirectiveQueue | None = None,
        control: DemoControl | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._speech_provider = speech_provider
        self._media_output = media_output
        self._action_executor = action_executor
        self._manual_directives = manual_directives
        self._control = control
        self._sleep = sleep

    def run_step(self, step: DemoStep) -> StepRunResult:
        if self._control is not None and not self._control.wait_before_step():
            return StepRunResult(step_id=step.id, skipped=True, stopped=True)

        narration_text = step.narration.text.strip()
        directive = self._peek_manual_directive()
        if directive is not None:
            if directive.kind == "skip":
                if not directive.text or _matches_step_directive(step, directive.text):
                    self._consume_manual_directive()
                    return StepRunResult(step_id=step.id, skipped=True)
            elif directive.kind == "focus":
                if _matches_step_directive(step, directive.text):
                    self._consume_manual_directive()
                else:
                    return StepRunResult(step_id=step.id, skipped=True)
            elif directive.kind == "say":
                self._consume_manual_directive()
                narration_text = directive.text

        placement = step.narration.placement
        if placement == "before":
            control_result = self._speak(step.id, narration_text)
            if control_result is not None:
                return control_result
            control_result = self._wait_for_resume_or_stop(step.id, narration_text)
            if control_result is not None:
                return control_result
            self._action_executor.execute(step.action)
            self._cleanup_pending_action()
        elif placement == "after":
            self._action_executor.execute(step.action)
            control_result = self._wait_for_resume_or_stop(step.id, narration_text)
            if control_result is not None:
                self._cleanup_pending_action()
                return control_result
            control_result = self._speak(step.id, narration_text)
            if control_result is not None:
                self._cleanup_pending_action()
                return control_result
            self._cleanup_pending_action()
        elif placement == "during":
            audio = self._speech_provider.synthesize(narration_text)
            playback = _BackgroundPlayback(self._media_output, audio)
            playback.start()
            self._sleep(step.narration.action_offset_ms / 1000)
            control_result = self._wait_for_resume_or_stop(step.id, narration_text)
            if control_result is not None:
                playback.stop()
                playback.join_and_raise()
                return control_result
            self._action_executor.execute(step.action)
            control_result = self._join_playback(step.id, narration_text, playback)
            if control_result is not None:
                self._cleanup_pending_action()
                return control_result
            self._cleanup_pending_action()
            control_result = self._wait_for_resume_or_stop(step.id, narration_text)
            if control_result is not None:
                return control_result
        else:
            raise ValueError(f"Unsupported narration placement: {placement}")

        return StepRunResult(step_id=step.id, skipped=False, narration_text=narration_text)

    def _speak(self, step_id: str, text: str) -> StepRunResult | None:
        audio = self._speech_provider.synthesize(text)
        playback = _BackgroundPlayback(self._media_output, audio)
        playback.start()
        return self._join_playback(step_id, text, playback)

    def _join_playback(
        self,
        step_id: str,
        narration_text: str,
        playback: _BackgroundPlayback,
    ) -> StepRunResult | None:
        if self._control is None:
            playback.join_and_raise()
            return None
        while playback.is_alive:
            if self._control.is_stop_requested:
                playback.stop()
                playback.join_and_raise()
                return _stopped_step(step_id, narration_text=narration_text)
            self._sleep(0.05)
        playback.join_and_raise()
        if self._control.is_stop_requested:
            return _stopped_step(step_id, narration_text=narration_text)
        return None

    def _cleanup_pending_action(self) -> None:
        cleanup = getattr(self._action_executor, "cleanup_pending", None)
        if callable(cleanup):
            cleanup()

    def _peek_manual_directive(self) -> ManualDirective | None:
        if self._manual_directives is None:
            return None
        return self._manual_directives.peek_next()

    def _consume_manual_directive(self) -> None:
        if self._manual_directives is not None:
            self._manual_directives.consume_next()

    def _wait_for_resume_or_stop(
        self,
        step_id: str,
        narration_text: str,
    ) -> StepRunResult | None:
        if self._control is None:
            return None
        if self._control.wait_before_step():
            return None
        return _stopped_step(step_id, narration_text=narration_text)


class _BackgroundPlayback:
    def __init__(self, media_output: MediaOutput, audio: SpeechAudio) -> None:
        self._media_output = media_output
        self._audio = audio
        self._error: BaseException | None = None
        self._thread = threading.Thread(target=self._play, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def join_and_raise(self) -> None:
        self._thread.join()
        if self._error is not None:
            raise RuntimeError("Timeline audio playback failed.") from self._error

    @property
    def is_alive(self) -> bool:
        return self._thread.is_alive()

    def stop(self) -> None:
        stop = getattr(self._media_output, "stop", None)
        if callable(stop):
            stop()

    def _play(self) -> None:
        try:
            self._media_output.play(self._audio)
        except BaseException as exc:
            self._error = exc


def _stopped_step(step_id: str, *, narration_text: str | None) -> StepRunResult:
    return StepRunResult(
        step_id=step_id,
        skipped=True,
        stopped=True,
        narration_text=narration_text,
    )


def _matches_step_directive(step: DemoStep, query: str) -> bool:
    needle = query.strip().casefold()
    if not needle:
        return True
    values = (
        step.id,
        step.title,
        step.action.entrypoint_id,
        step.action.operation,
        step.action.target or "",
    )
    return any(needle in value.casefold() for value in values)
