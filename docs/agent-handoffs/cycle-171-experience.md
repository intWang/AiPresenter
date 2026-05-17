# Cycle 171 Experience: Broad Tokens And Privacy Boundaries

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Head inspected: `a3fc826`
Role: Cycle171 experience handoff subagent

## Scope

Docs-only handoff for RingCentral Video broad status/security prompts, Meeting
information privacy prompts, and share/copy false-positive boundaries. This
pass writes only:

- `docs/agent-handoffs/cycle-171-experience.md`

It did not edit code, tests, package YAML, `.coverage`, staging, or commits.

The shared tree was already active. Observed pre-existing or concurrent dirty
work included `.coverage`, `packages/ringcentral-video.yaml`,
`src/ai_presenter/runtime/questions.py`, `tests/unit/test_cli.py`,
`tests/unit/test_diagnostics.py`, `tests/unit/test_questions.py`, and the
untracked Cycle171 demand/risk/technical handoffs. Do not revert those from
this experience pass.

## Core Lessons

### One-word broad tokens should not become Q&A prompts

Bare prompts such as `status`, `security`, `secure`, and `verify` are too broad
to safely become normal Q&A prompt fragments. They can mean connection health,
recording state, encryption status, host/security controls, app verification,
or a general reassurance request. A static package answer must not turn those
one-word tokens into a claim that the live meeting is secure, encrypted,
verified, enabled, disabled, locked, or unlocked.

Current Cycle171 technical work adds a broad-fragment guard for these terms.
Keep that posture unless a future matcher can prove exact-only handling for
bare one-word prompts. If product wants helpful bare-word behavior, prefer an
exact disambiguation answer that says status can mean several things and asks
or points to the right surface. Do not let the bare word substring-match longer
requests such as `share secure`, `open security`, `security settings`,
`recording status`, or `copy status`.

### Exact action-like Meeting information prompts belong in privacy Q&A

Prompts that look like actions against Meeting information should be handled by
the Meeting information privacy Q&A, not by a generic entrypoint answer and not
by an operation. This includes exact forms around `read`, `copy`, `share`,
`show`, `open`, or `display` combined with Meeting information, meeting
details, meeting info, meeting ID, meeting link, dial-in details, host
information, or encryption details.

The safe answer shape is answer-only, `ringcentral.video.top.meeting-info`
related, `can_operate=False`, and no question interrupt. It may explain that
Meeting information is the top-left meeting details area and that it can
contain private values. It must not open the panel, read aloud, copy, share,
paste, expose, summarize exact values, or imply that it already verified the
visible content.

### Exact share/copy security or status prompts need security-status guidance

Prompts such as `share meeting security status`, `copy encryption status`,
`share security`, `share status`, `share secure`, `share verify`,
`copy security`, or `copy status` should not fall into the Share toolbar just
because they start with `share`. They also should not receive a generic Meeting
information answer if the user is asking about security/status content.

The safer lane is answer-only encryption/security-status guidance tied to
Meeting information, or an explicit privacy Q&A where the object is a private
Meeting information value. The answer should say where the user can verify the
visible encryption or end-to-end encryption status, while avoiding any live
security claim. It should not say AiPresenter shared, copied, verified,
enabled, disabled, locked, unlocked, secured, or changed anything.

## Matcher Fragment Risks

Future subagents should treat broad matcher fragments as a sharp edge. A single
short Q&A prompt can steal unrelated longer prompts through substring,
fragment, or token-overlap scoring. The risky terms in this slice are:

- `status`
- `security`
- `secure`
- `verify`
- action words such as `read`, `copy`, `share`, `show`, and `open`

Do not add those as package-owned aliases or broad Q&A fragments for
RingCentral Video without negative-route tests. If exact one-word prompts are
introduced, the matcher must distinguish exact user text from fragment matches
inside longer prompts. Keep tests for no interrupt, `can_operate=False`, no
wrong-surface prefix, and no route to Share, Leave, Settings, Background
settings, Network quality, Participants, or RingCentralDevelop unless the user
explicitly asked for that exact surface.

## RingCentral Video Privacy Boundaries

Meeting information is private by default. It can expose meeting title, host
identity, meeting ID, invite link, dial-in numbers, passcodes or passwords,
account context, encryption details, and end-to-end encryption status. Exact
values should not be read, copied, shared, pasted, summarized, or invented
unless the user explicitly asks, visible content is verified, and a privacy-safe
redaction/recovery path exists.

Encryption, E2EE, and security status are verified-state information. Static
package text can explain where the visible status appears, but it cannot assert
the current meeting's security state. Host/security controls such as lock
meeting, waiting room, admit/remove, participant permissions, and security
settings are separate role-gated areas. Do not collapse them into Meeting
information answers unless a future owned workflow explicitly covers the side
effects and recovery policy.

## Suggested Regression Prompts

Keep these prompt groups pinned before accepting further routing changes:

- Bare broad words: `status`, `security`, `secure`, `verify`
- Status/security action forms: `share secure`, `share verify`,
  `share security`, `share status`, `copy security`, `copy status`,
  `read security`, `read status`, `open security`, `open status`
- Meeting information privacy forms: `Read meeting information`,
  `Copy meeting information`, `Share meeting information`,
  `Read meeting info aloud`, `Copy meeting details`, `Share meeting details`,
  `Read meeting ID`, `Copy meeting link`, `Read dial-in details`,
  `Copy host information`, `Copy encryption status`
- Cycle170 security prompts: `Security status`,
  `What is the security status?`, `Is the meeting secure?`,
  `Can you verify meeting security?`, `Open encryption settings`,
  `Show encryption settings`, `Change encryption settings`,
  `Leave encryption off`, `Share meeting security status`,
  `Open security tab in RingCentralDevelop`

Expected behavior stays answer-only, non-operable, and no interrupt. Security
answers should locate visible status instead of claiming state. Privacy answers
should avoid exact IDs, links, domains, host names, phone-like dial-in strings,
participant names, roles, or any copied/read/shared/opened outcome claim.

## Guidance For Future Subagents

Start by checking the current dirty tree and the other Cycle171 handoffs. The
implementation files are shared with other agents, so coordinate ownership
before touching `questions.py`, `packages/ringcentral-video.yaml`, diagnostics,
CLI counts, or question tests.

When changing package Q&A prompt text, update diagnostics/CLI prompt counts only
for intentional inventory changes. When changing matcher behavior, add focused
negative tests for broad fragments before adding positive Q&A prompts. When
changing answer copy, check that tone rendering does not weaken the privacy
boundary or remove the no-live-state caveat.

## Blockers

No blocker prevented writing this handoff.

Implementation blockers remain:

- Exact bare-word answers for `status`, `security`, `secure`, and `verify`
  need exact-only matcher protection before they can safely be package Q&A
  prompts.
- Share/copy status and security prompts need an explicit product policy so
  they do not drift into the Share toolbar or generic Meeting information copy.
- Reading, copying, or verifying exact Meeting information values requires a
  separate visible-content verification and privacy/redaction workflow.
- Concurrent dirty implementation files must be owned before a follow-up agent
  edits code, tests, package YAML, or `.coverage`.
