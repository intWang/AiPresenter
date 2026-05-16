# Cycle 119 Risk Scan: Spanish Next-Slice Boundaries

Date: 2026-05-16
Scope: documentation-only risk scan for candidate Cycle 119 work after Spanish Q&A completion and the Spanish `vbg-blur-demo` narration wedge. This handoff creates only `docs/agent-handoffs/cycle-119-risk-scan.md`.

## Current Baseline

- Spanish Q&A is complete for report coverage: `12/12` questions and `12/12` answers.
- Spanish demo narration is partial: `4/51`, all from `vbg-blur-demo`.
- Spanish runtime presenter language remains unsupported and must continue to reject `es`.
- Spanish aliases remain narrow and package-local; do not broaden them as part of a narration or diagnostics slice.
- `.coverage` is already a modified worktree artifact and must not be staged, deleted, reset, or normalized by the next cycle.

## Candidate Risk Review

### Another Spanish Narration Wedge

Safety/privacy risk is manageable if the wedge is small and preserves existing demo semantics. `meeting-basics-demo` is the lowest-risk next narration wedge because it is only three steps and mainly introduces meeting startup and basic readiness. `meeting-controls-tour` and `meeting-control-map-demo` are larger and touch more sensitive surfaces: chat, participants, invite links, notes, recording, captions/transcripts, translation, host controls, reactions, and leave/end behavior.

Localization risk is the main hazard. Spanish narration should localize the explanatory prose while keeping visible RingCentral UI labels in English, such as `Settings`, `Background`, `Blur`, `Chat`, `Participants`, `Invite`, `Share`, `Notes`, `Recording`, `More`, `Leave`, and `Stop video`. Translated UI labels would mislead users because the actual product surface remains English.

Runtime risk remains P0: adding more `localizedText.es` must not add Spanish to `PresenterVoiceSettings`, CLI/controller language choices, provider routing, `voices`, no-match text, or profile compatibility.

Performance risk is low for package-only text edits, except that broad test runs can update `.coverage`.

### Diagnostics Guard

Diagnostics work is safe for one cycle if it only adds an invariant or clearer failure around current package/report state. Good targets are: Q&A prompt index count, alias count/overlap, partial Spanish localization status, or a guard that Spanish report coverage does not imply runtime support.

The risk is accidental semantics creep: diagnostics output must not call Spanish "supported", "accepted", "runtime-ready", or "live verified". It should say report/package localization state, not presenter capability. If diagnostics count expectations move, the implementation must document why and prove Q&A prompt count/alias count drift is intentional.

Performance risk is moderate if diagnostics scans become more expensive or run duplicate package traversals. Keep checks package-local, deterministic, and O(number of package texts/aliases), with no provider calls, UI automation, or live RingCentral dependency.

### Performance Optimization

This is no-go unless the target is sharply defined before implementation. The likely risk is broad runtime churn across launch/bind, observation scan, narration, TTS, audio playback, and controller refresh without a stable benchmark. Any optimization that touches event timing, narration scheduling, or action offsets can change demo behavior.

Safe single-cycle performance work would add measurement or tighten one isolated hot path with before/after evidence. It should not alter localization semantics, provider behavior, safety gates, routes, or package text.

### Skill/Playbook Documentation

This is low-risk and useful if the scope is documentation only: capture the Spanish localization playbook, runtime-promotion gates, `.coverage` staging warning, literal UI-label rule, and live-acceptance language rules.

The main risk is hidden claims. Docs must distinguish package localization, localization-report completeness, dry-run/runtime support, diagnostics health, and live RingCentral acceptance. Do not write language suggesting Spanish is ready for live presenting until runtime and voice support are explicitly implemented and verified.

## Recommendation

Go for exactly one narrow Cycle 119 slice:

- Preferred: add Spanish narration for `meeting-basics-demo` only, moving Spanish demo narration from `4/51` to `7/51`, while keeping runtime Spanish unsupported.
- Acceptable: add a diagnostics guard that makes partial Spanish coverage and runtime rejection explicit without package text changes.
- Acceptable: write a skill/playbook documentation pass for Spanish localization boundaries and runtime-promotion gates.
- No-go by default: performance optimization, unless a single measured target and verification method are defined first.

No-go for combining narration, diagnostics behavior, performance optimization, and playbook updates in one cycle. No-go for Spanish runtime promotion in Cycle 119 unless the user explicitly replaces the scope with a runtime-promotion plan and verification matrix.

## Go Boundaries For One Cycle

For a Spanish narration wedge:

- Add `localizedText.es` only to the selected flow/steps.
- Preserve existing `placement`, `actionOffsetMs`, operations, locators, cleanup, `openSteps`, `questionPolicy`, route authorization, and Q&A behavior.
- Keep English RingCentral UI labels literal inside Spanish prose.
- Keep Spanish Q&A at `12/12` and Spanish aliases unchanged.
- Keep Spanish `--require-complete` failing until all required demo narration is complete.
- Keep `voices` excluding Spanish and Spanish `demo --language es --dry-run` rejecting `Unsupported presenter language: es`.

For a diagnostics guard:

- Change diagnostics/tests only.
- Avoid provider calls, UI automation, live RingCentral checks, and runtime language enablement.
- Report package localization and prompt-index facts precisely.
- Update expected diagnostic counts only with an explicit handoff note.

For a playbook/doc slice:

- Documentation only.
- No package YAML, runtime, diagnostics, test, profile, provider, or CLI behavior changes.
- Use "Spanish Q&A coverage" or "Spanish demo narration coverage", not "Spanish presenter support".

## No-Go Triggers

Stop the implementation if it:

- Enables `PresenterVoiceSettings(language="es")`, CLI/controller Spanish choices, Spanish provider routing, Spanish no-match runtime text, or a Spanish `voices` listing.
- Translates visible RingCentral UI labels rather than keeping the actual English labels users must find.
- Adds broad Spanish aliases for chat, participants, invite links, share, recording, notes, captions, translation, reactions, raise hand, mute, leave, end, or host/security controls.
- Changes Q&A-first matching, route authorization, `can_operate`, interrupt creation, locator behavior, cleanup, or demo action semantics.
- Treats partial Spanish narration or Q&A report completion as full localization, runtime support, or live acceptance.
- Adds hidden live acceptance claims without dated manual/live evidence.
- Broadens diagnostics into live UI probing, provider checks, or expensive repeated package scans.
- Stages, deletes, resets, or normalizes `.coverage`.

## Failure Modes To Test

| Risk | Failure mode | Required test or check |
| --- | --- | --- |
| Accidental runtime Spanish enablement | A package/report change makes `voices` list Spanish or lets `demo --language es --dry-run` proceed. | Assert `voices` lists only English, Chinese, and Japanese; assert Spanish demo dry-run still rejects `es`. |
| Translated UI labels | Spanish narration says `Configuración`, `Fondo`, `Chat`, or other translated labels where the RingCentral UI remains English. | Review touched Spanish strings and add focused assertions for literal English labels in the wedge. |
| Broad aliases | Spanish aliases such as short nouns or commands overmatch private or state-changing prompts. | Do not add aliases in a narration slice; if redirected, add negative routing tests for private/destructive prompts. |
| Incomplete localization semantics | Spanish `--require-complete` passes while only `7/51` or another partial demo count is localized. | Assert `--require-complete` still exits nonzero until all required Spanish demo narration is present. |
| Hidden live acceptance claims | Handoffs, docs, test names, or CLI text imply live RingCentral validation from YAML/unit tests. | Grep touched files for `accepted`, `live verified`, `demo-ready`, `supported`, and similar wording; require dated live evidence for any live claim. |
| Diagnostics drift | Prompt/alias counts move without intent, or diagnostics bless stale partial Spanish state. | Run diagnostics tests and doctor; document any intentional expected-count movement. |
| Safety phrasing drift | Spanish narration implies reading chat, names, links, transcripts, captions, recordings, or summaries by default. | Review sensitive surfaces; keep explain-only wording and explicit user-control boundaries. |
| Performance regression | Diagnostics or optimization adds repeated package scans, provider calls, or UI automation to normal checks. | Keep diagnostics deterministic and package-local; benchmark any optimization target before/after. |
| `.coverage` staging | Focused pytest updates `.coverage`, and it is staged with source/doc changes. | Run `git status --short --untracked-files=all` and `git diff --cached --name-status`; leave `.coverage` unstaged. |

## Verification Checklist

For this documentation-only scan:

- [ ] Diff contains only `docs/agent-handoffs/cycle-119-risk-scan.md`.
- [ ] `git diff --check -- docs\agent-handoffs\cycle-119-risk-scan.md` passes.
- [ ] `git status --short --untracked-files=all` is reviewed; `.coverage` remains unstaged.

For the selected Cycle 119 implementation:

- [ ] Spanish localization report shows the intended partial demo count and unchanged Q&A/alias counts.
- [ ] Spanish `--require-complete` still fails unless the cycle explicitly completes all `51/51` demo steps.
- [ ] Chinese and Japanese `--require-complete` reports still pass.
- [ ] `voices` still excludes Spanish.
- [ ] Spanish `demo --language es --dry-run` still rejects unsupported Spanish runtime.
- [ ] Touched Spanish narration keeps visible RingCentral UI labels in English and avoids private-content reading claims.
- [ ] No broad Spanish aliases are introduced.
- [ ] Diagnostics counts are checked and any intentional drift is documented.
- [ ] No touched file claims live acceptance, runtime support, or full Spanish support from package/report evidence.
- [ ] `.coverage` is not staged.

## Bottom Line

Proceed only with a narrow, evidence-friendly slice. The safest next move is a three-step `meeting-basics-demo` Spanish narration wedge, followed by focused tests that prove Spanish remains a partial package localization surface and not a runtime presenter language. Diagnostics or playbook work is also acceptable if kept single-purpose. Defer performance optimization and runtime Spanish promotion until they have their own explicit plan, benchmark, and acceptance gates.
