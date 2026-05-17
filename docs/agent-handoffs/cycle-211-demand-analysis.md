# Cycle 211 Demand Analysis

Date: 2026-05-17
Cycle: 211
Role: Demand analysis subagent

## Recommendation

Add the selected flow's step count to the CLI loaded-flow summary.

## User Value

- Gives operators immediate confidence that `demo` or `controller` loaded the
  intended flow before automation starts.
- Helps distinguish similarly named RingCentral flows such as
  `meeting-controls-tour` and `meeting-control-map-demo`.
- Aligns loaded-flow output with the existing `flows` command, which already
  displays step counts.

## Selected Slice

- Change the existing `Loaded flow: <id>` line to
  `Loaded flow: <id> (<N> steps)` for both `demo` and `controller`.
- Keep the original prefix so existing operator habits and substring checks
  remain useful.

## Non-Goals

- No package YAML, flow metadata, language, tone, presenter skill, controller UI,
  or live RingCentral evidence changes.
- No missing-flow error changes.
- No new abstraction unless this output pattern grows beyond the two existing
  loaded-flow lines.

## Acceptance Criteria

- `demo --dry-run` prints `Loaded flow: meeting-controls-tour (22 steps)`.
- `controller --dry-run` prints
  `Loaded flow: meeting-control-map-demo (22 steps)`.
- Existing profile/package/voice/dry-run completion lines remain unchanged.
- Missing-flow error tests remain green.
