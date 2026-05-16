# Mixed Validation Draft Guidance Design

Date: 2026-05-16
Cycle: 030

## Problem

Some validation targets intentionally combine a demo flow and an entrypoint. The current example is `rcv-controller-chat-question`, which should be accepted by running `meeting-control-map-demo` and asking about the Chat entrypoint during that flow.

`validation-targets` already knows both IDs, but the generated draft command falls back to checklist-only context. That forces operators and subagents to reconstruct the precise `acceptance-draft` command from surrounding output.

## Acceptance

- A validation target with exactly one flow ID and exactly one entrypoint ID emits an `acceptance-draft` command with both `--flow` and `--entrypoint`.
- The command still includes `--checklist-target`.
- Single-entrypoint-only and single-flow-only commands keep their existing behavior.
- Multi-entrypoint or multi-flow group targets stay checklist-only.
- `acceptance-draft` mixed drafts prefill `Steps executed` with a sentence that names both the flow and the target entrypoint.
- Existing flow/entrypoint membership validation stays unchanged.
- No live RingCentral action or evidence write is performed.

## Design

Update `acceptance_draft_command()`:

- one entrypoint, no flow: `--entrypoint`
- one flow, no entrypoint: `--flow`
- one flow and one entrypoint: `--flow` plus `--entrypoint`
- otherwise: checklist-only fallback

Update `_intended_steps()` in `manual_record.py` so mixed requests mention both IDs before asking the operator to fill actual steps after the run.

## Out Of Scope

- Shell parsing or command execution.
- Acceptance evidence updates.
- Controller runtime changes.
- JSON output or target aliases.
