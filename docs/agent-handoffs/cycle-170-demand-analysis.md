# Cycle 170 Demand Analysis: Meeting Information And Encryption Status

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Head inspected: `de46eea` (`test: route full screen prompts to views`)
Role: Cycle170 demand-analysis subagent

## Scope

This pass investigates RingCentral Video user need around Meeting information,
encryption, and security-status questions. It writes only this file. It did not
edit code, tests, package YAML, staging, commits, or `.coverage`.

Initial git status caveat: `git status --short` showed ` M .coverage` before
this handoff was written. Final status after concurrent work appeared:

```text
 M .coverage
 M packages/ringcentral-video.yaml
 M tests/unit/test_cli.py
 M tests/unit/test_diagnostics.py
 M tests/unit/test_questions.py
?? docs/agent-handoffs/cycle-170-demand-analysis.md
?? docs/agent-handoffs/cycle-170-risk-scan.md
```

Only `cycle-170-demand-analysis.md` was written by this pass. Treat the
package/test edits and `cycle-170-risk-scan.md` as concurrent other-agent work;
do not revert or overwrite them.

## User Need

Users ask these questions for reassurance, orientation, or urgent privacy
checks during a live meeting. The AI presenter should be useful without turning
static package knowledge into a false security claim or exposing private meeting
values.

- **Participant reassurance**: "Is this meeting encrypted?" The user wants to
  know whether the current meeting is protected. The safe answer points to where
  RingCentral shows encryption/E2EE status and states that AiPresenter cannot
  claim the live status unless the visible signal is verified.
- **Presenter orientation**: "Where can I see encryption?" The user wants the
  control location. The safe answer identifies Meeting information or the E2EE
  status indicator without reading meeting IDs, links, dial-in details, host
  identity, or encryption values.
- **Sensitive panel request**: "Show meeting information." The user may expect
  the info panel to open, but that panel can expose meeting metadata. The safe
  default stays answer-only and explains the panel's purpose unless an approved
  future workflow adds explicit confirmation and redaction.
- **Action-like security request**: "Open encryption settings." The user may be
  asking to configure E2EE, but this can imply settings changes and currently
  routes incorrectly to Background settings. The safe answer should be
  Q&A-first, non-operable, and should not change settings.
- **Host/security control confusion**: "Where are security settings?" This is
  adjacent to lock, waiting room, host controls, and participant permissions.
  Keep it separate from encryption-status work so Meeting information Q&A does
  not become a broad "security" catch-all.

## Product Context

Official RingCentral support distinguishes normal meeting encryption from
end-to-end encryption. The E2EE FAQ says normal video conferencing is protected
in transit, recordings are encrypted at rest, and E2EE is an additional mode for
confidential meetings. It also says E2EE disables dial-in/Call me/Call out,
cloud recording, live transcript, and closed captions, and that meetings secured
by E2EE show a unique lock icon on the bottom left of the window.

Useful references:

- RingCentral E2EE FAQ:
  https://support.ringcentral.com/es/es/shared/content/app/end-to-end-encryption-for-ringcentral-video-faq.html
- RingCentral Meeting settings index:
  https://support.ringcentral.com/ca/en/video/meeting-settings.html
- RingCentral meeting ID reference:
  https://support.ringcentral.com/shared/content/app/using-personal-id-ringcentral-app-desktop-web.html

Repository policy already treats Meeting information as sensitive. The package
purpose for `ringcentral.video.top.meeting-info` includes title, host, meeting
ID, copy link, dial-in info, encryption, and the end-to-end encryption option.
`questionPolicy: answerOnly`, the privacy matrix, and the RingCentral safety
skill all say exact values require explicit user intent and verified visible
context.

## Behavior Probes

Two read-only probes were useful because a concurrent agent appears to have
started the encryption Q&A implementation while this demand handoff was being
written. The "initial" column reflects the pre-concurrent state observed during
this pass; the "current dirty" column reflects the final dirty tree and should
be treated as other-agent work until reviewed.

| Prompt | Initial observation | Current dirty observation | Demand signal |
| --- | --- | --- | --- |
| `Show meeting information` | Meeting information, non-operable, no interrupt, generic `Meeting information:` answer | Same | Still needs explicit privacy/status wording if included in Cycle170. |
| `Where can I see encryption?` | Meeting information generic answer | Meeting information encryption Q&A, non-operable, no interrupt | Dirty work appears to cover this; verify answer quality. |
| `Is this meeting encrypted?` | No match | Meeting information encryption Q&A, non-operable, no interrupt | Dirty work appears to fix the no-match gap. |
| `What is the encryption status?` | Meeting information generic answer | Meeting information encryption Q&A, non-operable, no interrupt | Dirty work appears to improve the route and answer. |
| `Can you verify end-to-end encryption?` | Wrong Leave safety answer | Meeting information encryption Q&A, non-operable, no interrupt | Dirty work appears to fix the `end` token regression. |
| `Open encryption settings` | Wrong Background settings route, operable interrupt | Still wrong Background settings route, operable interrupt | Highest-risk remaining exact prompt. |
| `Read the encryption details` | Meeting-info privacy Q&A | Same | Safe route, but answer still centers IDs/links more than encryption. |
| `Copy the encryption details` | Meeting-info privacy Q&A | Same | Safe route, same wording gap. |
| `Where are security settings?` | Host/participant safety answer | Same | Keep separate from Meeting information encryption. |
| `Change meeting security` | Host/participant safety answer | Same | Separate host/security backlog. |

## Candidate Prompts

Recommended English exact prompts for the next package/test slice:

- `Show meeting information`
- `Open meeting information`
- `Where is meeting information?`
- `Where can I see encryption?`
- `Where is end-to-end encryption?`
- `Is this meeting encrypted?`
- `Is the meeting encrypted?`
- `What is the encryption status?`
- `Can you check encryption status?`
- `Show encryption status`
- `Show meeting encryption status`
- `Is end-to-end encryption on?`
- `Is end-to-end encryption enabled?`
- `Can you verify encryption?`
- `Can you verify end-to-end encryption?`
- `Open encryption settings`
- `Read the encryption details`
- `Copy the encryption details`

Useful localized hints for a later pass:

- zh: `这场会议加密了吗？`, `在哪里看加密状态？`, `显示会议信息`, `端到端加密开了吗？`
- ja: `この会議は暗号化されていますか`, `暗号化状態はどこで確認できますか`, `会議情報を表示して`, `エンドツーエンド暗号化は有効ですか`
- es: `¿Esta reunión está cifrada?`, `¿Dónde puedo ver el cifrado?`, `Mostrar información de la reunión`, `¿Está activado el cifrado de extremo a extremo?`

## Recommended One-Cycle Slice

Finish and review the in-progress English, Q&A-first, answer-only Meeting
information privacy slice rather than expanding into broad security controls.
The dirty tree already appears to add a dedicated encryption-status Q&A item for
several exact prompts; keep that work if it passes review, and close the
remaining exact gaps such as `Open encryption settings`, `Show meeting
information`, `Read the encryption details`, and `Copy the encryption details`.

Do not add broad package-owned aliases such as `encryption`, `security`,
`status`, `settings`, `read`, `copy`, or `details`. Use exact Q&A prompts so the
safety answer wins before entrypoint token fallback.

The safe answer should say, in substance:

> Encryption status is sensitive meeting information. I can point you to the
> Meeting information area or RingCentral's E2EE status indicator, but I should
> not claim this meeting is encrypted, change encryption settings, or read/copy
> exact meeting values unless you explicitly ask and the visible status is
> verified.

Keep `ringcentral.video.top.meeting-info` as the related entrypoint so the
answer can identify the right surface while `questionPolicy: answerOnly`
prevents a queued click. If extending an existing localized Q&A item, update
localized answers semantically; defer localized exact prompt additions unless
tests and diagnostics are updated in the same slice.

## Success Criteria

- All recommended English prompts route to
  `ringcentral.video.top.meeting-info`.
- `can_operate is False` and `create_question_interrupt_step(...) is None` for
  every prompt.
- Answers do not expose, invent, copy, or read meeting IDs, links, dial-in
  numbers, host identity, account details, passcodes, passwords, or encryption
  values.
- Answers do not claim the current meeting is encrypted, unencrypted,
  E2EE-enabled, verified, compliant, or secure from static package data.
- `Can you verify end-to-end encryption?` no longer falls to Leave.
- `Open encryption settings` no longer routes to Background settings or creates
  an interrupt.
- `Show meeting information` and `Where can I see encryption?` get explicit
  privacy/status-verification wording instead of thin generic
  `Meeting information:` fallback.
- Existing full-screen Views routing from Cycle169 remains untouched.
- Host/security prompts such as `Lock the meeting`, `Where are security
  settings?`, and `Change meeting security` remain in the participant/host
  safety lane, not the Meeting information encryption lane.
- Focused question and diagnostics tests account for any Q&A count changes.
- `.coverage` remains untouched and unstaged.

## Backlog

1. Add zh/ja/es exact prompt coverage after the English safety copy and counts
   settle.
2. Capture live/manual evidence for the RingCentral Video E2EE lock/status
   indicator on the current desktop build using a disposable meeting and
   redacted notes.
3. Decide whether "Show/Open meeting information" should ever become a
   confirmed operation. For now, keep answer-only because the panel exposes
   private meeting metadata.
4. Create a separate host/security-status slice for lock state, waiting room,
   admit/remove, and permission controls.
5. Create a separate settings/scheduling slice for enabling or disabling E2EE,
   including feature trade-offs such as captions, transcripts, recording, and
   dial-in availability.
6. Only consider reading or copying exact encryption details after there is a
   confirmation workflow, visible-content verification, and redaction policy.

## Blockers

No blocker for the demand handoff. Live verification of actual encryption state
would require a disposable RingCentral Video meeting with E2EE enabled and a
privacy-safe evidence capture plan.
