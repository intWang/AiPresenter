from dataclasses import dataclass

from ai_presenter.config.models import DesktopAppProfile
from ai_presenter.desktop.base import VisibleControl, VisibleWindow
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
        self._target = target
        if isinstance(target, MaterialPackageTarget):
            validate_profile_voice(target.profile, self._voice)
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
        self._voice = voice

    def answer_question(self, question: str) -> QuestionResponse:
        if self._active_package is None:
            return QuestionResponse("Select or scan an app first.")
        return answer_question(
            package=self._active_package,
            question=question,
            voice=self._voice,
        )

    def mark_running_for_test(self) -> None:
        self._running = True
