# Cycle 136 Technical Scan: Spanish Display Metadata Wedge

Date: 2026-05-16

## Scope

Read-only technical scan for the next small Cycle136 implementation slice after
Cycle135 added the durable-doc count guard for optional Spanish entrypoint
display metadata. This scan changed only this handoff file.

Relevant baseline verified during this scan:

- `.coverage` is already modified in the worktree; leave it untouched.
- Spanish required package localization passes for RingCentral Video:
  `51/51` demo steps, `12/12` Q&A questions, and `12/12` Q&A answers.
- Spanish package-owned aliases are present on `26/27` entrypoints with `69`
  aliases.
- Optional Spanish display metadata is still partial:
  `localizedTitles.es` on `2/27` entrypoints and `localizedPurposes.es` on
  `2/27` entrypoints.
- The two current localized display entries are
  `ringcentral.video.overview` and `ringcentral.video.top.network-quality`.
- Cycle135 now protects durable docs with
  `test_ringcentral_spanish_display_metadata_counts_match_durable_docs`.

## Recommendation

Implement a small Spanish display metadata expansion for three low-risk,
non-sensitive entrypoints:

1. `ringcentral.video.top.views`
2. `ringcentral.video.toolbar.more`
3. `ringcentral.video.more.settings`

This moves optional Spanish display metadata from `2/27` to `5/27` while staying
inside package-local inspection and answer-rendering behavior. It is cleaner
than a CLI/report ergonomics change because the count guard is now in place and
the current tests already have natural update points. It is safer than touching
meeting info, chat, participants, share, recording, leave, invite, mic/camera
toggles, or background selection because those surfaces carry stronger privacy
or state-changing implications.

Do not combine this with README polish, CLI output formatting, runtime language
support, provider changes, live acceptance evidence, or broader RingCentral YAML
restructuring.

## Recommended File Touch Set

Primary content:

- `packages/ringcentral-video.yaml`

Tests:

- `tests/unit/test_material_packages.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_questions.py`

Durable docs with count claims:

- `docs/knowledge/language-lifecycle.md`
- `docs/knowledge/ringcentral-video/source-index.md`

Implementation handoff:

- `docs/agent-handoffs/cycle-136-implementation.md`

Do not touch:

- `.coverage`
- `README.md` unless explicitly changing the slice
- profiles, source package models, CLI source, provider code, controller code,
  live acceptance files, historical handoffs

## Proposed YAML Copy

Add `localizedTitles.es` and `localizedPurposes.es` to these entries.

For `ringcentral.video.top.views`:

```yaml
  localizedTitles:
    es: Diseño de vista
  localizedPurposes:
    es: Abre Views para revisar Gallery view o Full screen en tu vista local sin cambiar audio, video ni participantes.
```

For `ringcentral.video.toolbar.more`:

```yaml
  localizedTitles:
    es: Más acciones
  localizedPurposes:
    es: Abre More para mostrar acciones adicionales de la reunión y explicar su ubicación sin iniciar grabaciones ni otros cambios.
```

For `ringcentral.video.more.settings`:

```yaml
  localizedTitles:
    es: Ajustes
  localizedPurposes:
    es: Abre Settings para revisar opciones de audio, video, Background, Translation, Join preferences y General sin cambiar configuraciones ni leer datos privados.
```

Style guardrails:

- Keep visible RingCentral labels literal where users need to find them:
  `Views`, `Gallery view`, `Full screen`, `More`, `Settings`, `Background`,
  `Translation`, `Join preferences`, and `General`.
- Use neutral Spanish. The current package contains UTF-8 text; avoid replacing
  unrelated encoded lines or line endings.
- Do not say the presenter changes layout, starts recording, changes settings,
  reads device/account data, or makes participant/media changes by default.
- Keep this as display metadata only. Do not add new aliases in this slice.

## Test Strategy

Update existing package/report tests:

- In `test_ringcentral_localization_status_reports_complete_spanish_package`,
  change `entrypoint_titles_present` and `entrypoint_purposes_present` from `2`
  to `5`.
- Keep `entrypoints_with_aliases == 26`, `alias_total == 69`,
  `required_localization_complete is True`, and all demo/Q&A counts unchanged.
- The Cycle135 durable-doc count guard should now require both durable docs to
  mention `5/27`.
- Update `test_localization_report_outputs_complete_spanish_package` to expect:
  - `localizedTitles.es present on 5/27 entrypoints`
  - `localizedPurposes.es present on 5/27 entrypoints`

Update CLI localized/fallback inspection:

- In `test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy`,
  `ringcentral.video.top.views` should change from fallback to localized in the
  Meeting top bar output.
- `ringcentral.video.top.meeting-info` should remain fallback and answer-only.
- `ringcentral.video.top.report-issue` should remain fallback.

Update answer-rendering coverage:

- Expand `test_ringcentral_spanish_entrypoint_answer_uses_localized_pilot_copy`
  to include the three new entries and assert exact Spanish title/purpose output.
- Keep `test_spanish_entrypoint_answer_uses_package_alias_label` and
  `test_ringcentral_spanish_unseeded_entrypoint_keeps_alias_label_fallback`
  so unseeded entries still use alias label plus canonical English purpose.
- Add or retain a negative assertion that the English purpose is not present for
  each newly seeded entry.

Suggested answer-rendering cases:

- Question `menú de vista de reunión` returns
  `Diseño de vista: Abre Views ...`
- Question `menú de más acciones` returns
  `Más acciones: Abre More ...`
- Question `ubicación de settings en more` returns
  `Ajustes: Abre Settings ...`

Docs:

- Update current-state Spanish display metadata counts in
  `docs/knowledge/language-lifecycle.md` from `2/27` to `5/27`.
- Update the RingCentral source index package summary and localization summary
  from `2/27` to `5/27`.
- Do not update historical `docs/agent-handoffs/` counts except for the new
  Cycle136 implementation handoff.

## Exact Commands

Run the red checks before or immediately after package edits if doing TDD:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_complete_spanish_package tests\unit\test_material_packages.py::test_ringcentral_spanish_display_metadata_counts_match_durable_docs tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_questions.py::test_ringcentral_spanish_entrypoint_answer_uses_localized_pilot_copy
```

After implementation:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting top bar" --language es
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting toolbar" --language es
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "More menu" --language es
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_complete_spanish_package tests\unit\test_material_packages.py::test_ringcentral_spanish_display_metadata_counts_match_durable_docs tests\unit\test_material_packages.py::test_entrypoint_title_and_purpose_counts_do_not_gate_required_localization tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_cli.py::test_localization_report_require_complete_passes_for_spanish_package tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_entrypoints_language_uses_package_local_metadata_without_runtime_voice_validation tests\unit\test_questions.py::test_ringcentral_spanish_entrypoint_answer_uses_localized_pilot_copy tests\unit\test_questions.py::test_spanish_entrypoint_answer_uses_package_alias_label tests\unit\test_questions.py::test_ringcentral_spanish_unseeded_entrypoint_keeps_alias_label_fallback tests\unit\test_questions.py::test_ringcentral_spanish_location_questions_match_package_aliases_without_legacy_table
.\.venv\Scripts\python.exe -m ruff check tests\unit\test_material_packages.py tests\unit\test_cli.py tests\unit\test_questions.py
rg -n "localizedTitles.es|localizedPurposes.es|2/27|5/27|fully localized|runtime voice|SAPI|Piper|live RingCentral|live acceptance" packages\ringcentral-video.yaml docs\knowledge\language-lifecycle.md docs\knowledge\ringcentral-video\source-index.md tests\unit\test_material_packages.py tests\unit\test_cli.py tests\unit\test_questions.py
git diff --check
git status --short
```

Expected post-implementation CLI facts:

- `localization-report --language es --require-complete` still exits `0`.
- Required localization remains `51/51`, `12/12`, `12/12`.
- Alias count remains `questionAliases.es present on 26/27 entrypoints (69 aliases)`.
- Optional display metadata becomes:
  - `localizedTitles.es present on 5/27 entrypoints`
  - `localizedPurposes.es present on 5/27 entrypoints`

## Likely Edge Cases

- Count drift: package and CLI tests may be updated while durable docs still say
  `2/27`; the Cycle135 guard should fail until docs say `5/27`.
- Overclaiming: Spanish required localization is complete, but Spanish
  entrypoint display metadata is still partial at `5/27`.
- Runtime confusion: `entrypoints --language es` is package-local inspection and
  must not validate voice assets, OpenAI availability, local SAPI/Piper support,
  controller readiness, or live RingCentral acceptance.
- Sensitive wording: `More` contains recording and other tools. Spanish purpose
  must say it opens or shows the menu, not that it starts actions.
- Settings wording: settings can expose devices, accounts, and saved join
  preferences. Say review/explain only; do not say read, switch, save, or change.
- Matching semantics: `localizedTitles` and `localizedPurposes` must not add
  match candidates. Existing alias tests should remain unchanged.
- Question policy: `ringcentral.video.top.meeting-info` remains answer-only and
  unseeded in this slice.

## Rollback And Guardrails

Rollback is straightforward:

- Remove the three added `localizedTitles.es` / `localizedPurposes.es` blocks.
- Revert test and durable-doc count expectations from `5/27` to `2/27`.
- Revert answer-rendering parametrization additions for the three entries.
- Re-run the focused commands above and confirm Spanish required localization
  still passes.

Guardrails for the implementation worker:

- Stage and commit only the intended files. Do not stage `.coverage`.
- Keep the commit small and named around Spanish display metadata, not runtime
  Spanish readiness.
- Do not touch CLI source unless a test reveals a real defect.
- Do not reformat the whole YAML file.
- Do not add aliases, flows, open steps, presenter notes, or acceptance evidence
  in this slice.
- Do not claim live RingCentral acceptance or local Spanish speech support.

## Verification Performed For This Scan

Ran:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting top bar" --language es
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_spanish_display_metadata_counts_match_durable_docs tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_complete_spanish_package tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy
git status --short
```

Observed:

- Spanish required localization passes.
- Optional Spanish display metadata remains `2/27` before this recommended
  slice.
- Meeting top bar localized/fallback behavior is currently:
  - `meeting-info`: fallback
  - `network-quality`: localized
  - `views`: fallback
  - `report-issue`: fallback
- Focused baseline tests passed: `4 passed in 1.60s`.
- Worktree status showed modified `.coverage`; it was not touched.
