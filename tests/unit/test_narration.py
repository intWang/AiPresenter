from ai_presenter.config.models import NarrationConfig
from ai_presenter.domain.state import MeetingState, PresenterEvent
from ai_presenter.providers.fake import FakeNarrationProvider
from ai_presenter.runtime.narration import NarrationEngine


class RecordingNarrationProvider:
    def __init__(self, responses: list[str] | None = None) -> None:
        self.calls: list[list[str]] = []
        self.event_batches: list[list[PresenterEvent]] = []
        self._responses = responses or []

    def narrate(self, state: MeetingState, events: list[PresenterEvent]) -> str:
        self.calls.append([event.type for event in events])
        self.event_batches.append(list(events))
        if self._responses:
            return self._responses.pop(0)
        event_names = ", ".join(event.type for event in events)
        return f"Detected meeting event: {event_names}."


class SequenceClock:
    def __init__(self, times: list[float]) -> None:
        self._times = times
        self.calls = 0

    def __call__(self) -> float:
        self.calls += 1
        if self._times:
            return self._times.pop(0)
        raise AssertionError("clock called more times than expected")


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


def test_samples_clock_once_per_narration_attempt() -> None:
    clock = SequenceClock([100.0])
    engine = NarrationEngine(make_config(), FakeNarrationProvider(), now=clock)

    text = engine.maybe_narrate(
        MeetingState(confidence=0.9),
        [PresenterEvent("meeting_joined", {}, 0.9)],
    )

    assert text == "Detected meeting event: meeting_joined."
    assert clock.calls == 1


def test_prepared_narration_does_not_update_cooldown_until_committed() -> None:
    current_time = 100.0

    def now() -> float:
        return current_time

    provider = RecordingNarrationProvider()
    engine = NarrationEngine(make_config(), provider, now=now)
    event = PresenterEvent("meeting_joined", {}, 0.9)

    first = engine.prepare_narration(MeetingState(confidence=0.9), [event])
    current_time = 101.0
    second = engine.prepare_narration(MeetingState(confidence=0.9), [event])
    assert first is not None
    assert second is not None

    engine.commit(first)
    current_time = 102.0
    third = engine.prepare_narration(MeetingState(confidence=0.9), [event])

    assert third is None
    assert provider.calls == [["meeting_joined"], ["meeting_joined"]]


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


def test_suppresses_exact_same_event_payload_during_repeat_cooldown() -> None:
    current_time = 100.0

    def now() -> float:
        return current_time

    provider = RecordingNarrationProvider()
    engine = NarrationEngine(make_config(), provider, now=now)

    first = engine.maybe_narrate(
        MeetingState(confidence=0.9),
        [PresenterEvent("mic_state_changed", {"micMuted": True}, 0.9)],
    )
    current_time = 105.0
    second = engine.maybe_narrate(
        MeetingState(confidence=0.9),
        [PresenterEvent("mic_state_changed", {"micMuted": True}, 0.9)],
    )

    assert first == "Detected meeting event: mic_state_changed."
    assert second is None
    assert provider.calls == [["mic_state_changed"]]


def test_dedupes_identical_events_within_same_batch() -> None:
    provider = RecordingNarrationProvider()
    engine = NarrationEngine(make_config(), provider, now=lambda: 100.0)

    text = engine.maybe_narrate(
        MeetingState(confidence=0.9),
        [
            PresenterEvent("mic_state_changed", {"micMuted": True}, 0.9),
            PresenterEvent("mic_state_changed", {"micMuted": True}, 0.9),
        ],
    )

    assert text == "Detected meeting event: mic_state_changed."
    assert provider.calls == [["mic_state_changed"]]
    assert len(provider.event_batches[0]) == 1
    assert provider.event_batches[0][0].payload == {"micMuted": True}


def test_keeps_distinct_event_fingerprint_when_deduping_batch() -> None:
    provider = RecordingNarrationProvider()
    engine = NarrationEngine(make_config(), provider, now=lambda: 100.0)

    text = engine.maybe_narrate(
        MeetingState(confidence=0.9),
        [
            PresenterEvent("mic_state_changed", {"micMuted": True}, 0.9),
            PresenterEvent("mic_state_changed", {"micMuted": True}, 0.9),
            PresenterEvent("mic_state_changed", {"micMuted": False}, 0.9),
        ],
    )

    assert text == "Detected meeting event: mic_state_changed, mic_state_changed."
    assert provider.calls == [["mic_state_changed", "mic_state_changed"]]
    assert [event.payload for event in provider.event_batches[0]] == [
        {"micMuted": True},
        {"micMuted": False},
    ]


def test_allows_opposite_mic_transitions_during_repeat_cooldown() -> None:
    current_time = 100.0

    def now() -> float:
        return current_time

    provider = RecordingNarrationProvider()
    engine = NarrationEngine(make_config(), provider, now=now)

    first = engine.maybe_narrate(
        MeetingState(confidence=0.9),
        [PresenterEvent("mic_state_changed", {"micMuted": True}, 0.9)],
    )
    current_time = 105.0
    second = engine.maybe_narrate(
        MeetingState(confidence=0.9),
        [PresenterEvent("mic_state_changed", {"micMuted": False}, 0.9)],
    )

    assert first == "Detected meeting event: mic_state_changed."
    assert second == "Detected meeting event: mic_state_changed."
    assert provider.calls == [["mic_state_changed"], ["mic_state_changed"]]


def test_allows_participant_count_changes_to_different_counts() -> None:
    current_time = 100.0

    def now() -> float:
        return current_time

    provider = RecordingNarrationProvider()
    engine = NarrationEngine(make_config(), provider, now=now)

    first = engine.maybe_narrate(
        MeetingState(confidence=0.9),
        [PresenterEvent("participant_count_changed", {"participantCount": 2}, 0.9)],
    )
    current_time = 105.0
    second = engine.maybe_narrate(
        MeetingState(confidence=0.9),
        [PresenterEvent("participant_count_changed", {"participantCount": 3}, 0.9)],
    )

    assert first == "Detected meeting event: participant_count_changed."
    assert second == "Detected meeting event: participant_count_changed."
    assert provider.calls == [["participant_count_changed"], ["participant_count_changed"]]


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
