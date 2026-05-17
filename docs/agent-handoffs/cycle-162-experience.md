# Cycle 162 Experience: Meeting And Invite Link Variants

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## What This Cycle Learned

- Safe fallback routing is not the same as authored coverage. If a private-link
  prompt reaches a safe Q&A through token overlap, the runtime may stay
  non-operable, but the package inventory and tests do not clearly document the
  intended privacy boundary.
- Meeting links, invite links, meeting URLs, clipboard-like copy/paste requests,
  and read-aloud requests belong in explicit answer-only privacy Q&A coverage
  when they are exact high-risk variants.
- Thin entrypoint labels are mechanically safe but experientially weak for
  private-link commands. A response like `Meeting information:` or
  `Invite participants:` does not explain why AiPresenter should avoid copying,
  pasting, reading, exposing, or sending private meeting access details.
- Clipboard and speech verbs are side-effect-shaped even when handled by Q&A.
  Tests should keep proving that these prompts do not touch the clipboard, paste
  into any target, read aloud a real value, queue UI actions, or claim success.
- Count hygiene is part of the implementation, not follow-up cleanup. Exact
  authored Q&A prompt additions, Q&A item additions, localized coverage, and
  package-owned entrypoint aliases are different counted units.

## Authored Coverage Beats Accidental Safety

- `Copy the invite link` is the sharpest lesson from this cycle. It can route
  safely through overlap with `Read the invite link`, but that makes the safety
  boundary implicit and fragile.
- Prefer adding high-risk exact variants to the focused Q&A item that owns the
  answer. That makes doctor output, tests, handoffs, and future reviews agree on
  why the prompt is protected.
- Do not solve this by adding broad aliases such as `copy`, `paste`, `read`,
  `link`, `URL`, `meeting`, or `invite`. Exact prompts are enough for this
  privacy slice and are less likely to steal ordinary location or control
  lookup intents.
- Keep the distinction from Cycle 161: meeting-info value prompts belong with
  `ringcentral.video.top.meeting-info`; invite action and invite-link prompts
  belong with `ringcentral.video.toolbar.invite`, unless a future cycle
  deliberately documents a different routing contract.

## Guard Clipboard, Paste, And Read-Aloud Variants

- `Can you copy the meeting link?`, `Copy the meeting URL`, and
  `Copy the invite link` must not press `Copy meeting link`, call clipboard
  APIs, inspect clipboard state, or say a link was copied.
- `Can you paste the meeting link?` must not read clipboard contents, paste into
  chat, paste into invite search, paste into notes, or imply clipboard contents
  are known.
- `Read the meeting link aloud` must not speak, synthesize, paraphrase, redact,
  summarize, or invent a private URL, meeting ID, dial-in detail, host detail,
  invite text, or clipboard value.
- These prompts should remain answer-only, `can_operate is False`, and
  `create_question_interrupt_step(package, response) is None`.
- Negative answer assertions matter. Guard against `https://`,
  `ringcentral.com`, email addresses, numeric meeting IDs, copied/pasted/read
  success claims, invite-sent claims, and coworker or directory verification.

## Avoid Thin Labels For Private Links

- A private-link command needs privacy guidance, not just a control label. The
  user should hear that meeting and invite links are sensitive access details
  and that AiPresenter will not expose or move exact values from package Q&A
  alone.
- Generic entrypoint fallback text is still useful for ordinary lookup prompts
  such as `where is the meeting link` or `how do I invite people`. Preserve that
  behavior while making exact copy/paste/read variants Q&A-first.
- Tests should assert both the positive answer family and the negative fallback
  boundary. A non-operable thin label can still be the wrong user experience.
- Do not claim live RingCentral validation from package tests. The evidence here
  proves package routing, answer text, non-operability, and no interrupt; it
  does not prove UI contents, clipboard state, speech output, invite delivery,
  or directory membership.

## Count Synchronization

- Before updating counts, identify the unit that changed:
  - new exact English Q&A prompts;
  - new Q&A items;
  - new localized prompts or answers;
  - package-owned entrypoint aliases.
- Cycle 162's meeting-link variants increased authored Q&A prompt inventory.
  Any explicit `Copy the invite link` Q&A addition should increase that same
  prompt count again.
- Package-owned alias counts should not change unless entrypoint aliases change.
  Do not bump alias totals for Q&A-only prompt strings.
- Keep `doctor`, diagnostics tests, CLI expectations, and material-package tests
  synchronized with the actual package inventory. Avoid count churn by
  intuition.
- Document whether a prompt is explicit authored coverage or only safe through
  fallback/overlap. That distinction affects both count expectations and future
  review confidence.

## Candidate Next-Cycle Gaps

- Add higher-layer presenter/session coverage proving these private-link Q&A
  responses cannot become queued demo steps, live interrupts, clipboard actions,
  paste actions, speech actions, or invite sends.
- Audit adjacent private meeting access prompts: passcodes, dial-in numbers,
  host details, waiting-room state, copied link state, encryption details, and
  meeting-lock status.
- Review participant-list and directory-adjacent prompts separately. Invite
  safety should not become permission to read coworker suggestions, names,
  emails, domains, roles, recipient lists, attendee lists, or eligibility.
- Add localized exact prompt coverage only after mapping intent per locale.
  Translation should preserve the privacy action boundary for copy, paste,
  read-aloud, URL, link, and invite wording.
- If future product work wants operable invite or copy-link behavior, split it
  into a separate confirmed workflow with visible context verification, exact
  recipient or target review, cancellation behavior, final confirmation, and
  live acceptance evidence.

## Safe Wording To Preserve

- "Meeting links, meeting URLs, and meeting IDs are sensitive access details, so
  AiPresenter should not copy, paste, read aloud, or expose exact values from
  package Q&A alone."
- "Invite links and invite actions are private: AiPresenter should not inspect
  suggestions, read names or emails, copy links, paste values, or send invites
  without verified visible context and explicit confirmation."
- "Exact privacy-shaped Q&A prompts should beat thin entrypoint fallback labels,
  while ordinary location questions should keep normal control lookup behavior."
- "These prompts are answer-only, non-operable, and should not create a question
  interrupt step."
- "Synchronize counts with the actual inventory changed; authored Q&A prompts,
  Q&A items, localized coverage, and package-owned aliases are not the same
  unit."
