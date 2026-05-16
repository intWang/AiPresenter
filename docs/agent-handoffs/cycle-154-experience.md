# Cycle 154 Experience: Notes, Transcript, and Captions Answer-Only Slice

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## What This Cycle Learned

- The sharper Cycle 154 user value was not the microphone button alias, even
  though that scan found a real route-quality issue. `Where is the microphone
  button?` currently prefers the audio device menu over the toolbar microphone
  control, but both routes remain non-operable and stay inside the same audio
  neighborhood.
- The notes, transcript, and captions prompts had a more important safety
  boundary. `start meeting notes` could route toward the meeting-start surface,
  `summarize meeting notes` could route to the Notes entrypoint, and `turn on
  captions` could miss entirely. Those are action-like requests around private
  meeting artifacts, so answer-only Q&A was the better first slice.
- Exact Q&A prompts were preferable to entrypoint aliases because this work was
  about refusing to imply action or content access. The intended answer explains
  the Notes and Transcript discovery surface and keeps starting notes,
  transcription, captions, translation, or reading/summarizing content behind
  explicit user request and verified visible context.
- The microphone button alias still looks worthwhile, but it can be a separate
  package-owned alias cycle with a simpler contract: route the explicit button
  wording to `ringcentral.video.toolbar.audio` and keep `can_operate=False`.

## TDD Red and Green

- Red target:
  `tests/unit/test_questions.py::test_ringcentral_english_notes_action_requests_do_not_match_start_meeting`
  should fail for the added prompts before the package Q&A edit because
  `Start meeting notes` does not select the answer-only notes guidance.
- Red target:
  `tests/unit/test_questions.py::test_ringcentral_captions_and_translation_questions_are_answer_only`
  should fail for `Turn on captions` before the package Q&A edit because the
  prompt is not yet part of the curated captions/transcription/translation
  answer-only set.
- Green implementation:
  add exactly these English `localizedQuestions.en` prompts to the existing
  Q&A item `Where are captions, live transcription, and translation controls?`:
  `Start meeting notes`, `Summarize meeting notes`, and `Turn on captions`.
- Green assertions:
  the covered prompts return `entrypoint_id is None`, `can_operate is False`,
  no question interrupt step, answer text mentioning `Notes and Transcript`,
  and boundary language around explicit request plus verified context.
- No runtime matcher change was needed. The final behavior is deterministic
  package Q&A precedence over package-owned entrypoint aliases and token
  scoring.

## Diagnostic Count Learning

- Adding three Q&A prompts changes the durable diagnostics count from 84 to 87.
  Both `qa questions` and `qa alias overlap` count every authored Q&A prompt,
  so the CLI doctor expectation and diagnostics expectation must move together.
- The package-owned alias count remains 156 because this slice intentionally
  added no entrypoint aliases.
- The substring-risk report remains informational and still reports 11 prompts.
  Treat that as reviewed signal, not noise to suppress.
- Count-only assertion edits are legitimate when the added prompts are the
  intended new inventory. They should not be used to relax duplicate, overlap,
  or substring-risk diagnostics.

## Safe Wording

- Say "Adds exact English answer-only Q&A prompts for covered Notes,
  Transcript, and captions action phrasings."
- Say "The prompts route through package Q&A and return `can_operate=False`
  without creating a question interrupt step."
- Say "The answer explains known discovery surfaces and keeps starting notes,
  transcription, captions, translation, reading, or summarizing behind explicit
  request and verified visible context."
- Say "The diagnostic Q&A prompt count increases from 84 to 87 because three
  authored prompts were added."
- Say "This is package-routing evidence, not live RingCentral Video acceptance."
- Avoid "privacy-safe", "recording-safe", "transcript ready", "live-ready",
  "provider validated", "semantic understanding", or any claim that
  AiPresenter can read, summarize, enable, start, stop, record, transcribe, or
  translate meeting artifacts without a separate explicit request and verified
  context.

## Next-Cycle Ideas

- Implement the microphone button alias as its own narrow package/test slice:
  add `microphone button` under `ringcentral.video.toolbar.audio`, assert
  `Where is the microphone button?` selects that entrypoint, and keep
  `can_operate=False` plus no interrupt step.
- Consider a recording answer-only exact-prompt slice. Good candidates to
  evaluate are `Record this meeting`, `Start recording`, `Stop recording`,
  `Are we recording?`, and `Recording status`. Keep the first pass exact and
  answer-only unless a product decision says an entrypoint route is preferred.
- If recording prompts are added, test both action requests and status/location
  requests so the route does not imply consent, host permission, live recording
  state, or transcript/artifact access.
- Keep diagnostics in the loop for every prompt or alias increment: duplicate
  Q&A prompts, unsafe Q&A/alias overlap, substring-risk review, and count
  expectations should all move only when the authored inventory really changes.
