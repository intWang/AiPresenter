from __future__ import annotations

import threading
from queue import Empty, Queue

from ai_presenter.packages.models import DemoStep


class DemoControl:
    def __init__(self) -> None:
        self._resume_event = threading.Event()
        self._resume_event.set()
        self._stop_event = threading.Event()
        self._interrupts: Queue[DemoStep] = Queue()

    def pause(self) -> None:
        self._resume_event.clear()

    def resume(self) -> None:
        self._resume_event.set()

    def request_stop(self) -> None:
        self._stop_event.set()
        self._resume_event.set()

    def reset(self) -> None:
        self._stop_event.clear()
        self._resume_event.set()
        self._clear_interrupts()

    @property
    def is_paused(self) -> bool:
        return not self._resume_event.is_set()

    @property
    def is_stop_requested(self) -> bool:
        return self._stop_event.is_set()

    def wait_before_step(self) -> bool:
        while not self._stop_event.is_set():
            if self._resume_event.wait(timeout=0.1):
                return not self._stop_event.is_set()
        return False

    def enqueue_interrupt(self, step: DemoStep) -> None:
        self._interrupts.put(step)

    def pop_interrupt(self) -> DemoStep | None:
        try:
            return self._interrupts.get_nowait()
        except Empty:
            return None

    def _clear_interrupts(self) -> None:
        while True:
            try:
                self._interrupts.get_nowait()
            except Empty:
                return
