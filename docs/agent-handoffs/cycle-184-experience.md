# Cycle 184 Experience Handoff

Date: 2026-05-17

## Lessons Learned

- Observability should reuse bounded routing tokens rather than derived prose or answer text.
- Privacy tests need realistic prompts whose full raw text cannot be confused with route ids. `show network quality` is a better entrypoint logging sentinel than `participants`.
- Successful logs and error logs have different privacy needs. Success can report safe route metadata; failure should stay minimal because exception text may be private.
- Maintenance guidance is the right durable home for cross-cycle logging rules. Handoff docs explain the slice, but the playbook keeps the reusable rule.

## Future Subagent Prompts

- Audit controller/UI history events for the same answer-source distinction without exposing question or answer content.
- Review whether log consumers parse `question_answered` as flexible key-value metadata or fixed text.
- Add a small diagnostics report for question routing counts only if it can stay package-local and privacy-safe.
- Continue the RingCentralVideo knowledge pack with privacy-safe observability examples for chat, participants, meeting info, recording, and notes.

## Next-Cycle Backlog

1. Add UI-side privacy-safe status affordance for text-only source if the controller surface needs it.
2. Inspect package diagnostics for answer-only policy counts.
3. Keep expanding localized privacy sentinel tests without adding broad fuzzy routing.
4. Keep `.coverage` out of commits.
