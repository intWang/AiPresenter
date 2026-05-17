# Cycle 194 Experience Handoff

Date: 2026-05-17

## Lessons Learned

- View-model privacy gating is useful, but controller state should still be cleaned at the source.
- A tiny private state holder is easier to test than closure-local Tk callback state.
- Scan invalidation should clear dependent metadata only after `_RunningAppScanState` decides the
  selected window is no longer the scanned window.

## Future Subagent Prompts

- Consider a controller callback harness only if more Tk closure behavior becomes hard to verify.
- Continue scan performance work by deriving aggregate thresholds from the Cycle 192 telemetry.
- Look for other places where privacy-sensitive runtime metadata is hidden but still retained.
- Keep `.coverage` out of every commit.

## Next-Cycle Backlog

1. Add a RingCentralVideo scan-latency note or threshold once there is enough telemetry.
2. Explore answer/demo handoff copy for running-app Q&A after scan invalidation.
3. Continue evidence workflow hardening with metadata-only artifacts.
