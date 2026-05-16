# Direct Acceptance Draft Safety Design

Date: 2026-05-16

## Context

Blocked RingCentral controls such as Recording and Leave have no executable package `openSteps`. Cycle 041 removed copy-paste draft commands for these blocked validation targets, but direct `acceptance-draft --entrypoint` can still render a draft for the same entrypoints.

## Design

Reject direct acceptance drafts for entrypoints with no executable `openSteps`.

The rejection should be clear and non-destructive:

- mention the entrypoint ID
- mention no executable open steps
- mention that a separate confirmation workflow is required before live execution
- avoid printing or writing draft text

Flow-only drafts remain supported because explain-only steps inside a flow do not by themselves select a direct live operation target.

## Non-Goals

- No confirmation workflow.
- No package YAML changes.
- No validation checklist parsing changes.
- No evidence promotion.
- No live RingCentral actions.

