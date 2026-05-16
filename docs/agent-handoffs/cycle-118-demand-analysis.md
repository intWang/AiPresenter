# Cycle 118 Demand Analysis: Spanish VBG Demo Narration Wedge

Date: 2026-05-16
Scope: demand analysis only. This file is the only file edited by this handoff.

## Recommendation

The highest-value Cycle 118 slice is to add Spanish demo narration for the complete `vbg-blur-demo` flow in `packages/ringcentral-video.yaml`, while keeping Spanish runtime presenter support disabled.

This is a small, user-facing language wedge: Spanish RingCentral Video Q&A is already complete at `12/12`, and the most coherent next step is to make the existing virtual-background privacy demo report as localized in Spanish. The flow is only four steps, already centered on a high-demand RingCentral Video use case, and connects directly to the existing Spanish background/privacy Q&A seed and the three Spanish background aliases.

Target delta:

- Spanish demo narration: `0/51` -> `4/51`.
- Spanish `vbg-blur-demo`: `0/4` -> `4/4`.
- Spanish Q&A remains `12/12` questions and `12/12` answers.
- Spanish entrypoint aliases remain `1/27` entrypoints and `3` aliases.
- Spanish runtime remains unsupported.

## Why This Fits Demand

AiPresenter demand: the user asked for continuous optimization with committed, reviewable cycles. This slice is visible in the CLI localization report, improves a real demo path, and can be completed safely in one cycle without broad runtime risk.

RingCentralVideo knowledge: `vbg-blur-demo` demonstrates a concrete RingCentral Video privacy workflow: open video settings, open Background, select Blur, and verify the live tile. That aligns with existing package notes about protecting the real environment and with the current Spanish Q&A answer for background privacy.

Language and tone expansion: Cycle 117 made Spanish useful for report-only Q&A. Cycle 118 should start Spanish demo narration with a complete flow rather than scattering one-off lines across larger tours. The narration should sound like a concise Spanish product-demo coach, preserve literal RingCentral UI labels, and avoid overclaiming live Spanish support.

UI, performance, and skills goals: this is package-local and should not touch UI code, runtime performance paths, or presenter skill files. It does preserve the product's synchronized-demo contract by keeping each step's `placement` and `actionOffsetMs` unchanged. Because no Q&A prompts or aliases are added, diagnostics prompt-count drift should not occur in this slice.

## Out Of Scope

- Do not add Spanish runtime support.
- Do not add `es` to `PresenterLanguage`, CLI/controller language choices, `voices`, provider routing, speech assets, profiles, or no-match answers.
- Do not translate `meeting-basics-demo`, `meeting-controls-tour`, or `meeting-control-map-demo` in this cycle.
- Do not change Q&A, `questionAliases.es`, `questionPolicy`, `openSteps`, cleanup behavior, locators, route authorization, operation types, action placement, or offsets.
- Do not add live RingCentral acceptance claims.
- Do not edit README, durable knowledge docs, presenter skills, source code, runtime tests unrelated to localization reporting, `.coverage`, git history, or other handoff files.
- Do not implement a diagnostic prompt-count guard in Cycle 118 unless the user explicitly redirects. Narration-only Spanish should leave Q&A prompt counts unchanged.
- Do not draft or implement a Spanish runtime promotion plan in this cycle.

## Acceptance Criteria

A Cycle 118 implementation satisfies this demand when:

- `packages/ringcentral-video.yaml` adds `narration.localizedText.es` only for these four steps:
  - `vbg-blur-demo` -> `open-video-settings`
  - `vbg-blur-demo` -> `open-background-panel`
  - `vbg-blur-demo` -> `select-blur`
  - `vbg-blur-demo` -> `verify-meeting-video`
- The Spanish narration keeps RingCentral UI labels literal where they name controls or panels: `Settings`, `Background`, `Blur`, and `Stop video`.
- The Spanish narration preserves privacy and safety meaning: configure the presenter's own visual presentation, protect the real environment, select blur deliberately, and verify video state without implying participant data access or broader meeting control.
- Existing `placement` and `actionOffsetMs` values for the four steps remain unchanged.
- No Spanish `localizedText.es` is added to the other 47 demo steps.
- `localization-report --package ringcentral-video --language es` reports `4/51` demo steps and `vbg-blur-demo: 4/4 narration localized`.
- The same report still shows `meeting-basics-demo: 0/3`, `meeting-controls-tour: 0/22`, and `meeting-control-map-demo: 0/22` Spanish narration.
- Spanish Q&A remains `12/12` questions and `12/12` answers.
- Spanish aliases remain `questionAliases.es present on 1/27 entrypoints (3 aliases)`.
- `localization-report --package ringcentral-video --language es --require-complete` still exits nonzero with incomplete Spanish localization.
- `voices` still lists English, Chinese, and Japanese only.
- `demo --profile ringcentral-video --package ringcentral-video --flow vbg-blur-demo --language es --dry-run` still rejects Spanish with `Unsupported presenter language: es`.
- Chinese and Japanese `--require-complete` localization reports still pass.
- RingCentral doctor diagnostics still pass; Q&A prompt counts should remain `84` and package-owned alias count should remain `90`.
- `.coverage` is not staged.

## Suggested Technical Handoff Prompt

You are the Cycle 118 technical-scan subagent for AiPresenter. Inspect the current Spanish localization tests and `packages/ringcentral-video.yaml`. Produce a technical handoff for adding Spanish `localizedText.es` only to the four `vbg-blur-demo` narration steps. Preserve placements, offsets, UI labels, Q&A, aliases, runtime language rejection, and diagnostics counts. Identify exact tests to update or add in `tests/unit/test_material_packages.py` and `tests/unit/test_cli.py`, and note any checks in `tests/unit/test_diagnostics.py`, `tests/unit/test_voice.py`, or `tests/unit/test_questions.py` that must remain unchanged. Do not modify files except your assigned handoff.

## Suggested Test Handoff Prompt

You are the Cycle 118 test-review subagent for AiPresenter. Review the Spanish VBG demo narration implementation. Verify the localization report moved from `0/51` to `4/51`, `vbg-blur-demo` is `4/4`, other Spanish demo flows remain `0`, Spanish Q&A remains `12/12`, Spanish aliases remain `1/27` and `3`, Spanish runtime remains unsupported, and Q&A prompt/alias diagnostics did not drift. Run focused pytest for material package and CLI localization tests plus CLI checks for `localization-report`, `voices`, Spanish `demo --dry-run`, and Chinese/Japanese `--require-complete`. Confirm `.coverage` is unstaged.

## Suggested Experience Handoff Prompt

You are the Cycle 118 experience subagent for AiPresenter. Capture user-facing lessons from adding Spanish narration for the full `vbg-blur-demo` flow while runtime Spanish remains unsupported. Explain how to describe this as "Spanish VBG demo narration coverage" rather than "Spanish presenter support", note why literal RingCentral UI labels should remain in Spanish prose, and recommend the next Spanish demo wedge only after Cycle 118 verification. Do not modify files except your assigned experience handoff.

## Read-Only Evidence Used

Inspected:

- `README.md`
- `docs/knowledge/ai-presenter-maintenance.md`
- `docs/agent-handoffs/cycle-117-demand-analysis.md`
- `docs/agent-handoffs/cycle-117-technical-scan.md`
- `docs/agent-handoffs/cycle-117-risk-scan.md`
- `docs/agent-handoffs/cycle-117-implementation.md`
- `docs/agent-handoffs/cycle-117-test-review.md`
- `docs/agent-handoffs/cycle-117-experience.md`
- `packages/ringcentral-video.yaml`
- Relevant localization, CLI, diagnostics, questions, and voice tests.

Observed current CLI state:

- Spanish localization report: `0/51` demo steps, `12/12` Q&A questions, `12/12` Q&A answers, `questionAliases.es present on 1/27 entrypoints (3 aliases)`.
- Japanese localization report: `51/51` demo steps, `12/12` Q&A questions, `12/12` Q&A answers.
- `voices` lists English, Chinese, and Japanese runtime languages only.
- Worktree had `.coverage` modified before this handoff; it is out of scope.
