# Cycle 169 Experience: Local Layout, Full-Screen, And Views Routing

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Role: Cycle169 experience/knowledge subagent

## Scope

Docs-only knowledge pack for RingCentral Video local layout, full-screen wording,
and `Views` menu routing. This pass writes only
`docs/agent-handoffs/cycle-169-experience.md`. It did not edit code, tests,
package YAML, staging, commits, `.coverage`, or run the full suite.

Observed concurrent dirty work remains owned by other agents:
`packages/ringcentral-video.yaml`, `tests/unit/test_questions.py`,
`tests/unit/test_diagnostics.py`, `tests/unit/test_cli.py`, and Cycle169 scan
handoffs.

## What We Learned

- Full-screen prompts are local layout/view prompts, not screen-sharing prompts.
  They should route to `ringcentral.video.top.views`.
- The safe behavior is to open the `Views` layout menu only. Do not select the
  Full screen option or claim the meeting entered full-screen mode.
- `screen` is an unsafe broad token. Broad aliases can steal `Share screen`,
  system-audio, and screen-description Q&A prompts.
- Current Cycle169 scans observed good routing for prompts such as `Show full
  screen`, `Switch to full screen`, `Where is full screen?`, and `Full screen
  view`, while `Go full screen` and `Enter full screen mode` remained important
  variants to decide and verify.
- Diagnostics count strings must follow the final package inventory. Do not
  hard-code old alias counts after full-screen aliases are added or removed.

## Prompt Taxonomy

- **Views layout prompts**: `Switch to gallery view`, `Change meeting layout`,
  `Can you open views?`. Operable route to `ringcentral.video.top.views`.
- **Full-screen layout prompts**: `Show full screen`, `Switch to full screen`,
  `Where is full screen?`, `Full screen view`, possible variants `Go full
  screen` and `Enter full screen mode`. Route to `Views`, not Share.
- **Screen-share prompts**: `Share screen`, `Share my screen`, `Can you share
  system audio?`, `Share computer audio`. Keep screen-sharing safety Q&A,
  non-operable, no interrupt.
- **Meeting information prompts**: meeting ID, link, host, dial-in, encryption
  details. Answer-only unless future verified visible context supports exact
  value handling.
- **Security/host prompts**: lock/unlock, host controls, meeting security.
  Separate answer-only host-control slice; do not mix with Views routing.

## Operable Vs Answer-Only Rules

- Operable: local layout/view navigation that only opens the `Views` menu and
  has Escape cleanup.
- Not operable: any prompt that asks to share screen/system audio, read private
  meeting information, verify encryption status, change host/security controls,
  or report live state from static package data.
- A full-screen question interrupt may open `Views`; it must not queue a second
  click that selects Full screen.
- Full-screen answers should start from `View layout menu:` and should not fall
  back to `Screen sharing:`.
- Keep runtime matcher logic out of this slice. Exact package prompts/tests are
  safer than global matching changes.

## Safe Wording

- Say: "View layout menu: open Views to choose layout options such as gallery or
  full screen."
- Say: "I can open the layout menu, but I should not claim the layout changed
  unless the visible state is verified."
- Avoid: "I switched to full screen", "entered full screen", "full screen is
  on", "changed your layout", or "started sharing the screen."
- Avoid broad aliases: `screen`, `show screen`, `display`, `share screen`,
  `status`, `settings`, or `security` for this slice.

## Future Backlog

1. Decide whether `Go full screen` and `Enter full screen mode` should be exact
   Views aliases, then verify they do not regress screen-sharing prompts.
2. Add live/manual acceptance for the `Views` coordinate route across bounds,
   DPI, narrow window, and actual full-screen variants before upgrading
   confidence beyond repo-tested.
3. Implement encryption-status Q&A separately under Meeting information privacy:
   `What is the encryption status?`, `Is this meeting encrypted?`, `Can you
   verify end-to-end encryption?`, and `Open encryption settings` should remain
   answer-only and must not claim live encryption state.
4. Exact-pin `Read the encryption details` and `Copy the encryption details`
   only if reviewers want prompt-level coverage beyond answer-copy updates.
5. Keep password, passcode, and access-code prompts blocked until product or
   runtime evidence proves RingCentral Video exposes those values and where.
6. Keep localized full-screen/encryption variants for a later pass after English
   routing, answer wording, and diagnostic counts are stable.

## Suggested Subagent Prompts

- **Full-screen implementer**: "Finish only RingCentral Video full-screen layout
  routing. Route exact full-screen prompts to `ringcentral.video.top.views`, open
  only the Views menu, preserve screen-share Q&A, and do not touch encryption,
  host/security Q&A, `.coverage`, staging, commits, or full-suite runs."
- **Views verifier**: "Verify full-screen and layout prompts route to Views,
  create only a Views-menu interrupt with Escape cleanup, avoid completed-action
  wording, and keep `Share screen` and system-audio prompts answer-only."
- **Diagnostics verifier**: "Recompute package-owned alias and Q&A counts after
  the final full-screen alias inventory. Update only stale count assertions; do
  not change package behavior."
- **Encryption Q&A subagent**: "Handle encryption-status and encryption-detail
  prompts only under Meeting information privacy. Keep them answer-only,
  non-operable, no interrupt, and do not claim live encryption state."
- **Evidence researcher**: "Gather live/product evidence for full-screen Views
  coordinates, encryption detail surfaces, and password/passcode/access-code
  exposure. Report evidence and recommended exact prompts only; do not
  implement."
