# Acceptance Draft Helper Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an offline CLI helper that renders a RingCentral manual acceptance markdown draft without operating RingCentral.

**Architecture:** Implement pure markdown rendering in `src/ai_presenter/acceptance/manual_record.py`, then add a lightweight `acceptance-draft` Typer command that loads a material package and prints or writes the draft.

**Tech Stack:** Python dataclasses, Typer, pytest, existing material package models and loader.

---

## File Structure

- Create: `src/ai_presenter/acceptance/__init__.py`
  - Export public draft rendering helpers.
- Create: `src/ai_presenter/acceptance/manual_record.py`
  - Pure request/summary validation and markdown rendering.
- Modify: `src/ai_presenter/cli.py`
  - Add `acceptance-draft` command.
- Create: `tests/unit/test_acceptance_manual_record.py`
  - Renderer and validation tests.
- Modify: `tests/unit/test_cli.py`
  - CLI integration tests.
- Modify: `docs/runbooks/ringcentral-manual-acceptance.md`
  - Add one helper example, preserving evidence discipline.
- Create: `docs/agent-handoffs/cycle-018-implementation.md`
  - Record TDD and verification evidence.
- Create: `docs/agent-handoffs/cycle-018-review.md`
  - Record review findings.
- Create: `docs/agent-handoffs/cycle-018-summary.md`
  - Record final outcome.

No live RingCentral action, no package YAML edits, and no automatic append to `acceptance-runs.md`.

---

### Task 1: Pure Renderer Tests

**Files:**
- Create: `tests/unit/test_acceptance_manual_record.py`

- [ ] **Step 1: Add failing renderer tests**

Create the file with these tests:

```python
from pathlib import Path

import pytest

from ai_presenter.acceptance.manual_record import AcceptanceDraftRequest
from ai_presenter.acceptance.manual_record import render_manual_acceptance_draft
from ai_presenter.acceptance.manual_record import required_manual_acceptance_fields
from ai_presenter.packages.loader import load_material_package


def load_ringcentral_package():
    return load_material_package(Path("packages/ringcentral-video.yaml"))


def test_manual_acceptance_draft_includes_all_required_template_fields() -> None:
    draft = render_manual_acceptance_draft(
        load_ringcentral_package(),
        AcceptanceDraftRequest(entrypoint_id="ringcentral.video.main.add-coworkers"),
    )

    for field in required_manual_acceptance_fields():
        assert f"- {field}:" in draft


def test_manual_acceptance_draft_prefills_entrypoint_context_without_claiming_acceptance() -> None:
    draft = render_manual_acceptance_draft(
        load_ringcentral_package(),
        AcceptanceDraftRequest(entrypoint_id="ringcentral.video.main.add-coworkers"),
    )

    assert "Draft only" in draft
    assert "not acceptance evidence" in draft
    assert "ringcentral.video.main.add-coworkers" in draft
    assert "Add coworkers" in draft
    assert "Meeting canvas" in draft
    assert "clickWindowControl target=Add coworkers cleanup=modal" in draft
    assert "No live RingCentral action has been performed by this helper." in draft
    assert "- Pass/fail:" in draft
    assert "Accepted" not in draft


def test_manual_acceptance_draft_prefills_flow_steps() -> None:
    draft = render_manual_acceptance_draft(
        load_ringcentral_package(),
        AcceptanceDraftRequest(flow_id="meeting-control-map-demo"),
    )

    assert "meeting-control-map-demo" in draft
    assert "Meeting Control Map" in draft
    assert "ringcentral.video.toolbar.chat" in draft
    assert "ringcentral.video.main.add-coworkers" in draft


def test_manual_acceptance_draft_rejects_unknown_entrypoint() -> None:
    with pytest.raises(ValueError, match="Unknown operation entrypoint: missing"):
        render_manual_acceptance_draft(
            load_ringcentral_package(),
            AcceptanceDraftRequest(entrypoint_id="missing"),
        )


def test_manual_acceptance_draft_rejects_unknown_flow() -> None:
    with pytest.raises(ValueError, match="Unknown demo flow: missing-flow"):
        render_manual_acceptance_draft(
            load_ringcentral_package(),
            AcceptanceDraftRequest(flow_id="missing-flow"),
        )


def test_manual_acceptance_draft_rejects_entrypoint_outside_selected_flow() -> None:
    with pytest.raises(
        ValueError,
        match="is not used by selected flow vbg-blur-demo",
    ):
        render_manual_acceptance_draft(
            load_ringcentral_package(),
            AcceptanceDraftRequest(
                flow_id="vbg-blur-demo",
                entrypoint_id="ringcentral.video.toolbar.chat",
            ),
        )


def test_manual_acceptance_draft_warns_for_blocked_routes() -> None:
    draft = render_manual_acceptance_draft(
        load_ringcentral_package(),
        AcceptanceDraftRequest(entrypoint_id="ringcentral.video.toolbar.leave"),
    )

    assert "Explain-only or blocked route warning" in draft
    assert "do not execute the live action" in draft
    assert "ringcentral.video.toolbar.leave" in draft
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_acceptance_manual_record.py
```

Expected: FAIL because `ai_presenter.acceptance.manual_record` does not exist.

---

### Task 2: Pure Renderer Implementation

**Files:**
- Create: `src/ai_presenter/acceptance/__init__.py`
- Create: `src/ai_presenter/acceptance/manual_record.py`

- [ ] **Step 1: Implement dataclasses and rendering**

Create `src/ai_presenter/acceptance/__init__.py`:

```python
from ai_presenter.acceptance.manual_record import AcceptanceDraftRequest
from ai_presenter.acceptance.manual_record import render_manual_acceptance_draft
from ai_presenter.acceptance.manual_record import required_manual_acceptance_fields

__all__ = [
    "AcceptanceDraftRequest",
    "render_manual_acceptance_draft",
    "required_manual_acceptance_fields",
]
```

Create `src/ai_presenter/acceptance/manual_record.py` with:

```python
from dataclasses import dataclass
from typing import Iterable

from ai_presenter.packages.models import DemoFlow
from ai_presenter.packages.models import MaterialPackage
from ai_presenter.packages.models import OperationEntrypoint
from ai_presenter.packages.models import PackageOpenStep


_REQUIRED_MANUAL_ACCEPTANCE_FIELDS = (
    "Tester",
    "RingCentral app/build",
    "App channel",
    "Windows version",
    "Locale",
    "DPI/display scale",
    "Monitor setup",
    "Audio devices",
    "Virtual mic",
    "Profile",
    "Package flow",
    "Meeting role",
    "Meeting scenario",
    "Participant count",
    "Window bounds",
    "Evidence files",
    "Steps executed",
    "Pass/fail",
    "Failures",
    "Recovery",
    "Privacy notes",
    "Locator updates needed",
)


@dataclass(frozen=True)
class AcceptanceDraftRequest:
    profile_id: str | None = None
    flow_id: str | None = None
    entrypoint_id: str | None = None
    checklist_target: str | None = None
    tester: str | None = None
    local_time: str | None = None


@dataclass(frozen=True)
class AcceptanceTargetSummary:
    flow: DemoFlow | None
    entrypoint: OperationEntrypoint | None
    checklist_target: str | None


def required_manual_acceptance_fields() -> tuple[str, ...]:
    return _REQUIRED_MANUAL_ACCEPTANCE_FIELDS


def build_acceptance_target_summary(
    package: MaterialPackage,
    request: AcceptanceDraftRequest,
) -> AcceptanceTargetSummary:
    if not any((request.flow_id, request.entrypoint_id, request.checklist_target)):
        raise ValueError("Provide at least one target: --flow, --entrypoint, or --checklist-target.")

    flow = _resolve_flow(package, request.flow_id)
    entrypoint = _resolve_entrypoint(package, request.entrypoint_id)
    checklist_target = _normalize_optional_text(request.checklist_target)

    if flow is not None and entrypoint is not None:
        flow_entrypoints = {step.action.entrypoint_id for step in flow.steps}
        if entrypoint.id not in flow_entrypoints:
            raise ValueError(
                f"Entrypoint {entrypoint.id} is not used by selected flow {flow.id}."
            )

    return AcceptanceTargetSummary(
        flow=flow,
        entrypoint=entrypoint,
        checklist_target=checklist_target,
    )


def render_manual_acceptance_draft(
    package: MaterialPackage,
    request: AcceptanceDraftRequest,
) -> str:
    summary = build_acceptance_target_summary(package, request)
    lines: list[str] = [
        f"## {request.local_time or 'YYYY-MM-DD HH:mm Local'} - Manual RingCentral Acceptance Draft",
        "",
        "> Draft only: this is not acceptance evidence until filled after the manual run and appended to `acceptance-runs.md`.",
        "> No live RingCentral action has been performed by this helper.",
        "",
        "### Package Context",
        "",
        f"- Package: `{package.app_id}` ({package.app_name})",
        f"- Package version: {package.version}",
        f"- Profile: {request.profile_id or ''}",
    ]

    if summary.flow is not None:
        lines.extend(_render_flow_context(summary.flow))
    if summary.entrypoint is not None:
        lines.extend(_render_entrypoint_context(summary.entrypoint))
    if summary.checklist_target is not None:
        lines.extend(["", "### Checklist Context", "", f"- Checklist target: {summary.checklist_target}"])

    lines.extend(
        [
            "",
            "### Manual Acceptance Fields",
            "",
        ]
    )
    field_prefills = {
        "Tester": request.tester or "",
        "Profile": request.profile_id or "",
        "Package flow": summary.flow.id if summary.flow is not None else "",
        "Steps executed": _intended_steps(summary),
        "Privacy notes": _privacy_notes(summary),
    }
    for field in required_manual_acceptance_fields():
        lines.append(f"- {field}: {field_prefills.get(field, '')}")

    lines.extend(
        [
            "",
            "### Post-Run Documentation Order",
            "",
            "1. Complete the fields above only after the manual run.",
            "2. Append the completed record to `acceptance-runs.md` first.",
            "3. Update `locator-matrix.md`, `state-matrix.md`, `privacy-matrix.md`, and `evidence-index.md` only when the completed run justifies it.",
        ]
    )
    return "\n".join(lines) + "\n"
```

Then implement helper functions:

```python
def _resolve_flow(package: MaterialPackage, flow_id: str | None) -> DemoFlow | None:
    if flow_id is None:
        return None
    try:
        return package.demo_flow_by_id(flow_id)
    except KeyError as exc:
        raise ValueError(str(exc.args[0])) from exc


def _resolve_entrypoint(
    package: MaterialPackage,
    entrypoint_id: str | None,
) -> OperationEntrypoint | None:
    if entrypoint_id is None:
        return None
    try:
        return package.entrypoint_by_id(entrypoint_id)
    except KeyError as exc:
        raise ValueError(str(exc.args[0])) from exc


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _render_flow_context(flow: DemoFlow) -> list[str]:
    entrypoints = ", ".join(dict.fromkeys(step.action.entrypoint_id for step in flow.steps))
    return [
        "",
        "### Flow Context",
        "",
        f"- Flow: `{flow.id}` ({flow.title})",
        f"- Goal: {flow.goal}",
        f"- Referenced entrypoints: {entrypoints}",
    ]


def _render_entrypoint_context(entrypoint: OperationEntrypoint) -> list[str]:
    lines = [
        "",
        "### Entrypoint Context",
        "",
        f"- Entrypoint: `{entrypoint.id}` ({entrypoint.title})",
        f"- Area: {entrypoint.area}",
        f"- Purpose: {entrypoint.purpose}",
        "- Open steps:",
    ]
    open_steps = _format_open_steps(entrypoint.open_steps)
    if open_steps:
        lines.extend(f"  - {step}" for step in open_steps)
    else:
        lines.append("  - None; explain-only or blocked route.")
        lines.extend(
            [
                "",
                "### Explain-only or blocked route warning",
                "",
                "- This route has no executable open steps in the package; do not execute the live action without a separate confirmation workflow.",
            ]
        )
    if entrypoint.presenter_notes:
        lines.append("- Presenter notes:")
        lines.extend(f"  - {note}" for note in entrypoint.presenter_notes)
    return lines


def _format_open_steps(open_steps: Iterable[PackageOpenStep]) -> list[str]:
    formatted: list[str] = []
    for step in open_steps:
        parts = [step.action]
        if step.target:
            parts.append(f"target={step.target}")
        cleanup = step.match.get("cleanup")
        if cleanup:
            parts.append(f"cleanup={cleanup}")
        formatted.append(" ".join(parts))
    return formatted


def _intended_steps(summary: AcceptanceTargetSummary) -> str:
    if summary.entrypoint is not None:
        return f"Intended target: {summary.entrypoint.id}; fill with actual steps after the run."
    if summary.flow is not None:
        return f"Intended flow: {summary.flow.id}; fill with actual steps after the run."
    if summary.checklist_target is not None:
        return f"Intended checklist target: {summary.checklist_target}; fill with actual steps after the run."
    return ""


def _privacy_notes(summary: AcceptanceTargetSummary) -> str:
    reminders = [
        "Draft reminder: do not record private chat text, participant names, invite links, meeting IDs, shared content, notes, transcripts, device lists, account details, or report contents.",
    ]
    if summary.entrypoint is not None and not summary.entrypoint.open_steps:
        reminders.append("Explain-only or blocked route; do not execute the live action without confirmation workflow.")
    return " ".join(reminders)
```

- [ ] **Step 2: Run renderer tests and verify GREEN**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_acceptance_manual_record.py
```

Expected: PASS.

---

### Task 3: CLI Acceptance Draft Tests

**Files:**
- Modify: `tests/unit/test_cli.py`

- [ ] **Step 1: Add failing CLI tests**

Add these tests near `flows` and `entrypoints` tests:

```python
def test_acceptance_draft_outputs_entrypoint_template() -> None:
    result = CliRunner().invoke(
        app,
        [
            "acceptance-draft",
            "--package",
            "ringcentral-video",
            "--entrypoint",
            "ringcentral.video.toolbar.chat",
        ],
    )

    assert result.exit_code == 0
    assert "Draft only" in result.stdout
    assert "Package: `ringcentral-video`" in result.stdout
    assert "ringcentral.video.toolbar.chat" in result.stdout
    assert "- Privacy notes:" in result.stdout
    assert "- Locator updates needed:" in result.stdout
    assert "Loaded profile" not in result.stdout


def test_acceptance_draft_outputs_flow_template() -> None:
    result = CliRunner().invoke(
        app,
        [
            "acceptance-draft",
            "--package",
            "ringcentral-video",
            "--flow",
            "meeting-control-map-demo",
        ],
    )

    assert result.exit_code == 0
    assert "meeting-control-map-demo" in result.stdout
    assert "Meeting Control Map" in result.stdout
    assert "ringcentral.video.main.add-coworkers" in result.stdout


def test_acceptance_draft_requires_target() -> None:
    result = CliRunner().invoke(app, ["acceptance-draft", "--package", "ringcentral-video"])

    assert result.exit_code != 0
    assert "Provide at least one target" in result.output


def test_acceptance_draft_rejects_missing_flow_with_available_flows() -> None:
    result = CliRunner().invoke(
        app,
        ["acceptance-draft", "--package", "ringcentral-video", "--flow", "missing-flow"],
    )

    assert result.exit_code != 0
    assert "Unknown demo flow: missing-flow" in result.output
    assert "Available flows:" in result.output


def test_acceptance_draft_can_write_to_output_file(tmp_path: Path) -> None:
    output_path = tmp_path / "acceptance-draft.md"

    result = CliRunner().invoke(
        app,
        [
            "acceptance-draft",
            "--package",
            "ringcentral-video",
            "--entrypoint",
            "ringcentral.video.main.add-coworkers",
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    assert f"Wrote acceptance draft: {output_path}" in result.stdout
    text = output_path.read_text(encoding="utf-8")
    assert "ringcentral.video.main.add-coworkers" in text
    assert "Draft only" in text
```

- [ ] **Step 2: Run CLI tests and verify RED**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_acceptance_draft_outputs_entrypoint_template tests\unit\test_cli.py::test_acceptance_draft_outputs_flow_template tests\unit\test_cli.py::test_acceptance_draft_requires_target tests\unit\test_cli.py::test_acceptance_draft_rejects_missing_flow_with_available_flows tests\unit\test_cli.py::test_acceptance_draft_can_write_to_output_file
```

Expected: FAIL because `acceptance-draft` command does not exist yet.

---

### Task 4: CLI Acceptance Draft Implementation

**Files:**
- Modify: `src/ai_presenter/cli.py`

- [ ] **Step 1: Import renderer helpers**

Add near existing imports:

```python
from ai_presenter.acceptance.manual_record import AcceptanceDraftRequest
from ai_presenter.acceptance.manual_record import render_manual_acceptance_draft
```

- [ ] **Step 2: Add the CLI command**

Add this command near `entrypoints`/`flows`:

```python
@app.command("acceptance-draft")
def acceptance_draft(
    package: str = typer.Option(..., "--package", help="Material package id or YAML path."),
    flow: str | None = typer.Option(None, "--flow", help="Optional demo flow id."),
    entrypoint: str | None = typer.Option(
        None,
        "--entrypoint",
        help="Optional operation entrypoint id.",
    ),
    checklist_target: str | None = typer.Option(
        None,
        "--checklist-target",
        help="Optional validation checklist target label.",
    ),
    profile: str | None = typer.Option(None, "--profile", help="Optional profile text prefill."),
    tester: str | None = typer.Option(None, "--tester", help="Optional tester name prefill."),
    local_time: str | None = typer.Option(
        None,
        "--local-time",
        help="Optional local timestamp text for the draft header.",
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        help="Optional path to write the draft instead of printing it.",
    ),
) -> None:
    """Render a manual RingCentral acceptance markdown draft without automation."""
    loaded_package = load_material_package(resolve_material_package(package))
    request = AcceptanceDraftRequest(
        profile_id=profile,
        flow_id=flow,
        entrypoint_id=entrypoint,
        checklist_target=checklist_target,
        tester=tester,
        local_time=local_time,
    )
    try:
        draft = render_manual_acceptance_draft(loaded_package, request)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(draft, encoding="utf-8")
        typer.echo(f"Wrote acceptance draft: {output}")
        return

    typer.echo(draft, nl=False)
```

- [ ] **Step 3: Run CLI tests and verify GREEN**

Run the five CLI tests from Task 3.

Expected: PASS.

---

### Task 5: Docs And Implementation Handoff

**Files:**
- Modify: `docs/runbooks/ringcentral-manual-acceptance.md`
- Create: `docs/agent-handoffs/cycle-018-implementation.md`

- [ ] **Step 1: Add runbook helper note**

Near the live route validation checklist note, add:

```markdown
- To prepare a manual evidence draft without touching RingCentral, run `.venv\Scripts\ai-presenter acceptance-draft --package ringcentral-video --entrypoint ringcentral.video.main.add-coworkers`; complete the draft only after the actual manual run.
```

- [ ] **Step 2: Write implementation handoff**

Create `docs/agent-handoffs/cycle-018-implementation.md`:

```markdown
# Cycle 018 Implementation

Date: 2026-05-16

## Changes

- Added pure manual acceptance draft rendering.
- Added `ai-presenter acceptance-draft`.
- Added renderer and CLI tests.
- Added a runbook note for preparing drafts.

## TDD Evidence

- RED renderer tests:
- GREEN renderer tests:
- RED CLI tests:
- GREEN CLI tests:

## Verification

- Renderer tests:
- CLI tests:
- Full suite:
- Ruff:
- Mypy:
- Diff check:

## Notes

- No live RingCentral actions were run.
- No route was promoted to Accepted.
- No package YAML schema was changed.
- The helper writes drafts only; it does not append to `acceptance-runs.md`.
```

---

### Task 6: Verification

**Files:** no code changes unless verification exposes an issue.

- [ ] **Step 1: Run renderer tests**

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_acceptance_manual_record.py
```

- [ ] **Step 2: Run CLI tests**

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py
```

- [ ] **Step 3: Run full tests**

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
```

- [ ] **Step 4: Run ruff**

```powershell
.\.venv\Scripts\python -m ruff check --no-cache .
```

- [ ] **Step 5: Run mypy**

```powershell
.\.venv\Scripts\python -m mypy --no-incremental src tests
```

- [ ] **Step 6: Run diff check**

```powershell
git diff --check -- src\ai_presenter\acceptance\__init__.py src\ai_presenter\acceptance\manual_record.py src\ai_presenter\cli.py tests\unit\test_acceptance_manual_record.py tests\unit\test_cli.py docs\runbooks\ringcentral-manual-acceptance.md docs\agent-handoffs\cycle-018-implementation.md
```

Expected: all verification passes. Pytest may emit the existing pywinauto STA warning.
