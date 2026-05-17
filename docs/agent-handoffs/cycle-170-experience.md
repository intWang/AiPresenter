# Cycle 170 Experience: Meeting Information, Encryption, And Security Status

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Head inspected: `de46eea`
Role: Cycle170 experience/knowledge subagent

## Scope

Docs-only handoff for RingCentral Video Meeting information, encryption/E2EE,
and security-status routing. This pass writes only
`docs/agent-handoffs/cycle-170-experience.md`. It did not edit code, tests,
package YAML, `.coverage`, staging, or commits.

The tree is shared. Current dirty files such as `.coverage`,
`packages/ringcentral-video.yaml`, `tests/unit/test_cli.py`,
`tests/unit/test_diagnostics.py`, `tests/unit/test_material_packages.py`, and
`tests/unit/test_questions.py` are other-agent work and must not be reverted.

## Core Lesson

Visible encryption and E2EE status belongs in the Meeting information privacy
lane, with answer-only guidance that points the user to the Meeting information
area or RingCentral's visible E2EE status indicator. AiPresenter may explain
where status is shown, but must not claim the live meeting is encrypted,
unencrypted, secure, insecure, E2EE-enabled, enabled, disabled, locked, or
unlocked unless a separate approved visible-state verification path proves it.

Keep `ringcentral.video.top.meeting-info` as the related entrypoint for
encryption-status Q&A. The route can name the surface, but `can_operate` should
stay false and no question interrupt should be created by default.

## False-Positive Hazards

- Do not route `Open encryption settings` to Background settings. That opens
  the wrong settings surface and can create an unsafe operable interrupt.
- Do not route `Share meeting security status` or similar prompts to Share.
  The user is asking about status, not screen sharing.
- Do not let `end-to-end` or `leave encryption off` fall into Leave. "End" and
  "leave" can be status/configuration words here, not meeting-exit intent.
- Do not route `Open security tab in RingCentralDevelop` to the
  RingCentralDevelop Video tab. App-shell navigation is not a security-status
  answer.
- Avoid broad aliases like `encryption`, `security`, `settings`, `status`,
  `read`, `copy`, or `details`. Use exact Q&A prompts so the safety answer wins
  before token fallback.

## Privacy Boundaries

Meeting information can expose meeting title, host identity, meeting ID, links,
dial-in details, account context, passcodes, passwords, and encryption details.
Default behavior may explain where those values live, but must not read, copy,
paste, expose, or invent exact values.

Encryption/security status is verified-state information. A static package
answer is allowed to say where to verify the visible indicator; it is not
allowed to assert the current meeting's state. Host/security controls such as
lock meeting, waiting room, admit/remove, and permission changes are separate
role-gated surfaces and remain answer-only unless a future confirmed workflow
owns side effects and recovery.

## Localized Prompt Treatment

Localized prompts should preserve the same safety semantics as English:
answer-only, Meeting information related, no interrupt, no live-state claim, and
no exact private-value disclosure. Localized Q&A text is package-local content,
not evidence of runtime voice support or live acceptance.

When localized prompts are added, keep them with the matching safety Q&A item
and update diagnostics/localization counts in the same implementation slice.
Do not use localized titles, purposes, or aliases to broaden matcher behavior
for security/settings/status words.

## Future Backlog

1. Close the remaining exact false positives: `Open encryption settings`,
   `Show encryption settings`, `Change encryption settings`,
   `Turn off end-to-end encryption`, `Leave encryption off`,
   `Share meeting security status`, and `Open security tab in
   RingCentralDevelop`.
2. Add a separate security-status Q&A slice for `Security status`,
   `What is the security status?`, `Is the meeting secure?`, and
   `Can you verify meeting security?` Keep it answer-only and separate from
   host-control operations.
3. Capture live visible-state evidence in a disposable RingCentral Video
   meeting with E2EE enabled. Record build, locale, DPI, window bounds, visible
   lock/status labels, and redacted notes. Prefer UIA/window metadata first;
   use screenshots only with a privacy review path.
4. Only consider reading or copying exact encryption details after explicit
   confirmation, verified visible content, redaction rules, and recovery policy
   exist.
5. Keep diagnostics counts synchronized with the final package inventory after
   any Q&A prompt additions.

## Blockers

- Live encryption/E2EE state cannot be truthfully verified from static package
  data; it needs a disposable live meeting and privacy-safe evidence capture.
- Existing concurrent package/test work must be reviewed before implementation
  agents edit the same files.
- Security-status prompts still need a dedicated answer-only decision so they
  do not no-match or drift into Share, Leave, Background settings, or
  RingCentralDevelop routes.
