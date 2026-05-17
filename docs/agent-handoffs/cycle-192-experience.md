# Cycle 192 Experience Handoff

Date: 2026-05-17

## Lessons Learned

- Performance work should start with privacy-safe measurement before optimization.
- Running-app scans touch arbitrary desktop surfaces, so logs must avoid window titles and
  control labels even when the UI itself can show them to the operator.
- Deriving safe/explain-only counts from the generated package keeps telemetry aligned with
  runtime behavior.
- Language lifecycle docs can drift from CLI reports; tests should guard count text when it is
  used as operator-facing status.

## Future Subagent Prompts

- Use the new `running_app_scanned` telemetry to identify whether control listing or package
  generation dominates scan latency.
- Consider refresh-window telemetry only if operators report slow window refreshes.
- Continue language/tone expansion by adding behavior, not just aliases, when privacy boundaries
  stay stable.
- Keep `.coverage` out of every commit.

## Next-Cycle Backlog

1. Add scan performance aggregation or thresholds if telemetry shows slow paths.
2. Explore controller UI affordances for copying generated scan/package summaries.
3. Continue language/tone expansion with provider-gated behavior tests.
