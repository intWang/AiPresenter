# Cycle 132 Implementation: Spanish Entrypoint Copy Pilot

Date: 2026-05-16

## Scope

Seeded a tiny Spanish localized entrypoint-copy pilot for RingCentral Video using
the Cycle131 optional display-copy schema.

Implemented exactly two entrypoints:

- `ringcentral.video.overview`
- `ringcentral.video.top.network-quality`

No CLI `--language` support was implemented in this cycle.

## Files Changed

- `packages/ringcentral-video.yaml`
  - Added `localizedTitles.es` and `localizedPurposes.es` for
    `ringcentral.video.overview`.
  - Added `localizedTitles.es` and `localizedPurposes.es` for
    `ringcentral.video.top.network-quality`.
  - Did not change canonical `title`, `purpose`, `questionAliases`,
    `questionPolicy`, `openSteps`, presenter notes, Q&A, demo narration, or
    other package fields.
- `tests/unit/test_material_packages.py`
  - Added real-package assertions for the exact Spanish title/purpose copy.
  - Asserted only the two requested entrypoints contain localized title/purpose
    maps.
  - Updated Spanish localization status expectations to 2/27 localized titles
    and 2/27 localized purposes while keeping required localization complete.
- `tests/unit/test_questions.py`
  - Added real-package Spanish answer-rendering assertions for overview and
    network quality.
  - Asserted the localized answers include Spanish title and purpose and exclude
    the previous English purpose prose.
  - Added unseeded Spanish fallback evidence using Participants.
- `tests/unit/test_cli.py`
  - Updated Spanish localization report expectations to 2/27 localized titles
    and 2/27 localized purposes.

## Verification

Red check before package content:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit\test_material_packages.py::test_ringcentral_spanish_entrypoint_copy_pilot_is_present tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_complete_spanish_package tests\unit\test_questions.py::test_ringcentral_spanish_entrypoint_answer_uses_localized_pilot_copy tests\unit\test_questions.py::test_ringcentral_spanish_unseeded_entrypoint_keeps_alias_label_fallback tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package -q --no-cov
```

Result: failed as expected because the package still had no Spanish localized
entrypoint title/purpose copy and report counts were 0/27. The unseeded
Participants fallback assertion already passed.

Final checks:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_cli.py -q --no-cov
```

Result: `358 passed in 67.38s`.

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
```

Result: exit 0. Report shows `localizedTitles.es present on 2/27 entrypoints`,
`localizedPurposes.es present on 2/27 entrypoints`, and 51/51 demo steps plus
12/12 Q&A questions and answers localized for Spanish.

```powershell
.\.venv\Scripts\ruff check --no-cache packages tests
```

Result: `All checks passed!`

Additional boundary check:

```powershell
rg -n "localizedTitles:|localizedPurposes:" packages\ringcentral-video.yaml
```

Result: four matches total, exactly the title and purpose maps under overview
and network quality.

## Boundaries

- Localized title/purpose copy remains display-only.
- Matching, routing, aliases, `questionPolicy`, open steps, controller behavior,
  safety gating, and Q&A precedence were not changed.
- Existing Spanish Q&A precedence tests remain in `tests/unit/test_questions.py`
  and passed in the requested unit suite.
- Spanish localized title/purpose coverage is still optional report data; it
  does not affect `--require-complete`.
- No staging or commit was performed.
- `.coverage` was already modified in the working tree and was left unstaged.

## Residual Risk

- This is a two-entrypoint pilot, not full Spanish entrypoint localization.
- The tests prove package loading, report counts, answer rendering, fallback,
  and existing safety/Q&A boundaries locally; they do not prove live
  RingCentral UI acceptance or audio behavior.
