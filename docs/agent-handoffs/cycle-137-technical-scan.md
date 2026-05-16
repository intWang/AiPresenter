# Cycle 137 Technical Scan

Date: 2026-05-16

## Scope

Read-only scan for a small technically clean Cycle137 slice. The worktree
precondition matched the handoff request before this file was added:
`.coverage` was the only modified file.

Inspected:

- `README.md`
- `docs/knowledge/language-lifecycle.md`
- `docs/knowledge/ringcentral-video/runtime-safety-routing.md`
- `docs/knowledge/ringcentral-video/source-index.md`
- `src/ai_presenter/cli.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_material_packages.py`
- `pyproject.toml`

Recent commits checked:

- `e27d482 feat: expand Spanish entrypoint display copy`
- `2d1d070 test: guard Spanish display metadata docs`
- `436ff9c docs: document entrypoint localization lifecycle`

## Recommendation

Implement one docs-only future-date cleanup:

- Edit `docs/knowledge/ringcentral-video/runtime-safety-routing.md`.
- In `## Localization And Counts`, replace the future verification phrase
  `verified on 2026-05-17 with localization-report and doctor` with a
  `2026-05-16`-anchored statement.
- Keep the package counts unchanged.
- Do not edit `.coverage`.
- Do not stage or commit unless a later owner explicitly asks.

Suggested wording:

```markdown
Current expected package signals, verified on 2026-05-16 with
`localization-report` and `doctor`:
```

This is the cleanest slice because the counts are already consistent with the
current CLI output and tests, but the existing doc date is one day ahead of the
requested Cycle137 anchor date. It removes a future verification claim without
changing runtime behavior, package content, README guidance, or test fixtures.

## Evidence From Scan

README boundary language is already aligned with the current Spanish provider
state:

- `localization-report` is presented as package coverage, separate from runtime
  voice support.
- Spanish package localization is described as complete.
- `--language es` is described as runtime-selectable only with OpenAI-backed
  speech.
- local SAPI and Piper Spanish are explicitly out of scope.

`docs/knowledge/language-lifecycle.md` is also aligned:

- date is `2026-05-16`;
- Spanish is complete for required package localization;
- optional entrypoint display metadata remains partial at `5/27` titles and
  `5/27` purposes;
- OpenAI-backed Spanish runtime support is separated from local SAPI/Piper and
  live RingCentral acceptance.

`docs/knowledge/ringcentral-video/source-index.md` has the same package and
metadata counts as the CLI and the durable-doc regression test.

The only scanned future-date issue in the target docs is:

- `docs/knowledge/ringcentral-video/runtime-safety-routing.md`: `Current expected package signals, verified on 2026-05-17...`

Relevant current command observations from this scan:

- `localization-report --package ringcentral-video --language es --require-complete`
  reports `51/51` demo steps, `12/12` Q&A questions, `12/12` Q&A answers,
  `questionAliases.es` on `26/27` entrypoints with `69` aliases,
  `localizedTitles.es` on `5/27` entrypoints, and `localizedPurposes.es` on
  `5/27` entrypoints.
- `entrypoints --package ringcentral-video --area "Meeting top bar" --language es`
  shows localized Spanish display copy for Network quality and Views, while
  Meeting information and Report issue fall back to canonical English metadata.
- `doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --require-localization --localization-language es`
  reports the expected package diagnostics: `156` aliases, `84` Q&A prompts,
  `11` INFO-level substring-risk prompts, Spanish required localization
  complete, and runtime language recognition.
- `demo --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run`
  rejects Spanish on `windows-sapi-en` before runtime and states that Spanish
  voice output requires `openai`.

## Exact Files For Implementation

Primary implementation file:

- `docs/knowledge/ringcentral-video/runtime-safety-routing.md`

No source or test edits are recommended for this slice.

Files that should stay unchanged:

- `README.md`
- `docs/knowledge/language-lifecycle.md`
- `docs/knowledge/ringcentral-video/source-index.md`
- `src/ai_presenter/cli.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_material_packages.py`
- `.coverage`

## Test Strategy

Because this is docs-only, prioritize commands that prove the doc anchor does
not drift from current package/CLI signals and that no coverage artifact is
updated.

Focused no-coverage tests:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_spanish_display_metadata_counts_match_durable_docs tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_demo_openai_profile_accepts_spanish_dry_run tests\unit\test_cli.py::test_demo_rejects_spanish_local_profile_before_runtime
```

Read-only CLI probes:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting top bar" --language es
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --require-localization --localization-language es
.\.venv\Scripts\ai-presenter.exe demo --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
rg -n "2026-05-17|future work until a dated acceptance run proves them|live verified|accepted" README.md docs\knowledge\language-lifecycle.md docs\knowledge\ringcentral-video\runtime-safety-routing.md docs\knowledge\ringcentral-video\source-index.md
git diff --check
git status --short
```

Expected behavior:

- pytest focused tests pass without writing `.coverage` because `addopts` is
  overridden;
- Spanish package localization remains complete;
- entrypoint display metadata remains partial, not re-described as full
  entrypoint localization;
- local `windows-sapi-en` Spanish dry run still fails before runtime;
- `git status --short` shows only the intended docs file plus the pre-existing
  `.coverage` modification.

## Edge Cases

- Do not replace every `2026-05-17` in historical handoff files. Those are
  archival cycle records outside this slice.
- Do not remove wording that Spanish local SAPI/Piper support and live
  RingCentral Video acceptance remain future work.
- Do not call Spanish "accepted", "live verified", or "demo-ready" based on
  package localization, doctor, unit tests, or dry-run output.
- Do not change counts unless the implementation reruns the relevant commands
  and finds a real mismatch.
- `doctor --require-localization --localization-language es` checks package
  localization separately from selected runtime voice. That distinction should
  remain explicit.
- The OpenAI Spanish route is runtime-selectable, but local profile rejection is
  still required behavior.

## Rollback

Rollback is a single-file docs revert:

```powershell
git diff -- docs\knowledge\ringcentral-video\runtime-safety-routing.md
git checkout -- docs\knowledge\ringcentral-video\runtime-safety-routing.md
```

Only run the checkout command if the implementation owner intentionally wants
to discard their own runtime-safety-routing edit. Do not use broad reset or
checkout commands, and do not touch `.coverage`.
