# Cycle 125 Experience: Spanish Alias Readiness Lessons

Date: 2026-05-17
Cycle: 125
Scope: experience extraction only. This file records reusable lessons from the
Cycle 125 Spanish alias slice for future optimization work.

## 1) Package-local completeness is not runtime support

Cycle 125 reinforced a lifecycle boundary that future language work should keep
explicit: a language can be package-local complete without being a runnable
presenter language.

For RingCentral Video, Spanish reached package-local completeness before this
cycle:

- Demo narration: `51/51`
- Localized Q&A questions: `12/12`
- Localized Q&A answers: `12/12`

Cycle 125 then expanded Spanish package-owned aliases to improve question
discovery, but deliberately kept runtime Spanish unsupported. That distinction
matters because runtime promotion has a much wider surface than package content:
presenter language normalization, voice/provider routing, voice catalogs,
controller language choices, profile readiness, setup docs, runbooks, and live
acceptance evidence.

Reusable lesson: do not treat `localization-report --language es
--require-complete` as proof that `demo --language es` should run. The former is
a package content gate. The latter is a runtime capability gate. Doctor should
continue to make that distinction visible by allowing Spanish localization to be
`[OK]` while runtime language support remains `[FAIL]`.

## 2) Aliases and Q&A fuzzy fallback need a clear ordering contract

Cycle 125 exposed an important routing nuance. Runtime question matching already
prioritizes exact Q&A, safety Q&A, and fragment Q&A before package aliases. That
is the right safety posture because authored Q&A is the best place for privacy,
consent, and content-reading boundaries.

However, the final fuzzy Q&A token fallback is different. It can be broader than
curated package aliases and may steal location/control questions that should
resolve through package-owned aliases. The implementation therefore updated
matching so curated package aliases are not overridden by that last fuzzy Q&A
token fallback. Exact Q&A and safety-oriented Q&A checks still stay ahead of
aliases.

Reusable lesson: the ordering should be read as:

1. Q&A exact/safety/fragment matches protect authored answers.
2. Package-owned aliases handle curated control-location and discovery wording.
3. Legacy aliases and broad token fallback fill remaining gaps.

When future aliases seem ineffective, inspect whether a fuzzy Q&A fallback is
winning before assuming the alias phrase is wrong. When future safety prompts
route through aliases, add or refine localized Q&A prompts instead of broadening
aliases.

## 3) Sensitive entrypoint aliases need location-only guardrails

Spanish aliases are substring triggers after `strip().casefold()` normalization.
They are not accent-folded, punctuation-stripped, or scoped by selected presenter
runtime language. That makes short or action-like aliases risky, especially for
sensitive controls.

The safe pattern from this cycle is to phrase sensitive aliases as explicit
location/control labels, not commands or content requests. Good shapes include
`panel de ...`, `boton de ...`, `menu de ...`, `ubicacion de ...`, and
`controles de ...`. Risky shapes include verbs or broad nouns that imply reading,
copying, sending, starting, stopping, changing state, leaving, inviting, sharing,
recording, summarizing, or exporting.

Entrypoints that deserve extra caution:

- Meeting information: IDs, links, dial-in details, host details, and security
  information.
- Recording: consent and meeting-state changes.
- Notes/transcript: reading, summarizing, or promising artifacts.
- Share: starting share or inspecting private shared content.
- Invite/Add coworkers: names, emails, links, and external participants.
- Participants/Chat: private names, roles, and messages.
- Raise hand/Reactions/Leave: visible or destructive meeting actions.

Reusable lesson: for sensitive entrypoints, either skip aliases or keep them
location-only and pair them with tests proving `can_operate` and Q&A-first
safety still hold. Do not use alias expansion to encode actions.

## 4) Count assertions are useful when they are exact

This cycle kept exact expected counts instead of loosening tests. That made the
scope of the alias expansion auditable:

- Spanish aliases moved from `1/27 (3 aliases)` to `26/27 (69 aliases)`.
- Package-owned aliases moved from `90` to `156`.
- Q&A prompt count stayed at `84`.
- Q&A alias substring risk stayed at `11`.

Reusable lesson: exact count assertions are valuable for package-local language
work because they catch accidental alias drift, unintended runtime promotion,
and weakened diagnostics. If a count changes, update the expectation only after
reviewing the cause and documenting why the new count is intentional.

## 5) Verification commands worth keeping

Keep the focused pytest command that covers package counts, routing, safety,
diagnostics, and CLI boundary behavior:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_diagnostics.py tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_cli.py::test_localization_report_require_complete_passes_for_spanish_package tests\unit\test_cli.py::test_demo_rejects_unknown_language_before_runtime tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow tests\unit\test_cli.py::test_doctor_require_localization_accepts_package_only_spanish_language tests\unit\test_cli.py::test_doctor_require_localization_language_overrides_runtime_voice
```

Keep the Spanish package-local report:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
```

Keep the package/runtime boundary doctor check:

```powershell
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --localization-language es
```

Expected shape: localization is OK, runtime language support is FAIL.

Keep the runtime rejection check:

```powershell
.\.venv\Scripts\ai-presenter.exe demo --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
```

Expected shape: fails with `Unsupported presenter language: es`.

Keep cross-language strict localization checks when alias work touches shared
package structures:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language zh --require-complete
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
```

Keep the hygiene checks:

```powershell
git diff --check
git status --short
```

Reusable lesson: the high-value verification set is not just "tests pass". It
must prove four things at once: Spanish package-local completeness, Spanish
runtime non-support, Q&A-first safety, and alias diagnostics stability.
