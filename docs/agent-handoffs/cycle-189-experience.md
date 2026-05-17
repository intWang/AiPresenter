# Cycle 189 Experience Handoff

Date: 2026-05-17

## Lessons Learned

- The safest place for recurring manual evidence guidance is the draft generator, because it
  appears before operators perform live validation.
- Evidence templates should make metadata-first capture the default and screenshot capture the
  exception.
- Privacy notes are more useful when they name both redacted material and material intentionally
  not captured.
- Keeping generator and `acceptance-runs.md` template language aligned reduces future drift.

## Future Subagent Prompts

- Audit whether validation target output should show a one-line redaction reminder for P0/P1
  manual routes.
- Consider a docs-only sample completed record with obviously synthetic private fields redacted.
- Continue expanding language/tone support only after privacy boundaries stay stable in tests.
- Keep `.coverage` out of every commit.

## Next-Cycle Backlog

1. Add a lightweight CLI reminder to `validation-targets` output if tests can keep it concise.
2. Review whether controller UI should surface redaction guidance for generated package scans.
3. Continue RingCentralVideo manual acceptance preparation without claiming live proof.
