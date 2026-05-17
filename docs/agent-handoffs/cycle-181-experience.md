# Cycle 181 Experience Handoff

Date: 2026-05-17

## Lessons Learned

- Localized privacy boundaries need their own sentinel tests. English `show/list/who` behavior does not protect CJK or Spanish substring aliases.
- Panel/list wording is safe only while it remains about navigation. As soon as names, roles, who-is, host, or moderator terms appear, the privacy Q&A must win.
- Reclassifying `谁在会议里` is intentional: it asks for identity disclosure, even though it was previously a convenient Participants alias.
- Question-routing tests can cover ja/es localized answers without requiring speech-provider readiness.
- Controller/session tests should use a profile that supports the selected voice. For this cycle, Chinese gives enough end-to-end mixed-meta coverage without changing profile setup.
- Do not broaden YAML aliases to solve privacy matching. Runtime Q&A matching is the correct layer for policy boundaries.

## Future Subagent Prompts

- Add accented Spanish variants for localized participant privacy, including `Muéstrame`, `Quién`, `está`, and `reunión`.
- Audit bare localized participant aliases (`参会者`, `参加者`, `participantes`) and decide whether product semantics should prefer panel navigation or privacy guidance.
- Add OpenAI-profile controller/session coverage for ja/es mixed-meta prompts if voice-provider behavior becomes part of the test goal.
- Extend durable RingCentralVideo docs with a localized participant privacy matrix.
- Review whether host/moderator identity should always use the participant privacy answer rather than meeting-info or host-control guidance.

## Next-Cycle Backlog

1. Broaden Spanish accented privacy variants with tests first.
2. Add localized participant privacy notes to `docs/knowledge/ringcentral-video/privacy-matrix.md`.
3. Explore UI/diagnostic copy for explaining why identity prompts are answered without opening the Participants panel.
4. Keep `.coverage` out of commits.
