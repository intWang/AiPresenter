# Cycle 161 Risk Scan: RingCentral Video Invite Link Privacy Prompts

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Scope

Documentation-only risk scan for the proposed Cycle161 RingCentral Video
invite/link/privacy prompt slice. Per instruction, this scan did not stage,
commit, reset, or edit source/package/test/runtime files.

Proposed prompt surface:

- `Copy meeting link`
- `Read the invite link`
- `Invite John`
- `Send the invite`
- `Who can I invite?`
- `Can you read the meeting ID?`

Only this handoff file was written.

## Current Evidence

The six proposed exact English prompts are not currently present as exact
package Q&A prompts or unit-test parameters. Current routing is driven by
existing meeting-info aliases, invite aliases, token scoring, `answerOnly`
policy, and risky-word gating.

Direct runtime probe for the six prompts:

```text
Copy meeting link | entrypoint=ringcentral.video.top.meeting-info | can_operate=False | interrupt=False
Read the invite link | entrypoint=ringcentral.video.toolbar.invite | can_operate=False | interrupt=False
Invite John | entrypoint=ringcentral.video.toolbar.invite | can_operate=False | interrupt=False
Send the invite | entrypoint=ringcentral.video.toolbar.invite | can_operate=False | interrupt=False
Who can I invite? | entrypoint=ringcentral.video.toolbar.invite | can_operate=False | interrupt=False
Can you read the meeting ID? | entrypoint=ringcentral.video.top.meeting-info | can_operate=False | interrupt=False
```

Current package/runtime safety anchors:

- `ringcentral.video.top.meeting-info` is `questionPolicy: answerOnly`.
- `ringcentral.video.toolbar.invite` contains the risky term `invite`, so
  `_can_operate` returns `False` even though the entrypoint has `openSteps`.
- `create_question_interrupt_step(package, response)` returns `None` whenever
  `can_operate=False`.
- Existing package notes say meeting IDs, links, dial-in details, invite links,
  names, emails, and suggestions are sensitive by default.

Focused verification command:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests/unit/test_questions.py::test_meeting_info_privacy_questions_are_answer_only tests/unit/test_questions.py::test_invite_people_prefers_invite_entrypoint tests/unit/test_questions.py::test_bring_people_into_meeting_matches_invite_package_qa tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package
```

Result: `12 passed`.

Doctor output currently reports:

```text
[OK] question aliases: 157 package-owned aliases have no cross-entrypoint duplicates
[OK] qa questions: 124 Q&A question prompts have no cross-item duplicates
[OK] qa alias overlap: 124 Q&A question prompts have no unsafe package-owned alias overlaps
[INFO] qa alias substring risk: 11 Q&A question prompts contain package-owned alias substrings outside related entrypoints
Doctor completed: 11 ok, 1 info, 0 warnings, 0 failed.
```

## Safety Assessment

No current evidence that these prompts copy a meeting link, read a meeting ID,
read an invite link, send an invite, type a name, select a suggestion, expose a
participant, or queue a UI interrupt.

The current behavior is safe at the operation layer because every proposed
prompt returns `can_operate=False` and no interrupt. The weaker area is answer
specificity: current fallback answers are generic entrypoint answers such as
`Invite participants: Invite coworkers or copy meeting details.` They are safe,
but they do not explicitly say "I will not copy/send/read that from an offline
package route." A future exact-QA slice can improve the user-facing answer
without adding operability.

## Risks Found

### Medium: Command-Shaped Prompts Must Stay Answer-Only

`Copy meeting link`, `Send the invite`, and `Invite John` are imperative
prompts. Do not let exact prompt coverage become a UI automation path. The
correct behavior is a text answer that explains the invite/meeting-info area
and confirms no private link, meeting ID, contact, or invite was copied, read,
typed, selected, or sent.

### Medium: Explicit Read Requests Still Need Visible-Context Verification

`Read the invite link` and `Can you read the meeting ID?` sound explicit, but
the package question path does not verify a live visible value. Do not read or
invent a link/ID from package content, logs, clipboard, OCR, UIA text, or prior
state. A safe answer can say where the value appears and that exact values
require explicit user intent plus verified visible context.

### Medium: Private Names And Suggestions

`Invite John` includes a person name. Do not echo arbitrary names into
narration as if a contact exists, type the name into a search box, select a
suggestion, read suggestions aloud, or infer who is eligible to invite. `Who
can I invite?` should answer at workflow/policy level only, not enumerate
contacts, emails, participants, domains, suggestions, or roles.

### Low: Exact Prompt Coverage Is Not Yet Present

The current runtime already routes safely, but these six prompts are not exact
Q&A/test cases. If Cycle161 implements the prompt slice, add focused tests that
assert:

- expected entrypoint is invite or meeting-info;
- `can_operate is False`;
- `create_question_interrupt_step(...) is None`;
- answer text contains no `https://`, `ringcentral.com`, numeric meeting ID,
  email address, copied/sent/read success claim, or `John` confirmation.

### Low: Counts And Alias Diagnostics Need Updating If Prompts Are Added

Current diagnostics are at `124` Q&A prompts. Adding these six as English
localized questions on existing related Q&A items should move Q&A prompt counts
to `130`. Update `tests/unit/test_diagnostics.py` and `tests/unit/test_cli.py`
count expectations if the package changes. Package-owned alias count should
remain `157` if no entrypoint aliases are added.

Keep alias scope exact. Do not add broad aliases such as `copy`, `read`,
`send`, `John`, `link`, `meeting`, `meeting ID`, `invite link`, or `who` as
package-owned entrypoint aliases. Exact Q&A prompts are safer than widening the
entrypoint alias layer.

## What Not To Change

- Do not add live RingCentral automation for these prompts.
- Do not add or modify `openSteps`.
- Do not make invite, copy-link, send-invite, or read-value prompts operable.
- Do not touch clipboard APIs, type into invite search, press `Copy meeting
  link`, press `Invite`, or select contact suggestions.
- Do not read private invite links, meeting IDs, emails, names, suggestions,
  participant rosters, chat, clipboard contents, or dial-in details.
- Do not claim a link was copied, an invite was sent, a contact was found, or a
  meeting ID/link was verified.
- Do not add live RingCentral acceptance claims from package/unit evidence.

## Recommended Acceptance

Before the main agent commits a Cycle161 package/test change, verify:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests/unit/test_questions.py tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
```

Expected after adding six exact prompts:

- all six proposed prompts route deterministically;
- all six return `can_operate=False`;
- all six produce no question interrupt;
- no answer contains a real-looking URL, `ringcentral.com`, email address,
  numeric meeting ID, contact confirmation, or copied/sent/read success claim;
- doctor reports `130 Q&A question prompts` for duplicate and alias-overlap
  checks;
- package-owned alias count remains unchanged unless the implementation
  intentionally changes entrypoint aliases.

## Handoff Note

This risk-scan agent only inspected the current package/tests/runtime behavior
and wrote this document. It did not run `git add`, `git commit`, or `git reset`.
