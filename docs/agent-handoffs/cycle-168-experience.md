# Cycle 168 Experience: Meeting Security And Host Controls

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Role: Cycle168 experience/knowledge subagent

## Scope

Docs-only knowledge pack for RingCentral Video meeting security, lock/unlock,
security-settings, and host-control privacy prompts. This pass writes only
`docs/agent-handoffs/cycle-168-experience.md`. It did not edit code, tests,
package YAML, staging, commits, `.coverage`, or run the full suite.

## What We Learned

- Security and lock prompts belong with host/moderator controls, not generic
  participant-panel location, Meeting information encryption, or full-screen
  layout routing.
- Current concurrent work adds exact English Q&A prompts under `Where are host
  controls for participants?`: `Unlock the meeting`, `Change meeting security`,
  `Where are security settings?`, `Open meeting security settings`, and
  `Meeting security settings`.
- Existing host-control prompts already include `Mute all participants`,
  `Remove a participant`, and `Lock the meeting`. The safest expansion is more
  exact Q&A prompts on that item, not broad aliases or runtime matcher changes.
- The answer should explain that the Participants panel is where attendee count,
  search, invite, and host/moderator control areas are discussed, while refusing
  to perform or claim high-impact actions without explicit intent and verified
  visible context.
- Privacy docs classify Security/waiting room as always-confirm controls:
  locking/unlocking, admitting/removing people, muting others, and changing
  permissions are meeting-impacting and role-gated.

## Prompt Taxonomy

- **Host-control action prompts**: `Mute all participants`, `Remove a
  participant`, `Lock the meeting`, `Unlock the meeting`, `Change meeting
  security`. Answer-only; do not queue a UI step.
- **Security-settings location prompts**: `Where are security settings?`, `Open
  meeting security settings`, `Meeting security settings`. Treat as host-control
  privacy prompts, not normal operable navigation.
- **Security state prompts**: `Is the meeting locked?`, `Is the waiting room
  on?`, `Who can join?`, `Are participants restricted?`. Backlog only; these
  need live state/product evidence and should not reuse static Q&A as facts.
- **Meeting information encryption prompts**: `What is the encryption status?`,
  `Read the encryption details`, `Copy the encryption details`. Separate slice;
  route to Meeting information privacy, not host/security settings.
- **Password/passcode/access-code prompts**: blocked until product evidence
  proves RingCentral Video exposes these values and where.
- **Full-screen/view prompts**: `Show full screen`, `Go full screen`, `Where is
  full screen?`. Separate Views-routing issue; do not mix with meeting security.

## Operable Vs Answer-Only Rules

- Answer-only for any prompt asking to mute others, remove/admit participants,
  lock/unlock the meeting, change permissions, change security settings, or
  expose host-control state.
- Expected host-control privacy route: no operation, `can_operate is False`, no
  question interrupt, and no fallback label such as `Participants panel:`.
- General `Participants` location prompts may still route to the Participants
  panel. Host-control/security prompts should not become an operable
  Participants open step just because those controls live there.
- Explicit user intent and verified visible context are prerequisites for
  discussing sensitive details, but execution still needs a future confirmation,
  role, and cleanup policy before any live operation is allowed.
- Do not add broad aliases such as `security`, `lock`, `unlock`, `settings`, or
  `host`; they can steal unrelated encryption, settings, participant, or
  troubleshooting prompts.

## Safe Wording

- Say: "Use the Participants panel to explain attendee count, search, invite,
  and host or moderator control areas."
- Say: "Do not mute others, remove people, lock or unlock the meeting, change
  security settings, or read names and roles unless the user explicitly asks and
  the visible context is verified."
- Say: "I can explain where host controls live, but I should not make
  meeting-impacting changes from a Q&A prompt alone."
- Avoid: "I locked the meeting", "I unlocked the meeting", "I changed security
  settings", "the meeting is locked", "waiting room is on", or any claim that a
  host-control action or state was completed or verified.
- Avoid wrong-route text: `Participants panel:`, `Background settings:`,
  `Meeting information:`, `Screen sharing:`, and `I could not find a matching
  control`.

## Future Backlog

1. Add a separate state-verification slice for `Is the meeting locked?`, `Is the
   waiting room on?`, and related permission/status prompts after adapter or
   product evidence exists.
2. Finish the Cycle168 encryption-status slice separately under Meeting
   information privacy. Do not classify encryption details as host/security
   settings.
3. Finish the full-screen/views misroute separately by routing exact full-screen
   prompts to Views, not Share, and not touching security Q&A.
4. Keep password/passcode/access-code prompts blocked until RingCentral Video
   product evidence confirms the fields and surface. If confirmed, update
   Meeting information privacy wording first.
5. Add localized security/lock variants only after English exact prompts,
   answer text, and Q&A count expectations are stable.

## Suggested Subagent Prompts

- **Security Q&A implementer**: "Finalize only the RingCentral Video
  lock/unlock/security-settings exact Q&A prompts under `Where are host controls
  for participants?`. Keep them answer-only, non-operable, no interrupt, and do
  not add broad aliases, runtime matcher changes, `.coverage`, staging, commits,
  or full-suite runs."
- **Security privacy verifier**: "Verify `Mute all participants`, `Remove a
  participant`, `Lock the meeting`, `Unlock the meeting`, `Change meeting
  security`, `Where are security settings?`, `Open meeting security settings`,
  and `Meeting security settings` all return host-control privacy guidance with
  no operation, no interrupt, and no fallback labels."
- **State evidence researcher**: "Gather product/runtime evidence for lock
  status, waiting-room status, admit/remove permissions, and host/moderator role
  visibility. Report recommended exact prompts only; do not implement."
- **Encryption subagent**: "Handle encryption-status and encryption-detail
  prompts only under Meeting information privacy. Keep them separate from
  host/security settings and do not claim live encryption state from static
  package data."
- **Full-screen subagent**: "Resolve full-screen layout prompts by routing exact
  full-screen wording to `ringcentral.video.top.views`. Do not alter host-control
  Q&A, security prompts, or encryption prompts."
