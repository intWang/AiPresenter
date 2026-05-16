# Cycle 124 Risk Scan

Date: 2026-05-16

Scope: documentation-only risk pre-review for Spanish `meeting-control-map-demo` package-local localization. This scan does not change business code, package YAML, tests, runtime language support, generated artifacts, or existing handoffs.

## Risk assessment

Current verified Spanish package status is still partial: `localization-report --package ringcentral-video --language es` reports `29/51` demo steps, `meeting-controls-tour: 22/22`, `meeting-control-map-demo: 0/22`, Q&A `12/12`, and `questionAliases.es` on `1/27` entrypoints with `3` aliases. The intended next package-local slice would move `meeting-control-map-demo` to `22/22` and Spanish demo narration to `51/51`; that is package completeness only, not Spanish runtime readiness.

Main risks for the `meeting-control-map-demo` 22/22 slice:

- Privacy: Spanish narration must not read or expose Meeting ID, meeting links, dial-in details, host data, participant names, chat contents, notes, recording metadata, invite data, or network details. Meeting-info, participants, chat, notes, recording, invite, and network steps should describe control locations and safe intent without disclosing observed values.
- Dangerous meeting actions: `Share`, `Recording`, `Notes`, microphone/camera toggles, audio/video menus, background/settings changes, reactions, raise-hand state, invite/add-coworker flows, and `Leave` can affect the live meeting or operator state. Spanish wording must remain explain-first and confirmation-bound, and must not imply the agent will click, start, stop, leave, invite, publish, share, record, or reveal anything automatically.
- Runtime Spanish mis-enablement: completing all 22 map-demo Spanish strings will likely make `localization-report --language es --require-complete` pass. That must not add `es` to runtime language validation, provider catalogs, voice aliases, profile routes, speech routes, controller language choices, manual acceptance claims, README support tables, or the `voices` command.
- Count drift: expected completed package counts are exactly `51/51` demo steps, `meeting-controls-tour: 22/22`, `meeting-control-map-demo: 22/22`, Q&A questions `12/12`, Q&A answers `12/12`, and aliases `1/27 (3 aliases)`. Any smaller slice must keep reports and handoffs honest about partial status.
- Documentation lifecycle boundary: durable docs and handoffs must keep package localization, diagnostics completeness, runtime language support, voice readiness, controller availability, provider support, and live acceptance as separate gates. A complete package report is not a lifecycle promotion.
- Submit hygiene: `.coverage` is modified in the worktree and is generated drift. It must not be staged, committed, rewritten, or used as evidence for this documentation-only risk scan.

## What must not change

- No files except `docs/agent-handoffs/cycle-124-risk-scan.md` for this risk-scan subagent.
- No edits to `packages/ringcentral-video.yaml`, runtime code, CLI behavior, tests, profiles, README, durable lifecycle docs, generated artifacts, or previous handoff files.
- No runtime Spanish enablement unless a separate runtime-promotion cycle explicitly owns voice inventory, provider routing, profile support, controller UX, acceptance criteria, and durable docs.
- No claims that Spanish is supported, runnable, live-ready, voice-ready, manually accepted, or available through `demo/controller --language es`.
- No changes to action placement, locators, `actionOffsetMs`, cleanup behavior, operation ids, Q&A matching order, alias precedence, package index semantics, or diagnostics semantics while adding localized narration.
- No translation of RingCentral UI labels that the operator must visually find, including `Meeting information`, `Network quality`, `Views`, `Report`, `Add coworkers`, `Invite`, `Participants`, `Chat`, `Mute`, `Audio options`, `Start video`, `Share`, `Reactions`, `Raise hand`, `More`, `Recording`, `Notes`, `Background`, `Settings`, and `Leave`.
- No staging or committing `.coverage` or unrelated files from other agents.

## Verification gates

For this documentation-only Cycle 124 risk scan:

- `git diff -- docs/agent-handoffs/cycle-124-risk-scan.md`
- `git diff --check -- docs/agent-handoffs/cycle-124-risk-scan.md`
- `git status --short`

Expected docs-only outcome: only `docs/agent-handoffs/cycle-124-risk-scan.md` is changed by this subagent; `.coverage` remains an unrelated unstaged generated file; no business code, package YAML, tests, README, durable docs, or generated artifacts are modified.

For the future Spanish `meeting-control-map-demo` package-localization slice:

- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_cli.py::test_localization_report_outputs_spanish_meeting_controls_tour tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_spanish_meeting_controls_tour tests\unit\test_diagnostics.py::test_diagnostics_require_localization_flags_package_only_runtime_language`
- `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language es`
- `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language es --require-complete`
- `.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --localization-language es`
- `.\.venv\Scripts\ai-presenter demo --profile ringcentral-video --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run`
- `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language zh --require-complete`
- `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja --require-complete`
- `git diff --check`
- `git status --short`

Expected localization outcome: Spanish package report shows `51/51` demo steps and `meeting-control-map-demo: 22/22`; Spanish package `--require-complete` may pass; Spanish runtime gates still reject `es`; Chinese and Japanese complete reports still pass; `.coverage` remains unstaged.

## Review focus

Review Spanish map-demo text as safety-critical operator guidance:

- Private meeting data is referenced only by category, never read aloud or exposed.
- Risky controls remain framed as places to review or actions requiring explicit user confirmation.
- English RingCentral UI labels remain preserved where they are visual anchors.
- State-changing actions distinguish local-only effects from actions visible to other participants.
- Network and meeting diagnostics do not infer causes without observed values.

Review lifecycle and count boundaries:

- `localization-report` measures package text coverage.
- `--require-complete` measures package localization completeness, not runtime support.
- `doctor --localization-language es --require-localization` may inspect Spanish package coverage but must still surface runtime Spanish unsupported status.
- `demo/controller --language es` must remain rejected until runtime promotion is deliberately implemented.
- Handoffs and tests should state exact count deltas: `29/51` to `51/51`, `0/22` to `22/22`, Q&A still `12/12`, aliases still `1/27 (3 aliases)`.

Review submit hygiene:

- This risk-scan subagent changed only `docs/agent-handoffs/cycle-124-risk-scan.md`.
- Do not stage `.coverage`.
- Do not include unrelated files from other agents in any future localization commit.

## Decision

Proceed with Spanish `meeting-control-map-demo` only as a package-local localization slice if the implementation owner keeps the runtime rejection gates intact and records the exact count transition. Treat `51/51` package coverage as a localization milestone, not a Spanish runtime launch signal. Block or re-scope the slice if it changes runtime language support, expands aliases or Q&A, weakens dangerous-action confirmation language, exposes private meeting data, or stages `.coverage`.
