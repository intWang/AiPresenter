# Cycle 034 Technical Scan: Tk Operator Summary Wrapping

Date: 2026-05-16
Role: technical discovery
Scope: read-only technical scan. No implementation changes were made in this pass.

## Recommendation

Make the smallest Tk-only change in `src/ai_presenter/runtime/controller.py`.

The summary data is already split into stable rows by `controller_view_model.py`, and `render_operator_summary_text()` already newline-joins those rows for Tk. The remaining issue is the single packed `Label` has `anchor` and `justify` but no `wraplength`, so long row values can extend horizontally.

## Implementation Shape

Add private helpers in `controller.py`:

- `_apply_operator_summary_wraplength(label: Any, width: int) -> bool`
- `_configure_operator_summary_label(label: Any) -> None`

Wire the existing summary label as a variable, call the configure helper, keep `pack(fill="x")`, set `anchor="nw"` and `justify="left"`, and bind `<Configure>` so `wraplength` tracks the allocated label width with `max(1, event.width)`.

Do not change `controller_view_model.py`, root geometry, or switch to grid.

## First Failing Tests

Add fake-widget tests in `tests/unit/test_controller.py`:

- `test_configure_operator_summary_label_sets_multiline_alignment_and_resize_binding`
- `test_apply_operator_summary_wraplength_skips_unchanged_width`
- `test_apply_operator_summary_wraplength_clamps_zero_width`

Use a `_FakeLabel` similar to the existing `_FakeButton` seam; no real Tk is needed for unit coverage.

## Residual Risk

Unit tests can prove widget configuration logic, but they cannot prove real font, DPI, and window behavior. A live Tk smoke is still useful after implementation. If unavailable, record residual risk around extreme unbroken tokens and unusually long diagnostic detail.

## Suggested Verification

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller.py tests\unit\test_controller_view_model.py
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\runtime\controller.py tests\unit\test_controller.py
.\.venv\Scripts\mypy --no-incremental src\ai_presenter\runtime\controller.py tests\unit\test_controller.py
```
