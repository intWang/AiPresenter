# Cycle 185 Demand Analysis: Answer-Only Policy Visibility

Date: 2026-05-17

## User Need

Maintainers need RingCentralVideo's answer-only entrypoint policy to be visible in routine diagnostics. The package already relies on `questionPolicy: answerOnly` for sensitive but identifiable surfaces; `doctor` should make that boundary easy to review without reading YAML by hand.

## Chosen Slice

Expose a privacy-safe `question policy` diagnostic in `doctor`:

```text
2/27 entrypoints use answerOnly question policy: ringcentral.video.top.meeting-info, ringcentral.video.more.notes
```

This complements the existing Q&A duplicate, alias overlap, alias substring, and explainer coverage checks.

## Why This Slice

- It strengthens the RingCentralVideo knowledge pack and safety review loop.
- It is package metadata only, not live meeting data.
- It does not change routing, controller UI, package YAML, aliases, localization, or operation permission.
- It gives future package changes an intentional count-drift tripwire.

## Deferred Demand

The demand-analysis subagent recommended controller/UI answer-source parity for text-only outcomes. That remains valuable and should be considered for Cycle186, but this cycle stays focused on diagnostics and RingCentralVideo資料包 hardening.

## Acceptance Criteria

- `doctor` includes an OK-level `question policy` check whenever a package is loaded.
- RingCentralVideo reports exactly `2/27` answer-only policy entrypoints: Meeting information and Notes/Transcript.
- Generic packages with no `answerOnly` entrypoints report `0/N`.
- CLI doctor output includes the new check.
- Runtime safety-routing and source-index docs record the diagnostic signal.
- No package count, YAML, routing, localization, or UI behavior changes.

## Non-Goals

- Do not add or remove `questionPolicy` declarations.
- Do not count Q&A items as entrypoint policy.
- Do not expose user questions, answer text, meeting content, participant names, links, or live UI text.
- Do not implement controller answer-source UI parity in this cycle.
