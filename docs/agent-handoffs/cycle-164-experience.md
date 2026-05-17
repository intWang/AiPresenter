# Cycle 164 Experience: Meeting Information Privacy

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Scope

Docs-only knowledge pack for the RingCentral Video Meeting information private-value slice. This handoff captures what the cycle learned about host, dial-in, and detail-value requests. No code, tests, `.coverage`, staging, commits, or full-suite runs were touched by this subagent.

## What We Learned About Meeting Information UX

- Meeting information is useful as a location and explanation surface, but it sits on high-risk access metadata: meeting title, host identity, meeting ID, links, copy controls, dial-in details, encryption, and related meeting policy signals.
- The UX should distinguish "where is this surface?" from "tell me the value." Location-style prompts can remain answer-only surface guidance. Value requests need privacy guidance.
- Thin fallback text such as `Meeting information:` is mechanically safe, but weak for privacy-shaped prompts. Users asking to read, copy, or identify host/dial-in/details should get the existing safety answer, not a generic control label.
- Exact Q&A prompts are the right tool for this slice. They preserve the Meeting information entrypoint context while keeping `can_operate` false and preventing interrupt steps.
- Package routing evidence proves only static answer behavior. It does not prove visible RingCentral Video values, host identity, dial-in availability, encryption state, clipboard contents, or live meeting policy.

## Prompt Taxonomy For Private Meeting Values

- **Location lookup**: `meeting information`, `where is the meeting ID`, `where is the meeting link`. Answer with where the surface is and what category it contains; do not expose values.
- **Dial-in value readout**: `Read the dial-in number`, `What is the dial-in number?`, `Can you read the dial-in number?`. Route to Meeting information privacy Q&A.
- **Dial-in copy/detail action**: `Copy the dial-in details`, `Read dial-in details aloud`. Treat as private meeting access metadata; no copy, readout, or interrupt.
- **Host identity readout**: `Who is the host?`, `Can you read the host name?`. Treat host name/account/company as private unless a future workflow verifies visible content and user intent.
- **Broad meeting-detail readout**: `Read meeting details aloud`. Treat as a bundle of private values, not as a harmless Meeting information lookup.
- **State or policy status**: encryption, lock, and security-status questions need their own state-verification wording. Do not claim a current state from package Q&A alone.
- **Broad aliases to avoid**: `host`, `phone`, `number`, `copy`, `read`, `dial`, `details`, `password`, `passcode`. These can steal unrelated location, participant, invite, or meeting-control prompts.

## Answer-Only Wording Rules

- Use privacy guidance for private-value prompts: exact meeting IDs, links, dial-in details, host information, and similar access metadata should not be copied, read aloud, or exposed unless the user explicitly asks, visible content is verified, and the permission boundary is clear.
- Keep the response answer-only: `entrypoint_id` may remain `ringcentral.video.top.meeting-info`, but `can_operate` must be false and `create_question_interrupt_step(...)` must return `None`.
- Do not open the popover, dial audio, copy to clipboard, paste invite details, read aloud meeting details, or queue a UI step from package Q&A.
- Do not invent, mask, validate, summarize, or expose concrete private values: no host names, company names, phone numbers, access codes, meeting IDs, meeting links, invite text, passwords, or passcodes.
- Do not claim success or verification. Avoid wording such as copied, pasted, dialed, read, confirmed, visible, verified, the host is, the number is, or the meeting is encrypted unless a later live workflow actually proves it.
- Do not start privacy answers with the thin fallback label `Meeting information:`. The user should hear the boundary, not just the control name.

## Next-Cycle Backlog

1. **Password/passcode prompts**: Confirm whether RingCentral Video Meeting information exposes passcode/password fields in the observed product state. If yes, add exact Q&A prompts such as `Read the meeting passcode`, `What is the meeting password?`, and `Copy the meeting password`; update safety answer copy, localized answers, and diagnostics counts by the actual authored-prompt delta.
2. **Participant roles**: Add answer-only coverage for `Show participant roles`, `List participant roles`, and nearby role/name variants so they do not become Participants panel interrupts or leak roster information.
3. **Caption text**: Add answer-only coverage for `Read caption text`, `Show caption text`, and `Show live caption text`. Caption prompts should not drift to Audio or caption-location behavior when the user asks for text contents.

## Suggested Prompts For Future Subagents

- **Technical scan subagent**: "Inspect RingCentral Video routing for meeting password/passcode prompts, participant-role prompts, and caption-text prompts. Report current entrypoint, `can_operate`, interrupt creation, thin fallback labels, and exact tests to extend. Do not modify files, stage, commit, run the full suite, or touch `.coverage`."
- **Implementation subagent**: "Implement the smallest package/test-only exact Q&A prompt slice from Cycle 164. Add exact prompts to existing privacy Q&A items, update only focused tests and prompt-count expectations that actually change, and avoid runtime matcher changes, broad aliases, `.coverage`, and unrelated docs."
- **Risk/test subagent**: "Review the new exact prompts for alias overlap, stale diagnostics counts, accidental operability, private-value leakage, location-prompt shadowing, and missing no-interrupt assertions. Run only focused tests with coverage disabled."
- **Experience subagent**: "Write a concise docs-only knowledge pack summarizing UX learning, prompt taxonomy, answer-only wording, backlog, and next subagent prompts for the latest privacy hardening slice. Only write the requested handoff file."
