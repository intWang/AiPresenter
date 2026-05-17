# Cycle 162 Risk Scan: Meeting Link Copy/Paste/Read Variants

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Scope

Documentation-only risk scan for the proposed Cycle162 RingCentral Video
meeting/invite link prompt variants. Per instruction, this scan did not stage,
commit, reset, or edit source/package/test/runtime files.

Proposed prompt surface:

- `Can you copy the meeting link?`
- `Copy the invite link`
- `Copy the meeting URL`
- `Can you paste the meeting link?`
- `Read the meeting link aloud`

Only this handoff file was written.

## Current Evidence

Current package/test coverage already includes these five exact English prompts:

- `packages/ringcentral-video.yaml` includes `Copy the invite link` under the
  invite privacy Q&A and the four meeting-link variants under the meeting
  ID/link privacy Q&A.
- `tests/unit/test_questions.py` includes focused parametrized assertions for
  invite privacy prompts and meeting-info privacy prompts.

Runtime probe, executed with `PYTHONPATH=src` so the workspace runtime was used:

```text
Can you copy the meeting link? | entrypoint=ringcentral.video.top.meeting-info | can_operate=False | interrupt=False
Copy the invite link | entrypoint=ringcentral.video.toolbar.invite | can_operate=False | interrupt=False
Copy the meeting URL | entrypoint=ringcentral.video.top.meeting-info | can_operate=False | interrupt=False
Can you paste the meeting link? | entrypoint=ringcentral.video.top.meeting-info | can_operate=False | interrupt=False
Read the meeting link aloud | entrypoint=ringcentral.video.top.meeting-info | can_operate=False | interrupt=False
```

Focused question tests:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests/unit/test_questions.py::test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first tests/unit/test_questions.py::test_ringcentral_english_invite_privacy_questions_stay_qa_first
```

Result: `11 passed`.

Doctor output currently reports:

```text
[OK] question aliases: 157 package-owned aliases have no cross-entrypoint duplicates
[OK] qa questions: 138 Q&A question prompts have no cross-item duplicates
[OK] qa alias overlap: 138 Q&A question prompts have no unsafe package-owned alias overlaps
[INFO] qa alias substring risk: 11 Q&A question prompts contain package-owned alias substrings outside related entrypoints
Doctor completed: 11 ok, 1 info, 0 warnings, 0 failed.
```

## Safety Assessment

The current runtime behavior is safe at the operation layer for this prompt
slice. Each prompt resolves to a privacy Q&A or sensitive entrypoint, returns
`can_operate=False`, and does not create a question interrupt.

The current answers are also privacy-oriented:

- meeting-link variants say meeting IDs and links are private details and
  should not be copied, read aloud, or exposed unless explicitly requested and
  visible content is verified;
- `Copy the invite link` says not to read private invite links, names, emails,
  or suggestions, and not to send invites unless explicitly requested and
  visible content is verified.

No current evidence shows clipboard reads/writes, paste operations, speech of a
real link, UI automation, invite sending, contact selection, or live meeting
state changes for these prompts.

## Risks Found

### Medium: Clipboard And Paste Semantics Must Stay Out Of Q&A

`copy` and `paste` are command-shaped words. Treat them as privacy Q&A prompts,
not as permission to touch the OS clipboard, press `Copy meeting link`, paste
into chat/email/notes, or inspect clipboard contents. A safe answer can explain
the boundary, but must not claim the link was copied or pasted.

### Medium: Reading Aloud Is A Speech Side Effect

`Read the meeting link aloud` sounds explicit, but the package route has no
verified visible value and should not synthesize or speak a private URL from
package text, clipboard data, OCR, UIA, logs, or memory. Reading exact links
aloud needs a separate visible-context verification and confirmation flow,
outside this Q&A-only path.

### Medium: Private Link Values Must Never Appear In Answers Or Logs

Keep assertions that answers contain no `https://`, `ringcentral.com`, email
address, numeric meeting ID, dial-in detail, host identity, copied/pasted
success claim, or invite-sent claim. Logging in `runtime.questions` currently
omits raw question text, which is good; do not add raw prompt/link logging while
working this area.

### Medium: No Interrupt Is The Critical Runtime Guard

`entrypoint_id` alone is not permission. The important invariant is:
`can_operate=False` and `create_question_interrupt_step(...) is None` for all
five prompts. Keep this explicit in tests because future alias changes could
still identify meeting-info or invite surfaces while accidentally queuing a UI
step.

### Low: Duplicate Q&A And Alias Overlap Checks Are Healthy

Doctor reports no duplicate package-owned aliases, no duplicate Q&A prompts,
and no unsafe Q&A alias overlap at the current `138` prompt count. The existing
INFO-level substring risk remains `11` prompts and is not introduced by this
slice.

### Low: Count Assertions Are Currently Stale

Focused diagnostics tests currently fail because expected Q&A prompt counts
still say `134`, while package/runtime diagnostics report `138`.

Observed failure:

```text
tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package
expected 134 Q&A question prompts, got 138

tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package
expected 134 Q&A question prompts, got 138
```

`tests/unit/test_cli.py` also contains `134` expectations for doctor output.
Update those count assertions if the main agent is committing the package Q&A
changes already present in the working tree. Package-owned alias count should
remain `157` unless entrypoint aliases are intentionally changed.

## What Not To Change

- Do not add live RingCentral automation for these prompts.
- Do not add or modify `openSteps`.
- Do not make copy-link, paste-link, read-link, or invite-link prompts operable.
- Do not call clipboard APIs, press `Copy meeting link`, paste into any field,
  type an invite target, select contact suggestions, or press `Invite`.
- Do not read private invite links, meeting URLs, meeting IDs, emails, names,
  suggestions, participant rosters, chat, clipboard contents, or dial-in
  details.
- Do not claim a link was copied, pasted, read aloud, verified, or sent.
- Do not broaden package-owned entrypoint aliases with generic action words
  such as `copy`, `paste`, `read`, `aloud`, `url`, or `link`.

## Recommended Acceptance

Before the main agent commits Cycle162, verify:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests/unit/test_questions.py::test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first tests/unit/test_questions.py::test_ringcentral_english_invite_privacy_questions_stay_qa_first
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
```

Expected after count assertions are updated:

- all five proposed prompts route deterministically;
- all five return `can_operate=False`;
- all five produce no question interrupt;
- no answer contains a real-looking URL, `ringcentral.com`, email address,
  numeric meeting ID, private name, copied/pasted/read-aloud success claim, or
  sent-invite claim;
- doctor reports `138 Q&A question prompts` for duplicate and alias-overlap
  checks;
- package-owned alias count remains `157`.

## Handoff Note

This risk-scan agent only inspected the current package/tests/runtime behavior
and wrote this document. It did not run `git add`, `git commit`, or `git reset`.
