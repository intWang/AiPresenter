# Cycle 131 Entrypoint Localization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add optional localized entrypoint title and purpose copy so runtime answers can render localized labels and prose without expanding fuzzy matching.

**Architecture:** `OperationEntrypoint` gains optional `localizedTitles` and `localizedPurposes` maps plus small fallback helpers. Runtime question answers use the helpers for display only; matcher candidates, safety gating, controller interrupt behavior, and package YAML remain unchanged. Localization status adds optional coverage counts that do not affect required completeness.

**Tech Stack:** Python, Pydantic package models, pytest, Typer CLI report rendering, ruff, mypy.

---

### Task 1: Package Model Fields

**Files:**
- Modify: `src/ai_presenter/packages/models.py`
- Test: `tests/unit/test_material_packages.py`

- [ ] **Step 1: Add failing model tests**

Add tests that build an inline `MaterialPackage` containing one entrypoint with:

```yaml
localizedTitles:
  es: "Panel de participantes"
  ja: "参加者パネル"
localizedPurposes:
  es: "Abre la lista de participantes."
```

Assert:

```python
entrypoint.localized_titles["es"] == "Panel de participantes"
entrypoint.localized_purposes["es"] == "Abre la lista de participantes."
entrypoint.title_for_language("es") == "Panel de participantes"
entrypoint.purpose_for_language("es") == "Abre la lista de participantes."
entrypoint.title_for_language("zh") == entrypoint.title
entrypoint.purpose_for_language("ja") == entrypoint.purpose
```

Also assert blank localized strings fall back to English and existing unknown-key validation still fails for unrelated keys.

- [ ] **Step 2: Verify tests fail before implementation**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit\test_material_packages.py::test_material_package_parses_localized_entrypoint_title_and_purpose -q --no-cov
```

Expected: failure because `localizedTitles`, `localizedPurposes`, or helper methods do not exist.

- [ ] **Step 3: Implement minimal model support**

Add fields to `OperationEntrypoint`:

```python
localized_titles: dict[str, str] = Field(default_factory=dict, alias="localizedTitles")
localized_purposes: dict[str, str] = Field(default_factory=dict, alias="localizedPurposes")
```

Add helpers:

```python
def title_for_language(self, language: str) -> str:
    localized = self.localized_titles.get(language, "").strip()
    if localized:
        return localized
    return self.title

def purpose_for_language(self, language: str) -> str:
    localized = self.localized_purposes.get(language, "").strip()
    if localized:
        return localized
    return self.purpose
```

- [ ] **Step 4: Re-run focused model tests**

Run the same targeted pytest command with `--no-cov`; expected: pass.

### Task 2: Runtime Answer Rendering

**Files:**
- Modify: `src/ai_presenter/runtime/questions.py`
- Test: `tests/unit/test_questions.py`

- [ ] **Step 1: Add failing rendering tests**

Add tests proving:

```python
answer.answer_text == "Panel de participantes: Abre la lista de participantes."
```

when Spanish localized title and purpose exist.

Add regressions that:

- localized title with missing localized purpose renders localized title plus English purpose;
- Spanish with no localized title keeps the Cycle130 alias-label fallback;
- non-Spanish behavior still uses canonical title/purpose unless localized copy exists for that exact language;
- adding `localizedTitles.es` alone does not create a match for a Spanish query unless an alias or Q&A entry matches.

- [ ] **Step 2: Verify rendering tests fail before runtime changes**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit\test_questions.py::test_entrypoint_answer_uses_localized_title_and_purpose -q --no-cov
```

Expected: failure because runtime still renders English `entrypoint.purpose`.

- [ ] **Step 3: Implement runtime display-only selection**

Update `_render_entrypoint_answer()` to render:

```python
base = f"{_entrypoint_answer_label(entrypoint, voice)}: {entrypoint.purpose_for_language(voice.language)}"
```

Update `_entrypoint_answer_label()` to prefer a nonblank localized title, then preserve the Spanish alias fallback, then fall back to canonical title.

Do not modify `_build_entrypoint_match_candidates()`, alias indexes, safety gating, or controller routing.

- [ ] **Step 4: Re-run focused rendering tests**

Run the focused test selection with `--no-cov`; expected: pass.

### Task 3: Optional Localization Status Counts

**Files:**
- Modify: `src/ai_presenter/packages/localization_status.py`
- Test: `tests/unit/test_material_packages.py`
- Test: `tests/unit/test_cli.py`

- [ ] **Step 1: Add failing report tests**

Add or update tests so `build_localization_status(..., language="es")` reports:

```python
report.entrypoint_titles_present == 1
report.entrypoint_purposes_present == 1
report.required_localization_complete is True
```

for a fixture whose demo narration and Q&A are complete but whose entrypoint localized title/purpose coverage is partial.

If CLI output is updated, assert it contains separate optional lines such as:

```text
- localizedTitles.es present on 1/1 entrypoints
- localizedPurposes.es present on 1/1 entrypoints
```

- [ ] **Step 2: Implement optional counts**

Extend `LocalizationStatusReport` with entrypoint title/purpose counts. Keep `required_localization_complete` based only on demo narration and Q&A question/answer coverage.

- [ ] **Step 3: Re-run report tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit\test_material_packages.py tests\unit\test_cli.py -q --no-cov
```

Expected: pass.

### Task 4: Review, Handoff, And Verification

**Files:**
- Create: `docs/agent-handoffs/cycle-131-implementation.md`

- [ ] **Step 1: Write implementation handoff**

Document scope, changed files, behavioral contract, tests run, and known boundaries. Use `Date: 2026-05-16`.

- [ ] **Step 2: Run focused verification**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_controller.py tests\unit\test_cli.py tests\unit\test_diagnostics.py
.\.venv\Scripts\ruff check --no-cache src tests
.\.venv\Scripts\mypy --no-incremental src tests
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe voices --profile profiles\ringcentral-video-openai.example.yaml --language es
.\.venv\Scripts\ai-presenter.exe voices --profile ringcentral-video-bind-speaker --language es
git diff --check
```

Expected: tests, ruff, mypy, OpenAI Spanish voices, and localization report pass. Bind-speaker Spanish voices should fail with the existing OpenAI-backed runtime boundary message.

- [ ] **Step 3: Commit cycle**

Stage only source, tests, and Cycle131 docs. Do not stage `.coverage`. Commit with a concise Cycle131 message after verification passes.
