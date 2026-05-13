import re

from ai_presenter.domain.state import MeetingState, RawObservation


class RingCentralAdapter:
    def extract_state(self, observation: RawObservation) -> MeetingState:
        labels = tuple(observation.ui_text)
        text = " ".join(observation.ui_text)
        meeting_joined = (
            observation.metadata.process == "RingCentralVideo"
            and observation.metadata.window_class == "RingCentralVideoClass"
        )
        mic_muted = self._mic_muted(labels)
        camera_off = self._camera_off(labels)
        participant_count = self._participant_count(text)
        active_dialog = self._active_dialog(labels)
        connection_warning = self._connection_warning(labels)
        return MeetingState(
            meeting_joined=meeting_joined,
            mic_muted=mic_muted,
            camera_off=camera_off,
            active_dialog=active_dialog,
            participant_count=participant_count,
            connection_warning=connection_warning,
            confidence=self._confidence(
                meeting_joined=meeting_joined,
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

    def _participant_count(self, text: str) -> int | None:
        match = re.search(r"\bParticipants?\s*(?:\(\s*(\d+)\s*\)|:\s*(\d+)|\s+(\d+))", text)
        if not match:
            return None
        count = next(group for group in match.groups() if group is not None)
        return int(count)

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

    def _confidence(self, *, meeting_joined: bool, signals: tuple[object, ...]) -> float:
        has_explicit_signal = any(signal is not None for signal in signals)
        if meeting_joined and has_explicit_signal:
            return 0.85
        if meeting_joined:
            return 0.45
        return 0.2
