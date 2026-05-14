from pathlib import Path

from ai_presenter.config.loader import load_profile
from ai_presenter.runtime.presenter_context import PresenterContext
from ai_presenter.runtime.presenter_context import PresenterSkill
from ai_presenter.runtime.presenter_context import format_presenter_context
from ai_presenter.runtime.presenter_context import load_presenter_context


def test_load_presenter_context_reads_configured_soul_and_memory() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))

    context = load_presenter_context(profile.narration)

    assert "professional live software presenter" in context.soul.lower()
    assert "Use English for RingCentral Video demos." in context.memory
    assert [skill.name for skill in context.skills] == ["app-director", "live-explainer"]
    assert "professional app demonstration director" in context.skills[0].content.lower()
    assert "professional live explainer" in context.skills[1].content.lower()


def test_format_presenter_context_includes_named_skills() -> None:
    context = PresenterContext(
        soul="Presenter identity.",
        memory="Durable coaching.",
        skills=(
            PresenterSkill(name="app-director", content="Plan clear app slices."),
            PresenterSkill(name="live-explainer", content="Recover from interruptions."),
        ),
    )

    formatted = format_presenter_context(context)

    assert "Presenter skill - app-director:" in formatted
    assert "Plan clear app slices." in formatted
    assert "Presenter skill - live-explainer:" in formatted
    assert "Recover from interruptions." in formatted
