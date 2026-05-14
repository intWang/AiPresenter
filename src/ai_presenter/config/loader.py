from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]
from pydantic import TypeAdapter

from ai_presenter.config.models import AppProfile

_APP_PROFILE_ADAPTER: TypeAdapter[AppProfile] = TypeAdapter(AppProfile)


def load_profile(path: Path) -> AppProfile:
    profile_path = path.expanduser()
    raw = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Profile must be a YAML mapping: {path}")
    _resolve_presenter_context_paths(raw, profile_path.parent)
    return _APP_PROFILE_ADAPTER.validate_python(raw)


def profile_to_public_dict(profile: AppProfile) -> dict[str, Any]:
    return profile.model_dump(mode="json", by_alias=True)


def _resolve_presenter_context_paths(raw: dict[str, Any], profile_dir: Path) -> None:
    narration = raw.get("narration")
    if not isinstance(narration, dict):
        return

    for yaml_key in ("soulPath", "memoryPath"):
        value = narration.get(yaml_key)
        if value is None:
            continue
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{yaml_key} must be a non-empty file path")

        candidate = Path(value).expanduser()
        if not candidate.is_absolute():
            candidate = profile_dir / candidate
        resolved = candidate.resolve()
        if not resolved.is_file():
            raise ValueError(f"{yaml_key} file not found: {resolved}")
        narration[yaml_key] = resolved

    skill_paths = narration.get("skillPaths")
    if skill_paths is None:
        return
    if not isinstance(skill_paths, list):
        raise ValueError("skillPaths must be a list of file paths")

    resolved_skill_paths: list[Path] = []
    for value in skill_paths:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("skillPaths entries must be non-empty file paths")
        candidate = Path(value).expanduser()
        if not candidate.is_absolute():
            candidate = profile_dir / candidate
        resolved = candidate.resolve()
        if not resolved.is_file():
            raise ValueError(f"skillPaths file not found: {resolved}")
        resolved_skill_paths.append(resolved)
    narration["skillPaths"] = resolved_skill_paths
