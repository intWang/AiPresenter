# Cycle 133 Technical Scan: Read-Only Entrypoints Language Display

Date: 2026-05-16

## Scope

Investigated feasibility of adding a read-only CLI
`entrypoints --language` option after Cycle132. This scan also compares that
work against another small Spanish entrypoint-copy seed and durable
documentation work.

This agent changed only this handoff file. No source, tests, package YAML,
staging, or commits were changed.

## Current Baseline

Cycle132 seeded Spanish localized entrypoint display copy for exactly two
RingCentral Video entrypoints:

- `ringcentral.video.overview`
- `ringcentral.video.top.network-quality`

The current package report confirms Spanish required localization is complete,
while localized entrypoint title/purpose coverage remains optional and partial:

- `questionAliases.es present on 26/27 entrypoints (69 aliases)`
- `localizedTitles.es present on 2/27 entrypoints`
- `localizedPurposes.es present on 2/27 entrypoints`
- `51/51` demo steps, `12/12` localized questions, and `12/12` localized answers

`entrypoints` has not yet been updated. A read-only check showed:

```powershell
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting top bar"
```

Current output still uses canonical English titles, including:

```text
- ringcentral.video.top.network-quality: Network quality [Meeting top bar]
```

That is the behavior the default command must preserve.

## Feasibility: `entrypoints --language`

Recommendation: feasible, small, and a good Cycle133 implementation candidate.

Exact implementation files:

- `src/ai_presenter/cli.py`
- `tests/unit/test_cli.py`

Likely code shape in `src/ai_presenter/cli.py`:

- Add a new optional Typer option to `entrypoints()`:
  `language: str | None = typer.Option(None, "--language", help="Optional package-local language for localized entrypoint display.")`
- Keep current default output byte-for-byte unchanged when `language is None`:
  `- {entrypoint.id}: {entrypoint.title} [{entrypoint.area}]`
- When `language` is present, display:
  `entrypoint.title_for_language(language)`
- Do not call `resolve_voice_settings()`, `PresenterVoiceSettings`,
  `language_label()`, `validate_profile_voice()`, `resolve_speech_provider_name()`,
  or `check_voice_asset_availability()`.
- Treat the raw language string as package-local metadata lookup only. This
  mirrors `localization-report --language`, not runtime `demo/controller
  --language`.

The helper already exists in `src/ai_presenter/packages/models.py`:

- `OperationEntrypoint.localized_titles`
- `OperationEntrypoint.localized_purposes`
- `OperationEntrypoint.title_for_language(language)`
- `OperationEntrypoint.purpose_for_language(language)`

So no package model change is needed.

Recommended first output design:

```text
- ringcentral.video.top.network-quality: Calidad de red [Meeting top bar]
```

Fallback behavior should be per entrypoint:

- If `localizedTitles.<language>` is nonblank, show it.
- If absent or blank, show canonical `title`.

Do not include localized purpose by default in the first pass. Purpose/fallback
metadata is useful, but it increases output design and test surface. If included,
keep it explicit and compact, for example a future `--verbose` or
`--show-purpose` option with clear source labels such as `title: localized` or
`title: canonical fallback`. For Cycle133, title-only is enough.

## Required Tests

Add or update tests in `tests/unit/test_cli.py`:

- Keep `test_entrypoints_lists_material_package_entrypoints_by_area` asserting
  default output remains canonical and area filtering still works.
- Add a focused real-package test:
  `entrypoints --package ringcentral-video --area "Meeting top bar" --language es`
  should include `ringcentral.video.top.network-quality: Calidad de red` and
  still include canonical fallback for unseeded entries such as
  `ringcentral.video.top.meeting-info: Meeting information`.
- Add a package-local language boundary test using a temporary inline package:
  `localizedTitles.de` displays for `--language de` even though `de` is not a
  runtime presenter language. This proves no runtime voice normalization is
  called.
- Optional but valuable: monkeypatch or block `ai_presenter.cli.resolve_voice_settings`
  and `ai_presenter.cli.validate_cli_voice_profile` in the new `entrypoints`
  test so any accidental runtime voice check fails loudly.
- If purpose display is added, test both localized purpose and canonical fallback
  source. Otherwise do not add purpose assertions.

Tests that should not need changes:

- `tests/unit/test_material_packages.py`, because the model and Cycle132 package
  assertions already cover localized title/purpose parsing and counts.
- `tests/unit/test_questions.py`, because answer rendering already owns
  localized title/purpose use at runtime.
- `tests/unit/test_diagnostics.py`, unless implementation accidentally expands
  matching or diagnostics.
- `tests/unit/test_voice.py`, because this flag must stay outside voice
  normalization/provider support.

## Risks

- Highest risk: treating `entrypoints --language` like runtime voice selection.
  This would reject package-only languages or imply provider support. Avoid all
  runtime voice helpers for this command.
- Changing default output would create unnecessary operator/test churn. Preserve
  the current no-language path exactly.
- Showing purpose by default could make the command noisy and create a larger
  localization promise than Cycle132 established.
- Localized title/purpose must remain display-only. Do not add these fields to
  entrypoint matching, alias indexes, Q&A precedence, safety gating, controller
  interrupt creation, diagnostics matching, or acceptance operation routing.
- UTF-8 package content appears mojibake in some PowerShell views. Tests load the
  YAML correctly; avoid content rewrites in the CLI slice.

## Comparison: Another Spanish Content Seed

Another small Spanish content seed is feasible, but it is higher review risk
than `entrypoints --language` because it changes authored package content.

Candidate files:

- `packages/ringcentral-video.yaml`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_questions.py`
- `tests/unit/test_cli.py`

Best next candidates remain low-risk surfaces:

- `ringcentral.video.toolbar.chat`, only with an explicit privacy boundary:
  do not imply reading private chat by default.
- `ringcentral.video.toolbar.participants`, only with an explicit identity
  boundary: do not imply identifying names, roles, or details by default.
- Another passive or diagnostic entrypoint is preferable if the cycle wants
  minimum safety review.

Do not pair a content seed with broad alias work, `questionPolicy` changes,
`openSteps` changes, or runtime language promotion. If this path is chosen,
tests should assert the exact new Spanish strings, updated optional report
counts, unchanged `questionAliases.es` count unless explicitly scoped, Q&A-first
safety behavior, and unseeded fallback behavior.

Compared with CLI display, the content seed gives more Spanish user-facing
coverage, but it requires heavier safety copy review. The CLI flag unlocks
inspection of the Cycle132 seed without expanding the package risk surface.

## Comparison: Durable Docs

Durable documentation is also useful, but it is less urgent than the read-only
CLI flag because the key boundary already exists in
`docs/knowledge/language-lifecycle.md`.

Good durable-doc follow-up:

- Add a short `localizedTitles` / `localizedPurposes` authoring section to
  `docs/knowledge/language-lifecycle.md` or a linked localization authoring note.
- Document that localized entrypoint copy is package-local display metadata,
  optional in reports, and not evidence of live acceptance or local voice
  support.
- Include Spanish style guardrails from Cycle132: preserve visible RingCentral
  UI labels, keep privacy/state-changing controls bounded, and do not claim full
  `27/27` entrypoint localization from a small seed.

Durable docs are a good companion after either CLI inspection or the next
content seed. As a standalone Cycle133 item, they provide less immediate
verification value than letting package authors inspect localized entrypoint
titles directly.

## Recommended Cycle133 Slice

Implement `entrypoints --language` only.

Acceptance criteria:

- Default `entrypoints` output remains unchanged.
- `--language es` displays Cycle132 Spanish titles where present.
- Entries without localized titles fall back to canonical titles.
- Package-local languages are accepted without runtime voice normalization.
- No provider/profile/voice asset checks run.
- No package YAML or runtime matching behavior changes.

## Verification Commands

Recommended implementation verification:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_entrypoints_lists_material_package_entrypoints_by_area tests\unit\test_cli.py::<new_localized_entrypoints_test> tests\unit\test_cli.py::<new_package_local_language_test>
```

```powershell
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting top bar"
```

```powershell
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting top bar" --language es
```

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
```

```powershell
git diff --check
git status --short
```

Expected preserved signals:

- Default entrypoint titles are canonical English.
- Localized Spanish output shows `Calidad de red` for
  `ringcentral.video.top.network-quality`.
- Unseeded Spanish entries fall back to canonical title.
- Spanish report still shows `localizedTitles.es present on 2/27 entrypoints`
  and `localizedPurposes.es present on 2/27 entrypoints` unless another content
  seed is intentionally included.
- `.coverage` may already be modified and must remain unstaged.

## Verification Performed By This Scan

Read-only commands run:

```powershell
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting top bar"
```

Result: exit 0; current output uses canonical English titles only.

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
```

Result: exit 0; Spanish required package localization is complete and optional
localized entrypoint copy remains `2/27`.

```powershell
git status --short
```

Result before this file was written: `.coverage` was already modified.

## Final Recommendation

Proceed with the read-only CLI inspection slice before adding more Spanish
content. It is the smallest useful follow-up to Cycle132: it exposes the seeded
localized titles for package authors, preserves default operator output, and
keeps runtime voice/provider support out of scope.
