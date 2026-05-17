# Cycle 167 Experience: Caption/Transcript Action Privacy

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Role: Cycle167 experience/knowledge subagent

## Scope

Docs-only knowledge pack for RingCentral Video caption/transcript copy, export,
save, and download privacy. This pass writes only
`docs/agent-handoffs/cycle-167-experience.md`. It did not edit code, tests,
package YAML, staging, commits, `.coverage`, or run the full suite.

## What We Learned

- Caption and transcript text is private meeting content. Copy/export/save/
  download prompts are higher risk than location prompts because they sound like
  irreversible artifact or clipboard actions.
- Current Cycle167 context has concurrent package/test work adding exact action
  prompts such as `Copy captions`, `Export captions`, `Save captions`,
  `Download captions`, and `Download transcript text`. Treat that as other-agent
  work; this document only records experience guidance.
- Safe handling is answer-only: explain the privacy boundary and known discovery
  surfaces, but do not claim a copy, export, save, download, readout, summary, or
  current transcript artifact exists.
- Several caption/live-transcript readout variants are already routing safely by
  matcher guards or token fallback, but should be exact-pinned later so future
  scoring changes do not move them.
- Password/passcode/access-code prompts remain blocked until product evidence
  proves RingCentral Video exposes those values and where.

## Prompt Taxonomy

- **Location/control prompts**: `Where are captions?`, `Can I use live
  transcription?`, `How do I translate captions?`. Explain Notes and Transcript
  or Settings without starting controls or reading content.
- **Live text readout prompts**: `Show caption text`, `Read live caption text`,
  `Read the live transcript text`, `Show transcript text`. Private-content
  shaped; answer-only.
- **Artifact/action prompts**: `Copy captions`, `Can you copy the captions?`,
  `Export captions`, `Save captions`, `Download captions`, `Download transcript
  text`. Treat as private meeting text plus action request; answer-only unless a
  future verified workflow proves safe user intent and product support.
- **Post-meeting artifact prompts**: `Where can I find post-meeting
  transcripts?`, `Can AiPresenter read post-meeting transcripts?`. Keep distinct
  from live-caption/transcript controls.
- **Broad aliases to avoid**: `caption`, `captions`, `copy`, `download`,
  `export`, `save`, `text`, `transcript`, `read`, `show`, `live`. Prefer exact
  Q&A prompts under the existing captions/live transcription privacy answer.

## Operable Vs Answer-Only Rules

- Answer-only for any request to read, show, quote, narrate, summarize, copy,
  export, save, download, or clipboard caption/transcript text.
- Keep `entrypoint_id is None`, `can_operate is False`, and no question
  interrupt for caption/transcript content or artifact-action prompts.
- Operable behavior requires a supported control action, a safe entrypoint, and
  product evidence. Caption/transcript privacy Q&A does not satisfy that bar.
- Do not infer visible caption text, speaker identity, translation state,
  transcript availability, saved file presence, export support, download support,
  or clipboard success from static package evidence.
- Do not add `relatedEntrypointIds`, broad entrypoint aliases, or runtime matcher
  changes for this privacy slice.

## Safe Wording

- Say: "I can explain where caption and transcript controls usually live, but I
  should not read, copy, export, save, or download caption or transcript text
  unless user intent, visible context, and product support are verified."
- Say: "Treat live captions and transcripts as meeting content, not harmless UI
  labels."
- Say: "Use Notes and Transcript for transcript-related discovery and Settings
  for translation-related preferences; do not start or claim content actions from
  Q&A alone."
- Avoid: "Copied", "Exported", "Saved", "Downloaded", "The caption says",
  "Here are the captions", "I verified the transcript", "Started captions", or
  invented/masked speaker text.
- Avoid wrong-route fallback labels for these prompts, especially `Microphone
  control:`, `Meeting information:`, `Notes and transcript:`, and `I could not
  find a matching control`.

## Future Backlog

1. Exact-pin already-safe caption/live-transcript variants under the existing
   captions/live transcription Q&A: `Show caption text`, `Read live captions
   aloud`, `Read live caption text`, `Read the live caption text`, `Read the
   live transcript text`, and `Show transcript text`.
2. Review the concurrent copy/export/save/download prompt slice as action
   privacy, not as simple caption readout. Assert no copied/exported/saved/
   downloaded wording leaks into answers.
3. Gather RingCentral Video product evidence for transcript export, download,
   copy, save, clipboard behavior, and whether live captions produce artifacts.
   Only then decide whether any operable workflow belongs in scope.
4. Keep password/passcode/access-code prompts blocked until product evidence
   confirms RingCentral Video exposes those values in a verified surface. If
   confirmed, update meeting-info privacy copy before adding exact prompts.
5. Add localized variants only after English exact prompts and Q&A count
   expectations are stable.

## Suggested Subagent Prompts

- **Exact-pinning implementer**: "Add only the already-safe exact variants
  `Show caption text`, `Read live captions aloud`, `Read live caption text`,
  `Read the live caption text`, `Read the live transcript text`, and `Show
  transcript text` under the existing RingCentral captions/live transcription
  Q&A. Update focused tests and count assertions only; do not edit runtime
  matcher code, broad aliases, `.coverage`, staging, or commits."
- **Action-privacy verifier**: "Review caption/transcript copy/export/save/
  download prompts. Prove they are answer-only, non-operable, no interrupt, and
  contain no copied/exported/saved/downloaded/readout claims. Use focused checks
  only, with coverage disabled."
- **Product-evidence researcher**: "Collect RingCentral Video evidence for live
  caption artifacts, transcript copy/export/save/download behavior, and
  post-meeting transcript availability. Report evidence and recommended exact
  prompts only; do not implement."
- **Password/passcode researcher**: "Find product/source evidence for whether
  RingCentral Video exposes meeting password, passcode, or access-code values
  and where. If confirmed, recommend meeting-info privacy wording and exact
  prompts; otherwise keep the backlog blocked."
- **Regression scan**: "Check that caption/transcript privacy prompts do not
  steal `Where are Notes and transcript`, microphone, meeting information, or
  post-meeting transcript routes. Report only focused risks and count guidance."
