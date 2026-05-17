# Cycle 187 Experience Handoff

Date: 2026-05-17

## Lessons Learned

- Question privacy and controller status privacy are adjacent but separate. Sanitizing `submit_question()` was not enough; background controller paths needed their own public formatter.
- Status strings are UI content, not debug logs. They should default to safe public wording.
- Allowlists should stay narrow. `Unknown demo flow` is useful and repo-controlled; arbitrary runtime exception text is not.
- Voice compatibility errors are product guidance, but voice asset checker exceptions are implementation details and should be collapsed.

## Future Subagent Prompts

- Add RingCentralVideo private-surface examples for chat, meeting information, recording, and notes/transcript.
- Review whether detailed exception text should be available in debug logs with redaction, separate from UI status.
- Audit provider and desktop adapter exceptions for public/private boundaries if UI surfaces grow.

## Next-Cycle Backlog

1. RingCentralVideo private-surface examples in durable docs.
2. Optional debug logging for sanitized controller exceptions.
3. Continue UI polish without broad layout churn.
4. Keep `.coverage` out of commits.
