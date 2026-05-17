# Cycle 182 Experience Handoff

Date: 2026-05-17

## Lessons Learned

- Spanish accent folding already covers singular `Quién está...` and `Muéstrame...` variants, but plural `Quiénes están...` needed explicit identity terms.
- A no-entrypoint answer can still be the wrong privacy family. `¿Quiénes están en la reunión?` was non-operable, but it answered with post-meeting artifact policy until participant privacy matched first.
- Panel/list terms are not enough to prove navigation. If the same Spanish prompt asks `quién`, `quiénes`, names, roles, host, or moderator, participant privacy must win.
- Durable docs belong in `docs/knowledge/ringcentral-video/privacy-matrix.md`, not only cycle handoffs, because this is a product safety boundary for future live validation and package work.
- Avoid YAML aliases for accent variants. Runtime privacy matching and tests are safer for boundary intent.

## Future Subagent Prompts

- Add voice/profile-aware controller coverage for Spanish with the OpenAI profile if controller Spanish execution becomes in-scope.
- Audit other Spanish privacy-sensitive surfaces for plural who-is phrasing, especially meeting info, invite suggestions, post-meeting artifacts, and chat.
- Consider a helper for language-specific privacy intent terms if runtime constants keep growing.
- Add localized docs for Chinese and Japanese participant boundaries in the durable privacy matrix.

## Next-Cycle Backlog

1. Review Chinese/Japanese durable privacy docs for parity with the new Spanish block.
2. Explore whether `normalize_question_prompt()` should have direct unit tests for accent folding contracts.
3. Check UI/operator summary copy for answer-only participant privacy prompts.
4. Keep `.coverage` out of commits.
