from dataclasses import dataclass

from ai_presenter.config.models import DesktopAppProfile
from ai_presenter.desktop.base import VisibleControl, VisibleWindow
from ai_presenter.packages.models import DemoStep, DemoStepAction, DemoStepNarration
from ai_presenter.packages.models import MaterialPackage
from ai_presenter.runtime.questions import QuestionResponse, answer_question
from ai_presenter.runtime.temporary_package import build_temporary_package
from ai_presenter.runtime.voice import PresenterVoiceSettings, validate_profile_voice


@dataclass(frozen=True)
class MaterialPackageTarget:
    profile: DesktopAppProfile
    package: MaterialPackage
    flow_id: str


@dataclass(frozen=True)
class RunningAppTarget:
    window: VisibleWindow


ControllerTarget = MaterialPackageTarget | RunningAppTarget


class ControllerSession:
    def __init__(self) -> None:
        self._target: ControllerTarget | None = None
        self._active_package: MaterialPackage | None = None
        self._voice = PresenterVoiceSettings()
        self._running = False

    def select_target(self, target: ControllerTarget) -> None:
        if self._running:
            raise RuntimeError("Cannot change target while a demo is running.")
        if isinstance(target, MaterialPackageTarget):
            validate_profile_voice(target.profile, self._voice)
        self._target = target
        if isinstance(target, MaterialPackageTarget):
            self._active_package = target.package

    def scan_running_app(
        self,
        target: RunningAppTarget,
        controls: tuple[VisibleControl, ...],
    ) -> MaterialPackage:
        if self._running:
            raise RuntimeError("Cannot scan while a demo is running.")
        package = build_temporary_package(window=target.window, controls=controls)
        self._target = target
        self._active_package = package
        return package

    def set_voice(self, voice: PresenterVoiceSettings) -> None:
        if isinstance(self._target, MaterialPackageTarget):
            validate_profile_voice(self._target.profile, voice)
        self._voice = voice

    def answer_question(self, question: str) -> QuestionResponse:
        if self._active_package is None:
            return QuestionResponse("Select or scan an app first.")
        return answer_question(
            package=self._active_package,
            question=question,
            voice=self._voice,
        )

    def create_interrupt_step(self, response: QuestionResponse) -> DemoStep | None:
        if self._active_package is None:
            return None
        return create_question_interrupt_step(self._active_package, response)

    def mark_running(self) -> None:
        self._running = True

    def mark_stopped(self) -> None:
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    def mark_running_for_test(self) -> None:
        self.mark_running()


def create_question_interrupt_step(
    package: MaterialPackage,
    response: QuestionResponse,
) -> DemoStep | None:
    if response.entrypoint_id is None or not response.can_operate:
        return None
    entrypoint = package.entrypoint_by_id(response.entrypoint_id)
    if not entrypoint.open_steps:
        return None
    return DemoStep(
        id=f"question-{entrypoint.id}",
        title=f"Question: {entrypoint.title}",
        action=DemoStepAction(entrypointId=entrypoint.id, operation="open"),
        narration=DemoStepNarration(
            text=response.answer_text,
            placement="during",
            actionOffsetMs=300,
        ),
    )
