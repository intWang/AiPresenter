# Cycle 122 Risk Scan

Date: 2026-05-16

Scope: documentation-only risk pre-review for a narrow Spanish `meeting-controls-tour` package-localization slice. This scan does not change business code, package YAML, tests, runtime language support, or generated artifacts.

## Risk assessment

The safest Cycle 122 content slice is a small Spanish narration wedge under `meeting-controls-tour`, not a runtime language promotion. Cycle 121 preserved package content and implemented a diagnostics index guard, so the current Spanish baseline remains package-local and incomplete: `localization-report --package ringcentral-video --language es` should still show `7/51` demo steps overall, `meeting-controls-tour: 0/22`, `meeting-control-map-demo: 0/22`, Q&A `12/12`, and Spanish aliases `1/27 (3 aliases)` until the new slice is intentionally added.

If Cycle 122 adds the previously discussed four-step orientation/status wedge for `meeting-controls-tour` (`meeting-overview`, `explain-meeting-info`, `explain-network-quality`, `explain-view-layout`), the expected package-only report state becomes `11/51` demo steps overall and `meeting-controls-tour: 4/22`, while `meeting-control-map-demo` remains `0/22`, Q&A remains `12/12`, and Spanish aliases remain `1/27 (3 aliases)`.

Main risks:

- Runtime Spanish leakage: adding `localizedText.es` must not make `--language es` accepted by `demo`, `controller`, voice validation, provider routing, or the `voices` command.
- Diagnostics/report confusion: `localization-report` is a package coverage report, while `doctor --localization-language es --require-localization` may inspect Spanish package coverage but must still report runtime language support failure.
- UI-label translation drift: RingCentral visible labels such as `Meeting information`, `Network quality`, `Views`, `Gallery view`, `Full screen`, `Report`, `Invite`, `Participants`, `Chat`, `Mute`, `Start video`, `Share`, `Notes`, `Recording`, `More`, and `Leave` should stay literal where the user must find the English UI.
- Scope creep: do not add Spanish Q&A, aliases, `meeting-control-map-demo`, voice/provider/profile support, controller language choices, or docs claiming Spanish presenter support.
- Count drift: Spanish diagnostic and CLI assertions must be updated only to the exact new package-derived totals for the chosen slice.
- Submit hygiene: `.coverage` is already a generated local artifact in the worktree and must remain unstaged; do not sweep it into any docs or content commit.

## What must not change

- No runtime support for Spanish. `es` remains package-local localization coverage only.
- No changes to `src/ai_presenter/runtime/voice.py`, provider catalogs, speech routes, profile voice support, controller voice choices, or presenter runtime language validation unless a separate runtime-promotion cycle is explicitly approved.
- No changes to `doctor --language` semantics. `--language` remains runtime voice input; `--localization-language` remains the package localization selector for required localization checks.
- No changes to `localization-report` semantics. It should not gain runtime support checks or imply that Spanish can run as a presenter voice.
- No Spanish additions outside the selected `meeting-controls-tour` step ids.
- No translation of UI labels that are visible in the RingCentral product when the narration is pointing the user at controls.
- No changes to action placement, `actionOffsetMs`, open steps, cleanup mode, `questionPolicy`, package indexes, Q&A matching, alias precedence, or diagnostics ordering.
- No README, durable knowledge, runbook, or handoff wording that says Spanish is supported, accepted, runnable, voice-ready, live-ready, or manually validated.
- No staging or committing `.coverage` or unrelated files.

## Verification gates

Minimum focused gates for the small Spanish content slice:

- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_cli.py::test_localization_report_lists_ringcentral_package tests\unit\test_cli.py::test_localization_report_reports_spanish_partial_package tests\unit\test_cli.py::test_doctor_require_localization_accepts_package_only_spanish_language tests\unit\test_cli.py::test_demo_rejects_unknown_language_before_runtime`
- `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language es`
- `.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --localization-language es`
- `.\.venv\Scripts\ai-presenter demo --profile ringcentral-video --package ringcentral-video --flow meeting-controls-tour --language es --dry-run`
- `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language zh --require-complete`
- `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja --require-complete`
- `git diff --check`
- `git status --short`

Expected gate outcomes:

- Spanish `localization-report` exits `0` and reports the exact current Spanish package totals for the slice.
- Spanish `doctor --require-localization --localization-language es` exits nonzero until Spanish package coverage is complete, includes incomplete package-localization detail, and includes `[FAIL] runtime language support` for `--language es`.
- Spanish `demo --language es --dry-run` exits nonzero before runtime launch with `Unsupported presenter language: es`.
- Chinese and Japanese complete localization reports still pass.
- `git status --short` shows only the intended assigned files plus any pre-existing generated `.coverage`; `.coverage` must not be staged.

## Review focus

Review the Spanish strings as product guidance, not just translation coverage:

- The four-step orientation wedge should explain the meeting surface, meeting information privacy, network-quality uncertainty, and local view-layout behavior without claiming live validation.
- Meeting identifiers, host details, dial-in values, invite links, attendee names, and chat content should be described as private unless the user explicitly asks for them.
- Network-quality narration should avoid diagnosing cause without observed values.
- View-layout narration should state that the change is local display behavior and does not alter who is in the meeting.
- Keep English RingCentral UI labels literal where the operator must locate controls.

Review diagnostics/report behavior as a lifecycle boundary:

- `localization-report` answers "what package text exists for `es`?"
- `doctor --localization-language es --require-localization` answers "is this package localization complete, and is the selected localization language supported by runtime?"
- `demo/controller --language es` must remain rejected because runtime language support is not present.

Review submit hygiene before any handoff or commit:

- Diff should contain only the assigned content/test/docs files for the implementation cycle.
- This risk-scan subagent changed only `docs/agent-handoffs/cycle-122-risk-scan.md`.
- Do not stage generated `.coverage`.

## Decision

Go only for a narrow package-local Spanish `meeting-controls-tour` wedge with exact count updates and runtime rejection preserved. No-go if the slice requires Spanish voices, profile/provider support, controller language options, translated UI labels, `meeting-control-map-demo` content, Q&A/alias expansion, diagnostics semantics changes, or support wording that implies Spanish runtime availability.
