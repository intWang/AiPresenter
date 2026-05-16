# Controller Operator Summary Wrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Constrain the Tk controller operator summary label so long diagnostic rows wrap instead of widening the window.

**Architecture:** Add a small presentation helper in `controller.py` and fake-widget tests in `test_controller.py`. Do not change the controller view model or runtime behavior.

**Tech Stack:** Python, Tkinter widget configuration, pytest, ruff, mypy.

---

### Task 1: Add Failing Helper Tests

**Files:**
- Modify: `tests/unit/test_controller.py`

- [ ] **Step 1: Import helpers**

Import the new helpers:

```python
from ai_presenter.runtime.controller import _apply_operator_summary_wraplength
from ai_presenter.runtime.controller import _configure_operator_summary_label
```

- [ ] **Step 2: Add fake label**

Add a small fake label near `_FakeButton`:

```python
class _FakeLabel:
    def __init__(self, **options: object) -> None:
        self.options = dict(options)
        self.configure_calls: list[dict[str, object]] = []
        self.bindings: dict[str, object] = {}

    def cget(self, key: str) -> object:
        return self.options.get(key, "")

    def configure(self, **kwargs: object) -> None:
        self.configure_calls.append(kwargs)
        self.options.update(kwargs)

    def bind(self, sequence: str, callback: object) -> None:
        self.bindings[sequence] = callback
```

- [ ] **Step 3: Add tests**

Add:

```python
def test_configure_operator_summary_label_sets_multiline_alignment_and_resize_binding() -> None:
    label = _FakeLabel()

    _configure_operator_summary_label(label)

    assert label.options["anchor"] == "nw"
    assert label.options["justify"] == "left"
    callback = label.bindings["<Configure>"]
    callback(type("Event", (), {"width": 640})())
    assert label.options["wraplength"] == 640
```

```python
def test_apply_operator_summary_wraplength_skips_unchanged_width() -> None:
    label = _FakeLabel(wraplength=640)

    changed = _apply_operator_summary_wraplength(label, 640)

    assert changed is False
    assert label.configure_calls == []
```

```python
@pytest.mark.parametrize("width", [0, -12])
def test_apply_operator_summary_wraplength_clamps_non_positive_width(width: int) -> None:
    label = _FakeLabel()

    changed = _apply_operator_summary_wraplength(label, width)

    assert changed is True
    assert label.options["wraplength"] == 1
```

- [ ] **Step 4: Run RED tests**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller.py::test_configure_operator_summary_label_sets_multiline_alignment_and_resize_binding tests\unit\test_controller.py::test_apply_operator_summary_wraplength_skips_unchanged_width tests\unit\test_controller.py::test_apply_operator_summary_wraplength_clamps_non_positive_width
```

Expected: import errors because helpers do not exist yet.

### Task 2: Implement Tk Wrap Helpers

**Files:**
- Modify: `src/ai_presenter/runtime/controller.py`

- [ ] **Step 1: Add helper functions**

Add near `_apply_button_state`:

```python
def _apply_operator_summary_wraplength(label: Any, width: int) -> bool:
    wraplength = max(1, int(width))
    try:
        current = int(label.cget("wraplength"))
    except (TypeError, ValueError):
        current = 0
    if current == wraplength:
        return False
    label.configure(wraplength=wraplength)
    return True


def _configure_operator_summary_label(label: Any) -> None:
    label.configure(anchor="nw", justify="left")

    def sync_wraplength(event: Any) -> None:
        _apply_operator_summary_wraplength(label, int(getattr(event, "width", 1)))

    label.bind("<Configure>", sync_wraplength)
```

- [ ] **Step 2: Wire the label**

Replace the inline summary label creation with:

```python
operator_summary_label = tk.Label(frame, textvariable=operator_summary)
_configure_operator_summary_label(operator_summary_label)
operator_summary_label.pack(fill="x", pady=(0, 12))
```

- [ ] **Step 3: Run GREEN tests**

Run the same tests from Task 1 Step 4.

Expected: all pass.

### Task 3: Verify And Commit

**Files:**
- Modify: `src/ai_presenter/runtime/controller.py`
- Modify: `tests/unit/test_controller.py`
- Add Cycle 034 docs

- [ ] **Step 1: Run focused tests**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller.py tests\unit\test_controller_view_model.py
```

- [ ] **Step 2: Run static checks**

Run:

```powershell
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\runtime\controller.py tests\unit\test_controller.py
.\.venv\Scripts\mypy --no-incremental src\ai_presenter\runtime\controller.py tests\unit\test_controller.py
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

Ask a review subagent to check that the change is Tk-only, does not alter view-model/runtime behavior, and keeps full text visible.

- [ ] **Step 5: Commit**

Stage only Cycle 034 files and commit:

```powershell
git commit -m "fix: wrap controller operator summary"
```
