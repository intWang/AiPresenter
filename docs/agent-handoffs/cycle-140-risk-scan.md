# Cycle 140 Risk Scan: Spanish Optional Entrypoint Display Metadata

Date: 2026-05-17
Cycle: 140
Scope: risk scan only for adding Spanish `localizedTitles.es` and
`localizedPurposes.es` to exactly three optional RingCentral Video UI-control
entrypoints:

- `ringcentral.video.toolbar.audio-menu`
- `ringcentral.video.toolbar.video-menu`
- `ringcentral.video.more.background`

This handoff is the only file owned by this scan. Do not revert concurrent
source, test, package, docs, `.coverage`, or handoff edits made by others.

## Read Basis

- Package routes and copy: `packages/ringcentral-video.yaml`
- Current demand handoff: `docs/agent-handoffs/cycle-140-demand-analysis.md`
- Prior risk/demand/technical handoffs: Cycles 135, 136, 138, and 139
- Durable docs: `docs/knowledge/language-lifecycle.md`,
  `docs/knowledge/ringcentral-video/source-index.md`,
  `docs/knowledge/ringcentral-video/privacy-matrix.md`,
  `docs/knowledge/ringcentral-video/locator-matrix.md`,
  `docs/knowledge/ringcentral-video/runtime-safety-routing.md`,
  `docs/knowledge/ringcentral-video/validation-checklist-index.md`, and
  `docs/knowledge/ringcentral-video/acceptance-runs.md`
- Tests: `tests/unit/test_material_packages.py`,
  `tests/unit/test_cli.py`, and `tests/unit/test_questions.py`

No `data` directory is present in this checkout. During this scan, concurrent
worktree edits appeared for the candidate implementation. Treat those as other
agents' work: review with them, but do not revert them from this handoff.

## Current State Observed

- Required Spanish package localization remains complete: `51/51` demo steps,
  `12/12` localized questions, and `12/12` localized answers.
- Spanish aliases remain broad but curated: `questionAliases.es` on `26/27`
  entrypoints with `69` aliases.
- The intended candidate moves optional Spanish display metadata from `5/27` to
  `8/27` for both `localizedTitles.es` and `localizedPurposes.es`.
- `entrypoints --language es`, `--language Spanish`, and `--language es-MX`
  are package-local inspection paths. They do not validate runtime voice
  providers, OpenAI availability, local SAPI/Piper assets, controller/demo
  execution, virtual microphone routing, or live RingCentral Video acceptance.
- Spanish runtime speech remains OpenAI-backed only. Local SAPI, Piper, fake,
  and bind-speaker/local profiles must still reject Spanish before runtime.
- Live RingCentral route evidence remains limited. The relevant `More`
  occurrence routes are low repo confidence and need dated manual acceptance
  before anyone treats them as live-safe across current builds, locales, DPI
  settings, layouts, and meeting states.

## Semantic Risks

`localizedTitles` and `localizedPurposes` are display and inspection metadata.
They must not become match candidates, aliases, route eligibility signals,
question-policy changes, or interrupt permission.

The implementation must not imply:

- device switching for microphone, speaker, camera, computer audio, phone audio,
  or video settings;
- reading, translating, logging, screenshotting, or narrating actual device
  labels, selected-device labels, audio levels, camera labels, or settings
  values;
- selecting `Blur`, choosing a virtual background, uploading or inspecting
  custom backgrounds, changing Mirror my video, or proving the room is hidden;
- runtime Spanish voice support beyond OpenAI-backed profiles;
- local SAPI/Piper Spanish readiness;
- live RingCentral acceptance or current-build locator reliability.

Keep the distinction sharp: package display copy can explain where a surface is,
but operation safety still comes from `questionPolicy`, `_can_operate`, Q&A-first
matching, reviewed `openSteps`, cleanup behavior, and dated acceptance evidence.

## Copy Risks By Entrypoint

| Entrypoint | Route risk | Copy boundary |
| --- | --- | --- |
| `ringcentral.video.toolbar.audio-menu` | `More` occurrence 1, `cleanup: escape`, low repo confidence. Menu can expose `Microphone`, `Speaker`, `Leave computer audio`, `Use phone audio`, levels, and deeper audio settings. | Spanish title/purpose may say this opens the audio menu for navigation or recovery. It must not say AiPresenter switches microphone/speaker, leaves computer audio, selects phone audio, tests sound, reads device names, reads levels, or changes audio settings. |
| `ringcentral.video.toolbar.video-menu` | `More` occurrence 2, `cleanup: escape`, low repo confidence. Menu can expose selected camera and `More video settings`. | Spanish copy may say this opens the camera/video menu and points toward `More video settings`. It must not say AiPresenter changes cameras, toggles video, reads selected camera labels, inspects preview, opens deeper settings, improves quality, or changes background/appearance. |
| `ringcentral.video.more.background` | `More` occurrence 3 -> `Background`, `cleanup: settings`, low repo confidence. Settings can expose room privacy, custom assets, uploads, video backgrounds, and Mirror my video. | Spanish copy may say `More` > `Background` opens `Settings` on the `Background` tab for reviewing `Blur` and virtual background options. It must not say Blur is selected, the room is hidden, custom images are safe to inspect, uploaded assets are read, or any background setting changes by default. |

Keep product labels literal where the user must find them in RingCentral:
`Microphone`, `Speaker`, `Leave computer audio`, `Use phone audio`,
`More audio settings`, `More video settings`, `More`, `Background`, `Blur`, and
`Settings`.

Avoid Spanish verbs or claims that convert navigation into action, especially:
`cambia`, `selecciona`, `elige`, `activa`, `desactiva`, `aplica`, `corrige`,
`garantiza`, `lee`, `detecta`, `confirma`, or `diagnostica` when they refer to
devices, settings, previews, background state, provider support, or live
acceptance. Negative boundary clauses such as "sin cambiar..." are acceptable
when they clearly limit behavior.

## Product Risks

- The three routes are useful operator surfaces, but they are not accepted live
  routes. Unit tests and CLI inspection can prove package shape, not RingCentral
  acceptance.
- `More` occurrence routing is brittle. Audio menu, video menu, and overflow
  More are distinguished by occurrence order observed only in a narrow empty-room
  state.
- RingCentral UI labels are assumed English. Spanish package copy must not imply
  the live RingCentral app is localized or that Spanish UI labels are locatable.
- Audio/video/background settings can reveal private local environment details.
  Do not read or store device names, selected labels, room imagery, thumbnails,
  custom files, account preferences, or meeting identifiers as evidence for this
  copy-only wedge.
- Background wording is privacy-positive only if it stays explanatory. A promise
  that Blur protects privacy, hides the room, or is currently active would
  overclaim both product state and user consent.

## Test Risks

Count drift is the main local regression risk. Package YAML, focused tests, and
current durable docs must move together from `5/27` to `8/27`; historical
handoffs should not be rewritten just to change old counts.

Required checks for the implementation owner:

- Assert the exact three localized entrypoint ids, no more and no fewer.
- Assert exact Spanish title/purpose strings for the three entries.
- Assert `localizedTitles.es` and `localizedPurposes.es` report `8/27`.
- Assert required Spanish completeness stays `51/51`, `12/12`, and `12/12`.
- Assert `questionAliases.es` stays `26/27` with `69` aliases.
- Assert `--require-complete` still ignores optional title/purpose metadata.
- Assert `entrypoints` output marks the three new entries localized while
  unrelated entries keep expected localized/fallback markers.
- Keep or run matcher-boundary tests proving localized title/purpose text alone
  does not create a question match or change alias precedence.
- Keep provider-boundary tests proving `entrypoints --language` does not inspect
  runtime voices and local Spanish profiles still reject before runtime.

Recommended focused verification:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_complete_spanish_package tests\unit\test_material_packages.py::test_ringcentral_spanish_display_metadata_covers_optional_menu_surfaces tests\unit\test_material_packages.py::test_ringcentral_spanish_display_metadata_counts_match_durable_docs tests\unit\test_material_packages.py::test_entrypoint_localized_title_and_purpose_do_not_affect_match_candidates tests\unit\test_material_packages.py::test_entrypoint_title_and_purpose_counts_do_not_gate_required_localization
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_cli.py::test_localization_report_normalizes_spanish_language_aliases tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_entrypoints_language_normalizes_spanish_alias_for_display_metadata tests\unit\test_cli.py::test_entrypoints_language_uses_package_local_metadata_without_runtime_voice_validation
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_spanish_entrypoint_answer_uses_localized_pilot_copy tests\unit\test_questions.py::test_ringcentral_spanish_unseeded_entrypoint_keeps_alias_label_fallback tests\unit\test_questions.py::test_ringcentral_spanish_location_questions_match_package_aliases_without_legacy_table
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language Spanish
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting toolbar" --language es
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "More menu" --language es-MX
.\.venv\Scripts\python.exe -m ruff check --no-cache packages tests
git diff --check
git status --short
```

Expected status: only intended implementation files for that owner, this risk
scan if it is part of the cycle, pre-existing `.coverage`, and any other
clearly unrelated concurrent handoff edits. Do not stage or commit unless the
implementation task explicitly asks for it.

## Final Recommendation

Go, with constraints.

This is a reasonable low-to-medium risk package-content wedge if it remains
exactly three entrypoints, display metadata only, and count-guarded. The copy
should be approved only if it describes navigation/review surfaces and includes
clear "no change / no reading private labels" boundaries.

No-go if the implementation expands to more entrypoints, changes aliases, Q&A,
routes, cleanup, matcher behavior, controller interrupts, provider/runtime voice
support, `--require-complete`, or live RingCentral acceptance claims. No-go if
copy implies device switching, device-label reading, blur/background selection,
custom asset inspection, local Spanish voice support, or live route acceptance.
