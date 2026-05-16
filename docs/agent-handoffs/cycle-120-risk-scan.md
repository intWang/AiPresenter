# Cycle 120 Risk Scan: Localization Runtime Boundary

Date: 2026-05-16
Scope: documentation-only risk scan for candidate Cycle 120 work. This handoff creates only `docs/agent-handoffs/cycle-120-risk-scan.md`; do not stage or commit from this scan.

## Current Baseline

- Spanish package localization is partial: `vbg-blur-demo` and `meeting-basics-demo` narration are localized, for `7/51` demo steps.
- Spanish Q&A coverage is complete for report purposes: `12/12` questions and `12/12` answers.
- Spanish aliases remain narrow: `questionAliases.es` is present on `1/27` entrypoints with `3` aliases.
- Runtime Spanish remains unsupported and should still be rejected by CLI/controller language parsing and `PresenterVoiceSettings`.
- Chinese and Japanese remain the runtime-supported non-English package localization paths.
- `.coverage` is a dirty local artifact risk and must remain unstaged.

## Candidate Risk Review

### Diagnostics Guard Around Localization/Runtime Confusion

This is the preferred Cycle 120 candidate if kept narrow. The guard should make the distinction explicit: package localization report coverage is not the same as runtime presenter language support. Spanish can be partially localized in package content while still being unsupported for live or dry-run presenter execution.

Main risks:

- Misleading wording such as "Spanish supported", "Spanish runtime-ready", "Spanish accepted", or "Spanish live verified".
- CLI parsing side effects if `doctor --language es` starts accepting Spanish as a runtime voice merely to report localization status.
- Accidentally moving language validation from voice/runtime code into localization-report code or vice versa.
- Count drift if diagnostics starts reusing stale expected totals instead of current package-derived coverage.

Go if:

- The change is diagnostics/test only.
- The output says package/report status and runtime status separately.
- Runtime language rejection remains unchanged for `es`.
- The implementation avoids provider calls, UI automation, live RingCentral probing, and broad package rescans.

No-go if:

- Spanish becomes selectable in `voices`, controller language choices, profile voices, provider routing, or dry-run runtime paths.
- The diagnostics line can be read as a live acceptance claim.
- The guard requires changing package YAML or Q&A text.

### Another Spanish Narration Wedge

This is acceptable for one cycle only if it is a very small package-local wedge. The next large flows are higher risk than the completed short demos because they touch privacy-sensitive and state-changing surfaces: chat, participants, invite links, notes, recording, captions, translation, reactions, raise hand, host controls, leave/end, and cleanup.

Main risks:

- Translating visible RingCentral UI labels into Spanish when the actual UI remains English.
- Adding Spanish narration that implies reading chat contents, participant names, invite links, transcripts, recordings, or private details by default.
- Letting partial narration plus full Q&A be described as full Spanish support.
- Adding aliases or runtime language support while "just adding narration".

Go if:

- One cycle adds `localizedText.es` for a tiny named slice only.
- English UI labels stay literal in Spanish prose, such as `Chat`, `Participants`, `Invite`, `Share`, `Notes`, `Recording`, `More`, `Leave`, and `Stop video`.
- Existing operations, locators, action offsets, cleanup, route authorization, Q&A, and aliases remain unchanged.
- Spanish `--require-complete` continues to fail until all `51/51` demo steps are localized.

No-go if:

- The slice combines narration with diagnostics, aliases, runtime support, or source-index/playbook expansion.
- The work touches live meeting operation semantics or claims manual acceptance without dated evidence.

### Performance/Index Work

This is a no-go by default unless Cycle 120 defines a single measured target first. The current package/runtime matching already has precomputed candidate/index surfaces; changing them can affect Q&A precedence, alias matching, localized question behavior, and diagnostics counts.

Main risks:

- Stale private indexes after package mutation or copied flow construction.
- Different Q&A-first matching behavior, tie ordering, alias precedence, or token scoring.
- Diagnostics counts becoming stale or expensive through duplicate scans.
- "Performance" work hiding behavior changes in runtime questions, package validation, or diagnostics.

Go if:

- The target is one isolated hot path with structural parity tests and before/after evidence.
- Tests prove index rebuilding for copied packages/flows and non-leakage into serialized package data.
- Matching order, answers, safety flags, localized behavior, and logging privacy remain identical.

No-go if:

- The cycle lacks a benchmark or a specific algorithmic target.
- The change touches provider behavior, event timing, narration scheduling, action offsets, or live UI observation.

## Recommendation

For Cycle 120, prefer a diagnostics guard that clearly reports "Spanish package localization is partial/full by report counts, but Spanish runtime presenter language is unsupported." This directly addresses the current confusion risk without increasing package or runtime blast radius.

Acceptable fallback: one small Spanish narration wedge, but only if explicitly named and package-local.

Defer performance/index work unless a separate technical scan defines one measured target, parity tests, and stale-index protections.

Do not combine diagnostics guard, Spanish narration, performance/index work, and playbook/docs in a single cycle.

## One-Cycle Boundaries

Diagnostics guard boundaries:

- Change only diagnostics/CLI tests and the smallest production diagnostics code needed.
- Keep `demo --language es --dry-run` rejecting `Unsupported presenter language: es`.
- Keep `voices` excluding Spanish.
- Keep localization report counts package-derived.
- Use wording like "package localization" and "runtime language support" rather than "Spanish support".

Spanish wedge boundaries:

- Add only `localizedText.es` for the selected steps.
- Keep Spanish Q&A at `12/12`, aliases at `1/27` and `3`, and runtime Spanish unsupported.
- Keep UI labels literal in English.
- Keep Spanish `--require-complete` failing unless the cycle explicitly finishes all remaining demo narration.

Performance/index boundaries:

- Require a narrow target and parity-first tests before implementation.
- Preserve Q&A-first matching, alias precedence, route authorization, localized question matching, safety flags, and privacy-safe logs.
- Prove indexes rebuild where package copies are created and do not leak into model dumps/YAML.

## Failure Modes To Test

| Risk | Failure mode | Required test or check |
| --- | --- | --- |
| Misleading diagnostics wording | Diagnostics says or implies Spanish is supported, runtime-ready, accepted, or live verified because package Q&A is complete. | Assert diagnostics output separates package localization from runtime language support; grep touched files for `supported`, `runtime-ready`, `accepted`, and `live verified`. |
| CLI language parsing side effects | `doctor --language es`, `demo --language es --dry-run`, or controller parsing starts accepting Spanish as a runtime voice. | Assert Spanish runtime commands still reject `es`; assert `voices` still excludes Spanish. |
| Runtime Spanish leakage | Spanish appears in `PresenterVoiceSettings`, provider routing, profile `voices`, no-match runtime text, or controller choices. | Diff-scope review plus focused tests around voice validation and language listings. |
| Stale counts | Diagnostics or localization-report shows old Spanish totals after a narration wedge or index change. | Use package-derived localization status in tests; assert current Spanish demo/Q&A/alias counts exactly. |
| Translated UI labels | Spanish narration translates actual RingCentral labels, making users search for labels not present in the English UI. | Add/review focused assertions that touched strings preserve literal labels like `Chat`, `Participants`, `Invite`, and `Recording`. |
| Live acceptance claims | Handoffs, docs, tests, or CLI text claim live validation from YAML/unit-test evidence. | Require dated manual/live evidence before any acceptance claim; otherwise say "package/report coverage" only. |
| `.coverage` staging | Focused pytest dirties `.coverage`, and it gets included with source/doc changes. | Run `git status --short --untracked-files=all` and `git diff --cached --name-status`; leave `.coverage` unstaged. |
| Performance/index regression | Index optimization changes matching order, stale indexes, or serialized package output. | Run parity tests for Q&A-first matching, alias precedence, copy rebuilds, and model-dump non-leakage. |

## Verification Checklist

For this documentation-only scan:

- [ ] Diff contains only `docs/agent-handoffs/cycle-120-risk-scan.md`.
- [ ] `git diff --check -- docs\agent-handoffs\cycle-120-risk-scan.md` passes.
- [ ] `git status --short --untracked-files=all` is reviewed; `.coverage` remains unstaged.

For the selected Cycle 120 implementation:

- [ ] Spanish package localization and runtime support are reported as separate concepts.
- [ ] Spanish runtime remains unsupported unless the cycle is explicitly re-scoped to runtime promotion.
- [ ] Localization counts are current and package-derived.
- [ ] Touched Spanish narration keeps visible UI labels in English.
- [ ] No hidden live acceptance wording is introduced.
- [ ] `.coverage` is not staged.

## Bottom Line

Go for a diagnostics guard as the safest one-cycle move. A tiny Spanish narration wedge is acceptable if it stays package-local. Performance/index work should wait for a measured technical plan because stale indexes and matching-order drift are the highest-risk failure modes.
