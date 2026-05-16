# Cycle 119 Demand Analysis: Spanish Meeting Basics Narration Wedge

Date: 2026-05-16
Scope: demand analysis only. This file is the only file edited by this handoff.

## Recommendation

The highest-value Cycle 119 slice is to add Spanish demo narration for the complete `meeting-basics-demo` flow in `packages/ringcentral-video.yaml`, while keeping Spanish runtime presenter support disabled.

This is the smallest coherent next language-and-tone expansion after Cycle 118. Spanish already has complete report-only RingCentral Video Q&A and a complete four-step virtual-background blur demo wedge. The next best step is the three-step meeting-basics flow because it covers the core live-meeting controls a presenter most often needs first: microphone, Participants, and Chat.

Target delta:

- Spanish demo narration: `4/51` -> `7/51`.
- Spanish `meeting-basics-demo`: `0/3` -> `3/3`.
- Spanish `vbg-blur-demo` remains `4/4`.
- Spanish `meeting-controls-tour` remains `0/22`.
- Spanish `meeting-control-map-demo` remains `0/22`.
- Spanish Q&A remains `12/12` questions and `12/12` answers.
- Spanish aliases remain `questionAliases.es present on 1/27 entrypoints (3 aliases)`.
- Spanish runtime remains unsupported.

## Why This Fits Demand

Demand discovery: this slice continues the proven Spanish demand path without overcommitting to full Spanish presenter support. It gives the user another visible reportable increment and keeps the change small enough to commit and review in one cycle.

UI/performance: the implementation should be package-local and should not touch UI automation, controller UI, indexes, routing, or runtime performance code. It preserves synchronized demo behavior by leaving every action, `placement`, and `actionOffsetMs` unchanged. The performance-index opportunity remains valid, but it is a better later cycle because it needs structural behavior-parity tests around package-derived indexes.

Language/tone expansion: `meeting-basics-demo` is a concise Spanish narration wedge that broadens beyond background privacy into everyday meeting readiness. The Spanish prose should sound like a calm product-demo coach, keep RingCentral UI labels literal where they name controls, and avoid implying Spanish TTS/provider availability.

Skills: this cycle should use the repo maintenance playbook rules, especially the localization wedge rules, without changing runtime presenter skills or Codex home skills. Repo-local skill/playbook improvements are lower value for Cycle 119 because the current playbook already gives enough guidance for this slice.

RingCentralVideo knowledge: microphone, Participants, and Chat are high-frequency RingCentral Video surfaces with important safety boundaries. The narration can reinforce local audio readiness, roster visibility without naming people, and chat collaboration without reading private messages.

## Why Not The Other Candidates

Diagnostics guard against coverage/runtime confusion is useful, but Cycle 118 already preserved the runtime boundary through CLI checks: `voices` omits Spanish and Spanish `demo --dry-run` rejects `es`. The next package-only wedge can keep that boundary without adding a new diagnostic surface.

Performance optimization for package/question indexes is attractive, but it has a broader source-code blast radius. It should wait for a cycle that can focus on behavior-preserving cache invalidation, index-order tests, and route/fallback parity.

Repo-local skill or playbook improvements are not the best immediate demand response. The current playbook already explains localization wedge rules, artifact selection, runtime performance hygiene, and staging checks.

## Out Of Scope

- Do not add Spanish runtime support.
- Do not add `es` to `PresenterLanguage`, CLI/controller language choices, `voices`, provider routing, speech assets, profiles, or no-match answers.
- Do not translate `meeting-controls-tour` or `meeting-control-map-demo` in this cycle.
- Do not add or change Q&A, `questionAliases.es`, question routing, diagnostics counts, entrypoint match order, locators, open steps, cleanup behavior, operation types, action placement, or offsets.
- Do not modify UI code, package/question index performance code, presenter skills, durable RingCentral knowledge docs, README, the maintenance playbook, runbooks, or other handoff files.
- Do not claim live RingCentral acceptance.
- Do not stage `.coverage`.

## Acceptance Criteria

A Cycle 119 implementation satisfies this demand when:

- `packages/ringcentral-video.yaml` adds `narration.localizedText.es` only for these three `meeting-basics-demo` steps:
  - `show-mic`
  - `show-participants`
  - `show-chat`
- The Spanish narration keeps literal RingCentral UI labels where they name controls or panels: `Participants` and `Chat`; use `microphone` only if the source text does not name a visible RingCentral label.
- The microphone line explains local audio readiness and recovery before speaking without implying remote control of other people.
- The Participants line explains checking the roster/room state without reading participant identities by default.
- The Chat line explains side-channel collaboration while preserving the boundary that chat content stays private unless the user explicitly asks.
- Existing `placement` and `actionOffsetMs` values for the three steps remain unchanged.
- No Spanish `localizedText.es` is added to `meeting-controls-tour` or `meeting-control-map-demo`.
- Spanish `vbg-blur-demo` remains `4/4`.
- `localization-report --package ringcentral-video --language es` reports `7/51` demo steps and `meeting-basics-demo: 3/3 narration localized`.
- The same report still shows `meeting-controls-tour: 0/22` and `meeting-control-map-demo: 0/22` Spanish narration.
- Spanish Q&A remains `12/12` questions and `12/12` answers.
- Spanish aliases remain `questionAliases.es present on 1/27 entrypoints (3 aliases)`.
- `localization-report --package ringcentral-video --language es --require-complete` still exits nonzero with incomplete Spanish localization.
- `voices` still lists English, Chinese, and Japanese only.
- `demo --profile ringcentral-video --package ringcentral-video --flow meeting-basics-demo --language es --dry-run` still rejects Spanish with `Unsupported presenter language: es`.
- Chinese and Japanese `--require-complete` localization reports still pass.
- RingCentral doctor diagnostics still pass; Q&A prompt counts should remain `84` and package-owned alias count should remain `90`.
- `.coverage` is not staged.

## Suggested Technical Handoff Prompt

You are the Cycle 119 technical-scan subagent for AiPresenter. Inspect the current Spanish localization tests and `packages/ringcentral-video.yaml`. Produce a technical handoff for adding Spanish `localizedText.es` only to the three `meeting-basics-demo` narration steps: `show-mic`, `show-participants`, and `show-chat`. Preserve placements, offsets, UI labels, Q&A, aliases, runtime language rejection, diagnostics counts, and the existing Spanish `vbg-blur-demo` coverage. Identify exact tests to update or add in `tests/unit/test_material_packages.py` and `tests/unit/test_cli.py`, and note checks in `tests/unit/test_diagnostics.py`, `tests/unit/test_voice.py`, or `tests/unit/test_questions.py` that must remain unchanged. Do not modify files except your assigned handoff.

## Suggested Test-Review Handoff Prompt

You are the Cycle 119 test-review subagent for AiPresenter. Review the Spanish `meeting-basics-demo` narration implementation. Verify Spanish localization reporting moved from `4/51` to `7/51`, `meeting-basics-demo` is `3/3`, `vbg-blur-demo` remains `4/4`, `meeting-controls-tour` and `meeting-control-map-demo` remain `0`, Spanish Q&A remains `12/12`, Spanish aliases remain `1/27` and `3`, Spanish runtime remains unsupported, and Q&A prompt/alias diagnostics did not drift. Run focused pytest for material package and CLI localization tests plus CLI checks for `localization-report`, `voices`, Spanish `demo --dry-run`, and Chinese/Japanese `--require-complete`. Confirm `.coverage` is unstaged.

## Suggested Experience Handoff Prompt

You are the Cycle 119 experience subagent for AiPresenter. Capture user-facing lessons from adding Spanish narration for the full `meeting-basics-demo` flow while runtime Spanish remains unsupported. Explain how to describe this as "Spanish meeting-basics demo narration coverage" rather than "Spanish presenter support", note why literal RingCentral UI labels should remain inside Spanish prose, and document the safety tone for microphone readiness, Participants roster visibility, and Chat privacy. Do not modify files except your assigned experience handoff.

## Read-Only Evidence Used

Inspected:

- `README.md`
- `docs/knowledge/ai-presenter-maintenance.md`
- `docs/agent-handoffs/cycle-118-demand-analysis.md`
- `docs/agent-handoffs/cycle-118-implementation.md`
- `docs/agent-handoffs/cycle-118-test-review.md`
- `packages/ringcentral-video.yaml`
- `src/ai_presenter/packages/localization_status.py`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_diagnostics.py`

Observed current CLI state:

- Spanish localization report: `4/51` demo steps, `vbg-blur-demo: 4/4`, `meeting-basics-demo: 0/3`, `meeting-controls-tour: 0/22`, `meeting-control-map-demo: 0/22`, `12/12` Q&A questions, `12/12` Q&A answers, and `questionAliases.es present on 1/27 entrypoints (3 aliases)`.
- `voices` lists English, Chinese, and Japanese runtime languages only.
- Worktree had `.coverage` modified before this handoff; it is out of scope.
