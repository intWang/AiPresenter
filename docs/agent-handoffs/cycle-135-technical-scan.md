# Cycle 135 Technical Scan: Post-Cycle134 Next Options

Date: 2026-05-16

## Scope

Investigated feasible next implementation options after Cycle134:

- small Spanish entrypoint display-copy expansion for low-risk entries;
- count drift guard test/tooling for `localizedTitles` / `localizedPurposes` and docs or reports;
- README inspection example.

This scan changed only this handoff file. No source, tests, packages, durable
docs, README, staging, or commits were changed.

## Current Baseline

Cycle134 documented optional entrypoint display metadata and left README
untouched. Current command output confirms:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
```

Reports:

```text
- questionAliases.es present on 26/27 entrypoints (69 aliases)
- localizedTitles.es present on 2/27 entrypoints
- localizedPurposes.es present on 2/27 entrypoints
Localization report: 51/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for es.
```

And:

```powershell
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --language es
```

Shows localized display copy only for:

- `ringcentral.video.overview`
- `ringcentral.video.top.network-quality`

All remaining entrypoints use canonical fallback title/purpose output with
explicit `(title: fallback)` and `(fallback)` markers.

Important boundary: Spanish required package localization is complete, but
Spanish optional entrypoint display metadata is intentionally partial at
`2/27`. `entrypoints --language es` is package-local inspection, not runtime
voice validation, provider readiness, local SAPI/Piper support, or live
RingCentral acceptance.

## Option A: Small Spanish Entrypoint Display-Copy Expansion

Feasibility: good, if kept to a tiny package-content slice and paired with exact
test/doc count updates.

Primary file:

- `packages/ringcentral-video.yaml`

Test files likely touched:

- `tests/unit/test_material_packages.py`
- `tests/unit/test_cli.py`

Docs likely touched because Cycle134 made dated counts durable:

- `docs/knowledge/language-lifecycle.md`
- `docs/knowledge/ringcentral-video/source-index.md`
- Optional: `README.md` only if combining with Option C.

Existing anchors:

- `packages/ringcentral-video.yaml:46` to `:49` and `:104` to `:107` hold the
  only current Spanish `localizedTitles` / `localizedPurposes` seeds.
- `tests/unit/test_material_packages.py::test_ringcentral_spanish_entrypoint_copy_pilot_is_present`
  currently asserts the exact two localized entrypoint ids.
- `tests/unit/test_cli.py::test_localization_report_outputs_complete_spanish_package`
  currently asserts `localizedTitles.es present on 2/27 entrypoints` and
  `localizedPurposes.es present on 2/27 entrypoints`.
- `tests/unit/test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy`
  currently expects `ringcentral.video.top.meeting-info` to fall back in the
  Meeting top bar filtered output.

Recommended candidate wedge: add three low-risk Spanish display-copy entries,
moving optional display metadata from `2/27` to `5/27`.

Candidate 1:

- Entrypoint: `ringcentral.video.top.meeting-info`
- YAML anchor: `packages/ringcentral-video.yaml:64`
- Why feasible: existing Spanish aliases and Spanish demo narration already
  explain the privacy boundary. The entrypoint has `questionPolicy: answerOnly`.
- Suggested shape:
  - `localizedTitles.es`: `Información de la reunión`
  - `localizedPurposes.es`: keep visible product labels literal, for example
    "Abre Meeting information para ubicar detalles como host, Meeting ID,
    copy link, dial-in y cifrado sin leer valores privados."
- Safety boundary: do not imply reading meeting IDs, links, dial-in numbers,
  host names, or encryption details by default. Keep `Meeting information`,
  `Meeting ID`, `copy link`, and `dial-in` recognizable as UI/product terms.

Candidate 2:

- Entrypoint: `ringcentral.video.top.views`
- YAML anchor: `packages/ringcentral-video.yaml:132`
- Why feasible: layout-only, local visual effect, already described in Spanish
  narration as not changing anyone's audio, video, or membership.
- Suggested shape:
  - `localizedTitles.es`: `Diseño de vista`
  - `localizedPurposes.es`: "Abre Views para cambiar Gallery view o Full
    screen en tu vista local sin alterar audio, video ni participantes."
- Safety boundary: do not imply host control, participant changes, media
  changes, or remote state changes.

Candidate 3:

- Entrypoint: `ringcentral.video.settings.background`
- YAML anchor: `packages/ringcentral-video.yaml:327`
- Why feasible: already has Spanish aliases and Spanish Q&A around background
  privacy; display metadata improves an existing safe learning path.
- Suggested shape:
  - `localizedTitles.es`: `Ajustes de fondo`
  - `localizedPurposes.es`: "Abre Background para revisar Blur, fondos
    virtuales y cargas personalizadas sin cambiar el fondo sin confirmación."
- Safety boundary: keep `Background` and `Blur` literal. Do not imply selecting
  a background, uploading an asset, or changing video appearance without an
  explicit user request.

Candidates to defer for this small wedge:

- `ringcentral.video.more.recording`, `ringcentral.video.toolbar.leave`,
  `ringcentral.video.toolbar.share`: higher-impact actions.
- `ringcentral.video.more.notes`, `ringcentral.video.toolbar.chat`,
  `ringcentral.video.toolbar.participants`: privacy-sensitive content or names.
- `ringcentral.develop.video.start`: starts or joins a meeting.
- `ringcentral.video.toolbar.audio`, `ringcentral.video.toolbar.video`: useful
  later, but media privacy switches deserve their own review.

Likely code/content shape:

```yaml
- id: ringcentral.video.top.views
  title: View layout menu
  area: Meeting top bar
  purpose: Switch the meeting layout, including Gallery view and Full screen.
  localizedTitles:
    es: Diseño de vista
  localizedPurposes:
    es: Abre Views para cambiar Gallery view o Full screen en tu vista local sin alterar audio, video ni participantes.
```

Test strategy:

- Update the exact expected id set in
  `test_ringcentral_spanish_entrypoint_copy_pilot_is_present` from two ids to
  the new five ids, and assert the new Spanish strings.
- Update `test_localization_report_outputs_complete_spanish_package` to expect
  `localizedTitles.es present on 5/27 entrypoints` and
  `localizedPurposes.es present on 5/27 entrypoints`.
- Update `test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy`
  if `meeting-info` or `views` is in its filtered output. For example,
  `meeting-info` should become `(title: localized)` and show the Spanish
  purpose if Candidate 1 is selected.
- Keep `required_localization_complete` expectations unchanged. Optional
  display metadata must not affect `--require-complete`.

Verification commands:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --language es
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting top bar" --language es
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_spanish_entrypoint_copy_pilot_is_present tests\unit\test_material_packages.py::test_entrypoint_title_and_purpose_counts_do_not_gate_required_localization tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_cli.py::test_localization_report_require_complete_passes_for_spanish_package tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_entrypoints_language_uses_package_local_metadata_without_runtime_voice_validation
rg -n "localizedTitles.es|localizedPurposes.es|2/27|5/27|entrypoints --language|fully localized|live acceptance|SAPI|Piper" README.md docs\knowledge\language-lifecycle.md docs\knowledge\ringcentral-video\source-index.md packages\ringcentral-video.yaml tests\unit\test_cli.py tests\unit\test_material_packages.py
git diff --check
```

Risks:

- Count drift: package moves to `5/27` while docs/tests still say `2/27`.
- Overclaiming: Spanish optional display metadata expansion must not be called
  full Spanish entrypoint localization.
- Safety wording drift: display purposes could accidentally promise reading
  private meeting details or changing settings.
- YAML encoding/line-ending churn: keep edits minimal and review strings in a
  UTF-8-aware editor if the terminal renders accents poorly.

## Option B: Count Drift Guard For Display Metadata And Docs

Feasibility: good as a narrow test/tooling slice. This is the best guardrail if
future cycles will keep adding optional entrypoint display copy.

Primary files:

- `tests/unit/test_material_packages.py`
- Optional if a CLI-level assertion is preferred: `tests/unit/test_cli.py`

No source changes are required for a test-only guard. Existing production code
already exposes the needed values through
`src/ai_presenter/packages/localization_status.py`.

Existing anchors:

- `src/ai_presenter/packages/localization_status.py:73` to `:83` counts
  nonblank `questionAliases`, `localizedTitles`, and `localizedPurposes`.
- `src/ai_presenter/packages/localization_status.py:170` to `:180` renders the
  three entrypoint metadata count lines.
- `docs/knowledge/language-lifecycle.md:119` to `:121` contains the dated
  Spanish `2/27` display-metadata counts.
- `docs/knowledge/ringcentral-video/source-index.md:61` contains the same
  Spanish display-metadata counts in the coverage summary.

Likely test shape:

Add a focused test in `tests/unit/test_material_packages.py`, near the existing
localization status and Spanish entrypoint copy tests:

```python
def test_ringcentral_spanish_display_metadata_counts_match_durable_docs() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    report = build_localization_status(package, language="es")

    expected_title_count = (
        f"localizedTitles.es` is present on `{report.entrypoint_titles_present}/"
        f"{report.entrypoint_total}` entrypoints"
    )
    expected_purpose_count = (
        f"localizedPurposes.es` is present on `{report.entrypoint_purposes_present}/"
        f"{report.entrypoint_total}` entrypoints"
    )

    lifecycle = Path("docs/knowledge/language-lifecycle.md").read_text(encoding="utf-8")
    source_index = Path("docs/knowledge/ringcentral-video/source-index.md").read_text(
        encoding="utf-8"
    )

    assert expected_title_count in lifecycle
    assert expected_purpose_count in lifecycle
    assert (
        f"localizedTitles.es` on {report.entrypoint_titles_present}/"
        f"{report.entrypoint_total} entrypoints"
    ) in source_index
    assert (
        f"localizedPurposes.es` on {report.entrypoint_purposes_present}/"
        f"{report.entrypoint_total} entrypoints"
    ) in source_index
```

Alternative, less wording-sensitive shape:

- Use regex to find every `localizedTitles.es` and `localizedPurposes.es`
  fraction in durable docs, then assert each discovered fraction matches the
  computed report count.
- Keep this scoped to evergreen docs under `docs/knowledge/`, not
  `docs/agent-handoffs/`, because old handoffs are historical and should not be
  rewritten when counts change.

Test strategy:

- First create the guard against current `2/27` docs and prove it passes.
- If paired with Option A, update package strings and docs counts in the same
  implementation, then prove the guard catches stale docs by temporarily
  observing the expected red state before fixing docs.
- Keep README out of the guard unless README uses exact counts. If README only
  says "localized versus fallback output", it should not become count-coupled.

Verification commands:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_spanish_display_metadata_counts_match_durable_docs tests\unit\test_material_packages.py::test_entrypoint_title_and_purpose_counts_do_not_gate_required_localization tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
rg -n "localizedTitles.es|localizedPurposes.es|[0-9]+/27" docs\knowledge\language-lifecycle.md docs\knowledge\ringcentral-video\source-index.md tests\unit\test_material_packages.py
git diff --check
```

Risks:

- Brittle docs tests can punish harmless prose edits. Prefer regex or compact
  expected snippets instead of asserting a whole paragraph.
- Historical handoffs contain old counts by design. Do not include
  `docs/agent-handoffs/` in the guard.
- If docs use prose like "two of twenty-seven" instead of `2/27`, a regex guard
  may miss it. Keep durable count mentions in a stable numeric format.
- This option does not improve operator usability by itself; it is a safety net
  for future content expansion.

## Option C: README Inspection Example

Feasibility: excellent. This is the smallest low-risk implementation after
Cycle134 because Cycle134 explicitly left README untouched.

Primary file:

- `README.md`

No source, tests, package YAML, or durable docs are required unless the wording
introduces exact counts or new behavior claims.

Recommended location:

- Under `## Run A Material Demo`, immediately after the existing entrypoint
  listing example:

```powershell
.venv\Scripts\ai-presenter entrypoints --package ringcentral-video --area "Meeting toolbar"
```

Likely content shape:

Inspect package-local entrypoint display copy for a language, including
localized versus fallback markers:

```powershell
.venv\Scripts\ai-presenter entrypoints --package ringcentral-video --language es
```

This checks authored package metadata only; it does not validate runtime voice
or provider support.

If adding only this README example, avoid exact `2/27` or `5/27` counts. The
README should stay operator-focused and should not need count-sync maintenance.

Test strategy:

- Run the command from the README and confirm it exits 0 and prints
  `Language: es`, localized markers for the two current entries, and fallback
  markers for others.
- Use `rg` to inspect README wording for overclaims.
- No unit test is necessary for a concise README-only example; the focused CLI
  tests already cover command behavior.

Verification commands:

```powershell
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --language es
rg -n "entrypoints --package ringcentral-video --language es|package-local|runtime voice|provider|localized|fallback|SAPI|Piper|live acceptance|fully localized" README.md
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_entrypoints_language_uses_package_local_metadata_without_runtime_voice_validation
git diff --check
```

Risks:

- Overexplaining README with lifecycle details already covered in
  `docs/knowledge/language-lifecycle.md`.
- Making `entrypoints --language es` sound like a demo readiness preflight.
- Accidentally implying Spanish local SAPI/Piper support or live acceptance.
- Combining README with package content without updating exact count docs and
  tests.

## Recommendation

Recommended next-cycle order:

1. If the goal is the lowest-risk visible improvement, implement Option C only.
   Add the README inspection example and verify the command plus focused CLI
   tests.
2. If the goal is engineering hygiene before more content, implement Option B
   only. Guard evergreen docs against `localizedTitles.es` /
   `localizedPurposes.es` count drift.
3. If the goal is package-content progress, implement Option A as a small
   three-entry display-copy wedge, but include count updates and focused tests
   in the same cycle. Prefer `meeting-info`, `views`, and `background settings`;
   defer recording, leave, share, chat, participants, notes/transcript, start
   meeting, and media toggles.

Do not combine all three unless explicitly requested. The safest paired slice
is Option A plus Option B, because content expansion benefits from a count-sync
guard. The smallest operator-facing slice is Option C alone.

## Verification Performed For This Scan

Ran:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --language es
git status --short
```

Observed:

- Spanish required localization still passes at `51/51`, `12/12`, `12/12`.
- Spanish optional display metadata remains `2/27` titles and `2/27` purposes.
- `entrypoints --language es` shows localized display copy for
  `ringcentral.video.overview` and `ringcentral.video.top.network-quality`,
  with fallback markers elsewhere.
- Worktree status showed unrelated modified `.coverage`; it was not touched.

## Final Boundaries

- Do not stage `.coverage`.
- Do not describe optional display metadata as required localization.
- Do not describe package-local Spanish metadata as local voice readiness,
  provider readiness, or live acceptance.
- Keep visible RingCentral UI labels recognizable in Spanish display purposes,
  especially `Meeting information`, `Meeting ID`, `copy link`, `dial-in`,
  `Views`, `Gallery view`, `Full screen`, `Background`, and `Blur`.
