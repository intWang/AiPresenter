# Cycle 123 Risk Scan

Date: 2026-05-16

Scope: documentation-only risk pre-review for the next Spanish localization step. This scan does not change business code, package YAML, tests, runtime language support, generated artifacts, or existing handoffs.

## Risk assessment

Current Spanish baseline is package-local and incomplete: `localization-report --package ringcentral-video --language es` reports `29/51` demo steps, `meeting-controls-tour: 22/22`, `meeting-control-map-demo: 0/22`, Q&A `12/12`, and `questionAliases.es` on `1/27` entrypoints with `3` aliases. Spanish remains unsupported by presenter runtime, even though package text exists.

The two plausible Cycle 123 options have different risk profiles:

- Continuing Spanish `meeting-control-map-demo` package localization is coherent but higher risk. It would move Spanish demo narration from `29/51` to `51/51`, making `localization-report --language es --require-complete` pass. That increases the chance reviewers or operators misread package completeness as Spanish runtime readiness.
- Adding language lifecycle documentation and guardrails is lower risk and should come first if the team is not explicitly ready to own runtime promotion. It clarifies that package localization, diagnostics completeness, Q&A coverage, aliases, voice routes, controller choices, and provider support are separate lifecycle gates.

Main risks to manage:

- Privacy: Spanish narration must not read or expose Meeting ID, meeting links, dial-in details, host data, participant names, chat contents, notes, recording metadata, or invite data unless the user explicitly asks. Meeting-info and chat-related steps should describe where controls are and what data may be present, not disclose values.
- Dangerous meeting actions: `Leave`, `Recording`, `Share`, `Notes`, camera/microphone toggles, settings/background changes, reactions, and invite/add-coworker flows must remain explain-first and confirmation-bound. Spanish text must not imply the agent will perform destructive or state-changing actions automatically.
- Runtime Spanish mis-enablement: completing `meeting-control-map-demo` may make Spanish package coverage complete, but must not add `es` to runtime language validation, voice aliases, provider catalogs, speech routes, controller language pickers, manual acceptance claims, or the `voices` command.
- Count drift: if `meeting-control-map-demo` is localized in full, expected Spanish package counts become exactly `51/51`, `meeting-controls-tour: 22/22`, `meeting-control-map-demo: 22/22`, Q&A `12/12`, and aliases `1/27 (3 aliases)`. Partial work must not pretend completion; tests and handoffs should state exact before/after counts.
- Alias and Q&A drift: Spanish Q&A and aliases are already complete for the current seed scope. Do not add route aliases casually; alias expansion affects Q&A-first matching and duplicate-alias diagnostics.
- Submit hygiene: `.coverage` is already dirty in the worktree and appears to be a generated artifact. It must not be staged or included in a localization, docs, or guardrail commit.

## What must not change

- No runtime support for Spanish unless a separate runtime-promotion cycle explicitly owns voice inventory, provider routing, profile support, controller UX, acceptance criteria, and docs.
- No changes to `src/ai_presenter/runtime/voice.py`, voice providers, speech routes, presenter runtime language validation, or controller language choices for a package-local localization cycle.
- No wording in README, runbooks, handoffs, or durable docs that says Spanish is supported, runnable, live-ready, voice-ready, manually validated, or accepted by `demo/controller --language es`.
- No diagnostics shortcut that treats package completeness as runtime support.
- No changes to action placement, locators, `actionOffsetMs`, cleanup behavior, `questionPolicy`, operation entrypoint ids, Q&A matching order, alias precedence, or package index semantics while localizing text.
- No translation of RingCentral UI labels the operator must visually find, such as `Meeting information`, `Network quality`, `Views`, `Report`, `Add coworkers`, `Invite`, `Participants`, `Chat`, `Mute`, `Audio options`, `Start video`, `Share`, `Reactions`, `Raise hand`, `More`, `Recording`, `Notes`, `Background`, `Settings`, and `Leave`.
- No staging or committing `.coverage` or unrelated files from other agents.

## Verification gates

For a guardrail/docs-only Cycle 123:

- `git diff -- docs docs/agent-handoffs`
- `rg -n "Spanish.*supported|es.*supported|voice-ready|live-ready|--language es" docs README*`
- `git diff --check`
- `git status --short`

Expected docs-only outcome: only intended documentation files changed; no business code, package YAML, tests, generated artifacts, or runtime wording changed; `.coverage` remains unstaged.

For a full Spanish `meeting-control-map-demo` package-localization Cycle 123:

- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_cli.py::test_localization_report_outputs_spanish_meeting_controls_tour tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_spanish_meeting_controls_tour tests\unit\test_diagnostics.py::test_diagnostics_require_localization_flags_package_only_runtime_language`
- `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language es`
- `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language es --require-complete`
- `.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --localization-language es`
- `.\.venv\Scripts\ai-presenter demo --profile ringcentral-video --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run`
- `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language zh --require-complete`
- `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja --require-complete`
- `git diff --check`
- `git status --short`

Expected full-localization outcome: Spanish package report shows `51/51` demo steps and `meeting-control-map-demo: 22/22`; Spanish `--require-complete` may pass for package coverage; Spanish `doctor --localization-language es --require-localization` still fails runtime language support; Spanish `demo --language es --dry-run` still rejects before runtime launch with `Unsupported presenter language: es`; Chinese and Japanese complete reports still pass.

## Review focus

Review Spanish `meeting-control-map-demo` wording as safety-critical operator guidance, not only translation coverage:

- It should explain controls and map behavior without opening private data, reading attendee or chat content, or implying live validation.
- It should preserve English RingCentral product labels where the operator must locate UI.
- It should distinguish local view changes from actions affecting other meeting participants.
- It should make recording, leaving, sharing, notes, invite, media toggles, settings, and background changes confirmation-bound.
- It should avoid diagnosing network cause without observed values.

Review lifecycle boundaries:

- `localization-report` answers whether package text exists for a language.
- `--require-complete` answers whether package localization is complete, not whether runtime can speak or run that language.
- `doctor --localization-language es --require-localization` should be able to inspect Spanish package coverage while still failing runtime language support.
- `demo/controller --language es` must remain rejected until runtime promotion is deliberately implemented.

Review submit hygiene:

- Diff should contain only the assigned files for the chosen Cycle 123 path.
- This risk-scan subagent changed only `docs/agent-handoffs/cycle-123-risk-scan.md`.
- Do not stage `.coverage`.

## Decision

Recommend doing language lifecycle documentation and guardrails before completing Spanish `meeting-control-map-demo`, unless Cycle 123 explicitly commits to preserving the runtime rejection gates above. If the team proceeds with `meeting-control-map-demo`, do it as package-local text only, update counts exactly to `51/51`, keep aliases and Q&A unchanged, and make runtime Spanish support a hard no-go for this cycle.
