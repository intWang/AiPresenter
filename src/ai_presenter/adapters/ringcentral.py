import re

from ai_presenter.domain.state import MeetingState, RawObservation


class RingCentralAdapter:
    def extract_state(self, observation: RawObservation) -> MeetingState:
        text = " ".join(observation.ui_text)
        participant_count = self._participant_count(text)
        active_dialog = self._active_dialog(text)
        return MeetingState(
            meeting_joined=observation.metadata.window_class == "RingCentralVideoClass",
            mic_muted=self._mic_muted(text),
            camera_off=self._camera_off(text),
            active_dialog=active_dialog,
            participant_count=participant_count,
            connection_warning=self._connection_warning(text),
            confidence=0.85,
        )

    def _mic_muted(self, text: str) -> bool | None:
        if "Unmute" in text:
            return True
        if "Mute microphone" in text or "Mute" in text:
            return False
        return None

    def _camera_off(self, text: str) -> bool | None:
        if "Start video" in text:
            return True
        if "Stop video" in text:
            return False
        return None

    def _participant_count(self, text: str) -> int | None:
        match = re.search(r"Participants?\s+(\d+)", text)
        return int(match.group(1)) if match else None

    def _active_dialog(self, text: str) -> str | None:
        dialog_markers = ["permission", "waiting room", "connection"]
        lowered = text.lower()
        for marker in dialog_markers:
            if marker in lowered:
                return marker
        return None

    def _connection_warning(self, text: str) -> str | None:
        lowered = text.lower()
        if "unstable" in lowered or "reconnecting" in lowered:
            return "connection issue"
        return None
