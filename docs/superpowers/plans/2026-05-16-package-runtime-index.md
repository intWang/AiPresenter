# Package Runtime Index Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build validated runtime indexes for material package entrypoints and package-owned question aliases so hot question/action paths avoid repeated linear lookup setup.

**Architecture:** Store indexes as Pydantic private attributes on `MaterialPackage`, built in the existing validation pass that already checks duplicate ids and references. Runtime code consumes the model methods/properties; package YAML and public question/action behavior remain unchanged.

**Tech Stack:** Python, Pydantic v2 models, pytest, ruff, mypy.

---

## File Structure

- Modify `src/ai_presenter/packages/models.py`.
  - Add an immutable alias record type.
  - Add private runtime index attributes to `MaterialPackage`.
  - Build the indexes in `validate_entrypoint_references()`.
  - Update `entrypoint_by_id()` to use the dict index.
- Modify `src/ai_presenter/runtime/questions.py`.
  - Replace per-question package alias enumeration with `package.entrypoint_question_aliases`.
- Modify `tests/unit/test_material_packages.py`.
  - Add tests for read-only entrypoint index and alias index contents.
- Modify `tests/unit/test_questions.py`.
  - Keep existing alias precedence and longest-alias tests as behavioral guardrails.

## Tasks

### Task 1: Material Package Entry Point Index

**Files:**

- Modify: `tests/unit/test_material_packages.py`
- Modify: `src/ai_presenter/packages/models.py`

- [ ] **Step 1: Write failing tests**

Add tests that require a read-only `entrypoints_by_id` mapping and unchanged unknown-id behavior:

```python
from types import MappingProxyType

def test_material_package_exposes_read_only_entrypoint_index() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    index = package.entrypoints_by_id

    assert isinstance(index, MappingProxyType)
    assert index["ringcentral.video.toolbar.chat"] is package.entrypoint_by_id(
        "ringcentral.video.toolbar.chat"
    )
    assert set(index) == {entrypoint.id for entrypoint in package.operation_entrypoints}


def test_entrypoint_by_id_preserves_unknown_id_error() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    with pytest.raises(KeyError, match="Unknown operation entrypoint: missing.entrypoint"):
        package.entrypoint_by_id("missing.entrypoint")
```

- [ ] **Step 2: Verify red**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_material_package_exposes_read_only_entrypoint_index tests\unit\test_material_packages.py::test_entrypoint_by_id_preserves_unknown_id_error
```

Expected: first test fails because `entrypoints_by_id` does not exist.

- [ ] **Step 3: Implement minimal index**

In `src/ai_presenter/packages/models.py`, add `PrivateAttr`, `Mapping`, and `MappingProxyType`; store `_entrypoints_by_id` during validation; expose it through `entrypoints_by_id`; use it in `entrypoint_by_id()`.

- [ ] **Step 4: Verify green**

Run the same focused pytest command. Expected: both tests pass.

### Task 2: Package-Owned Question Alias Index

**Files:**

- Modify: `tests/unit/test_material_packages.py`
- Modify: `src/ai_presenter/packages/models.py`
- Modify: `src/ai_presenter/runtime/questions.py`

- [ ] **Step 1: Write failing alias index test**

Add a test that requires package aliases to be pre-normalized:

```python
def test_material_package_exposes_normalized_question_alias_index() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    aliases = [
        alias
        for alias in package.entrypoint_question_aliases
        if alias.entrypoint_id == "ringcentral.video.toolbar.chat"
    ]

    assert aliases
    assert any(alias.language == "zh" for alias in aliases)
    assert any(alias.alias == "聊天在哪里" for alias in aliases)
    assert any(alias.normalized_alias == "聊天在哪里" for alias in aliases)
```

- [ ] **Step 2: Verify red**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_material_package_exposes_normalized_question_alias_index
```

Expected: fails because `entrypoint_question_aliases` does not exist.

- [ ] **Step 3: Implement alias record and index**

In `models.py`, add a frozen `EntrypointQuestionAlias` dataclass with `entrypoint_id`, `language`, `alias`, and `normalized_alias`. Build a tuple from each `OperationEntrypoint.question_aliases` item during validation. Ignore blank aliases after stripping.

- [ ] **Step 4: Update question matching**

In `runtime.questions._match_package_entrypoint_alias()`, iterate `package.entrypoint_question_aliases`, compare `alias.normalized_alias`, track the longest match, and resolve the selected entrypoint through `package.entrypoint_by_id()`.

- [ ] **Step 5: Verify behavior**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_questions.py
```

Expected: all material package and question tests pass, including package-owned alias precedence and longest alias coverage.

### Task 3: Quality Gate and Documentation

**Files:**

- Create: `docs/agent-handoffs/cycle-008-implementation.md`
- Create: `docs/agent-handoffs/cycle-008-summary.md`

- [ ] **Step 1: Run format/type/test gates**

Run:

```powershell
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\packages\models.py src\ai_presenter\runtime\questions.py tests\unit\test_material_packages.py tests\unit\test_questions.py
.\.venv\Scripts\mypy --no-incremental src\ai_presenter\packages\models.py src\ai_presenter\runtime\questions.py tests\unit\test_material_packages.py tests\unit\test_questions.py
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
```

Expected: ruff and mypy pass; full pytest passes.

- [ ] **Step 2: Write handoff docs**

Document implemented changes, red/green evidence, verification commands, and known follow-ups.

- [ ] **Step 3: Request review**

Dispatch a review subagent to inspect scope, behavior preservation, tests, and whether private Pydantic indexes are safe.
