from dataclasses import dataclass
from pathlib import Path

from ai_presenter.config.models import NarrationConfig


@dataclass(frozen=True)
class PresenterSkill:
    name: str
    content: str


@dataclass(frozen=True)
class PresenterContext:
    soul: str = ""
    memory: str = ""
    skills: tuple[PresenterSkill, ...] = ()


def load_presenter_context(config: NarrationConfig) -> PresenterContext:
    return PresenterContext(
        soul=_read_optional_markdown(config.soul_path),
        memory=_read_optional_markdown(config.memory_path),
        skills=tuple(
            PresenterSkill(name=path.stem, content=_read_optional_markdown(path))
            for path in config.skill_paths
        ),
    )


def format_presenter_context(context: PresenterContext | None) -> str:
    if context is None:
        return ""

    sections: list[str] = []
    if context.soul.strip():
        sections.append(f"Presenter soul:\n{context.soul.strip()}")
    if context.memory.strip():
        sections.append(f"Persistent user coaching memory:\n{context.memory.strip()}")
    for skill in context.skills:
        if skill.content.strip():
            sections.append(f"Presenter skill - {skill.name}:\n{skill.content.strip()}")
    return "\n\n".join(sections)


def _read_optional_markdown(path: Path | None) -> str:
    if path is None:
        return ""
    return path.read_text(encoding="utf-8").strip()
