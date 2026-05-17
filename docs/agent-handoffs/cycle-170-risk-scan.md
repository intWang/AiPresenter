# Cycle 170 Risk/Test Scan: Meeting Information, Encryption, And Security Status

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Latest inspected commit: `de46eea`
Role: Cycle170 risk/test-review subagent

## Scope

- Reviewed RingCentral Video natural-language routing for Meeting information, encryption, and security-status prompts.
- Focused on privacy boundaries, false-positive routing risks, focused regression tests, and acceptance criteria.
- Wrote only this handoff: `docs/agent-handoffs/cycle-170-risk-scan.md`.
- Did not edit code, tests, package YAML, staging, commits, or `.coverage`.
- Used read-only `git`, `rg`, file reads, a no-bytecode route probe, and focused pytest with coverage disabled.

## Shared Tree Note

The working tree changed during this scan. I did not modify these files:

- `.coverage` was already dirty and remains out of scope.
- `packages/ringcentral-video.yaml` and `tests/unit/test_questions.py` became dirty during the scan with encryption-status Q&A and tests.
- Final status also showed concurrent edits in `tests/unit/test_cli.py`, `tests/unit/test_diagnostics.py`, and untracked `docs/agent-handoffs/cycle-170-demand-analysis.md`.

Treat those changes as concurrent agent work. Coordinate before editing those files.

## Current Evidence

Current focused verification, after the concurrent package/test updates were present:

```powershell
.\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_encryption_status_questions_stay_meeting_info_answer_only tests\unit\test_questions.py::test_ringcentral_localized_encryption_status_questions_are_answer_only
```

Result: `11 passed in 3.33s`.

Current route probe highlights:

| Prompt | Current route | `can_operate` | Interrupt | Review note |
| --- | --- | --- | --- | --- |
| `meeting information` | `ringcentral.video.top.meeting-info` | `False` | no | Answer-only surface; safe default. |
| `Copy meeting link` | `ringcentral.video.top.meeting-info` | `False` | no | Q&A-first privacy answer; safe default. |
| `Is this meeting encrypted?` | `ringcentral.video.top.meeting-info` | `False` | no | Current concurrent Q&A covers this. |
| `Can you verify end-to-end encryption?` | `ringcentral.video.top.meeting-info` | `False` | no | Currently safe; should be pinned in tests. |
| `What is the encryption status?` | `ringcentral.video.top.meeting-info` | `False` | no | Currently safe; should be pinned in tests. |
| `Read encryption details aloud` | `ringcentral.video.top.meeting-info` | `False` | no | Falls to meeting-details privacy answer; safe but copy could mention encryption explicitly. |
| `Open encryption settings` | `ringcentral.video.settings.background` | `True` | yes | Blocking false positive. This can queue the wrong Settings route. |
| `Security status` | `None` | `False` | no | Safe but unhelpful no-match. |
| `What is the security status?` | `None` | `False` | no | Safe but unhelpful no-match. |
| `Is the meeting secure?` | `None` | `False` | no | Safe but unhelpful no-match. |
| `Where are security settings?` | `None` | `False` | no | Host/security Q&A; safe. |
| `Share meeting security status` | `ringcentral.video.toolbar.share` | `False` | no | Wrong surface, though still non-operable. |
| `Open security tab in RingCentralDevelop` | `ringcentral.develop.video.tab` | `False` | no | Wrong app-shell surface. |
| `Leave encryption off` | `ringcentral.video.toolbar.leave` | `False` | no | Wrong Leave safety answer. |

## Privacy Boundaries

Meeting information contains meeting title, host identity, meeting ID, links, dial-in details, encryption details, and end-to-end encryption options. The default answer may explain where these live, but must not read, copy, paste, expose, or invent exact values.

Encryption and security status should be treated as verified-state information. AiPresenter may say where to verify visible status, but must not claim the meeting is encrypted, unencrypted, secure, insecure, enabled, disabled, locked, unlocked, or end-to-end encrypted unless the visible status is verified from an approved source and the user explicitly asked for that value.

Security settings and host controls are role-gated and high-impact. Do not lock/unlock, admit/remove, mute others, change security settings, or read participant names/roles by default.

Share, RingCentralDevelop app-shell routes, Settings routes, and Leave are false-positive hazards for this prompt family. Even when those routes are non-operable, the answer can still point to the wrong surface and erode trust.

## Risk Matrix

| Risk | Likelihood | Impact | Recommended guard |
| --- | --- | --- | --- |
| Encryption prompt falls to generic Meeting information answer | Medium | Medium | Keep exact Q&A prompts for status wording and assert answer starts with the encryption safety copy. |
| Encryption prompt falls to Leave because of `end-to-end` | Medium | High | Add tests for `Can you verify end-to-end encryption?`, `Is end-to-end encryption on?`, and `Are we using end-to-end encryption?`. |
| `Open encryption settings` routes to Background settings and queues an interrupt | High in current tree | High | Add an answer-only Q&A or runtime guard for encryption settings/action wording; assert not Settings and no interrupt. |
| Security-status prompts no-match | High | Low/Medium | Decide expected answer-only copy for security status; avoid no-match if the user is asking a valid meeting-safety question. |
| `Share meeting security status` routes to Share | Medium | Medium | Add Q&A-first prompt coverage; assert not Share and no `Screen sharing:` answer. |
| RingCentralDevelop wording routes to the Develop Video tab | Medium | Medium | Add negative controls for `security tab in RingCentralDevelop`; status questions should not become app-shell navigation. |
| Ambiguous `Leave encryption off` routes to Leave meeting | Medium | Medium | Add negative controls where `leave` means "keep unchanged", not "exit meeting". |
| Privacy answer leaks exact values or claims copied/read | Low now, high if answer copy changes | High | Assert no URL, RingCentral domain, sample numeric meeting ID, copied/read/dialed claims, host names, participant names, roles, chat, captions, or private tabs. |
| Tone/localization changes safety | Low/Medium | Medium | Extend route-parity coverage for these prompts across supported tones and localized Q&A prompts. |

## Focused Regression Tests To Add

Extend `test_ringcentral_encryption_status_questions_stay_meeting_info_answer_only` with:

- `Is end-to-end encryption on?`
- `Are we using end-to-end encryption?`
- `Can you verify end-to-end encryption?`
- `What is the encryption status?`

Add a focused encryption-settings/action test:

- Prompts: `Open encryption settings`, `Show encryption settings`, `Change encryption settings`, `Turn off end-to-end encryption`, `Leave encryption off`.
- Expected: answer-only, no interrupt, `can_operate is False`.
- Negative routes: not `ringcentral.video.settings.background`, not `ringcentral.video.more.settings`, not `ringcentral.video.toolbar.leave`, not `ringcentral.video.toolbar.share`, not `ringcentral.develop.video.tab`.

Add a security-status test:

- Prompts: `Security status`, `What is the security status?`, `Is the meeting secure?`, `Can you verify meeting security?`, `Share meeting security status`, `Open security tab in RingCentralDevelop`.
- Expected: answer-only safety guidance; no live status claim; no interrupt.
- Negative answer prefixes: no `Screen sharing:`, no `Video tab in RingCentralDevelop:`, no `Leave meeting:`, no `Background settings:`.

Extend tone parity:

- Add representative prompts from the encryption-status, encryption-settings, and security-status sets to the sensitive prompt route-parity matrix.
- Assert tone changes do not alter `entrypoint_id`, `can_operate`, or interrupt creation.

If localized prompts are added, keep them in the same Q&A item as the English safety answer and add focused localized tests for answer-only behavior.

## Acceptance Criteria

- Meeting ID/link/dial-in/host prompts stay Q&A-first or Meeting information answer-only, never operable.
- Encryption and end-to-end encryption status prompts return answer-only guidance tied to Meeting information.
- No encryption/security/status prompt creates a question interrupt.
- No encryption/security/status prompt routes to Share, Background settings, More settings, RingCentralDevelop app-shell routes, or Leave unless the prompt is explicitly about those controls.
- Answer text does not expose or invent URLs, meeting IDs, RingCentral links, dial-in numbers, host identity, participant names, roles, chat, captions, transcript content, meeting links, private values, or copied/read/dialed outcomes.
- Answer text does not claim the live meeting is encrypted, secure, locked, unlocked, enabled, disabled, or end-to-end encrypted unless a separate approved visible-state verification path exists.
- Existing host/security prompts such as `Where are security settings?`, `Open meeting security settings`, and `Change meeting security` remain answer-only and do not open Participants or change host controls.
- Diagnostics count expectations are updated only if the package Q&A prompt count changes.
- Focused pytest passes with coverage disabled and pytest cache disabled.
- `git diff --check` passes for files touched by the implementation pass.

## Blockers And Watch Items

- Blocking false positive in current route probe: `Open encryption settings` routes to `ringcentral.video.settings.background`, has `can_operate=True`, and creates an interrupt.
- Wrong-surface false positives still need tests: `Share meeting security status`, `Open security tab in RingCentralDevelop`, and `Leave encryption off`.
- Security-status prompts currently no-match; this is safe but not a good user answer if Cycle170 intends to answer security-status questions.
- The working tree is shared and currently dirty in `.coverage`, `packages/ringcentral-video.yaml`, `tests/unit/test_cli.py`, `tests/unit/test_diagnostics.py`, `tests/unit/test_questions.py`, and untracked `docs/agent-handoffs/cycle-170-demand-analysis.md`. I did not edit those files.
