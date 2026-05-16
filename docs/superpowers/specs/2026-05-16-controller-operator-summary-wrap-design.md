# Controller Operator Summary Wrap Design

Date: 2026-05-16

## Goal

Prevent long controller operator summary rows from expanding the Tk controller window horizontally while preserving full diagnostic text.

## Context

Cycle 031 split the operator summary into multiple stable rows. The Tk controller currently renders those rows in a single `Label` with `justify="left"`, but no `wraplength`. Long voice asset readiness failures can still create very wide label requests.

## Design

Add a Tk presentation helper in `src/ai_presenter/runtime/controller.py`:

- `_apply_operator_summary_wraplength(label, width)` clamps width to at least 1, skips redundant configuration, and sets `wraplength`.
- `_configure_operator_summary_label(label)` sets multiline-friendly alignment and binds `<Configure>` so wrap length tracks the label's allocated width.

The existing `StringVar`, `render_operator_summary_text()`, row renderer, root geometry, and `pack(fill="x")` layout remain unchanged.

## Behavior Contract

- No Start/Pause/End/Refresh/Scan/Submit logic changes.
- No question submission behavior changes.
- No voice readiness or disabled reason text changes.
- No text truncation.
- No RingCentral automation.

## Tests

Use fake label tests to verify:

- alignment and resize binding are configured;
- resize events update `wraplength`;
- unchanged widths avoid redundant `configure()` calls;
- zero or negative widths clamp to `1`.

Run existing controller and controller view-model tests.

## Residual Risk

Fake label tests do not prove real Tk visual behavior under every font, DPI, or extreme unbroken string. A local Tk smoke can reduce that risk, but it is not required for this no-live RingCentral slice.
