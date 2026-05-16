# Cycle 042 Demand Analysis: Direct Acceptance Draft Safety

Date: 2026-05-16
Role: demand discovery
Scope: read-only demand analysis. No implementation changes were made by the demand agent.

## Recommended Slice

Harden direct `acceptance-draft --entrypoint ...` requests so entrypoints with no executable `openSteps` are refused instead of producing a manual-run draft.

Cycle 041 removed blocked draft links from `validation-targets`, but an operator who knows the entrypoint ID can still call `acceptance-draft` directly for Recording or Leave. The current draft warns, but still creates a manual acceptance template with “Steps executed” placeholders.

## User Value

Operators cannot accidentally turn explain-only or blocked RingCentral controls into manual acceptance runs by direct CLI invocation. Blocked routes stay visible for audit, but direct manual-run draft generation requires an executable route or a future confirmation workflow.

## Acceptance Criteria

- `acceptance-draft --entrypoint ringcentral.video.more.recording` exits nonzero.
- `acceptance-draft --entrypoint ringcentral.video.toolbar.leave` exits nonzero.
- The refusal mentions no executable open steps and a separate confirmation workflow.
- Refused requests do not print or write draft text.
- Executable entrypoints such as Add coworkers still render and write drafts.
- Flow-only drafts such as `meeting-control-map-demo` remain supported.
- Cycle 041 `validation-targets --include-blocked` behavior remains intact.

## Out Of Scope

- No confirmation workflow.
- No package route changes.
- No evidence promotion.
- No live RingCentral automation.
- No redesign of validation target parsing.

