from pathlib import Path

import yaml  # type: ignore[import-untyped]

from ai_presenter.packages.models import MaterialPackage


def load_material_package(path: Path) -> MaterialPackage:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Material package must be a YAML mapping: {path}")
    return MaterialPackage.model_validate(raw)
