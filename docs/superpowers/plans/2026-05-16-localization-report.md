# Localization Report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a read-only CLI report for material-package localization coverage.

**Architecture:** Add pure package-level localization status dataclasses and renderer in `ai_presenter.packages.localization_status`; expose them through a Typer `localization-report` command. Keep output count-based and stable.

**Tech Stack:** Python dataclasses, Pydantic package models, Typer CLI, pytest, ruff, mypy.

---

## File Structure

- Create `src/ai_presenter/packages/localization_status.py`: pure coverage calculation and text rendering.
- Modify `src/ai_presenter/cli.py`: add `localization-report` command.
- Modify `tests/unit/test_material_packages.py`: helper coverage tests.
- Modify `tests/unit/test_cli.py`: CLI command tests.
- Modify `README.md`: short usage example.
- Create `docs/agent-handoffs/cycle-026-implementation.md`: implementation handoff.

## Task 1: Add Failing Helper Tests

**Files:**

- Modify: `tests/unit/test_material_packages.py`

- [ ] **Step 1: Import helper APIs**

Add imports:

```python
from ai_presenter.packages.localization_status import build_localization_status
from ai_presenter.packages.localization_status import render_localization_status_lines
```

- [ ] **Step 2: Add RingCentral count test**

Add near existing package localization tests:

```python
def test_ringcentral_localization_status_reports_chinese_coverage() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    report = build_localization_status(package, language="zh")

    assert report.package_id == "ringcentral-video"
    assert report.package_version == 1
    assert report.language == "zh"
    assert report.demo_localized_steps == 51
    assert report.demo_total_steps == 51
    assert report.qa_localized_questions == 8
    assert report.qa_localized_answers == 8
    assert report.qa_total == 8
    assert report.entrypoints_with_aliases == 15
    assert report.entrypoint_total == 27
    assert report.alias_total == 49
    assert report.flow_by_id["meeting-controls-tour"].localized_steps == 22
    assert report.flow_by_id["meeting-controls-tour"].total_steps == 22
```

- [ ] **Step 3: Add rendered lines test for partial package**

Use `MaterialPackage.model_validate()` to build a small package:

```python
def test_localization_status_renders_partial_coverage_without_failing() -> None:
    package = MaterialPackage.model_validate(
        {
            "appId": "demo",
            "appName": "Demo",
            "version": 1,
            "profileIds": ["demo-profile"],
            "operationEntrypoints": [
                {
                    "id": "demo.panel",
                    "title": "Panel",
                    "area": "Main",
                    "purpose": "Open panel.",
                    "questionAliases": {"zh": ["面板"]},
                    "openSteps": [],
                },
                {
                    "id": "demo.other",
                    "title": "Other",
                    "area": "Main",
                    "purpose": "Other panel.",
                    "openSteps": [],
                },
            ],
            "demoFlows": [
                {
                    "id": "onboarding-demo",
                    "title": "Onboarding",
                    "goal": "Show onboarding.",
                    "steps": [
                        {
                            "id": "intro",
                            "title": "Intro",
                            "action": {"entrypointId": "demo.panel", "operation": "explain"},
                            "narration": {
                                "text": "Show the panel.",
                                "localizedText": {"zh": "介绍面板。"},
                            },
                        },
                        {
                            "id": "missing",
                            "title": "Missing",
                            "action": {"entrypointId": "demo.other", "operation": "explain"},
                            "narration": {"text": "Show the missing panel."},
                        },
                    ],
                }
            ],
            "qa": [
                {
                    "question": "Where is the panel?",
                    "answer": "Open Panel.",
                    "localizedQuestions": {"zh": ["面板在哪里"]},
                    "localizedAnswers": {},
                    "relatedEntrypointIds": ["demo.panel"],
                }
            ],
            "manualControls": [],
        }
    )

    report = build_localization_status(package, language="zh")
    lines = render_localization_status_lines(report)

    assert report.demo_localized_steps == 1
    assert report.demo_total_steps == 2
    assert report.qa_localized_questions == 1
    assert report.qa_localized_answers == 0
    assert report.entrypoints_with_aliases == 1
    assert report.alias_total == 1
    assert "- onboarding-demo: 1/2 narration localized" in lines
    assert "  missing: missing" in lines
    assert "  missing answers: #1 Where is the panel?" in lines
```

Import `MaterialPackage` if not already imported:

```python
from ai_presenter.packages.models import MaterialPackage
```

- [ ] **Step 4: Add explicit zero-coverage language test**

```python
def test_localization_status_reports_zero_for_explicit_uncovered_language() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    report = build_localization_status(package, language="ja")

    assert report.language == "ja"
    assert report.demo_localized_steps == 0
    assert report.demo_total_steps == 51
    assert report.qa_localized_questions == 0
    assert report.qa_localized_answers == 0
    assert report.entrypoints_with_aliases == 0
    assert report.alias_total == 0
```

- [ ] **Step 5: Run helper tests and verify RED**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_chinese_coverage tests\unit\test_material_packages.py::test_localization_status_renders_partial_coverage_without_failing tests\unit\test_material_packages.py::test_localization_status_reports_zero_for_explicit_uncovered_language
```

Expected: import error because `ai_presenter.packages.localization_status` does not exist.

## Task 2: Implement Pure Localization Status Helper

**Files:**

- Create: `src/ai_presenter/packages/localization_status.py`

- [ ] **Step 1: Create dataclasses and builder**

Create:

```python
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from ai_presenter.packages.models import MaterialPackage


@dataclass(frozen=True)
class FlowLocalizationStatus:
    flow_id: str
    localized_steps: int
    total_steps: int
    missing_step_ids: tuple[str, ...]


@dataclass(frozen=True)
class LocalizationStatusReport:
    package_id: str
    package_version: int
    language: str
    flow_statuses: tuple[FlowLocalizationStatus, ...]
    demo_localized_steps: int
    demo_total_steps: int
    qa_localized_questions: int
    qa_localized_answers: int
    qa_total: int
    missing_question_indexes: tuple[tuple[int, str], ...]
    missing_answer_indexes: tuple[tuple[int, str], ...]
    entrypoints_with_aliases: int
    entrypoint_total: int
    alias_total: int
    _flow_by_id: Mapping[str, FlowLocalizationStatus]

    @property
    def flow_by_id(self) -> Mapping[str, FlowLocalizationStatus]:
        return self._flow_by_id
```

Add:

```python
def build_localization_status(package: MaterialPackage, *, language: str = "zh") -> LocalizationStatusReport:
    flow_statuses: list[FlowLocalizationStatus] = []
    demo_localized_steps = 0
    demo_total_steps = 0
    for flow in package.demo_flows:
        missing: list[str] = []
        localized = 0
        for step in flow.steps:
            demo_total_steps += 1
            if step.narration.localized_text.get(language, "").strip():
                localized += 1
                demo_localized_steps += 1
            else:
                missing.append(step.id)
        flow_statuses.append(
            FlowLocalizationStatus(
                flow_id=flow.id,
                localized_steps=localized,
                total_steps=len(flow.steps),
                missing_step_ids=tuple(missing),
            )
        )

    missing_questions: list[tuple[int, str]] = []
    missing_answers: list[tuple[int, str]] = []
    for index, item in enumerate(package.qa, start=1):
        if not item.localized_questions.get(language):
            missing_questions.append((index, item.question))
        if not item.localized_answers.get(language, "").strip():
            missing_answers.append((index, item.question))

    entrypoints_with_aliases = 0
    alias_total = 0
    for entrypoint in package.operation_entrypoints:
        aliases = [alias for alias in entrypoint.question_aliases.get(language, []) if alias.strip()]
        if aliases:
            entrypoints_with_aliases += 1
            alias_total += len(aliases)

    flow_by_id = MappingProxyType({status.flow_id: status for status in flow_statuses})
    return LocalizationStatusReport(
        package_id=package.app_id,
        package_version=package.version,
        language=language,
        flow_statuses=tuple(flow_statuses),
        demo_localized_steps=demo_localized_steps,
        demo_total_steps=demo_total_steps,
        qa_localized_questions=len(package.qa) - len(missing_questions),
        qa_localized_answers=len(package.qa) - len(missing_answers),
        qa_total=len(package.qa),
        missing_question_indexes=tuple(missing_questions),
        missing_answer_indexes=tuple(missing_answers),
        entrypoints_with_aliases=entrypoints_with_aliases,
        entrypoint_total=len(package.operation_entrypoints),
        alias_total=alias_total,
        _flow_by_id=flow_by_id,
    )
```

- [ ] **Step 2: Add renderer**

Add:

```python
def render_localization_status_lines(report: LocalizationStatusReport) -> list[str]:
    lines = [
        f"Package: {report.package_id}",
        f"Package version: {report.package_version}",
        f"Language: {report.language}",
        "",
        "Demo flows:",
    ]
    for flow in report.flow_statuses:
        lines.append(
            f"- {flow.flow_id}: {flow.localized_steps}/{flow.total_steps} narration localized"
        )
        if flow.missing_step_ids:
            lines.append(f"  missing: {', '.join(flow.missing_step_ids)}")
    lines.extend(
        [
            "",
            "Q&A:",
            f"- localized questions: {report.qa_localized_questions}/{report.qa_total}",
        ]
    )
    if report.missing_question_indexes:
        lines.append(
            "  missing questions: "
            + ", ".join(
                f"#{index} {question}" for index, question in report.missing_question_indexes
            )
        )
    lines.append(f"- localized answers: {report.qa_localized_answers}/{report.qa_total}")
    if report.missing_answer_indexes:
        lines.append(
            "  missing answers: "
            + ", ".join(f"#{index} {question}" for index, question in report.missing_answer_indexes)
        )
    lines.extend(
        [
            "",
            "Entrypoint aliases:",
            (
                f"- questionAliases.{report.language} present on "
                f"{report.entrypoints_with_aliases}/{report.entrypoint_total} entrypoints "
                f"({report.alias_total} aliases)"
            ),
            "",
            (
                "Localization report: "
                f"{report.demo_localized_steps}/{report.demo_total_steps} demo steps, "
                f"{report.qa_localized_questions}/{report.qa_total} Q&A questions, "
                f"{report.qa_localized_answers}/{report.qa_total} Q&A answers localized "
                f"for {report.language}."
            ),
        ]
    )
    return lines
```

- [ ] **Step 3: Run helper tests and verify GREEN**

Run the same helper test command from Task 1 Step 5.

Expected: pass.

## Task 3: Add CLI Command And Tests

**Files:**

- Modify: `src/ai_presenter/cli.py`
- Modify: `tests/unit/test_cli.py`
- Modify: `README.md`

- [ ] **Step 1: Add CLI imports**

In `src/ai_presenter/cli.py`, add:

```python
from ai_presenter.packages.localization_status import build_localization_status
from ai_presenter.packages.localization_status import render_localization_status_lines
```

- [ ] **Step 2: Add Typer command**

Add near `flows`/`entrypoints`:

```python
@app.command("localization-report")
def localization_report(
    package: str = typer.Option(..., "--package", help="Material package id or YAML path."),
    language: str = typer.Option("zh", "--language", help="Localization language to report."),
) -> None:
    """Report material-package localization coverage without running automation."""
    loaded_package = load_material_package(resolve_material_package(package))
    report = build_localization_status(loaded_package, language=language)
    typer.echo("\n".join(render_localization_status_lines(report)))
```

- [ ] **Step 3: Add CLI tests**

Add to `tests/unit/test_cli.py` near `test_flows_lists_material_package_demo_flows`:

```python
def test_localization_report_outputs_ringcentral_chinese_coverage() -> None:
    result = CliRunner().invoke(
        app,
        ["localization-report", "--package", "ringcentral-video"],
    )

    assert result.exit_code == 0
    assert "Package: ringcentral-video" in result.stdout
    assert "Language: zh" in result.stdout
    assert "- meeting-controls-tour: 22/22 narration localized" in result.stdout
    assert "- localized questions: 8/8" in result.stdout
    assert "- localized answers: 8/8" in result.stdout
    assert "questionAliases.zh present on 15/27 entrypoints (49 aliases)" in result.stdout
    assert "Localization report: 51/51 demo steps" in result.stdout
    assert "Loaded profile" not in result.stdout
```

```python
def test_localization_report_outputs_zero_for_explicit_uncovered_language() -> None:
    result = CliRunner().invoke(
        app,
        ["localization-report", "--package", "ringcentral-video", "--language", "ja"],
    )

    assert result.exit_code == 0
    assert "Language: ja" in result.stdout
    assert "- meeting-controls-tour: 0/22 narration localized" in result.stdout
    assert "missing: meeting-overview" in result.stdout
    assert "- localized questions: 0/8" in result.stdout
    assert "- localized answers: 0/8" in result.stdout
    assert "questionAliases.ja present on 0/27 entrypoints (0 aliases)" in result.stdout
```

- [ ] **Step 4: Add README example**

Near the `flows` and `entrypoints` examples, add:

```markdown
Check package localization coverage without running automation:

```powershell
.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language zh
```
```

- [ ] **Step 5: Run CLI/helper tests and verify GREEN**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py tests\unit\test_material_packages.py
```

Expected: pass.

## Task 4: Verification And Handoff

**Files:**

- Create: `docs/agent-handoffs/cycle-026-implementation.md`

- [ ] **Step 1: Run focused tests**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py tests\unit\test_material_packages.py
```

Expected: pass.

- [ ] **Step 2: Run ruff on touched files**

Run:

```powershell
.\.venv\Scripts\python -m ruff check --no-cache src\ai_presenter\packages\localization_status.py src\ai_presenter\cli.py tests\unit\test_cli.py tests\unit\test_material_packages.py
```

Expected: `All checks passed!`

- [ ] **Step 3: Run mypy on touched source/tests**

Run:

```powershell
.\.venv\Scripts\python -m mypy --no-incremental src tests
```

Expected: `Success: no issues found`.

- [ ] **Step 4: Run diff check**

Run:

```powershell
git diff --check -- src\ai_presenter\packages\localization_status.py src\ai_presenter\cli.py tests\unit\test_cli.py tests\unit\test_material_packages.py README.md docs\agent-handoffs\cycle-026-implementation.md docs\superpowers\specs\2026-05-16-localization-report-design.md docs\superpowers\plans\2026-05-16-localization-report.md
```

Expected: exit 0. LF-to-CRLF warnings are acceptable if no whitespace errors are reported.

- [ ] **Step 5: Write implementation handoff**

Create `docs/agent-handoffs/cycle-026-implementation.md` with:

```markdown
# Cycle 026 Implementation Handoff

Date: 2026-05-16
Role: implementation subagent
Scope: read-only package localization report.

## Summary

- Added pure package localization status helper.
- Added `ai-presenter localization-report`.
- Added helper and CLI tests.
- Documented the command in README.

## Verification

- RED: [exact failing command and output]
- GREEN: [exact passing command and output]
- Focused tests: [exact output]
- Ruff: [exact output]
- Mypy: [exact output]
- Diff check: [exact output]

## Notes

- Command is report-only and exits 0 for partial coverage.
- No runtime/demo execution, desktop automation, provider, controller, or package content behavior changed.
```

- [ ] **Step 6: Do not commit**

This workspace is accumulating many optimization cycles. Do not stage or commit unless the main session explicitly asks.
