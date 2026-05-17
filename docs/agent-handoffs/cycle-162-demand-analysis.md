# Cycle 162 Demand Analysis: Meeting Link Copy, Paste, URL, And Read Variants

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Decision

Recommendation: make the next smallest high-value RingCentral Video increment
an exact English Q&A slice for meeting-link copy/read/paste variants and the
remaining invite-link copy phrasing.

This should be a narrow package/test-only follow-up to Cycle 161. Cycle 161
added privacy guidance for invite links, meeting IDs, coworker invites, and send
invite prompts, but review evidence called out a residual gap:
`Can you copy the meeting link?` still returned thin `Meeting information:`
fallback text in a direct probe. The next user-need slice is to close that exact
phrasing and cover the closest copy/read/send wording variants without making
any meeting-link, invite-link, clipboard, paste, or send-invite action operable.

## Current Evidence

The relevant surfaces are already present:

- `ringcentral.video.top.meeting-info` exposes meeting details, meeting ID,
  meeting link, copy link, dial-in info, encryption, and meeting lock. It has
  `questionPolicy: answerOnly`.
- `ringcentral.video.toolbar.invite` opens the Invite participants dialog and
  notes that it can include search, suggestions, Copy meeting link, Cancel, and
  Invite controls.
- Cycle 161 test review verified that `Copy meeting link` and
  `Can you read the meeting ID?` were protected by the new meeting-info privacy
  Q&A, while invite prompts such as `Read the invite link`, `Invite John`,
  `Send the invite`, and `Who can I invite?` were protected by invite privacy
  Q&A.
- The same review explicitly noted that `Can you copy the meeting link?` was
  not covered by the dirty diff and still returned thin meeting-info fallback
  text.

That residual gap is not an operability issue: the prompt still stays
non-operable and no-interrupt. The issue is answer quality and privacy framing.
The user asks for a clipboard-like action, and AiPresenter should answer with
the meeting-link privacy boundary instead of generic entrypoint text.

## Recommended Exact Prompts

Cover exactly these English prompts:

- `Can you copy the meeting link?`
- `Copy the invite link`
- `Copy the meeting URL`
- `Can you paste the meeting link?`
- `Read the meeting link aloud`

If the implementation discovers that some of these are already covered in the
current branch, keep the tests and package aliases aligned and treat Cycle 162
as the smallest exact-prompt cleanup for any still-missing aliases in this set.

## Expected Behavior

For `Can you copy the meeting link?`:

- Return the meeting ID/link privacy answer, not thin `Meeting information:`
  fallback text.
- Prefer `entrypoint_id == ringcentral.video.top.meeting-info`.
- Keep `can_operate is False`.
- Ensure `create_question_interrupt_step(package, response) is None`.
- Do not open Meeting information, click Copy meeting link, touch the
  clipboard, or claim the meeting link was copied.

For `Copy the meeting URL`:

- Treat `URL` as equivalent to a meeting link for privacy purposes.
- Return the meeting ID/link privacy answer associated with
  `ringcentral.video.top.meeting-info`.
- Keep the response non-operable and no-interrupt.
- Do not read, invent, mask, summarize, validate, copy, or send an actual URL.

For `Can you paste the meeting link?`:

- Return meeting-link privacy guidance, not a clipboard or paste workflow.
- Keep the response non-operable and no-interrupt.
- Do not inspect clipboard contents, paste into chat, paste into invite search,
  or claim any clipboard content is available.

For `Read the meeting link aloud`:

- Return meeting-link privacy guidance.
- Keep the response non-operable and no-interrupt.
- Do not read aloud, invent, partially redact, or paraphrase a meeting link,
  meeting ID, dial-in number, host name, or invite text.

For `Copy the invite link`:

- Return invite-link privacy guidance associated with
  `ringcentral.video.toolbar.invite`, unless the implementation deliberately
  routes all exact link-copy prompts through the meeting-info privacy Q&A and
  documents that choice in tests.
- Keep `can_operate is False`.
- Ensure no question interrupt step is created.
- Do not click Invite, Copy meeting link, Cancel, Invite, search fields,
  coworker suggestions, names, emails, or recipient controls.
- Do not claim an invite link was copied, visible, verified, safe, pasted, or
  sent.

## What To Avoid

- Do not make copy-link, invite-link, meeting-URL, paste-link, read-link, or
  send-invite prompts operable.
- Do not add or change `openSteps`.
- Do not click Meeting information, Invite, Add coworkers, Copy meeting link,
  Cancel, Invite, search fields, coworker suggestions, names, emails, dial-in
  controls, chat, or any paste target from these question prompts.
- Do not read, invent, redact, summarize, paraphrase, validate, copy, paste, or
  send actual meeting links, invite links, meeting URLs, meeting IDs, dial-in
  numbers, host names, invite text, clipboard contents, coworker names, email
  addresses, suggestions, or recipient lists.
- Do not claim a link was copied, a URL was pasted, a meeting link was read
  aloud, an invite was sent, a coworker was found, or a directory result was
  verified.
- Do not add broad aliases such as `copy`, `read`, `paste`, `send`, `invite`,
  `link`, `URL`, `meeting`, `ID`, `clipboard`, `coworker`, or `people`.
- Do not combine this with participant-list reading, chat, screen sharing,
  recording, notes, transcript, captions, microphone, camera, reactions, raise
  hand, leave/end, runtime matcher changes, clipboard integration, OCR,
  provider calls, or live RingCentral acceptance work.
- Do not update acceptance evidence or claim live RingCentral Video validation.
- Do not touch `.coverage` or unrelated dirty files.

## Implementation Handoff Prompt

```text
Cycle162 implementation task. You are not alone in the repo; do not revert
other workers' edits and do not touch `.coverage` or unrelated dirty files.

Repository: C:\Users\rcadmin\Documents\Repos\AiPresenter

Goal: implement the smallest exact English RingCentral Video Q&A cleanup for
meeting-link copy/read/paste variants and invite-link copy phrasing, so these
prompts return privacy-focused answer-only guidance instead of thin entrypoint
fallback text.

Read first:
- docs/agent-handoffs/cycle-162-demand-analysis.md
- docs/agent-handoffs/cycle-161-test-review.md
- packages/ringcentral-video.yaml around
  `ringcentral.video.top.meeting-info`,
  `ringcentral.video.toolbar.invite`, and the Q&A items for invite privacy and
  meeting ID/link privacy
- tests/unit/test_questions.py around the RingCentral invite privacy and
  meeting-info privacy question tests
- tests/unit/test_diagnostics.py, tests/unit/test_cli.py, and
  tests/unit/test_material_packages.py only if prompt inventory counts need
  updates

Scope:
- Package/test-only change.
- Cover exactly these English prompts:
  - `Can you copy the meeting link?`
  - `Copy the invite link`
  - `Copy the meeting URL`
  - `Can you paste the meeting link?`
  - `Read the meeting link aloud`
- Prefer exact English Q&A aliases on the existing focused answer-only package
  Q&A items.
- Prefer meeting-link/URL/paste/read-aloud prompts to route to
  `ringcentral.video.top.meeting-info`.
- Prefer `Copy the invite link` to route to
  `ringcentral.video.toolbar.invite`, unless tests deliberately encode a
  documented choice to handle all link-copy variants through meeting-info
  privacy guidance.
- Keep every response non-operable.
- Ensure `create_question_interrupt_step(package, response) is None` for every
  covered prompt.
- Ensure answers mention the privacy boundary for meeting links, invite links,
  meeting URLs, meeting IDs, clipboard-like copy/paste requests, and reading
  links aloud.
- Preserve existing location-style behavior for prompts such as `where is the
  meeting ID`, `where is the meeting link`, `invite people`, and `how do I
  bring people into the meeting`.
- Update diagnostics or doctor count expectations only for the exact authored
  Q&A prompt inventory change.

Do not:
- Edit runtime matcher source, package models, session interrupt logic,
  providers, profiles, README, runbooks, existing handoff docs, or acceptance
  evidence.
- Make copy-link, invite-link, meeting-URL, paste-link, read-link, or
  send-invite prompts operable.
- Add or change `openSteps`.
- Click or queue Meeting information, Invite, Add coworkers, Copy meeting link,
  Cancel, Invite, search fields, coworker suggestions, names, emails, dial-in
  controls, chat, or any paste target from these question prompts.
- Read, invent, redact, summarize, paraphrase, validate, copy, paste, or send
  actual meeting links, invite links, meeting URLs, meeting IDs, dial-in
  numbers, host names, invite text, clipboard contents, coworker names, email
  addresses, suggestions, or recipient lists.
- Claim a link was copied, a URL was pasted, a meeting link was read aloud, an
  invite was sent, a coworker was found, or a directory result was verified.
- Add broad aliases such as `copy`, `read`, `paste`, `send`, `invite`, `link`,
  `URL`, `meeting`, `ID`, `clipboard`, `coworker`, or `people`.
- Combine this with participant-list reading, chat, screen sharing, recording,
  notes, transcript, captions, microphone, camera, reactions, raise hand,
  leave/end, runtime matcher changes, clipboard integration, OCR, provider
  calls, or live RingCentral acceptance work.
- Touch `.coverage`.

Acceptance:
- All five exact prompts return privacy-focused answer-only guidance, not thin
  `Meeting information:` or `Invite participants:` fallback text.
- `Can you copy the meeting link?`, `Copy the meeting URL`,
  `Can you paste the meeting link?`, and `Read the meeting link aloud` remain
  non-operable, route to meeting-info privacy guidance, and do not claim any
  link, URL, ID, dial-in detail, host detail, clipboard value, paste target, or
  read-aloud action was verified or completed.
- `Copy the invite link` remains non-operable, routes to invite privacy guidance
  unless intentionally documented otherwise, and does not claim any invite link,
  coworker, suggestion, email, recipient, clipboard value, or sent-invite state
  was verified.
- `create_question_interrupt_step(package, response) is None` for all five
  prompts.
- Existing Cycle 161 invite, send-invite, meeting-ID, and location-style
  question behavior is preserved.
- Diagnostics remain green, with count expectations updated only for the exact
  authored prompt inventory change.
- Final diff excludes `.coverage`, runtime source, profiles, README,
  acceptance evidence, and unrelated tests.
```
