# Cycle 165 Experience: Participant Identity Metadata Privacy

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Role: Cycle165 experience/knowledge subagent

## Scope

Docs-only knowledge pack for RingCentral Video Participants privacy around roles, host/moderator labels, and attendee identity metadata. This pass only writes `docs/agent-handoffs/cycle-165-experience.md`. It did not edit code, tests, package YAML, `.coverage`, staging, commits, or run the full suite.

## What We Learned

- Participant identity is broader than names. Roles, host/moderator labels, roster membership, attendee counts tied to names, private tabs, and chat snippets are all meeting identity metadata.
- The Participants panel is a valid control surface for explaining attendee count, search, invite, and host/moderator control areas. It is not automatically permission to read the roster or role labels aloud.
- Role prompts should be handled like participant-name prompts: answer-only privacy guidance unless a future workflow proves explicit user intent, visible context, and a clear permission boundary.
- Current shared worktree context already adds exact role prompts such as `Show participant roles`, `Read participant roles`, `List participant roles`, and `Who is host or moderator?` to the existing participant privacy Q&A. Treat that as another agent's work; do not duplicate or overwrite it.
- Thin fallback text is not enough for privacy-shaped asks. A no-match answer is mechanically safe, but privacy guidance is better when the user asks to read, show, list, or identify people or roles.

## Prompt Taxonomy

- **Control/location prompts**: `participants`, `open participants`, `where are participant controls`, `where are host controls for participants`. These may describe or operate on the Participants surface when the package already supports that behavior.
- **Identity readout prompts**: `Who is in the meeting?`, `List participants`, `Read participant names`. These should stay answer-only and avoid roster readout.
- **Role/label prompts**: `Show participant roles`, `Read participant roles`, `List participant roles`, `Who is host or moderator?`. Treat as identity metadata, not harmless labels.
- **Host/moderator control prompts**: `where are host controls for participants`. Explain the control area and safety boundary; do not mute others, remove people, lock meetings, or change security settings from Q&A.
- **Broad aliases to avoid**: `roles`, `host`, `moderator`, `participant`, `attendee`, `names`, `read`, `show`, `list`. Use exact prompts in Q&A rather than broad matcher aliases.

## Operable Vs Answer-Only Rules

- Operable: opening or explaining a known control surface such as the Participants panel, when the prompt is about the surface or workflow and not about reading private values.
- Answer-only: any prompt asking to read, list, show, identify, summarize, copy, export, or announce participant names, roles, host/moderator labels, chat content, or private tabs.
- Answer-only responses must keep `can_operate` false and must not create an interrupt step.
- Prefer existing privacy Q&A items over entrypoint `questionAliases` for private-value prompts. Entrypoint aliases can route to control labels or interrupts before the privacy boundary is heard.
- Do not claim the current host, moderator, attendee roster, role assignments, chat content, or visible UI state from static package evidence.

## Safe Wording

- Say: "The Participants panel can show people context and host/moderator areas, but AiPresenter should not read participant names, roles, chat messages, or private tabs unless the user explicitly asks and the visible context is verified."
- Say: "I can explain where those controls are; I should not announce attendee identity metadata from the meeting roster by default."
- Avoid: "The host is...", "The moderator is...", "Here are the participants...", "I verified the roles...", "Copied", "Read aloud", "Exported", or any invented/masked roster values.
- Avoid starting privacy answers with thin fallback labels such as `Participants panel:` when the user asked for identity metadata.

## Next-Cycle Backlog

1. **Caption text first**: Add exact caption-content prompts such as `Read caption text`, `Show captions text`, and `Show live caption text` under the existing captions/transcript privacy Q&A. This fixes no-match and Audio fallback drift without new product evidence.
2. **Participant-role follow-up only if needed**: If the concurrent role diff lands, consider exact nearby variants like `Show roles` or `What are participant roles?` only after verifying they do not shadow location/control prompts.
3. **Password/passcode later**: Do not add password/passcode prompts until product evidence confirms RingCentral Video exposes those fields and where. If confirmed, update English and localized safety answers to name passwords/passcodes as private meeting access details.
4. **State/policy prompts**: Encryption, meeting lock, waiting room, and security status need state-verification wording. Static Q&A can explain surfaces, not assert current state.

## Suggested Subagent Prompts

- **Caption implementation subagent**: "Implement the smallest package/test-only caption-text privacy slice. Add exact English prompts to the existing captions/live transcription Q&A, update only focused tests and actual prompt-count expectations, avoid runtime matcher changes, broad aliases, `.coverage`, staging, commits, and full-suite runs."
- **Participant privacy review subagent**: "Review participant-role and host/moderator prompts for answer-only behavior. Confirm no route to `ringcentral.video.toolbar.participants`, no `Participants panel:` fallback, no interrupt step, and no roster or role values in answers."
- **Password/passcode evidence subagent**: "Gather product/source evidence for whether RingCentral Video exposes meeting password/passcode fields in Meeting information or another surface. Report evidence and recommended exact prompts only; do not implement without confirmation."
- **Risk/test subagent**: "Run focused privacy routing checks with coverage disabled for participant identity, caption text, and meeting-info private values. Verify prompt counts, alias overlap, no operability, no interrupts, and no private-value leakage. Do not run the full suite or touch `.coverage`."
