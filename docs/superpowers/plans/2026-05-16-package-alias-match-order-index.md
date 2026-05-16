# Package Alias Match-Order Index Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a runtime-only package alias match-order index so package-owned aliases match by longest alias first with stable source-order ties.

**Architecture:** Keep source-order aliases for reporting, add a private match-order tuple for runtime matching, and update only package-owned alias matching to use it.

**Tech Stack:** Python, Pydantic v2 private attrs, pytest, ruff, mypy.

---

### Task 1: Add Failing Tests

**Files:**
- Modify: `tests/unit/test_material_packages.py`
- Modify: `tests/unit/test_questions.py`

- [ ] **Step 1: Add match-order structure test**

Add `test_material_package_exposes_entrypoint_question_aliases_by_match_order`:

```python
def test_material_package_exposes_entrypoint_question_aliases_by_match_order() -> None:
    package = MaterialPackage.model_validate(
        {
            "appId": "demo",
            "appName": "Demo",
            "version": 1,
            "profileIds": ["demo-profile"],
            "operationEntrypoints": [
                {"id": "demo.one", "title": "One", "area": "Main", "purpose": "Open one.", "questionAliases": {"en": ["aa", "bbbb"]}},
                {"id": "demo.two", "title": "Two", "area": "Main", "purpose": "Open two.", "questionAliases": {"en": ["cccc", "d"]}},
            ],
            "demoFlows": [],
            "manualControls": [],
        }
    )

    assert [alias.normalized_alias for alias in package.entrypoint_question_aliases] == [
        "aa",
        "bbbb",
        "cccc",
        "d",
    ]
    assert [
        alias.normalized_alias for alias in package.entrypoint_question_aliases_by_match_order
    ] == ["bbbb", "cccc", "aa", "d"]
```

- [ ] **Step 2: Extend runtime index rebuild and dump tests**

Extend `test_with_demo_flow_rebuilds_runtime_indexes_for_appended_flow`:

```python
assert copied.entrypoint_question_aliases_by_match_order
assert copied.entrypoint_question_aliases_by_match_order is not package.entrypoint_question_aliases_by_match_order
```

Extend `test_runtime_indexes_do_not_leak_into_model_dump`:

```python
assert "entrypointQuestionAliasesByMatchOrder" not in dumped
assert "_entrypoint_question_aliases_by_match_order" not in dumped
```

- [ ] **Step 3: Add equal-length behavior test**

Add `test_package_owned_equal_length_aliases_keep_source_order` near the existing package alias tests:

```python
def test_package_owned_equal_length_aliases_keep_source_order() -> None:
    package = MaterialPackage.model_validate(
        {
            "appId": "demo",
            "appName": "Demo",
            "version": 1,
            "profileIds": ["demo-profile"],
            "operationEntrypoints": [
                {"id": "demo.alpha", "title": "Alpha", "area": "Main", "purpose": "Open alpha.", "questionAliases": {"en": ["alpha"]}},
                {"id": "demo.bravo", "title": "Bravo", "area": "Main", "purpose": "Open bravo.", "questionAliases": {"en": ["bravo"]}},
            ],
            "demoFlows": [],
            "manualControls": [],
        }
    )

    response = answer_question(
        package=package,
        question="alpha bravo",
        voice=PresenterVoiceSettings(),
    )

    assert response.entrypoint_id == "demo.alpha"
```

- [ ] **Step 4: Run RED tests**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_material_package_exposes_entrypoint_question_aliases_by_match_order tests\unit\test_material_packages.py::test_with_demo_flow_rebuilds_runtime_indexes_for_appended_flow tests\unit\test_material_packages.py::test_runtime_indexes_do_not_leak_into_model_dump tests\unit\test_questions.py::test_package_owned_equal_length_aliases_keep_source_order
```

Expected: missing-property failures for `entrypoint_question_aliases_by_match_order`.

### Task 2: Implement Match-Order Index

**Files:**
- Modify: `src/ai_presenter/packages/models.py`
- Modify: `src/ai_presenter/runtime/questions.py`

- [ ] **Step 1: Add private attr and property**

Add:

```python
_entrypoint_question_aliases_by_match_order: tuple[EntrypointQuestionAlias, ...] = PrivateAttr(
    default_factory=tuple
)
```

Add:

```python
@property
def entrypoint_question_aliases_by_match_order(self) -> tuple[EntrypointQuestionAlias, ...]:
    return self._entrypoint_question_aliases_by_match_order
```

- [ ] **Step 2: Build sorted tuple**

After building source-order aliases:

```python
entrypoint_question_aliases_by_match_order = tuple(
    alias
    for _index, alias in sorted(
        enumerate(entrypoint_question_aliases),
        key=lambda item: (-len(item[1].normalized_alias), item[0]),
    )
)
```

Assign it to the private attr.

- [ ] **Step 3: Use it at runtime**

In `_match_package_entrypoint_alias()`, replace the best-length loop with:

```python
for alias in package.entrypoint_question_aliases_by_match_order:
    if alias.normalized_alias in normalized_question:
        return package.entrypoint_by_id(alias.entrypoint_id)
return None
```

- [ ] **Step 4: Run GREEN focused tests**

Run the RED command again.

Expected: all selected tests pass.

### Task 3: Verify, Review, Commit

**Files:**
- Cycle 035 code, tests, and docs

- [ ] **Step 1: Run focused behavior tests**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_material_packages.py tests\unit\test_package_demo.py
```

- [ ] **Step 2: Run static checks**

Run:

```powershell
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\packages\models.py src\ai_presenter\runtime\questions.py tests\unit\test_material_packages.py tests\unit\test_questions.py
.\.venv\Scripts\mypy --no-incremental src\ai_presenter\packages\models.py src\ai_presenter\runtime\questions.py tests\unit\test_material_packages.py tests\unit\test_questions.py
```

- [ ] **Step 3: Run full verification**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
.\.venv\Scripts\ruff check --no-cache .
.\.venv\Scripts\mypy --no-incremental src tests
git diff --check
```

- [ ] **Step 4: Request review**

Ask a review subagent to inspect alias precedence, longest/stable ordering, legacy alias monkeypatch behavior, serialization leakage, and `with_demo_flow()` rebuild safety.

- [ ] **Step 5: Commit**

Stage only Cycle 035 files and commit:

```powershell
git commit -m "perf: precompute package alias match order"
```
