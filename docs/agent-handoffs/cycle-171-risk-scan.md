# Cycle 171 Risk Scan: Meeting Information, Encryption, And Security Prompt Boundaries

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Role: Cycle171 risk-scan handoff

## Scope

This scan reviewed privacy and false-positive risks after Cycle170 around RingCentral Video Meeting information, encryption/security-status Q&A, and action-word prompts.

This pass wrote only:

- `docs/agent-handoffs/cycle-171-risk-scan.md`

This pass did not edit source code, tests, package YAML, profiles, `.coverage`, staging, commits, or package metadata.

## Shared Tree Note

The shared working tree was already dirty before this handoff was written:

- `.coverage`
- `tests/unit/test_questions.py`

Those files were treated as parallel or pre-existing work. Do not revert them from this scan.

By verification time, `git status --short` also showed concurrent dirty edits in:

- `packages/ringcentral-video.yaml`
- `src/ai_presenter/runtime/questions.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_diagnostics.py`

Those files were not edited by this scan and remain out of scope.

## Sources Inspected

- `docs/agent-handoffs/cycle-170-risk-scan.md`
- `docs/agent-handoffs/cycle-170-technical-scan.md`
- `docs/agent-handoffs/cycle-170-technical-development.md`
- `docs/agent-handoffs/cycle-170-post-failure-review.md`
- `docs/agent-handoffs/cycle-170-final-review.md`
- `docs/agent-handoffs/cycle-170-test-review.md`
- `src/ai_presenter/runtime/questions.py`
- `packages/ringcentral-video.yaml`
- `tests/unit/test_questions.py`

Read-only probes were run with `PYTHONDONTWRITEBYTECODE=1` and `python.exe -B`. No pytest was run for this scan.

## Current Behavior Snapshot

Current dirty-tree probes show Cycle170's broad bare-word concern is partly pinned already:

| Prompt | Current route | Operable | Interrupt | Current answer shape |
| --- | --- | --- | --- | --- |
| `status` | none | false | no | no-match |
| `security` | none | false | no | no-match |
| `secure` | none | false | no | no-match |
| `verify` | none | false | no | no-match |
| `meeting security` | `ringcentral.video.top.meeting-info` | false | no | encryption-status Q&A |
| `security status` | `ringcentral.video.top.meeting-info` | false | no | encryption-status Q&A |
| `is the meeting secure?` | `ringcentral.video.top.meeting-info` | false | no | encryption-status Q&A |
| `open encryption settings` | `ringcentral.video.top.meeting-info` | false | no | encryption-status Q&A |
| `share meeting security status` | `ringcentral.video.top.meeting-info` | false | no | encryption-status Q&A |
| `read meeting information` | `ringcentral.video.top.meeting-info` | false | no | meeting-info privacy Q&A |
| `share meeting information` | `ringcentral.video.top.meeting-info` | false | no | meeting-info privacy Q&A |
| `copy meeting information` | `ringcentral.video.top.meeting-info` | false | no | meeting-info privacy Q&A |
| `copy status` | `ringcentral.video.top.meeting-info` | false | no | generic Meeting information answer |
| `copy security` | `ringcentral.video.top.meeting-info` | false | no | generic Meeting information answer |
| `copy secure` | `ringcentral.video.top.meeting-info` | false | no | generic Meeting information answer |
| `copy verify` | `ringcentral.video.top.meeting-info` | false | no | generic Meeting information answer |
| `share secure` | `ringcentral.video.toolbar.share` | false | no | Share answer |
| `share verify` | `ringcentral.video.toolbar.share` | false | no | Share answer |

No probed prompt exposed exact private values or created an interrupt. The remaining risk is wrong-surface answering and future answer-copy drift, not current automatic execution.

## Privacy And False-Positive Matrix

| Prompt family | Privacy risk | False-positive risk | Current posture | Recommended guard |
| --- | --- | --- | --- | --- |
| Bare one-word prompts: `status`, `security`, `secure`, `verify` | Low if no-match; medium if they start returning encryption/security status without enough context. | Medium. Fragment matching can make broad terms attach to the encryption Q&A if future prompt text or matcher logic changes. | Current dirty test pins these to no-match, non-operable, no interrupt. | Keep the bare-word test. Add route snapshots so these never become encryption Q&A through overlap scoring alone. |
| Multi-word security prompts: `security status`, `meeting security`, `is the meeting secure?` | Medium. Users may expect live security state, not a location hint. | Medium. These route to Meeting information encryption Q&A, which is safe but may conflate general security with encryption. | Answer-only Meeting information Q&A; no verified state claim. | Assert answer says where to verify visible status and does not claim secure, encrypted, enabled, disabled, locked, or unlocked. |
| Meeting information location prompts | Medium. The generic entrypoint purpose names meeting title, host, meeting ID, link, dial-in, encryption, and E2EE fields. | Low. Route is expected, but answer wording can become too specific later. | Answer-only entrypoint answer; no exact values. | Assert no exact IDs, URLs, RingCentral domains, phone numbers, host names, or copied/read/dialed claims. |
| Meeting information action prompts: `read`, `share`, `copy` plus meeting link/ID/host/dial-in/details | High. Action words imply exposing private values aloud or into another channel. | Medium. They must stay Q&A-first, not generic entrypoint answers. | Current direct prompts route to privacy Q&A. | Keep exact prompts for `read/share/copy` across meeting ID, link, URL, dial-in, host, details, and information. Assert privacy answer prefix or phrase. |
| Meeting information action prompts with generic objects: `copy status`, `copy security`, `copy verify` | Medium. They currently land on generic Meeting information, which enumerates private field classes. | Medium. The user may be asking to copy a private value or status, but routing does not surface privacy copy. | Non-operable and no interrupt, but generic answer. | Decide expected policy: no-match, privacy Q&A, or encryption Q&A. Add tests so these do not silently remain generic if the wording is considered sensitive. |
| `open` action prompts for encryption/security | Medium. `open` can imply opening a popover that may display IDs, links, host, dial-in, and encryption fields. | Medium. Cycle170 fixed `open encryption settings`; related forms may still drift to settings, app-shell, or generic surfaces. | `open encryption settings` and `open security` route answer-only to encryption Q&A; no interrupt. | Add coverage for `open/show/display security status`, `open meeting security`, and `open meeting information` with explicit no-interrupt assertions. |
| `share` action prompts for security/verification | Medium. "Share" can mean screen sharing or sending sensitive status/details. | High. `share secure` and `share verify` currently route to `ringcentral.video.toolbar.share`, though non-operable. | Wrong-surface answer, no execution. | Add tests for `share secure`, `share verify`, `share security`, `share status`, and `share encryption status`; expected route should not be Share unless the prompt explicitly asks to share screen/content. |
| E2EE and encryption-status prompts | Medium. Answer can overclaim live meeting state. | Medium. Terms like `end-to-end`, `leave`, `off`, `settings`, and `turn off` can collide with Leave or Settings. | Current covered prompts route answer-only to Meeting information. | Keep negative route assertions for Leave, Settings, Background, Share, Network, and RingCentralDevelop. Assert no live-state claim unless visible state is verified. |
| Localized encryption/security prompts | Medium. Localized answers can drift from English guardrails or accidentally include stronger state claims. | Medium. Localized aliases can overlap entrypoint aliases differently than English. | Current tests cover one zh/ja/es localized encryption prompt and privacy assertions. | Expand localized action-word prompts for read/share/open/copy where product demand exists. Keep localized no-URL/no-domain/no-action-claim checks. |
| Tone rendering | Low to medium. Tone wrappers can weaken safety copy or remove caveats. | Low. Tone should not change route or operability. | Sensitive prompt tone matrix includes representative encryption prompts. | Keep tone-invariance checks for route, `can_operate`, interrupt, and privacy phrases. |

## Recommended Regression Tests

Keep and expand the current bare-word guard:

- `status`
- `security`
- `secure`
- `verify`

Expected:

- `entrypoint_id is None`
- `can_operate is False`
- no interrupt
- answer does not start with `Encryption status:`
- answer does not route to Meeting information, Share, Settings, Leave, Network, Participants, or RingCentralDevelop

Add an action-word false-positive test for security/status fragments:

- `share secure`
- `share verify`
- `share security`
- `share status`
- `share encryption status`
- `open security`
- `open status`
- `copy security`
- `copy status`
- `read security`
- `read status`

Expected:

- no interrupt
- `can_operate is False`
- never route to `ringcentral.video.toolbar.share` unless the prompt explicitly says screen sharing
- never route to Settings, Leave, Participants, Network, or RingCentralDevelop
- answer must be either no-match, encryption-status Q&A, or a privacy Q&A per the policy decision; avoid generic Meeting information for copy/read/share forms if those are considered sensitive

Expand Meeting information privacy prompt coverage:

- `Open meeting information`
- `Show meeting information`
- `Display meeting information`
- `Read meeting information`
- `Share meeting information`
- `Copy meeting information`
- `Read meeting ID`
- `Copy meeting ID`
- `Read meeting link`
- `Copy meeting link`
- `Share meeting link`
- `Read dial-in details`
- `Copy dial-in details`
- `Read host information`
- `Copy host information`
- `Share host information`
- `Read encryption details aloud`
- `Copy encryption status`

Expected:

- route to `ringcentral.video.top.meeting-info` or no-match only when intentionally chosen
- `can_operate is False`
- no interrupt
- private-value answer path for read/share/copy variants
- no exact URL, `http://`, `https://`, `www.`, `ringcentral.com`, sample meeting ID, phone-like dial-in, host identity, participant name, or role
- no copied/read/dialed/opened/shared/verified outcome claim

Keep encryption/security-status exact prompt coverage:

- `Is this meeting encrypted?`
- `What is the encryption status?`
- `Can you verify encryption?`
- `Can you verify end-to-end encryption?`
- `Is end-to-end encryption on?`
- `Turn off end-to-end encryption`
- `Leave encryption off`
- `Security status`
- `What is the security status?`
- `Is the meeting secure?`
- `Can you verify meeting security?`
- `Open security tab in RingCentralDevelop`

Expected:

- route to `ringcentral.video.top.meeting-info`
- answer-only, no interrupt
- no live claim that the meeting is encrypted, secure, enabled, disabled, locked, unlocked, or E2EE unless visible status has been verified by an approved path
- no wrong-surface answer prefix such as `Screen sharing:`, `Background settings:`, `Leave meeting:`, `Network quality:`, or `Video tab in RingCentralDevelop:`

Expand localized and tone coverage only after English expectations are settled:

- Add one localized read/share/copy/open prompt per supported language for meeting information privacy.
- Add one localized security-status prompt per supported language.
- Reuse the same no-private-value and no-action-claim assertions.
- Keep diagnostics count updates limited to package Q&A prompt-count changes.

## Acceptance Criteria

- Bare `status`, `security`, `secure`, and `verify` do not route to encryption-status Q&A by substring or token overlap alone.
- Security/encryption status prompts remain answer-only and non-operable.
- No reviewed prompt creates a question interrupt unless the route is intentionally safe and explicitly approved.
- Read/share/copy/open prompts do not expose exact meeting IDs, links, RingCentral URLs, dial-in numbers, host information, participant names, roles, chat, captions, transcripts, notes, recording details, or other private values.
- Answers do not claim that AiPresenter copied, read aloud, dialed, opened, shared, verified, enabled, disabled, locked, unlocked, or changed anything unless an approved visible-state/action path exists.
- Meeting security prompts do not route to Share, Leave, Settings, Background settings, Network quality, Participants, or RingCentralDevelop app-shell routes unless the user explicitly asks for that specific surface.
- Generic Meeting information answers may explain where details live, but read/share/copy variants must prefer privacy Q&A wording.
- Encryption and E2EE answers must say where to verify visible status, not assert live state.
- Localized answers preserve the same privacy and false-positive boundaries as English.
- Tone changes do not change route, `can_operate`, interrupt creation, or required privacy caveats.
- If future Q&A prompts are added, diagnostics and localization counts are updated only for intentional prompt-count changes.
- Focused pytest for question routing passes with coverage disabled and pytest cache disabled.
- `git diff --check` passes for any files touched in a later implementation pass.

## Blockers And Watch Items

- Watch item: `share secure` and `share verify` currently route to `ringcentral.video.toolbar.share`. They are non-operable and create no interrupt, but they are wrong-surface answers for security/verification wording.
- Watch item: `copy status`, `copy security`, `copy secure`, `copy verify`, and `copy meeting security` currently route to the generic Meeting information answer. This does not expose exact values today, but it enumerates sensitive field classes and should be policy-pinned before future answer-copy changes.
- Watch item: broad multi-word security prompts currently use the encryption-status Q&A. That is safe if the intent is encryption verification, but it can under-answer broader host/security-control questions.
- No blocker prevented writing this handoff.
