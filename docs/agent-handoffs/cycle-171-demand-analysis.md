# Cycle 171 Demand Analysis: Broad Status And Meeting Information Requests

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Head inspected: `a3fc826` (`test: route encryption status prompts safely`)
Role: Cycle171 demand-analysis subagent

## Scope

This pass investigates the next RingCentral Video user need after Cycle170:
short/broad `status`, `security`, `secure`, and `verify` prompts, plus Meeting
information surface requests such as `Show meeting information`, `Open meeting
information`, and `Read meeting information`.

This pass writes only this file. It did not edit code, tests, package YAML,
`.coverage`, staging, or commits.

Initial git status caveat:

```text
 M .coverage
 M tests/unit/test_questions.py
```

Those changes were already present and were left untouched. The dirty
`tests/unit/test_questions.py` diff appears to add candidate coverage for bare
status/security words and additional Meeting information privacy prompts; treat
that as concurrent other-agent work, not as an edit from this pass.

Final verification caveat: by the end of this pass, additional concurrent
changes were visible in package/runtime/test files and other Cycle171 handoffs.
They were not edited by this pass and should be reviewed independently.

## Context From Cycle170

Cycle170 added a safe answer-only encryption/security-status Q&A tied to
`ringcentral.video.top.meeting-info`. That Q&A covers prompts such as
`Is this meeting encrypted?`, `Open encryption settings`, `Security status`,
`Is the meeting secure?`, and `Can you verify meeting security?`.

The answer points users to Meeting information for visible encryption and
end-to-end encryption status, but it does not claim the live meeting is
encrypted, enabled, disabled, verified, compliant, or secure.

Important existing constraints:

- `ringcentral.video.top.meeting-info` has `questionPolicy: answerOnly`.
- Meeting information can expose title, host, meeting ID, link, dial-in,
  encryption, and end-to-end encryption details.
- `presenter/skills/ringcentral-safety.md` says Meeting information is private:
  summarize purpose unless exact values are requested and visible content is
  verified.
- Runtime broad-fragment guard currently treats `secure`, `security`, `status`,
  and `verify` as too broad for Q&A fragment matching.

## Current Behavior Probes

Read-only probes were run with `PYTHONDONTWRITEBYTECODE=1` and
`.venv\Scripts\python.exe -B`. No tests were run and no bytecode/cache files
were written intentionally.

| Prompt | Current route | Current answer shape | Demand signal |
| --- | --- | --- | --- |
| `status` | no match | generic no-match | Safe, but not useful when a user asks urgently. |
| `security` | no match | generic no-match | Safe, but misses a common reassurance prompt. |
| `secure` | no match | generic no-match | Safe, but misses a shorthand security prompt. |
| `verify` | no match | generic no-match | Safe, but misses a shorthand verification prompt. |
| `meeting status` | no match | generic no-match | Useful next exact prompt; should not become a live-status claim. |
| `Show meeting status` | no match | generic no-match | Same as above. |
| `Open meeting status` | no match | generic no-match | Same as above; avoid creating an operation. |
| `What is the meeting status?` | Meeting information | encryption-status Q&A | Safe, but narrows "meeting status" to encryption. |
| `Can you verify the meeting?` | Meeting information | encryption-status Q&A | Safe, but broad verification is treated as encryption. |
| `Show meeting information` | Meeting information | thin entrypoint answer | Non-operable, but it names private fields without a strong boundary. |
| `Open meeting information` | Meeting information | thin entrypoint answer | Non-operable, but could sound like opening a private panel is accepted. |
| `Read meeting information` | Meeting information | meeting-info privacy Q&A | Good privacy boundary; keep this behavior. |
| `meeting information` | Meeting information | meeting-info privacy Q&A in current runtime | Safe; current dirty tests may still be settling expected copy here. |
| `Open security` | Meeting information | encryption-status Q&A | Non-operable, but semantically surprising; watch for fragment drift. |
| `Security status` | Meeting information | encryption-status Q&A | Good Cycle170 behavior. |

## User Need Scenarios

1. **Urgent reassurance**

   A user says `status`, `security`, `secure`, `verify`, or `meeting status`
   during a live meeting. They likely want reassurance, but the request is too
   broad to answer truthfully from static package data. A useful response should
   orient them to safe choices: connection health, Meeting information, visible
   encryption/E2EE status, participants, or host/security controls.

2. **Security confidence without security claims**

   A user asks `Is the meeting secure?`, `Can you verify meeting security?`, or
   `Security status`. Cycle170 already sends these to the encryption-status Q&A.
   The next cycle should preserve that safety while avoiding a broader claim
   that the meeting is secure, locked, compliant, authenticated, or protected.

3. **Meeting information surface request**

   A user says `Show meeting information` or `Open meeting information`. They
   may want orientation, not values. The current entrypoint answer is safe from
   operations, but it should state the privacy boundary before naming or
   summarizing the panel contents.

4. **Meeting information value request**

   A user says `Read meeting information`, `Copy meeting details`, or asks for
   the host, ID, link, or dial-in number. Existing privacy Q&A is the right lane:
   answer-only, no exact values, no copying, no reading aloud unless explicit
   user intent and visible verification exist.

5. **Ambiguous security operation**

   A user says `Open security`, `secure this meeting`, or `verify the meeting`.
   These should not become host/security operations, settings changes, or
   live-state assertions. They should either ask for specificity or point to
   the safe explanation route.

## Candidate Approaches

### Recommended: exact disambiguation plus Meeting information privacy copy

Add a narrow answer-only disambiguation path for ambiguous status/security
phrases, and improve Meeting information surface-copy so show/open/read
requests get useful privacy-aware guidance.

This is the best one-cycle slice because it improves the examples users are
actually likely to say while keeping every response non-operable and
non-assertive about live security state.

Implementation shape for the next cycle:

- Add or update package Q&A copy for Meeting information surface requests so
  `Show meeting information`, `Open meeting information`, and `Read meeting
  information` all produce privacy-aware guidance instead of a thin entrypoint
  fallback.
- Add a small ambiguous status/security answer that says AiPresenter can help
  locate status surfaces, but cannot verify or claim live meeting security from
  static package data.
- If exact one-word prompts are added as Q&A prompts, first adjust the runtime
  matcher so one-word broad Q&A candidates such as `status` or `security` do
  not substring-match longer prompts like `open security`, `security settings`,
  or unrelated status requests.
- Keep `questionPolicy: answerOnly`, `can_operate=False`, and no question
  interrupt for every prompt in this slice.

### Alternative: leave bare words as no-match

This is safest mechanically and aligns with the current broad-fragment guard,
but it is less useful. A generic no-match for `status` or `security` gives no
help to a user who is asking a reasonable meeting-safety question.

### Rejected: broad aliases or live verification

Do not add package-owned aliases such as `status`, `security`, `secure`,
`verify`, `read`, `copy`, or `details` to an entrypoint. Do not open Meeting
information by default. Do not claim the current meeting is secure, encrypted,
or verified unless a separate approved visible-state verification workflow
exists.

## Recommended One-Cycle Slice

Name: **Ambiguous status and Meeting information privacy answers**

Goal: Replace unhelpful no-match and thin Meeting information responses with
answer-only guidance that is useful, privacy-aware, and explicit about the
limits of static package knowledge.

Recommended prompt groups:

- Broad exact prompts:
  - `status`
  - `security`
  - `secure`
  - `verify`
  - `meeting status`
  - `show meeting status`
  - `open meeting status`
  - `what is the meeting status?`
  - `can you verify the meeting?`
- Meeting information surface prompts:
  - `Show meeting information`
  - `Open meeting information`
  - `Read meeting information`
  - `Show meeting details`
  - `Open meeting details`
  - `Read meeting details`
  - `Show meeting info`
  - `Open meeting info`
  - `Read meeting info`
- Regression prompts to preserve Cycle170:
  - `Security status`
  - `What is the security status?`
  - `Is the meeting secure?`
  - `Can you verify meeting security?`
  - `Open encryption settings`
  - `Show encryption settings`
  - `Change encryption settings`
  - `Leave encryption off`

Suggested broad-status answer substance:

```text
Meeting status can mean different things: connection health, Meeting
information, visible encryption/E2EE status, participants, or host/security
controls. I can point you to the right area, but I should not claim the live
meeting is secure, encrypted, or verified unless the visible status is checked.
```

Suggested Meeting information answer substance:

```text
Meeting information is the top-left meeting details area. It can show private
details such as title, host, meeting ID, link, dial-in information, encryption,
and end-to-end encryption status. I can explain where it is and what it is for,
but should not open, read, copy, or expose exact values unless you explicitly
ask and the visible content is verified.
```

## Privacy Boundaries

- Do not expose meeting IDs, links, dial-in numbers, host identity, passcodes,
  account details, participant names, roles, chat, transcripts, notes, or
  recording contents.
- Do not read or copy exact Meeting information values unless explicit user
  intent and visible-content verification exist.
- Do not claim live security, encryption, E2EE, lock state, compliance,
  authentication, or privacy status from package text.
- Do not click/open Meeting information by default in response to `show` or
  `open`; keep this cycle answer-only.
- Do not change encryption, security, participant, host, recording, transcript,
  or settings state.
- Do not collapse host/security controls into Meeting information. Lock,
  waiting room, admit/remove, mute, and participant permissions remain a
  separate host/security-control lane.

## Success Criteria

- `status`, `security`, `secure`, `verify`, `meeting status`,
  `show meeting status`, `open meeting status`, `what is the meeting status?`,
  and `can you verify the meeting?` return a helpful answer-only
  disambiguation, not the generic no-match string.
- The broad-status answer has `can_operate=False`, creates no interrupt, and
  does not route to Share, Participants, Leave, Network quality, Background
  settings, More settings, RingCentralDevelop, or any host/security operation.
- The broad-status answer does not claim the meeting is secure, encrypted,
  verified, locked, unlocked, compliant, enabled, or disabled.
- `Show meeting information`, `Open meeting information`, and
  `Read meeting information` route to `ringcentral.video.top.meeting-info`,
  stay `can_operate=False`, and create no interrupt.
- Meeting information answers include a privacy boundary and do not use the
  thin `Meeting information:` entrypoint fallback for show/open/read prompts.
- Meeting information answers do not include URLs, RingCentral domains,
  sample meeting IDs, copied values, host names, dial-in numbers, or exact
  encryption values.
- Cycle170 encryption/security-status prompts continue to return the
  `Encryption status:` answer and remain non-operable.
- `Open encryption settings`, `Show encryption settings`, `Change encryption
  settings`, and `Leave encryption off` remain answer-only Meeting information
  guidance, not settings, background, or leave operations.
- Existing controls remain reachable: `network quality` still routes to Network
  quality, `participants` still routes according to existing participant policy,
  and `recording status` still uses recording safety guidance.
- If one-word Q&A prompts are introduced, tests prove they do not shadow longer
  prompts through substring matching.
- Diagnostics/localization counts are updated intentionally if package Q&A
  inventory changes.
- `.coverage` remains untouched and unstaged.

## Backlog

1. Add zh/ja/es exact prompt coverage once English behavior and diagnostics
   settle.
2. Decide whether `Show/Open meeting information` should ever become a
   confirmed operation. Keep it answer-only until there is a redaction and
   confirmation workflow.
3. Create a separate live Meeting information verification workflow using a
   disposable meeting and redacted evidence before reading or summarizing exact
   visible values.
4. Create a separate host/security-control slice for lock state, waiting room,
   admit/remove, participant permissions, and security settings.
5. Create a separate connection-health/status slice for Network quality,
   device status, and meeting health, so `meeting status` does not remain
   overloaded with encryption guidance.
6. Review whether `_BROAD_QA_FRAGMENT_TOKENS` should support exact-only broad
   Q&A prompts without substring drift.
7. Add negative-route probes for ambiguous prompts such as `Open security`,
   `Show security`, `secure this meeting`, and `verify meeting settings`.

## Blockers

No blocker for this demand handoff.

Implementation of exact one-word `status`, `security`, `secure`, or `verify`
Q&A prompts should not proceed until the matcher behavior for one-word Q&A
candidates is reviewed. Exact matching is useful, but substring matching from
one-word candidates could otherwise steal longer security/settings prompts.
