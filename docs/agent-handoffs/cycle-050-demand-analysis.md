# Cycle 050 Demand Analysis

## Recommended Slice

Add one answer-only RingCentral Video Q&A item for captions, live transcription, and translation.

## User Value

RingCentral package knowledge already covers Notes and Transcript, Recording safety, and Settings as a general configuration area, but users can ask directly about captions, live transcription, translated captions, or live translation. AiPresenter should answer those questions without guessing availability or opening a sensitive panel automatically.

## Acceptance Criteria

- English captions, live transcription, translated captions, and caption-translation questions match the new Q&A.
- Chinese localized questions and answer are included.
- The response is answer-only: `entrypoint_id is None` and `can_operate is False`.
- The answer names Notes and Transcript plus Settings/Translation as discovery surfaces.
- The answer does not claim every feature is available in the current build.
- The answer requires explicit user request and verified visible context before starting notes/transcription/captions/translation or reading caption/transcript text.
- Existing Notes, Recording, Settings, Meeting Info, Host Controls, and no-match behavior remain unchanged.

## Out Of Scope

- No new executable route.
- No locator changes.
- No live RingCentral automation.
- No post-meeting artifact reader.
- No confirmation workflow.
- No broad matcher or safety-policy rewrite.
