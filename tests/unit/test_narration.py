from ai_presenter.config.models import NarrationConfig
from ai_presenter.domain.state import MeetingState, PresenterEvent
from ai_presenter.providers.fake import FakeNarrationProvider
from ai_presenter.runtime.narration import NarrationEngine


class RecordingNarrationProvider:
    def __init__(self, responses: list[str] | None = None) -> None:
        self.calls: list[list[str]] = []
        self._responses = responses or []

    def narrate(self, state: MeetingState, events: list[PresenterEvent]) -> str:
        self.calls.append([event.type for event in events])
        if self._responses:
            return self._responses.pop(0)
        event_names = ", ".join(event.type for event in events)
        return f"Detected meeting event: {event_names}."


def make_config(overrides: dict[str, object] | None = None) -> NarrationConfig:
    data = {
        "style": "concise_presenter",
        "maxSentences": 2,
        "minSecondsBetweenUtterances": 4,
        "repeatCooldownSeconds": 30,
        "confidenceThreshold": 0.75,
        "forbidSharedScreenInterpretation": True,
    }
    if overrides:
        data = {**data, **overrides}
    return NarrationConfig.model_validate(
        data,
    )


def test_generates_for_first_event() -> None:
    engine = NarrationEngine(make_config(), FakeNarrationProvider(), now=lambda: 100.0)
    text = engine.maybe_narrate(
        MeetingState(confidence=0.9),
        [PresenterEvent("meeting_joined", {}, 0.9)],
    )

    assert text == "Detected meeting event: meeting_joined."


def test_first_event_is_not_suppressed_by_large_min_interval() -> None:
    config = make_config({"minSecondsBetweenUtterances": 1_000_001})
    engine = NarrationEngine(config, FakeNarrationProvider(), now=lambda: 0.0)

    text = engine.maybe_narrate(
        MeetingState(confidence=0.9),
        [PresenterEvent("meeting_joined", {}, 0.9)],
    )

    assert text == "Detected meeting event: meeting_joined."


def test_suppresses_different_event_during_global_utterance_cooldown() -> None:
    current_time = 100.0

    def now() -> float:
        return current_time

    provider = RecordingNarrationProvider()
    engine = NarrationEngine(make_config(), provider, now=now)

    first = engine.maybe_narrate(
        MeetingState(confidence=0.9),
        [PresenterEvent("meeting_joined", {}, 0.9)],
    )
    current_time = 103.0
    second = engine.maybe_narrate(
        MeetingState(confidence=0.9),
        [PresenterEvent("mic_state_changed", {"micMuted": True}, 0.9)],
    )

    assert first == "Detected meeting event: meeting_joined."
    assert second is None
    assert provider.calls == [["meeting_joined"]]


def test_suppresses_repeated_event_during_cooldown() -> None:
    current_time = 100.0

    def now() -> float:
        return current_time

    engine = NarrationEngine(make_config(), FakeNarrationProvider(), now=now)

    first = engine.maybe_narrate(
        MeetingState(confidence=0.9),
        [PresenterEvent("meeting_joined", {}, 0.9)],
    )
    current_time = 105.0
    second = engine.maybe_narrate(
        MeetingState(confidence=0.9),
        [PresenterEvent("meeting_joined", {}, 0.9)],
    )

    assert first
    assert second is None


def test_allows_repeated_event_after_repeat_cooldown() -> None:
    current_time = 100.0

    def now() -> float:
        return current_time

    engine = NarrationEngine(make_config(), FakeNarrationProvider(), now=now)

    first = engine.maybe_narrate(
        MeetingState(confidence=0.9),
        [PresenterEvent("meeting_joined", {}, 0.9)],
    )
    current_time = 131.0
    second = engine.maybe_narrate(
        MeetingState(confidence=0.9),
        [PresenterEvent("meeting_joined", {}, 0.9)],
    )

    assert first == "Detected meeting event: meeting_joined."
    assert second == "Detected meeting event: meeting_joined."


def test_blank_narration_does_not_update_cooldown_state() -> None:
    current_time = 100.0

    def now() -> float:
        return current_time

    provider = RecordingNarrationProvider(["   ", "Meeting joined."])
    engine = NarrationEngine(make_config(), provider, now=now)

    first = engine.maybe_narrate(
        MeetingState(confidence=0.9),
        [PresenterEvent("meeting_joined", {}, 0.9)],
    )
    current_time = 105.0
    second = engine.maybe_narrate(
        MeetingState(confidence=0.9),
        [PresenterEvent("meeting_joined", {}, 0.9)],
    )

    assert first is None
    assert second == "Meeting joined."
    assert provider.calls == [["meeting_joined"], ["meeting_joined"]]


def test_suppresses_low_confidence_event() -> None:
    engine = NarrationEngine(make_config(), FakeNarrationProvider(), now=lambda: 100.0)
    text = engine.maybe_narrate(
        MeetingState(confidence=0.5),
        [PresenterEvent("meeting_joined", {}, 0.5)],
    )

    assert text is None
