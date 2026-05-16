# Blocked Validation Draft Safety Design

Date: 2026-05-16

## Context

RingCentral validation targets have a `Do Not Execute Yet` section for high-impact routes such as Recording and Leave. These targets are useful to list, but the rendered output currently includes normal-looking `acceptance-draft` commands.

That creates a safety mismatch: the text says blocked, while the command line looks actionable.

## Design

Suppress draft command rendering for targets with `blocked_reason`.

The blocked target should keep its evidence, current state, validation warning, privacy boundary, and blocked reason, but omit the executable-looking command.

Normal targets continue to render existing draft commands.

## Non-Goals

- No parser changes.
- No `acceptance_draft_command()` change.
- No package YAML or evidence changes.
- No confirmation workflow.
- No live RingCentral execution.

