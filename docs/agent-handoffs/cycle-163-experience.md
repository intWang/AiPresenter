# Cycle 163 Experience: Chat And Participants Privacy Boundaries

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Scope

This is a docs-only knowledge pack for the Cycle163 privacy-first RingCentral
Video Q&A hardening work. It captures what the cycle learned about Chat,
Participants, host participant actions, and adjacent private-value prompts. No
code, tests, `.coverage`, staging, or commits were touched by this handoff.

## What We Learned

- Chat and Participants are legitimate RingCentral Video navigation surfaces,
  but they sit next to private content. Opening a panel is not equivalent to
  reading messages, names, roles, private tabs, or host-only controls.
- Thin entrypoint fallback can be mechanically safe but experientially weak.
  For privacy-shaped prompts, answers should explain the boundary instead of
  returning labels such as `Participants panel:` or `Meeting information:`.
- Q&A-first exact prompts are the right hardening tool for high-risk variants.
  They make privacy intent explicit, keep package inventory honest, and give
  tests a stable contract.
- Chat content requests should not route to
  `ringcentral.video.toolbar.chat`. Participant identity, role, and host-action
  requests should not route to `ringcentral.video.toolbar.participants` unless a
  future confirmed workflow deliberately proves it is safe.
- Host participant actions such as muting others, removing people, locking the
  meeting, or changing security are state-changing and socially visible. They
  need answer-only guidance unless a separate workflow verifies context and
  gets explicit confirmation.
- Current evidence remains package/routing/unit-test evidence. It does not
  prove live RingCentral Video UI contents, participant roster state, roles,
  chat text, clipboard state, host status, or acceptance in a real meeting.

## Operable Vs Answer-Only

Treat a prompt as **operable** only when it asks for location or a safe demo
entrypoint and the matched entrypoint has open steps, no `answerOnly` policy,
and no risky control semantics. Examples: `chat`, `open chat`, or
`participants` can remain panel-navigation behavior if the user is asking where
the control is or wants the panel shown.

Treat a prompt as **answer-only** when it asks to read, summarize, expose,
verify, copy, send, select, mute, remove, lock, start, stop, or change anything
that could reveal private content or affect the meeting. The key checks are:

- Exact Q&A should beat entrypoint fallback for privacy-shaped commands.
- `response.can_operate is False`.
- `create_question_interrupt_step(package, response) is None`.
- The answer should not begin with a thin control label when privacy guidance is
  expected.
- The answer should avoid private-looking values and success claims: no real
  names, roles, emails, phone numbers, meeting IDs, links, chat messages,
  transcript/caption text, copied/read/sent/muted/removed/locked claims, or
  verified-live-state claims.

## Prompt Taxonomy

Use this taxonomy when deciding the next exact prompt slice:

- **Location lookup**: `Where is Chat?`, `Where are Participants?`,
  `Where are captions?`. Usually answer with the relevant surface; may be
  operable only if the surface is otherwise safe.
- **Panel navigation**: `Open Chat`, `Show Participants`. May be operable for
  simple panel opening, but do not infer permission to inspect contents.
- **Content readout**: `Read chat aloud`, `Summarize the chat`,
  `Read caption text`. Always answer-only unless a later visible-content
  workflow exists.
- **Identity readout**: `Who is in the meeting?`, `List participants`,
  `Read participant names`, `Show participant roles`. Answer-only by default.
- **Host or moderator action**: `Mute all participants`,
  `Remove a participant`, `Lock the meeting`. Answer-only by default because it
  changes meeting state or affects other people.
- **Private meeting access values**: `Read the dial-in number`,
  `Who is the host?`, `Can you copy the meeting link?`. Answer-only; no exact
  value exposure from package Q&A.
- **State or policy status**: `Is the meeting locked?`,
  `Can you tell me the encryption status?`. Answer-only unless visible state is
  verified; avoid claiming a current state from static package knowledge.
- **Broad aliases**: `host`, `roles`, `chat`, `participants`, `copy`, `read`.
  Avoid adding these as privacy Q&A prompts because they can steal legitimate
  location or panel intents.

## Backlog For Next Cycles

1. Add exact participant-role coverage for `Show participant roles` so it stays
   answer-only and does not create a Participants interrupt.
2. Add exact caption-text coverage for `Read caption text`,
   `Show captions text`, and `Show live caption text` so text-readout prompts
   do not no-match or drift to the Audio entrypoint.
3. Finish host and dial-in private-value prompts under the meeting-info privacy
   answer: `Read the dial-in number`, `Can you read the dial-in number?`,
   `Can you copy the dial-in number?`, `Who is the host?`,
   `Can you read the host name?`.
4. Split future passcode/password, meeting-lock, and encryption-status prompts
   into their own slices after confirming product wording and expected answer
   boundaries.
5. Add higher-layer presenter/session checks proving privacy Q&A responses
   cannot become queued demo steps, clipboard actions, speech readouts, invite
   sends, roster reads, participant control actions, or live interrupts.
6. Audit localized variants only after intent is mapped per locale. Translation
   must preserve the privacy boundary, not just mirror English verbs.

## Suggested Subagent Prompts

- **Technical scan subagent**: "Inspect current RingCentral Video Q&A routing
  for `Show participant roles`, caption-text prompts, and host/dial-in private
  values. Report current response entrypoint, `can_operate`, interrupt creation,
  thin fallback labels, and exact tests to extend. Do not modify files."
- **Implementation subagent**: "Implement the smallest package/test-only exact
  prompt hardening slice from the latest Cycle163 handoff. Add only exact Q&A
  prompt strings to existing items, update focused tests and prompt counts as
  needed, and do not touch runtime matcher code, `.coverage`, acceptance
  evidence, or unrelated docs."
- **Risk scan subagent**: "Review the proposed exact prompts for alias overlap,
  substring-risk count movement, accidental operability, location prompt
  shadowing, private-value leakage, and stale diagnostics/CLI inventory counts.
  Write a docs-only risk handoff."
- **Test review subagent**: "Run only the focused RingCentral Video question
  tests and any diagnostics/CLI count tests touched by the slice. Confirm
  privacy prompts are answer-only, no interrupt is created, nearby location
  prompts still route normally, and no live RingCentral acceptance is claimed."
- **Experience subagent**: "Summarize what the slice taught about prompt intent,
  privacy wording, operable versus answer-only routing, count hygiene, and the
  next smallest backlog item. Write only the requested experience handoff."

## Safe Wording To Preserve

- "Chat and Participants can be explained or opened as surfaces, but chat
  messages, participant names, roles, private tabs, and host controls are not
  safe to read or act on from package Q&A alone."
- "Exact privacy-shaped prompts should beat thin entrypoint labels, while
  ordinary location and panel-navigation prompts should keep normal lookup
  behavior."
- "These prompts are answer-only, non-operable, and should not create a
  question interrupt step."
- "Package and unit-test evidence proves routing and guard behavior only; it
  does not prove live RingCentral Video state, visible values, or acceptance."
