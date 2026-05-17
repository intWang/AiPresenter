# Cycle 196 Demand Analysis: Continuous Optimization Cycle Protocol

Date: 2026-05-17

## User Need

The user asked for a 48-hour optimization loop where the main session orchestrates, subagents
advance demand analysis, technical development, test review, and experience capture, and each
cycle ends in a commit. Recent cycles follow that pattern, but the durable maintenance playbook did
not state the protocol directly.

## Operator / Agent Value

- Makes the repeated optimization loop easier to run without relying on chat memory.
- Clarifies that the main session owns scope, integration, final verification, staging, and commit.
- Keeps subagent work valuable but bounded to lenses and handoff docs.
- Reduces `.coverage` staging mistakes by making cached-diff proof part of the cycle protocol.
- Sets the expectation that every completed cycle leaves one narrow, reviewable commit.

## Chosen Slice

Add `## Continuous Optimization Cycle Protocol` to `docs/knowledge/ai-presenter-maintenance.md`
after the artifact chooser and before RingCentral-specific rules.

## Acceptance Criteria

- The playbook names the main session as owner of orchestration, integration, verification,
  staging, and commit.
- The playbook names subagent lenses: demand, technical, risk/test review, and experience.
- The playbook says handoffs under `docs/agent-handoffs/` are coordination docs, not evergreen
  truth.
- The playbook requires one narrow commit after review.
- The final gate includes pytest, ruff, mypy, cached diff checks, and `.coverage` cached-diff proof.
- No runtime, package YAML, global Codex skill, provider, or RingCentral acceptance behavior changes.
