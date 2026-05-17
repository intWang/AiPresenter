# Cycle 161 Experience: Invite, Link, And Meeting ID Privacy

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## What This Cycle Learned

- Invite privacy has two nearby but distinct risks. Sending or selecting an
  invite recipient is an action privacy problem; reading, copying, or exposing a
  meeting link or meeting ID is a value privacy problem. Keep the answers and
  related entrypoints separate so each boundary stays crisp.
- Exact prompt Q&A-first routing is the right tool for this slice. The risky
  prompts should be answered by package Q&A before thin entrypoint fallback text
  can win, while still staying non-operable and no-interrupt.
- Thin entrypoint labels are safe mechanically, but weak experientially. For
  prompts like `Copy meeting link`, `Read the invite link`, or `Invite John`, a
  generic "Meeting information" or "Invite participants" answer hides the
  privacy boundary the user needs to hear.
- Count hygiene needs to follow the counted unit. Adding English exact prompts
  to existing Q&A items is different from adding new localized Q&A items, and
  diagnostics, CLI expectations, and localization-status tests may count those
  differently.
- The current evidence is package and unit-test evidence. It proves Q&A route,
  entrypoint association, non-operability, and no interrupt creation; it does
  not prove live RingCentral Video values, clipboard state, coworker directory
  contents, or invite delivery behavior.

## Separate The Two Privacy Boundaries

- Meeting-info value prompts belong with
  `ringcentral.video.top.meeting-info`. Examples include `Copy meeting link`,
  `Can you copy the meeting link?`, and `Can you read the meeting ID?`.
- These prompts should say meeting links, IDs, dial-in details, and host details
  are sensitive access information. AiPresenter should not copy, read aloud,
  invent, expose, or claim to verify those values from package routing alone.
- Invite action prompts belong with `ringcentral.video.toolbar.invite`. Examples
  include `Read the invite link`, `Invite John`, `Send the invite`, and
  `Who can I invite?`.
- These prompts should say AiPresenter should not type names or emails, inspect
  suggestions, select coworkers, read invite links, or send invites unless a
  later confirmed workflow verifies visible context and the user explicitly
  approves the exact action.
- Avoid collapsing both risks into one broad "invite" answer unless a future
  cycle deliberately retests meeting-info value prompts and accepts the route
  tradeoff.

## Guard Against Thin Entrypoint Labels

- The dangerous regression is not only accidental clicking. A non-operable
  answer can still be too thin if it sounds like ordinary location help for a
  command-shaped privacy request.
- Tests should assert that privacy Q&A answer text is returned and that generic
  entrypoint fallback labels are absent for the covered exact prompts.
- Preserve location-style behavior for ordinary lookup questions such as where
  to find meeting information or invite controls. The privacy answer should win
  for exact read/copy/send/search-shaped prompts, not for every mention of
  `invite`, `link`, or `meeting ID`.
- Do not add broad aliases like `copy`, `read`, `send`, `invite`, `link`, `ID`,
  `meeting`, `John`, or `who`. Exact prompts avoid stealing unrelated meeting
  control or location intents.

## Verification Lessons

- For each exact prompt, verify four properties together:
  - expected entrypoint association;
  - `can_operate is False`;
  - Q&A privacy answer text is returned before entrypoint fallback text;
  - `create_question_interrupt_step(package, response) is None`.
- Also verify the negative content boundary. Answers should not contain or
  imply a real URL, meeting ID, email address, coworker confirmation, copied
  state, read state, sent state, or directory verification.
- Focused tests with `--no-cov` are useful for this repo because partial pytest
  selections can otherwise fail on the repo-wide coverage gate even when the
  selected behavior passes.
- Do not claim live RingCentral acceptance from these tests. Package Q&A cannot
  prove what the Invite dialog shows, what is on the clipboard, who exists in a
  directory, or whether an invitation was sent.

## Count Synchronization

- First decide whether the implementation added a new Q&A item, new English
  exact prompts on an existing item, or new localized prompt/answer coverage.
  Those are different inventory changes.
- Keep diagnostics and doctor expectations synchronized with authored Q&A
  prompt counts when exact prompts are added.
- Keep localization-status expectations synchronized with Q&A item coverage
  when new Q&A items are added or localized answers change.
- If prompts are already present on existing Q&A items, counts may be unchanged
  for this cycle. Document that explicitly so the next agent does not update
  counts by intuition.

## Candidate Next-Cycle Gaps

- Add higher-layer presenter/session coverage proving invite and meeting-info
  privacy Q&A responses cannot become queued demo steps or live interrupt
  actions.
- Review adjacent private-value prompts for dial-in details, host information,
  passcodes, waiting-room status, and copied clipboard contents with the same
  exact-prompt Q&A-first boundary.
- Review participant-list and directory-adjacent questions separately. `Who can
  I invite?` should not become a path to reading coworker suggestions, emails,
  attendee lists, roles, domains, or policy-derived eligibility.
- Audit localized invite/link/meeting-ID privacy prompts only after deciding
  intent per locale. Translation should preserve the privacy boundary, not just
  substitute words for `copy`, `read`, `send`, or `invite`.
- If a future operable invite workflow is planned, scope it as a separate
  consented product slice with visible dialog verification, recipient review,
  final confirmation, cancellation behavior, and live acceptance evidence.

## Safe Wording To Preserve

- "Meeting links and meeting IDs are sensitive meeting access details, so
  AiPresenter should not copy, read aloud, or expose exact values from package
  Q&A alone."
- "Invite actions are separate from meeting-info values: searching coworkers,
  selecting suggestions, typing names or emails, and sending invitations require
  explicit confirmation and verified visible context."
- "These prompts are answer-only, non-operable, and should not create a question
  interrupt step."
- "Exact Q&A prompts should beat thin entrypoint labels for privacy-shaped
  commands, while broad location questions should keep their normal control
  lookup behavior."
- "Synchronize counts with the actual inventory changed: exact authored prompts,
  Q&A items, and localized coverage are not the same unit."
