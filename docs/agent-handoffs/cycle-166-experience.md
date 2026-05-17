# Cycle 166 Experience: Caption And Transcript Text Privacy

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Role: Cycle166 experience/knowledge subagent

## Scope

Docs-only knowledge pack for RingCentral Video caption, live-caption, live-transcript, and transcript text privacy. This pass only writes `docs/agent-handoffs/cycle-166-experience.md`. It did not edit code, tests, package YAML, `.coverage`, staging, commits, or run the full suite.

## What We Learned

- Caption and transcript text is live meeting content, not ordinary UI chrome. It can expose participant speech, names, customer details, internal topics, health/accessibility context, and other private meeting material.
- Cycle166 scans found that absent exact Q&A prompts can fall through to thin or wrong fallback copy. `Show live caption text` can look like Audio, and `Read captions aloud` can look like Meeting information from clean HEAD.
- The safest narrow fix is exact English Q&A prompts under `Where are captions, live transcription, and translation controls?`; do not add broad entrypoint aliases or runtime matcher changes.
- Current concurrent worktree context already adds `Read caption text`, `Show captions text`, `Show live caption text`, and `Read captions aloud` plus focused tests/count updates. Treat that as other-agent work.
- `Can you read the captions?` remains a high-value future exact prompt because demand analysis observed it routing to meeting-info privacy instead of caption/transcript privacy.

## Prompt Taxonomy

- **Control/location prompts**: `Where are captions?`, `Can I use live transcription?`, `How do I translate captions?`, `Where are translated captions?`. Explain the Notes and Transcript / Settings surfaces; do not read text or claim current state.
- **Caption text readout prompts**: `Read caption text`, `Show caption text`, `Show captions text`, `Show live caption text`, `Read captions aloud`, `Can you read the captions?`. Route to caption/transcript privacy guidance, answer-only.
- **Transcript content prompts**: `Read the transcript`, `Show transcript text`, `Read the live transcript text`, `Summarize the transcript`. Treat as private content unless a future workflow proves explicit intent and visible context.
- **Artifact/action prompts**: `Copy captions`, `Export captions`, `Save transcript`, `Download transcript`. Hold for later; answer copy and product evidence need to distinguish live text, transcript artifacts, downloads, and clipboard/export behavior.
- **Broad aliases to avoid**: `caption`, `captions`, `text`, `live`, `read`, `show`, `copy`, `export`, `transcript`. Use exact Q&A prompts so nearby location/control routes stay intact.

## Operable Vs Answer-Only Rules

- Operable only applies when a prompt asks for a supported control action on a known entrypoint and the package has a safe action path.
- Caption, live-caption, and transcript text requests are answer-only: keep `entrypoint_id is None`, `can_operate is False`, and no question interrupt step.
- Location/discovery prompts may explain where controls live, but should not start notes, transcription, captions, translation, summaries, exports, saves, or clipboard actions from Q&A.
- Any prompt asking to read, show, list, quote, summarize, copy, export, save, announce, or narrate caption/transcript content is private-content shaped.
- Do not claim visible caption text, speaker identity, translation state, transcript availability, or current UI state from static package evidence.

## Safe Wording

- Say: "Caption and transcript controls are usually around Notes and Transcript or Settings, but AiPresenter should not read caption or transcript text unless the user explicitly asks and the visible context is verified."
- Say: "I can explain where to find captions, live transcription, and translation controls; I should not quote, summarize, copy, or export meeting text by default."
- Say: "Treat live captions and transcripts as meeting content, not as harmless labels."
- Avoid: "The caption says...", "Here are the captions...", "I verified the transcript...", "Copied", "Exported", "Saved", "Started captions", or any invented/masked speaker text.
- Avoid fallback labels such as `Microphone control:`, `Meeting information:`, or `I could not find a matching control` for caption-text privacy prompts.

## Future Backlog

1. Add exact prompt coverage for `Show caption text` if user language suggests the singular form is common enough to pin separately. `Can you read the captions?` and `Can you read captions?` landed in the final Cycle166 six-prompt slice.
2. Consider localized caption-text privacy variants only after English exact prompts and count expectations are stable.
3. Expand copy/export/save/download coverage only after product evidence and answer copy clarify whether the target RingCentral build exposes live captions, transcript artifacts, or downloadable transcript files.
4. Add higher-layer checks proving privacy Q&A answers cannot become queued demo steps, speech readouts, clipboard actions, transcript starts, caption starts, or export/save operations.
5. Password/passcode prompts stay blocked until product evidence confirms RingCentral Video exposes password, passcode, or access-code values in Meeting information or another verified surface. If confirmed, update meeting-info privacy answers first, then add exact prompts such as `What is the meeting password?`, `Read the meeting passcode`, and `Copy the meeting passcode`.

## Suggested Subagent Prompts

- **Caption implementation follow-up**: "Review the final Cycle166 caption-text diff. If `Show caption text` still routes to no-match or the wrong privacy boundary and user-language evidence supports it, add it under the existing captions/live transcription Q&A, update only focused tests and actual Q&A count strings, avoid runtime matcher changes, broad aliases, `.coverage`, full-suite runs, staging, and commits."
- **Caption privacy review**: "Verify caption/live-caption/transcript text prompts are answer-only: no entrypoint, no operation, no interrupt, no Audio/Meeting information/no-match fallback text, and no copied/exported/read-aloud private content. Use focused checks with coverage disabled only."
- **Transcript artifact evidence**: "Gather RingCentral Video product evidence for transcript export, download, copy, save, and live-caption artifact behavior. Report evidence and recommended exact prompts only; do not implement without confirmation."
- **Password/passcode evidence**: "Gather product/source evidence for whether RingCentral Video exposes meeting password/passcode/access-code fields and where. If confirmed, recommend safe meeting-info privacy wording and exact prompts; otherwise keep backlog blocked."
- **Localization subagent**: "After English caption-text prompts stabilize, propose localized caption/live-caption/transcript text privacy prompts under the same Q&A item. Keep them exact, answer-only, and count-aware; avoid new entrypoint aliases."
