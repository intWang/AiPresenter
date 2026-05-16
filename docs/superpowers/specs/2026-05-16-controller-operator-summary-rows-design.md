# Controller Operator Summary Rows Design

Date: 2026-05-16
Cycle: 031

## Problem

The controller already has a pure operator view model with target, flow, voice, scan, question, run state, and disabled action reasons. The Tk UI compresses that model into one long label, which is hard to scan during live demo work, especially when voice assets are missing or a running app needs a scan.

## Acceptance

- Add stable operator summary rows derived from `ControllerOperatorViewModel`.
- Rows separate target, flow, voice/assets, state/scan, question, and blocked action reasons.
- Existing button state and disabled reason logic remains unchanged.
- Existing one-line summary remains available for compatibility.
- Tk controller renders the row output as a compact multi-line operator summary.
- Tests cover ready material package, blocked running-app scan state, and action-row behavior.
- No RingCentral routes, Q&A behavior, voice readiness policy, or provider behavior changes.

## Design

Add a `ControllerOperatorSummaryRow` dataclass and row renderer in `controller_view_model.py`.

Rows:

- `target`: source plus selected target.
- `flow`: selected flow or `-`.
- `voice`: language/tone plus local asset readiness.
- `state`: run status plus scan state.
- `question`: latest question state.
- `actions`: present only when Start or Submit is blocked with a reason.

Add `render_controller_operator_summary_rows()` for UI-friendly row strings. Keep `render_controller_operator_summary()` as a joined compatibility string. Update `run_controller()` to join the row strings with newlines and render them in the existing status area.

## Out Of Scope

- Full Tk redesign.
- Screenshots or live RingCentral validation.
- Runtime state machine changes.
- Question matching, language/tone, or provider changes.
