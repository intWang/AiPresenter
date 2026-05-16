# Cycle 107 Implementation Handoff

## Scope

Cycle 107 hardens English and Japanese Notes/Transcript action and content prompts so they prefer an explicit safety answer instead of incidental entrypoint matching.

No package YAML, alias, Q&A, demo route, or localization count changed.

## Implementation

Added a runtime-only matcher in `src/ai_presenter/runtime/questions.py`.

The matcher runs inside Q&A matching after the existing recording safety matcher and before title/entrypoint fallback. It requires both:

- A Notes/Transcript subject term, such as `Start notes`, `Transcript`, Japanese notes, Japanese transcription, minutes, or meeting memo wording.
- An action/content term, such as click, press, start, read, summarize, content, copy, save, export, create, or show in English or Japanese.

When both are present, the matcher returns the existing captions/transcription safety Q&A. That Q&A has no related entrypoint, so responses have:

- `entrypoint_id is None`
- `can_operate is False`
- no question interrupt step

## Fixed Residual Routes

Before implementation:

- `Start notes` plus Japanese click/press wording could associate with `ringcentral.develop.video.start`.
- `Transcript` plus Japanese summarize/read wording could associate with `ringcentral.video.more.notes`.
- Some Japanese content prompts fell through to no-match instead of a useful safety answer.

After implementation:

- Notes action prompts return the existing Notes/Transcript safety answer and do not match Start meeting.
- Transcript content prompts return the same safety answer and do not identify the Notes panel.
- Legitimate `start meeting` prompts still match `ringcentral.develop.video.start`.
- Cycle 106 Notes location aliases still match `ringcentral.video.more.notes` and remain answer-only.

## Red-Green Evidence

Red phase:

- Focused command returned `6 failed, 4 passed`.
- Failures showed the two unsafe route classes and confirmed the two guard classes already passed.

Green phase:

- Same focused command returned `10 passed`.

Review follow-up:

- Review found blocking undercoverage for English `Start notes`, `Click Start notes`, `Summarize the transcript`, and `Read the transcript`.
- Added English red tests; focused command returned `4 failed, 10 passed`.
- Added English action/content terms to the same subject+action matcher.
- Focused command returned `14 passed`.

Re-review follow-up:

- Re-review found a non-blocking `show me where...` overmatch risk.
- Added a red test for `Show me where Notes and Transcript is` as a location lookup.
- Added a location-intent exclusion for `where`, `location`, Japanese where/place, and entrance wording.
- Focused command returned `5 passed`, preserving transcript content safety and Notes location routes.

## Expected Counts

All counts should stay at the Cycle 106 baseline:

- Japanese aliases: `13/27` entrypoints and `34` aliases.
- Package-owned aliases: `87`.
- Q&A prompts: `71`.
- Q&A substring risk: INFO at `11`.

## Next Risk Item

Chinese content prompts can still associate with Notes in some cases, but they remain non-operable. Consider a later multilingual route-classification pass if product demand needs cleaner answer semantics outside English and Japanese.
