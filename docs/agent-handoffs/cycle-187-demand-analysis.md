# Cycle 187 Demand Analysis: Controller Public Error Boundary

Date: 2026-05-17

## User Need

After Cycle 186 made question outcomes privacy-safe, operators still need non-question controller failures to follow the same public/private boundary. A controller status row should help the user recover without exposing exception text that may contain raw prompt fragments, meeting content, local paths, or provider details.

## Chosen Slice

Sanitize non-question controller error status strings while preserving known public configuration errors.

## Alternatives Considered

The demand-analysis subagent recommended a docs-only RingCentralVideo privacy examples slice for chat, meeting information, recording, and notes/transcript. That remains useful and should be considered next. This cycle chose controller status hardening because the technical scan found an active UI privacy gap.

## Acceptance Criteria

- `resolve_controller_status(...)` hides arbitrary runtime exception text.
- Known public `Unknown demo flow: ...` KeyError messages remain visible.
- App refresh, scan, and start exception paths use bounded public status text.
- Voice asset checker exceptions do not copy exception text into readiness details.
- Operator summary rows can display the sanitized run status without private text.
- No package, YAML, localization, routing, or RingCentral acceptance changes.

## Non-Goals

- Do not redesign controller UI.
- Do not hide intentionally public voice compatibility errors such as unsupported language/provider combinations.
- Do not change logging, package diagnostics, or RingCentralVideo safety routing.
- Do not add the RingCentral private-surface examples in this cycle.
