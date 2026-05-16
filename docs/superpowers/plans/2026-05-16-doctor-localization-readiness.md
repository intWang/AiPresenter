# Doctor Localization Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add optional strict localization readiness to `ai-presenter doctor`.

**Architecture:** Keep localization counting in `packages.localization_status`; add a compact diagnostics-layer check that CLI can opt into with `--require-localization`. Preserve existing doctor behavior unless the new flag is used.

**Tech Stack:** Python, Typer, pytest, ruff, mypy.

---

### Task 1: Add Failing Tests

**Files:**
- Modify: `tests/unit/test_diagnostics.py`
- Modify: `tests/unit/test_cli.py`

- [ ] **Step 1: Add diagnostics missing-package test**

Add this test near existing diagnostics tests:

```python
def test_diagnostics_require_localization_fails_without_package() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))

    report = diagnostics.diagnose_configuration(
        profile=profile,
        require_localization=True,
    )

    localization_check = next(check for check in report.checks if check.name == "localization")
    assert localization_check.status == "FAIL"
    assert "--require-localization requires --package" in localization_check.detail
```

- [ ] **Step 2: Add diagnostics OK and FAIL coverage**

Add one test using the real RingCentral package and one tiny incomplete package fixture:

```python
def test_diagnostics_require_localization_passes_for_ringcentral_chinese() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    report = diagnostics.diagnose_configuration(
        profile=profile,
        material_package=package,
        require_localization=True,
        localization_language="zh",
    )

    localization_check = next(check for check in report.checks if check.name == "localization")
    assert localization_check.status == "OK"
    assert "required zh localization complete" in localization_check.detail
    assert "51/51 demo steps" in localization_check.detail
    assert "8/8 Q&A questions" in localization_check.detail
    assert "8/8 Q&A answers" in localization_check.detail
```

```python
def test_diagnostics_require_localization_fails_for_incomplete_package() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))
    package = MaterialPackage.model_validate(
        {
            "appId": "demo",
            "appName": "Demo",
            "version": 1,
            "profileIds": ["ringcentral-video-bind-speaker"],
            "operationEntrypoints": [
                {
                    "id": "demo.panel",
                    "title": "Panel",
                    "area": "Main",
                    "purpose": "Open panel.",
                    "openSteps": [],
                }
            ],
            "demoFlows": [
                {
                    "id": "demo-flow",
                    "title": "Demo",
                    "goal": "Show the panel.",
                    "steps": [
                        {
                            "id": "intro",
                            "title": "Intro",
                            "action": {
                                "entrypointId": "demo.panel",
                                "operation": "explain",
                            },
                            "narration": {
                                "text": "Show the panel.",
                                "localizedText": {"zh": "Localized intro."},
                            },
                        },
                        {
                            "id": "missing",
                            "title": "Missing",
                            "action": {
                                "entrypointId": "demo.panel",
                                "operation": "explain",
                            },
                            "narration": {"text": "Missing localization."},
                        },
                    ],
                }
            ],
            "qa": [
                {
                    "question": "Where is the panel?",
                    "answer": "Open Panel.",
                    "localizedQuestions": {"zh": ["Panel?"]},
                    "localizedAnswers": {},
                    "relatedEntrypointIds": ["demo.panel"],
                }
            ],
            "manualControls": [],
        }
    )

    report = diagnostics.diagnose_configuration(
        profile=profile,
        material_package=package,
        require_localization=True,
        localization_language="zh",
    )

    localization_check = next(check for check in report.checks if check.name == "localization")
    assert localization_check.status == "FAIL"
    assert "required zh localization incomplete" in localization_check.detail
    assert "1/2 demo steps" in localization_check.detail
    assert "1/1 Q&A questions" in localization_check.detail
    assert "0/1 Q&A answers" in localization_check.detail
```

- [ ] **Step 3: Add CLI tests**

Add tests near existing doctor CLI tests:

```python
def test_doctor_require_localization_fails_without_package(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(diagnostics, "_iter_process_executable_paths", lambda process_name: [])

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--profile",
            "ringcentral-video-bind-speaker",
            "--require-localization",
        ],
    )

    assert result.exit_code == 1
    assert "[FAIL] localization: --require-localization requires --package" in result.stdout
```

```python
def test_doctor_require_localization_passes_for_chinese_package(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(diagnostics, "_iter_process_executable_paths", lambda process_name: [])
    monkeypatch.setattr(
        diagnostics,
        "check_voice_asset_availability",
        lambda *_args, **_kwargs: VoiceAssetAvailability(
            status="OK",
            route="windows-sapi-zh",
            detail="speech=windows-sapi-zh found installed SAPI voice matching Huihui",
        ),
    )

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--profile",
            "ringcentral-video-bind-speaker",
            "--package",
            "ringcentral-video",
            "--language",
            "zh-CN",
            "--tone",
            "friendly",
            "--require-localization",
        ],
    )

    assert result.exit_code == 0
    assert "[OK] localization: required zh localization complete" in result.stdout
```

- [ ] **Step 4: Run RED tests**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_require_localization_fails_without_package tests\unit\test_diagnostics.py::test_diagnostics_require_localization_passes_for_ringcentral_chinese tests\unit\test_diagnostics.py::test_diagnostics_require_localization_fails_for_incomplete_package tests\unit\test_cli.py::test_doctor_require_localization_fails_without_package tests\unit\test_cli.py::test_doctor_require_localization_passes_for_chinese_package
```

Expected: tests fail because `require_localization`, `localization_language`, and `--require-localization` do not exist yet.

### Task 2: Implement Diagnostics And CLI Flag

**Files:**
- Modify: `src/ai_presenter/runtime/diagnostics.py`
- Modify: `src/ai_presenter/cli.py`

- [ ] **Step 1: Import localization status builder**

In `diagnostics.py`, add:

```python
from ai_presenter.packages.localization_status import LocalizationStatusReport
from ai_presenter.packages.localization_status import build_localization_status
```

- [ ] **Step 2: Add parameters to `diagnose_configuration()`**

Change the signature:

```python
def diagnose_configuration(
    *,
    profile: AppProfile,
    material_package: MaterialPackage | None = None,
    flow_id: str | None = None,
    ringcentral_config: Path | None = None,
    voice: PresenterVoiceSettings | None = None,
    require_localization: bool = False,
    localization_language: str | None = None,
) -> DiagnosticReport:
```

After package diagnostics, append the localization diagnostic when required.

- [ ] **Step 3: Add helper functions**

Add:

```python
def _diagnose_required_localization(
    material_package: MaterialPackage | None,
    *,
    language: str,
) -> DiagnosticCheck:
    if material_package is None:
        return DiagnosticCheck(
            "FAIL",
            "localization",
            "--require-localization requires --package",
        )
    report = build_localization_status(material_package, language=language)
    status: DiagnosticStatus = (
        "OK" if report.required_localization_complete else "FAIL"
    )
    state = "complete" if status == "OK" else "incomplete"
    return DiagnosticCheck(
        status,
        "localization",
        f"required {report.language} localization {state}: "
        f"{_format_localization_counts(report)}",
    )


def _format_localization_counts(report: LocalizationStatusReport) -> str:
    return (
        f"{report.demo_localized_steps}/{report.demo_total_steps} demo steps, "
        f"{report.qa_localized_questions}/{report.qa_total} Q&A questions, "
        f"{report.qa_localized_answers}/{report.qa_total} Q&A answers"
    )
```

Use `language = localization_language or (voice.language if voice is not None else "zh")`.

- [ ] **Step 4: Add CLI option and pass-through**

In `doctor()`, add:

```python
require_localization: bool = typer.Option(
    False,
    "--require-localization",
    help="Fail if the selected package language lacks required demo narration or Q&A localization.",
),
```

Pass:

```python
require_localization=require_localization,
localization_language=voice.language if voice is not None else None,
```

- [ ] **Step 5: Run GREEN targeted tests**

Run the RED command again.

Expected: all selected tests pass.

### Task 3: Update Runbook And Verify

**Files:**
- Modify: `docs/runbooks/ringcentral-manual-acceptance.md`
- Add: `docs/agent-handoffs/cycle-036-review.md`
- Add: `docs/agent-handoffs/cycle-036-summary.md`

- [ ] **Step 1: Update runbook smoke checklist**

Add a strict localization doctor command near the existing voice preflight checks:

```markdown
- [ ] Run `.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language zh-CN --tone friendly --require-localization` before a Chinese demo; confirm `[OK] localization:` as well as voice readiness.
```

- [ ] **Step 2: Run focused verification**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py tests\unit\test_cli.py tests\unit\test_material_packages.py
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\runtime\diagnostics.py src\ai_presenter\cli.py tests\unit\test_diagnostics.py tests\unit\test_cli.py
.\.venv\Scripts\mypy --no-incremental src\ai_presenter\runtime\diagnostics.py src\ai_presenter\cli.py tests\unit\test_diagnostics.py tests\unit\test_cli.py
```

- [ ] **Step 3: Request review**

Ask a review subagent to inspect CLI behavior, diagnostics layering, default language behavior, unchanged plain doctor output, and localization completeness rules.

- [ ] **Step 4: Run full verification**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
.\.venv\Scripts\ruff check --no-cache .
.\.venv\Scripts\mypy --no-incremental src tests
git diff --check
```

- [ ] **Step 5: Commit**

Stage only Cycle 036 files and commit:

```powershell
git commit -m "feat: add doctor localization readiness"
```
