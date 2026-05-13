import re

from ai_presenter.domain.state import MeetingState, RawObservation


class RingCentralAdapter:
    def extract_state(self, observation: RawObservation) -> MeetingState:
        labels = tuple(observation.ui_text)
        ringcentral_window = (
            observation.metadata.process == "RingCentralVideo"
            and observation.metadata.window_class == "RingCentralVideoClass"
        )
        mic_muted = self._mic_muted(labels)
        camera_off = self._camera_off(labels)
        participant_count = self._participant_count(labels)
        active_dialog = self._active_dialog(labels)
        meeting_joined = (
            ringcentral_window
            and active_dialog is None
            and self._has_in_meeting_evidence(
                mic_muted=mic_muted,
                camera_off=camera_off,
                participant_count=participant_count,
            )
        )
        connection_warning = self._connection_warning(labels)
        return MeetingState(
            meeting_joined=meeting_joined,
            mic_muted=mic_muted,
            camera_off=camera_off,
            active_dialog=active_dialog,
            participant_count=participant_count,
            connection_warning=connection_warning,
            confidence=self._confidence(
                ringcentral_window=ringcentral_window,
                signals=(mic_muted, camera_off, participant_count, active_dialog, connection_warning),
            ),
        )

    def _mic_muted(self, labels: tuple[str, ...]) -> bool | None:
        normalized = {label.strip().lower() for label in labels}
        if "unmute microphone" in normalized:
            return True
        if "mute microphone" in normalized:
            return False
        return None

    def _camera_off(self, labels: tuple[str, ...]) -> bool | None:
        normalized = {label.strip().lower() for label in labels}
        if "start video" in normalized:
            return True
        if "stop video" in normalized:
            return False
        return None

    def _participant_count(self, labels: tuple[str, ...]) -> int | None:
        for label in labels:
            match = re.fullmatch(
                r"\s*Participants\s*(?:\(\s*(\d+)\s*\)|:\s*(\d+)|\s+(\d+))\s*",
                label,
                flags=re.IGNORECASE,
            )
            if match:
                count = next(group for group in match.groups() if group is not None)
                return int(count)
        return None

    def _active_dialog(self, labels: tuple[str, ...]) -> str | None:
        normalized = {label.strip().lower() for label in labels}
        if normalized & {"permission required", "permissions required"}:
            return "permission"
        if normalized & {"waiting room", "waiting for host"}:
            return "waiting room"
        return None

    def _connection_warning(self, labels: tuple[str, ...]) -> str | None:
        normalized = {label.strip().lower() for label in labels}
        if normalized & {"reconnecting", "your connection is unstable"}:
            return "connection issue"
        return None

    def _has_in_meeting_evidence(
        self,
        *,
        mic_muted: bool | None,
        camera_off: bool | None,
        participant_count: int | None,
    ) -> bool:
        return mic_muted is not None or camera_off is not None or participant_count is not None

    def _confidence(self, *, ringcentral_window: bool, signals: tuple[object, ...]) -> float:
        has_explicit_signal = any(signal is not None for signal in signals)
        if ringcentral_window and has_explicit_signal:
            return 0.85
        if ringcentral_window:
            return 0.45
        return 0.2
