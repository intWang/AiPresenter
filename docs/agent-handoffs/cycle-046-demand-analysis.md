# Cycle 046 Demand Analysis

## Recommended Slice

Add a RingCentral Video Q&A item for host-style participant management.

## User Value

During live meetings, users often ask where host or moderator controls live and how to manage participants. Ai Presenter already knows the Participants panel and the privacy rules around names, roles, lock, mute, and invite controls, but it does not yet have a direct Q&A answer for that host-control intent. A content-level Q&A makes the presenter sound more prepared without adding risky automation.

## Acceptance Criteria

- English questions such as `where are host controls for participants` return the new Participants guidance.
- Chinese questions such as `主持人怎么管理参会者` return localized guidance.
- The answer mentions the Participants panel but remains answer-only: no related entrypoint is returned and `can_operate` stays false.
- The answer says the Presenter may explain where Participants lives, while muting/removing/locking/reading names requires explicit user request and visible verification.
- Existing recording, leave, invite, and share safety behavior remains unchanged.

## Out Of Scope

- No new host-control routes.
- No role-gated automation.
- No changes to `can_operate` policy.
- No broad matcher rewrite or legacy alias table changes; only a narrow guard to keep one-word generic queries from being shadowed by the new Q&A.
