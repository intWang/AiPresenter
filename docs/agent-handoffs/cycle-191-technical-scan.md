# Cycle 191 Technical Scan: Draft Example Rendering

Date: 2026-05-17

## Current Behavior

`acceptance_draft_command()` intentionally emits checklist-only commands for multi-entrypoint
targets. That canonical group command should stay unchanged because it represents the grouped
validation target.

## Implementation Shape

- Keep `acceptance_draft_command()` unchanged.
- Extend `_render_target_block()` with an optional detail-only flag.
- Pass the flag only when `render_validation_target_lines()` receives `target_id`.
- Generate per-entrypoint examples by temporarily narrowing the target to one entrypoint and
  reusing `acceptance_draft_command()`.
- Skip examples when the target has one entrypoint, any flow ids, or is blocked.

## Tests To Touch

- Renderer tests for grouped target examples.
- Renderer tests proving priority lists do not expand.
- Renderer tests proving single-entrypoint detail stays unchanged.
- CLI detail test for a grouped target.
- Existing blocked/no-draft tests remain the safety guard.

## Package Scope

Package YAML should remain untouched. This is a renderer clarity change over existing validated
target IDs.
