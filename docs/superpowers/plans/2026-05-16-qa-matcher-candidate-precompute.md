# Q&A Matcher Candidate Precompute Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Precompute stable Q&A and entrypoint matcher candidates on `MaterialPackage` so live questions reuse package-derived token data.

**Architecture:** Add runtime-only private indexes to the package model and update the existing matcher to consume them. Query-specific normalization remains in `runtime/questions.py`.

**Tech Stack:** Python, Pydantic v2 private attrs, pytest, ruff, mypy.

---

### Task 1: Add Candidate Structure Tests

**Files:**
- Modify: `tests/unit/test_material_packages.py`

- [ ] **Step 1: Add Q&A candidate structure test**

Add `test_material_package_exposes_precomputed_qa_question_candidates`:

```python
def test_material_package_exposes_precomputed_qa_question_candidates() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    item = package.qa[0]

    candidates = package.qa_question_candidates

    assert isinstance(candidates, tuple)
    assert any(candidate.item is item and candidate.question == item.question for candidate in candidates)
    localized_question = item.localized_questions["zh"][0]
    localized_candidate = next(
        candidate for candidate in candidates if candidate.question == localized_question
    )
    assert localized_candidate.item is item
    assert localized_candidate.normalized_question == localized_question.casefold()
    assert isinstance(localized_candidate.meaningful_tokens, frozenset)
```

- [ ] **Step 2: Add entrypoint candidate structure test**

Add `test_material_package_exposes_precomputed_entrypoint_match_candidates`:

```python
def test_material_package_exposes_precomputed_entrypoint_match_candidates() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    candidates = package.entrypoint_match_candidates
    chat = package.entrypoint_by_id("ringcentral.video.toolbar.chat")
    chat_candidate = next(candidate for candidate in candidates if candidate.entrypoint is chat)

    assert isinstance(candidates, tuple)
    assert [candidate.entrypoint.id for candidate in candidates] == [
        entrypoint.id for entrypoint in package.operation_entrypoints
    ]
    assert "chat" in chat_candidate.id_tokens
    assert "chat" in chat_candidate.title_tokens
    assert chat_candidate.title_or_id_tokens == chat_candidate.title_tokens | chat_candidate.id_tokens
```

- [ ] **Step 3: Extend existing runtime-index tests**

Extend `test_with_demo_flow_rebuilds_runtime_indexes_for_appended_flow`:

```python
assert copied.qa_question_candidates[0].item is copied.qa[0]
assert copied.entrypoint_match_candidates[0].entrypoint is copied.operation_entrypoints[0]
assert copied.qa_question_candidates[0].item is not package.qa[0]
assert copied.entrypoint_match_candidates[0].entrypoint is not package.operation_entrypoints[0]
```

Extend `test_runtime_indexes_do_not_leak_into_model_dump`:

```python
assert "qaQuestionCandidates" not in dumped
assert "entrypointMatchCandidates" not in dumped
assert "_qa_question_candidates" not in dumped
assert "_entrypoint_match_candidates" not in dumped
```

- [ ] **Step 4: Run RED tests**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_material_package_exposes_precomputed_qa_question_candidates tests\unit\test_material_packages.py::test_material_package_exposes_precomputed_entrypoint_match_candidates tests\unit\test_material_packages.py::test_with_demo_flow_rebuilds_runtime_indexes_for_appended_flow tests\unit\test_material_packages.py::test_runtime_indexes_do_not_leak_into_model_dump
```

Expected: missing-property failures for the new candidate properties.

### Task 2: Add Package Candidate Indexes

**Files:**
- Modify: `src/ai_presenter/packages/models.py`

- [ ] **Step 1: Add dataclasses**

Add frozen dataclasses near `EntrypointQuestionAlias`:

```python
@dataclass(frozen=True)
class QuestionAnswerMatchCandidate:
    item: QuestionAnswer
    question: str
    normalized_question: str
    meaningful_tokens: frozenset[str]


@dataclass(frozen=True)
class EntrypointMatchCandidate:
    entrypoint: OperationEntrypoint
    id_tokens: frozenset[str]
    title_tokens: frozenset[str]
    area_tokens: frozenset[str]
    purpose_tokens: frozenset[str]
    title_or_id_tokens: frozenset[str]
```

- [ ] **Step 2: Add private attrs and properties**

Add private attrs:

```python
_qa_question_candidates: tuple[QuestionAnswerMatchCandidate, ...] = PrivateAttr(
    default_factory=tuple
)
_entrypoint_match_candidates: tuple[EntrypointMatchCandidate, ...] = PrivateAttr(
    default_factory=tuple
)
```

Add properties:

```python
@property
def qa_question_candidates(self) -> tuple[QuestionAnswerMatchCandidate, ...]:
    return self._qa_question_candidates


@property
def entrypoint_match_candidates(self) -> tuple[EntrypointMatchCandidate, ...]:
    return self._entrypoint_match_candidates
```

- [ ] **Step 3: Build runtime indexes after validation**

Add helper functions in `models.py` that mirror current tokenization:

```python
_STOPWORDS = {...}
_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")

def _field_tokens(text: str) -> frozenset[str]:
    return frozenset(_TOKEN_PATTERN.findall(text.casefold()))

def _meaningful_tokens(text: str) -> frozenset[str]:
    return frozenset(token for token in _field_tokens(text) if token not in _STOPWORDS and len(token) >= 3)
```

Build Q&A candidates from base and localized questions. Build entrypoint candidates from each entrypoint field. Assign private attrs in `validate_entrypoint_references()`.

- [ ] **Step 4: Run GREEN structure tests**

Run the same command from Task 1 Step 4.

Expected: all selected tests pass.

### Task 3: Use Candidates In Runtime Matching

**Files:**
- Modify: `src/ai_presenter/runtime/questions.py`
- Modify: `tests/unit/test_questions.py` only if needed for behavior protection

- [ ] **Step 1: Replace Q&A candidate construction**

Update `_match_qa()` so it loops over `package.qa_question_candidates`. Preserve substring pass first, then token pass.

- [ ] **Step 2: Replace entrypoint token construction**

Update `_match_entrypoint()` so it loops over `package.entrypoint_match_candidates`.

Update `_score_entrypoint_match()` signature to accept an `EntrypointMatchCandidate`.

- [ ] **Step 3: Keep legacy alias path dynamic**

Do not precompute `_ENTRYPOINT_ALIASES`; existing tests monkeypatch it.

- [ ] **Step 4: Run focused behavior tests**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_material_packages.py tests\unit\test_package_demo.py
```

Expected: all selected tests pass.

### Task 4: Verify, Review, Commit

**Files:**
- All Cycle 033 files

- [ ] **Step 1: Run static checks**

Run:

```powershell
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\runtime\questions.py src\ai_presenter\packages\models.py tests\unit\test_questions.py tests\unit\test_material_packages.py tests\unit\test_package_demo.py
.\.venv\Scripts\mypy --no-incremental src\ai_presenter\runtime\questions.py src\ai_presenter\packages\models.py tests\unit\test_questions.py tests\unit\test_material_packages.py
```

Expected: ruff and mypy pass.

- [ ] **Step 2: Run full verification**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
.\.venv\Scripts\ruff check --no-cache .
.\.venv\Scripts\mypy --no-incremental src tests
git diff --check
```

Expected: all tests, ruff, mypy, and whitespace checks pass. Existing pywinauto STA warning may remain.

- [ ] **Step 3: Request review**

Ask a review subagent to inspect candidate ordering, serialization leakage, Pydantic private attr rebuild behavior, and unchanged matcher semantics.

- [ ] **Step 4: Commit**

Stage only Cycle 033 files and commit:

```powershell
git commit -m "perf: precompute question matcher candidates"
```
