from ai_presenter.config.models import NarrationConfig
from ai_presenter.domain.state import MeetingState, PresenterEvent
from ai_presenter.providers.fake import FakeNarrationProvider
from ai_presenter.runtime.narration import NarrationEngine


def make_config() -> NarrationConfig:
    return NarrationConfig.model_validate(
        {
            "style": "concise_presenter",
            "maxSentences": 2,
            "minSecondsBetweenUtterances": 4,
            "repeatCooldownSeconds": 30,
            "confidenceThreshold": 0.75,
            "forbidSharedScreenInterpretation": True,
        }
    )


def test_generates_for_first_event() -> None:
    engine = NarrationEngine(make_config(), FakeNarrationProvider(), now=lambda: 100.0)
    text = engine.maybe_narrate(
        MeetingState(confidence=0.9),
        [PresenterEvent("meeting_joined", {}, 0.9)],
    )

    assert text == "Detected meeting event: meeting_joined."


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


def test_suppresses_low_confidence_event() -> None:
    engine = NarrationEngine(make_config(), FakeNarrationProvider(), now=lambda: 100.0)
    text = engine.maybe_narrate(
        MeetingState(confidence=0.5),
        [PresenterEvent("meeting_joined", {}, 0.5)],
    )

    assert text is None
