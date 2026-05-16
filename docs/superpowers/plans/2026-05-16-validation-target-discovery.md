# Validation Target Discovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an offline `validation-targets` discovery command that joins RingCentralVideo package metadata, evidence docs, and validation checklist rows into a reviewer-friendly target list.

**Architecture:** Implement parsing and rendering in a pure `ai_presenter.acceptance.validation_targets` module. Wire the CLI as a read-only list command using existing package resolution. Keep evidence files, package YAML, runtime, desktop automation, and `acceptance-runs.md` untouched.

**Tech Stack:** Python dataclasses, Typer, existing package loader/models, pytest, ruff, mypy.

---

## File Structure

- Create `src/ai_presenter/acceptance/validation_targets.py`: pure models, Markdown parsing, target discovery, filtering, rendering, and draft command generation.
- Modify `src/ai_presenter/cli.py`: add `validation-targets` command and default RingCentral knowledge-doc paths.
- Modify `tests/unit/test_cli.py`: add CLI tests.
- Create `tests/unit/test_validation_targets.py`: pure discovery tests.
- Create `docs/agent-handoffs/cycle-021-implementation.md`: implementation handoff.

## Task 1: Pure Discovery Parser And Renderer

**Files:**

- Create: `tests/unit/test_validation_targets.py`
- Create: `src/ai_presenter/acceptance/validation_targets.py`

- [ ] **Step 1: Write failing pure tests**

Create `tests/unit/test_validation_targets.py` with these helpers and tests:

```python
from pathlib import Path

import pytest

from ai_presenter.acceptance.validation_targets import acceptance_draft_command
from ai_presenter.acceptance.validation_targets import discover_validation_targets
from ai_presenter.acceptance.validation_targets import render_validation_target_lines
from ai_presenter.acceptance.validation_targets import target_by_id
from ai_presenter.packages.loader import load_material_package
from ai_presenter.packages.models import MaterialPackage


def load_ringcentral_package() -> MaterialPackage:
    return load_material_package(Path("packages/ringcentral-video.yaml"))


def load_checklist_text() -> str:
    return Path("docs/knowledge/ringcentral-video/validation-checklist-index.md").read_text(
        encoding="utf-8"
    )


def load_evidence_text() -> str:
    return Path("docs/knowledge/ringcentral-video/evidence-index.md").read_text(
        encoding="utf-8"
    )


def discover_catalog(*, checklist_text: str | None = None, include_blocked: bool = False):
    return discover_validation_targets(
        load_ringcentral_package(),
        checklist_text=checklist_text or load_checklist_text(),
        checklist_path=Path("docs/knowledge/ringcentral-video/validation-checklist-index.md"),
        evidence_text=load_evidence_text(),
        evidence_path=Path("docs/knowledge/ringcentral-video/evidence-index.md"),
        include_blocked=include_blocked,
    )
```

```python
def test_discover_validation_targets_reads_priority_checklist_rows() -> None:
    catalog = discover_catalog()

    target = target_by_id(catalog, "p0-add-coworkers-modal")

    assert target.priority == "P0"
    assert target.route_or_group == "Add coworkers modal"
    assert target.entrypoint_ids == ("ringcentral.video.main.add-coworkers",)
    assert target.flow_ids == ()
    assert "no live click acceptance" in target.current_state
    assert "Modal close" in target.cleanup
    assert "invite links" in target.privacy_boundary
    assert target.evidence_levels["ringcentral.video.main.add-coworkers"] == "Observed"
```

```python
def test_discover_validation_targets_separates_flow_ids_from_entrypoints() -> None:
    catalog = discover_catalog()

    target = target_by_id(catalog, "p0-controller-queued-chat-question")

    assert target.entrypoint_ids == ("ringcentral.video.toolbar.chat",)
    assert target.flow_ids == ("meeting-control-map-demo",)
```

```python
def test_discover_validation_targets_filters_by_priority_in_renderer() -> None:
    catalog = discover_catalog()

    text = "\n".join(render_validation_target_lines(catalog, priority="P0"))

    assert "p0-add-coworkers-modal" in text
    assert "p0-controller-queued-chat-question" in text
    assert "p1-top-bar-coordinate-routes" not in text
```

```python
def test_target_by_id_reports_available_ids_for_missing_target() -> None:
    catalog = discover_catalog()

    with pytest.raises(ValueError, match="Unknown validation target: missing-target") as exc_info:
        target_by_id(catalog, "missing-target")

    assert "p0-add-coworkers-modal" in str(exc_info.value)
```

```python
def test_discover_validation_targets_rejects_unknown_checklist_entrypoint() -> None:
    checklist_text = load_checklist_text().replace(
        "ringcentral.video.toolbar.chat",
        "ringcentral.video.toolbar.missing",
        1,
    )

    with pytest.raises(ValueError, match="ringcentral.video.toolbar.missing") as exc_info:
        discover_catalog(checklist_text=checklist_text)

    assert "Controller queued Chat question" in str(exc_info.value)
```

```python
def test_discover_validation_targets_rejects_duplicate_generated_ids() -> None:
    duplicate_row = (
        "\n| P0 | Add coworkers modal | `ringcentral.video.main.add-coworkers` | "
        "Duplicate | Validate | Cleanup | Privacy | `acceptance-runs.md` |"
    )
    checklist_text = load_checklist_text().replace(
        "\n## Do Not Execute Yet",
        f"{duplicate_row}\n\n## Do Not Execute Yet",
    )

    with pytest.raises(ValueError, match="duplicate validation target id: p0-add-coworkers-modal"):
        discover_catalog(checklist_text=checklist_text)
```

```python
def test_discover_validation_targets_can_include_blocked_rows() -> None:
    catalog = discover_catalog(include_blocked=True)

    recording = target_by_id(catalog, "blocked-recording")
    leave = target_by_id(catalog, "blocked-leave-or-end-meeting")

    assert recording.entrypoint_ids == ("ringcentral.video.more.recording",)
    assert recording.blocked_reason is not None
    assert "consent" in recording.blocked_reason
    assert leave.entrypoint_ids == ("ringcentral.video.toolbar.leave",)
    assert leave.blocked_reason is not None
    assert "destructive" in leave.blocked_reason
```

```python
def test_acceptance_draft_command_uses_entrypoint_only_for_single_entrypoint_target() -> None:
    catalog = discover_catalog()
    target = target_by_id(catalog, "p0-add-coworkers-modal")

    command = acceptance_draft_command(catalog.package_id, target)

    assert "--entrypoint ringcentral.video.main.add-coworkers" in command
    assert '--checklist-target "P0 Add coworkers modal"' in command
```

```python
def test_acceptance_draft_command_omits_entrypoint_for_group_target() -> None:
    catalog = discover_catalog()
    target = target_by_id(catalog, "p1-top-bar-coordinate-routes")

    command = acceptance_draft_command(catalog.package_id, target)

    assert "--entrypoint" not in command
    assert '--checklist-target "P1 Top-bar coordinate routes"' in command
```

- [ ] **Step 2: Run pure tests and verify RED**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_validation_targets.py
```

Expected: collection fails because `ai_presenter.acceptance.validation_targets` does not exist.

- [ ] **Step 3: Implement discovery module**

Create `src/ai_presenter/acceptance/validation_targets.py` with:

```python
from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from ai_presenter.packages.models import MaterialPackage

_BACKTICKED_ID_RE = re.compile(r"`([^`]+)`")
_NON_SLUG_RE = re.compile(r"[^a-z0-9]+")
```

Add the dataclasses from the design.

Implement:

```python
def discover_validation_targets(
    package: MaterialPackage,
    *,
    checklist_text: str,
    checklist_path: Path,
    evidence_text: str | None = None,
    evidence_path: Path | None = None,
    include_blocked: bool = False,
) -> ValidationTargetCatalog:
    evidence_levels, evidence_gaps = _parse_entrypoint_evidence(evidence_text or "")
    targets = _parse_priority_checklist(
        package=package,
        checklist_text=checklist_text,
        evidence_levels=evidence_levels,
        evidence_gaps=evidence_gaps,
    )
    if include_blocked:
        targets.extend(
            _parse_blocked_targets(
                package=package,
                checklist_text=checklist_text,
                evidence_levels=evidence_levels,
                evidence_gaps=evidence_gaps,
            )
        )
    _validate_unique_target_ids(targets)
    return ValidationTargetCatalog(
        package_id=package.app_id,
        checklist_path=checklist_path,
        evidence_path=evidence_path,
        targets=tuple(targets),
    )
```

Implement helper behavior:

- `_extract_section(text, heading)` returns text between `## <heading>` and the next `## `.
- `_parse_first_table(section, required_headers)` parses the first Markdown pipe table.
- `_normalize_header(header)` uses `strip().casefold()`.
- `_split_table_row(row)` strips outer pipes and cell whitespace.
- `_extract_ids(cell)` returns backticked ids.
- `_classify_ids(package, route_or_group, ids)` returns `(entrypoint_ids, flow_ids)` and raises on unknown ids.
- `_slug(value)` lowercases, replaces non-alphanumeric runs with `-`, strips `-`.
- `_target_id(priority, route_or_group)` returns `f"{priority.lower()}-{_slug(route_or_group)}"`.
- `_evidence_for(entrypoint_ids, evidence_levels, evidence_gaps)` returns maps for each entrypoint id with `unknown` or empty gap fallback.
- `_parse_priority_checklist(...)` builds target rows from required columns.
- `_parse_blocked_targets(...)` parses `Do Not Execute Yet` rows with ids `blocked-{slug(route)}`, priority `P3`, current state `Do not execute`, validate `Do not execute without separate confirmation workflow.`, cleanup empty, privacy boundary from reason, record result `Do not execute`, and `blocked_reason` from reason.
- `target_by_id(catalog, target_id)` returns the matching target or raises `ValueError(f"Unknown validation target: {target_id}. Available targets: {available}")`.
- `acceptance_draft_command(package_id, target)` returns:
  - `ai-presenter acceptance-draft --package {package_id} --entrypoint {entrypoint} --checklist-target "{priority} {route_or_group}"` for one-entrypoint targets;
  - `ai-presenter acceptance-draft --package {package_id} --flow {flow} --checklist-target "{priority} {route_or_group}"` for one-flow targets with no single entrypoint;
  - checklist-target-only command for grouped targets.
- `render_validation_target_lines(catalog, priority=None, target_id=None, include_draft_command=True)` returns header lines plus compact target blocks.

Keep all formatting deterministic and ASCII-friendly.

- [ ] **Step 4: Run pure tests and verify GREEN**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_validation_targets.py
```

Expected: all validation-target pure tests pass.

## Task 2: Wire CLI Command

**Files:**

- Modify: `src/ai_presenter/cli.py`
- Modify: `tests/unit/test_cli.py`

- [ ] **Step 1: Write failing CLI tests**

Add to `tests/unit/test_cli.py`:

```python
def test_validation_targets_lists_ringcentral_targets() -> None:
    result = CliRunner().invoke(
        app,
        ["validation-targets", "--package", "ringcentral-video", "--priority", "P0"],
    )

    assert result.exit_code == 0
    assert "Package: ringcentral-video" in result.stdout
    assert "validation-checklist-index.md" in result.stdout
    assert "p0-add-coworkers-modal" in result.stdout
    assert "p0-controller-queued-chat-question" in result.stdout
    assert "Loaded profile" not in result.stdout
```

```python
def test_validation_targets_detail_outputs_draft_command() -> None:
    result = CliRunner().invoke(
        app,
        [
            "validation-targets",
            "--package",
            "ringcentral-video",
            "--target",
            "p0-add-coworkers-modal",
        ],
    )

    assert result.exit_code == 0
    assert "ringcentral.video.main.add-coworkers" in result.stdout
    assert "Modal close" in result.stdout
    assert "invite links" in result.stdout
    assert (
        "ai-presenter acceptance-draft --package ringcentral-video "
        "--entrypoint ringcentral.video.main.add-coworkers"
    ) in result.stdout
```

```python
def test_validation_targets_rejects_unknown_target_with_available_ids() -> None:
    result = CliRunner().invoke(
        app,
        [
            "validation-targets",
            "--package",
            "ringcentral-video",
            "--target",
            "missing-target",
        ],
    )

    assert result.exit_code != 0
    assert "Unknown validation target: missing-target" in result.output
    assert "p0-add-coworkers-modal" in result.output
```

```python
def test_validation_targets_rejects_unknown_checklist_reference(tmp_path: Path) -> None:
    checklist_path = tmp_path / "validation-checklist-index.md"
    checklist_path.write_text(
        "\n".join(
            [
                "# Validation Checklist",
                "",
                "## Priority Checklist",
                "",
                "| Priority | Route Or Group | Entrypoints | Current State | Validate | Cleanup | Privacy Boundary | Record Result |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
                "| P0 | Missing route | `ringcentral.video.missing` | Missing | Validate | Cleanup | Privacy | `acceptance-runs.md` |",
            ]
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "validation-targets",
            "--package",
            "ringcentral-video",
            "--checklist",
            str(checklist_path),
        ],
    )

    assert result.exit_code != 0
    assert "ringcentral.video.missing" in result.output
```

```python
def test_validation_targets_include_blocked_lists_do_not_execute_routes() -> None:
    result = CliRunner().invoke(
        app,
        ["validation-targets", "--package", "ringcentral-video", "--include-blocked"],
    )

    assert result.exit_code == 0
    assert "ringcentral.video.more.recording" in result.stdout
    assert "ringcentral.video.toolbar.leave" in result.stdout
    assert "Do not execute" in result.stdout
```

- [ ] **Step 2: Run CLI tests and verify RED**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_validation_targets_lists_ringcentral_targets
```

Expected: command fails because `validation-targets` is not registered.

- [ ] **Step 3: Add CLI command**

In `src/ai_presenter/cli.py`, import:

```python
from ai_presenter.acceptance.validation_targets import discover_validation_targets
from ai_presenter.acceptance.validation_targets import render_validation_target_lines
```

Add constants:

```python
RINGCENTRAL_KNOWLEDGE_DIR = Path(__file__).resolve().parents[2] / "docs" / "knowledge" / "ringcentral-video"
DEFAULT_VALIDATION_CHECKLIST = RINGCENTRAL_KNOWLEDGE_DIR / "validation-checklist-index.md"
DEFAULT_EVIDENCE_INDEX = RINGCENTRAL_KNOWLEDGE_DIR / "evidence-index.md"
```

Add command after `entrypoints()` and before `acceptance_draft()`:

```python
@app.command("validation-targets")
def validation_targets(
    package: str = typer.Option(..., "--package", help="Material package id or YAML path."),
    priority: str | None = typer.Option(None, "--priority", help="Optional priority filter such as P0."),
    target: str | None = typer.Option(None, "--target", help="Optional discovered validation target id."),
    checklist: Path = typer.Option(
        DEFAULT_VALIDATION_CHECKLIST,
        "--checklist",
        help="Validation checklist markdown path.",
    ),
    evidence: Path = typer.Option(
        DEFAULT_EVIDENCE_INDEX,
        "--evidence",
        help="Evidence index markdown path.",
    ),
    include_blocked: bool = typer.Option(
        False,
        "--include-blocked",
        help="Include Do Not Execute Yet targets.",
    ),
) -> None:
    """List offline RingCentral validation targets without running automation."""
    loaded_package = load_material_package(resolve_material_package(package))
    try:
        checklist_text = checklist.read_text(encoding="utf-8")
        evidence_text = evidence.read_text(encoding="utf-8")
        catalog = discover_validation_targets(
            loaded_package,
            checklist_text=checklist_text,
            checklist_path=checklist,
            evidence_text=evidence_text,
            evidence_path=evidence,
            include_blocked=include_blocked,
        )
        lines = render_validation_target_lines(catalog, priority=priority, target_id=target)
    except OSError as exc:
        raise typer.BadParameter(str(exc)) from exc
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo("\n".join(lines))
```

- [ ] **Step 4: Run CLI tests and verify GREEN**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py tests\unit\test_validation_targets.py
```

Expected: CLI and pure validation-target tests pass.

## Task 3: Verify And Record Handoff

**Files:**

- Create: `docs/agent-handoffs/cycle-021-implementation.md`

- [ ] **Step 1: Run verification commands**

Run:

```powershell
.\.venv\Scripts\python -m ruff check --no-cache src\ai_presenter\acceptance\validation_targets.py src\ai_presenter\cli.py tests\unit\test_validation_targets.py tests\unit\test_cli.py
.\.venv\Scripts\python -m mypy --no-incremental src tests
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q
git diff --check -- src\ai_presenter\acceptance\validation_targets.py src\ai_presenter\cli.py tests\unit\test_validation_targets.py tests\unit\test_cli.py docs\agent-handoffs\cycle-021-implementation.md
```

Expected:

- Ruff passes.
- Mypy passes.
- Full pytest passes.
- Diff check is clean except possible existing CRLF warnings.

- [ ] **Step 2: Manual CLI smoke**

Run:

```powershell
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video --priority P0
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video --target p0-add-coworkers-modal
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video --include-blocked
```

Expected:

- P0 output includes Add coworkers and queued Chat.
- Target output includes Add coworkers cleanup/privacy/draft command.
- Include-blocked output includes recording and leave with do-not-execute wording.
- No profile loading, RingCentral automation, desktop scan, or file writes happen.

- [ ] **Step 3: Write implementation handoff**

Create `docs/agent-handoffs/cycle-021-implementation.md` with:

```markdown
# Cycle 021 Implementation Handoff

## Summary

- Added offline validation-target discovery for RingCentralVideo.
- Added read-only `validation-targets` CLI.
- Preserved existing acceptance draft and package commands.

## Changed Paths

- `src/ai_presenter/acceptance/validation_targets.py`
- `src/ai_presenter/cli.py`
- `tests/unit/test_validation_targets.py`
- `tests/unit/test_cli.py`

## TDD Evidence

- Pure RED:
- Pure GREEN:
- CLI RED:
- CLI GREEN:

## Verification

- Ruff:
- Mypy:
- Full pytest:
- Diff check:
- CLI smoke:

## Notes

- No live RingCentralVideo interaction was performed.
- No desktop automation was performed.
- No evidence file or acceptance run was written.
```

- [ ] **Step 4: Return worker status**

Return `DONE` with changed paths, exact verification summaries, and any concerns.
