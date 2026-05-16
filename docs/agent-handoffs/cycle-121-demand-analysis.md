# Cycle 121 Demand Analysis: Spanish Meeting Controls Orientation Wedge

Date: 2026-05-16
Scope: demand analysis only. This file is the only file edited by this handoff.

## Recommendation

The highest-value Cycle 121 slice is another carefully scoped Spanish package-local narration wedge: add `localizedText.es` only to the first four `meeting-controls-tour` steps in `packages/ringcentral-video.yaml`.

Target steps:

- `meeting-controls-tour` -> `meeting-overview`
- `meeting-controls-tour` -> `explain-meeting-info`
- `meeting-controls-tour` -> `explain-network-quality`
- `meeting-controls-tour` -> `explain-view-layout`

Target delta:

- Spanish demo narration: `7/51` -> `11/51`.
- Spanish `meeting-controls-tour`: `0/22` -> `4/22`.
- Spanish `vbg-blur-demo` remains `4/4`.
- Spanish `meeting-basics-demo` remains `3/3`.
- Spanish `meeting-control-map-demo` remains `0/22`.
- Spanish Q&A remains `12/12` questions and `12/12` answers.
- Spanish aliases remain `questionAliases.es present on 1/27 entrypoints (3 aliases)`.
- Spanish runtime remains unsupported.

This is the safest useful next increment after Cycle 120 because the new `doctor --localization-language es` guard now makes partial Spanish package coverage explicit without promoting Spanish to runtime presenter support.

## Why This Fits Demand

Demand discovery: Spanish has complete Q&A and two complete short demo wedges. The remaining gap is the two large 22-step tours. A four-step orientation/status wedge starts the larger `meeting-controls-tour` without taking on recording, notes/transcript, share, invite, settings, or leave/end wording in the same cycle.

UI/performance: this should be package text and focused tests only. It must not change open steps, action placement, action offsets, locators, controller UI, package indexes, question routing, diagnostics behavior, or runtime performance paths. The performance/index guard remains valuable, but the current code already has validation-time package indexes and timing logs; the next performance slice should be a dedicated measured guard, not mixed with localization.

Language/tone: Spanish should remain calm product-demo narration with literal RingCentral UI labels where the UI labels are English. The wedge should explain the meeting window, meeting information, network quality, and view layout without reading private values, diagnosing network cause, or implying runtime Spanish voice support.

Skills: no runtime presenter skills, `presenter/soul.md`, `presenter/memory.md`, Codex home skills, or skill-candidate files should change. The maintenance playbook already contains the relevant localization lifecycle rule, and Cycle 120 encoded that boundary in CLI diagnostics.

RingCentralVideo knowledge: these four steps map to core low-to-medium-risk orientation surfaces. Meeting info can expose meeting ID, link, dial-in, and encryption details, so the Spanish line should say AiPresenter summarizes purpose without reading private values. Network quality should describe call-health troubleshooting without inventing causes. View layout should be framed as local display arrangement, not a meeting-state change.

## Why Not The Other Candidates

A full Spanish 22-step flow is too broad for one safe cycle. It would touch invitation privacy, participant names, chat content, device menus, screen sharing, reactions, More, recording, notes/transcript, settings, and leave/end boundaries all at once.

The performance/index guard is still attractive, but prior cycles already added package lookup indexes, Q&A candidates, alias match ordering, and question timing logs. A measured performance guard should be planned separately around a specific target and behavior-parity test.

Diagnostics/report usability polish just had the highest-leverage improvement in Cycle 120. Further polish is lower value than using the new `--localization-language` guard to advance package coverage.

RingCentral knowledge/playbook/skill-candidate work is useful when new evidence or repeated maintenance friction appears. For Cycle 121, there is no need to promote a skill candidate or edit durable knowledge just to add four package-local narration lines.

## Out Of Scope

- Do not add Spanish runtime support.
- Do not add `es` to runtime language choices, controller selectors, `voices`, providers, profiles, speech assets, no-match answers, or presenter voice validation.
- Do not add Spanish narration to `meeting-control-map-demo` or to later `meeting-controls-tour` steps beyond the four listed above.
- Do not add or change Q&A, `questionAliases.es`, question routing, diagnostics checks, package indexes, locators, open steps, cleanup behavior, operation types, action placement, or offsets.
- Do not edit README, the maintenance playbook, RingCentral knowledge docs, presenter skills, runbooks, or other handoff files.
- Do not claim live RingCentral acceptance.
- Do not stage `.coverage`.

## Acceptance Criteria

A Cycle 121 implementation satisfies this demand when:

- Exactly four new Spanish demo-step narration strings are added, all under `meeting-controls-tour`.
- The four step ids are `meeting-overview`, `explain-meeting-info`, `explain-network-quality`, and `explain-view-layout`.
- Existing English, Chinese, and Japanese text remains unchanged.
- Existing `placement` and `actionOffsetMs` values for those steps remain unchanged.
- The Spanish meeting-info line preserves the privacy boundary around meeting details, link, dial-in options, and encryption information.
- The Spanish network-quality line does not infer packet loss, jitter, device problems, or meeting health beyond the visible surface.
- The Spanish view-layout line describes local layout choices such as Gallery view or Full screen without implying membership, media, recording, or sharing state changes.
- `localization-report --package ringcentral-video --language es` reports `11/51` demo steps and `meeting-controls-tour: 4/22 narration localized`.
- The same report still shows `vbg-blur-demo: 4/4`, `meeting-basics-demo: 3/3`, `meeting-control-map-demo: 0/22`, Q&A `12/12`, and Spanish aliases `1/27 (3 aliases)`.
- `doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --localization-language es` still exits nonzero with incomplete Spanish localization and runtime language support failure.
- `demo --profile ringcentral-video --package ringcentral-video --flow meeting-controls-tour --language es --dry-run` still rejects Spanish as an unsupported runtime presenter language.
- Chinese and Japanese `localization-report --require-complete` still pass.

## Suggested Technical Handoff Prompt

You are the Cycle 121 technical-scan subagent for AiPresenter. Inspect `packages/ringcentral-video.yaml`, Spanish localization tests, `src/ai_presenter/packages/localization_status.py`, `src/ai_presenter/runtime/voice.py`, and Cycle 120 diagnostics behavior. Produce a technical handoff for adding Spanish `localizedText.es` only to `meeting-controls-tour` steps `meeting-overview`, `explain-meeting-info`, `explain-network-quality`, and `explain-view-layout`. Preserve action placement, offsets, open steps, Q&A, aliases, runtime Spanish rejection, diagnostics counts, and package indexes. Identify focused tests in `tests/unit/test_material_packages.py` and `tests/unit/test_cli.py`, plus CLI checks for Spanish localization report, Spanish doctor localization diagnostics, Spanish runtime rejection, and Chinese/Japanese complete reports. Do not modify files except your assigned handoff.

## Suggested Test-Review Handoff Prompt

You are the Cycle 121 test-review subagent for AiPresenter. Review the Spanish meeting-controls orientation wedge. Verify Spanish demo narration moves from `7/51` to `11/51`, `meeting-controls-tour` moves from `0/22` to `4/22`, the three previously complete Spanish surfaces remain unchanged, Spanish Q&A remains `12/12`, Spanish aliases remain `1/27` and `3`, and Spanish runtime remains unsupported. Run focused package/CLI localization tests, `localization-report --language es`, `doctor --require-localization --localization-language es`, Spanish `demo --dry-run` rejection, Chinese/Japanese `--require-complete` reports, and `git diff --check`. Confirm no README, durable knowledge, runtime voice, diagnostics, package-index, or presenter-skill drift occurred, and confirm `.coverage` is unstaged.

## Suggested Experience Handoff Prompt

You are the Cycle 121 experience subagent for AiPresenter. Capture the user-facing lesson from starting Spanish coverage of the large `meeting-controls-tour` with an orientation/status wedge. Explain how to describe this as partial package localization, not Spanish presenter support. Note the tone boundaries for meeting information privacy, network-quality uncertainty, and local view-layout changes. Recommend whether the next Spanish wedge should continue through `explain-report-issue` and invite/participants/chat, or pause for a performance/index guard. Do not modify files except your assigned experience handoff.

## Read-Only Evidence Used

Inspected:

- `README.md`
- `docs/knowledge/ai-presenter-maintenance.md`
- `docs/agent-handoffs/cycle-118-*`
- `docs/agent-handoffs/cycle-119-*`
- `docs/agent-handoffs/cycle-120-*`
- `docs/knowledge/ringcentral-video/evidence-index.md`
- `packages/ringcentral-video.yaml`
- `src/ai_presenter/cli.py`
- `src/ai_presenter/runtime/diagnostics.py`
- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/runtime/voice.py`
- `src/ai_presenter/packages/models.py`
- `src/ai_presenter/packages/localization_status.py`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_diagnostics.py`
- `tests/unit/test_questions.py`

Observed current CLI state:

- `localization-report --package ringcentral-video --language es` exits `0` and reports `7/51` demo steps, `vbg-blur-demo: 4/4`, `meeting-basics-demo: 3/3`, `meeting-controls-tour: 0/22`, `meeting-control-map-demo: 0/22`, Q&A `12/12`, and aliases `1/27 (3 aliases)`.
- `doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --localization-language es` reaches diagnostics and exits nonzero with `required es localization incomplete: 7/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers` plus `runtime language support` failure for `--language es`.
- Runtime Spanish remains unsupported.
- Worktree had `.coverage` modified before this handoff; it is out of scope.
