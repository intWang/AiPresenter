from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

from ai_presenter.config.models import AppProfile


def load_profile(path: Path) -> AppProfile:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Profile must be a YAML mapping: {path}")
    return AppProfile.model_validate(raw)


def profile_to_public_dict(profile: AppProfile) -> dict[str, Any]:
    return profile.model_dump(mode="json", by_alias=True)
