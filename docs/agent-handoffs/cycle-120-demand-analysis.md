# Cycle 120 Demand Analysis: Localization/Runtime Diagnostics Guard

Date: 2026-05-16
Scope: demand analysis only. This file is the only file edited by this handoff.

## Recommendation

The highest-value Cycle 120 slice is a small diagnostics/CLI guard that separates package localization checks from runtime voice language checks.

Add a `doctor` option such as `--localization-language es` that feeds the existing diagnostics `localization_language` path when `--require-localization` is used, without treating Spanish as a supported presenter voice. This lets maintainers verify Spanish package coverage directly through `doctor` after Cycles 117-119, while preserving the current runtime boundary that `--language es` is unsupported.

Target behavior:

- `doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --localization-language es` reports Spanish package localization as incomplete with the current `7/51` demo-step count and `12/12` Q&A counts.
- `doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --language es` still rejects Spanish as an unsupported presenter language.
- Existing Chinese and Japanese runtime/localization checks remain unchanged.
- No Spanish runtime, provider, controller, profile, or voice catalog support is added.

## Why This Fits Demand

Demand discovery: Spanish package localization has moved from Q&A-only to two short demo wedges, so the next user-facing risk is confusion between "Spanish content exists in reports" and "Spanish demos can run." A diagnostics guard is now more valuable than immediately adding another narration wedge because it protects the language lifecycle before coverage expands further.

UI/performance: this slice should not touch controller UI, desktop automation, package indexes, question matching, or performance code. It is a CLI/diagnostics usability improvement over existing data paths, so the blast radius is much smaller than a package index optimization cycle.

Language/tone: Spanish remains a report-only package localization seed. `--language` continues to mean runtime presenter voice and tone rendering, while the new localization option means package coverage inspection. Tone aliases remain style-only and do not affect routing or localization completeness.

Skills: no runtime presenter skills, Codex home skills, or repo-local skill candidates should change. The current maintenance playbook already contains the right rule: separate package localization from runtime language support. Cycle 120 should encode that rule in CLI behavior instead of adding another playbook paragraph.

RingCentralVideo knowledge: the RingCentral package now has Spanish Q&A, Spanish VBG narration, and Spanish meeting-basics narration. Doctor should be able to report those facts without implying live RingCentral Spanish voice readiness, manual acceptance, or provider compatibility.

## Why Not The Other Candidates

Next Spanish narration wedge is still valid, but the remaining demo gaps are the two large 22-step control flows. They carry broader safety and review surface around meeting information, report issue, invite, share, recording, notes/transcript, settings, and leave/end. A guard first makes future Spanish expansion easier to verify.

Performance/index guard is attractive but broader. It touches package-derived indexes and route parity, so it deserves a cycle focused on structural behavior-preservation tests.

Repo-local playbook or skill candidate improvements are lower value right now. The playbook already names the relevant distinction; the product needs a CLI affordance that makes the distinction hard to miss.

## Proposed Implementation Shape

- In `src/ai_presenter/cli.py`, add a `doctor` option named `--localization-language`.
- Keep `--language` as the runtime presenter voice selector only.
- When `--require-localization` is true, pass `localization_language` as:
  - the explicit `--localization-language` value when provided;
  - otherwise the selected voice language when a supported `--language` was provided;
  - otherwise the existing default behavior, which checks Chinese.
- Do not normalize `--localization-language` through `PresenterVoiceSettings`; it should accept package localization keys such as `es` even when they are not runtime presenter languages.
- Add focused CLI tests for Spanish localization diagnostics and unsupported Spanish runtime language rejection.
- Optionally update the README diagnostic example text to show package-localization checking separately from runtime voice checking, if the implementation cycle wants user-facing docs in scope.

## Out Of Scope

- Do not add Spanish runtime support.
- Do not add `es` to `PresenterLanguage`, `PRESENTER_LANGUAGE_CHOICES`, controller language choices, profile provider routes, speech assets, no-match answers, or `voices`.
- Do not add Spanish narration, Q&A, aliases, entrypoints, flows, locators, or RingCentral package facts.
- Do not change question routing, Q&A-first matching, `questionPolicy`, `can_operate`, or interrupt creation.
- Do not change package index construction or runtime performance behavior.
- Do not modify presenter skills, `presenter/soul.md`, `presenter/memory.md`, Codex home skills, or the maintenance playbook.
- Do not claim live RingCentral acceptance.
- Do not stage `.coverage`.

## Acceptance Criteria

A Cycle 120 implementation satisfies this demand when:

- `doctor` exposes a package localization option, preferably `--localization-language`.
- `doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --localization-language es` reaches diagnostics instead of voice parsing and exits nonzero because Spanish required localization is incomplete.
- The Spanish diagnostic detail includes `required es localization incomplete`, `7/51 demo steps`, `12/12 Q&A questions`, and `12/12 Q&A answers`.
- `doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --language es --require-localization` still rejects with `Unsupported presenter language: es` unless `--language` is omitted or changed to a supported runtime language.
- `doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --language zh-CN --tone friendly --require-localization` still checks Chinese localization and supported Chinese voice routing.
- If both `--language zh-CN` and `--localization-language es` are provided with `--require-localization`, voice checks Chinese while localization checks Spanish.
- `localization-report --package ringcentral-video --language es` remains unchanged at `7/51`, with `vbg-blur-demo: 4/4`, `meeting-basics-demo: 3/3`, both large flows at `0/22`, Q&A `12/12`, and aliases `1/27 (3 aliases)`.
- `voices` still lists English, Chinese, and Japanese only.
- RingCentral doctor package diagnostics still report `90` package-owned aliases, `84` Q&A prompts, and the expected INFO-level `qa alias substring risk`.
- No package YAML or runtime presenter skill files change.
- Focused tests pass without relying on coverage artifacts, and `.coverage` is not staged.

## Suggested Technical Handoff Prompt

You are the Cycle 120 technical-scan subagent for AiPresenter. Inspect `src/ai_presenter/cli.py`, `src/ai_presenter/runtime/diagnostics.py`, `src/ai_presenter/runtime/voice.py`, `tests/unit/test_cli.py`, `tests/unit/test_diagnostics.py`, and the current Spanish localization report. Produce a technical handoff for adding a `doctor --localization-language` option that lets `--require-localization` inspect package localization keys such as `es` without adding Spanish runtime voice support. Preserve `--language` as the runtime voice selector, keep Spanish `--language es` rejected, and identify exact focused tests for Spanish incomplete localization, Chinese voice/localization parity, override behavior, and unchanged `voices` output. Do not modify files except your assigned handoff.

## Suggested Test-Review Handoff Prompt

You are the Cycle 120 test-review subagent for AiPresenter. Review the diagnostics guard implementation. Verify `doctor --require-localization --localization-language es` reports incomplete Spanish package coverage at `7/51` with Q&A `12/12`, while `doctor --language es` and `demo --language es --dry-run` still reject Spanish as unsupported runtime language. Run focused CLI diagnostics tests, `voices`, Spanish `localization-report`, Chinese/Japanese `--require-complete` localization reports, and RingCentral doctor diagnostics. Confirm no package YAML, presenter skill, provider, controller, or runtime voice catalog drift occurred, and confirm `.coverage` is unstaged.

## Suggested Experience Handoff Prompt

You are the Cycle 120 experience subagent for AiPresenter. Capture the user-facing lesson from separating package localization diagnostics from runtime voice support. Explain how to describe Spanish as "reportable package localization coverage" until a future runtime promotion is explicitly planned, document the difference between `--language` and `--localization-language`, and note why this matters before expanding into the two large Spanish control-flow demos. Do not modify files except your assigned experience handoff.

## Read-Only Evidence Used

Inspected:

- `README.md`
- `docs/knowledge/ai-presenter-maintenance.md`
- `docs/agent-handoffs/cycle-117-*`
- `docs/agent-handoffs/cycle-118-demand-analysis.md`
- `docs/agent-handoffs/cycle-119-demand-analysis.md`
- `docs/agent-handoffs/cycle-119-technical-scan.md`
- `docs/agent-handoffs/cycle-119-implementation.md`
- `docs/agent-handoffs/cycle-119-test-review.md`
- `docs/agent-handoffs/cycle-119-experience.md`
- `docs/knowledge/ringcentral-video/source-index.md`
- `docs/knowledge/ringcentral-video/runtime-safety-routing.md`
- `docs/knowledge/ringcentral-video/privacy-matrix.md`
- `docs/runbooks/ringcentral-manual-acceptance.md`
- `packages/ringcentral-video.yaml`
- `src/ai_presenter/cli.py`
- `src/ai_presenter/runtime/diagnostics.py`
- `src/ai_presenter/runtime/voice.py`
- `src/ai_presenter/packages/localization_status.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_diagnostics.py`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_voice.py`

Observed current CLI state:

- Spanish localization report: `7/51` demo steps, `vbg-blur-demo: 4/4`, `meeting-basics-demo: 3/3`, `meeting-controls-tour: 0/22`, `meeting-control-map-demo: 0/22`, `12/12` Q&A questions, `12/12` Q&A answers, and `questionAliases.es present on 1/27 entrypoints (3 aliases)`.
- `doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --language es` currently exits during CLI parsing with `Unsupported presenter language: es`, so it cannot report Spanish package localization state.
- Runtime Spanish remains unsupported by `PresenterVoiceSettings`.
- Worktree had `.coverage` modified before this handoff; it is out of scope.
