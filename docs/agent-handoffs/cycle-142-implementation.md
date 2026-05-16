# Cycle 142 Implementation Handoff: CLI Spanish Entrypoint Inspection Guard

Date: 2026-05-17
Cycle: 142
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Scope: implementation handoff only. This handoff documents the current
tests-only Cycle142 implementation already present in `tests/unit/test_cli.py`
and adds no source, package, or test changes.

## Objective

Document the Cycle142 CLI guard for RingCentral Video Spanish entrypoint
inspection.

Cycle140 added optional Spanish display metadata for exactly three entrypoints:

- `ringcentral.video.toolbar.audio-menu`
- `ringcentral.video.toolbar.video-menu`
- `ringcentral.video.more.background`

Cycle141 guarded the runtime boundary: Spanish `localizedTitles.es` and
`localizedPurposes.es` may render after a valid match, but must not become query
matching metadata.

Cycle142 stays on the CLI inspection surface. It proves `entrypoints
--language` resolves Spanish language inputs to the package key `es` and prints
localized/fallback display markers for the relevant RingCentral Video
entrypoints without invoking runtime voice validation or changing matcher
behavior.

## Files Changed

Observed implementation file:

- `tests/unit/test_cli.py`
  - Extended
    `test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy`
    so `entrypoints --language es` now asserts localized titles and purposes
    for:
    - `ringcentral.video.toolbar.audio-menu`
    - `ringcentral.video.toolbar.video-menu`
    - `ringcentral.video.more.background`
  - Kept fallback marker assertions visible for non-localized entries,
    including `ringcentral.video.toolbar.audio` and
    `ringcentral.video.more.recording`.
  - Parameterized
    `test_entrypoints_language_normalizes_spanish_alias_for_display_metadata`
    over `Spanish` and `es-MX`.
  - Updated that alias-normalization test to inspect the `Meeting toolbar`
    area and assert `Language: es`, localized toolbar display output, and a
    toolbar fallback marker.

Documentation file added by this handoff:

- `docs/agent-handoffs/cycle-142-implementation.md`

Concurrent worktree state observed before this handoff:

- `.coverage` was already modified.
- `tests/unit/test_cli.py` was already modified with the Cycle142 tests.
- `docs/agent-handoffs/cycle-142-demand-analysis.md`,
  `docs/agent-handoffs/cycle-142-risk-scan.md`, and
  `docs/agent-handoffs/cycle-142-technical-scan.md` were already untracked.

Treat those as other workers' edits. Do not revert, normalize, stage, or claim
ownership of them from this documentation pass. Git also reported that
`tests/unit/test_cli.py` line endings may be normalized from LF to CRLF the next
time Git touches the file; this handoff intentionally does not touch that file.

## Exact Test Coverage

`test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy`
now covers three area-scoped Spanish inspection calls:

- `entrypoints --package ringcentral-video --area "Meeting top bar" --language es`
  - Asserts `Language: es`.
  - Asserts localized top-bar display metadata still appears for existing
    localized entries such as `ringcentral.video.top.network-quality` and
    `ringcentral.video.top.views`.
  - Asserts fallback top-bar display metadata still appears for entries such as
    `ringcentral.video.top.meeting-info` and
    `ringcentral.video.top.report-issue`.
  - Asserts `ringcentral.video.toolbar.audio` is not leaked into the top-bar
    area output.

- `entrypoints --package ringcentral-video --area "Meeting toolbar" --language es`
  - Asserts `ringcentral.video.toolbar.audio-menu` prints Spanish localized
    title `Menú de micrófono y altavoz` and a localized purpose marker.
  - Asserts `ringcentral.video.toolbar.video-menu` prints Spanish localized
    title `Menú de cámara` and a localized purpose marker.
  - Keeps the existing localized guard for `ringcentral.video.toolbar.more`.
  - Asserts `ringcentral.video.toolbar.audio` remains fallback, proving partial
    optional display metadata is still represented as localized and fallback
    states together.

- `entrypoints --package ringcentral-video --area "More menu" --language es`
  - Asserts `ringcentral.video.more.background` prints localized title and
    purpose markers.
  - Keeps the existing localized guard for `ringcentral.video.more.settings`.
  - Asserts `ringcentral.video.more.recording` remains fallback for both title
    and purpose markers.

`test_entrypoints_language_normalizes_spanish_alias_for_display_metadata` now
has two parameterized cases:

- `--language Spanish`
- `--language es-MX`

For each alias, the test invokes both:

```powershell
entrypoints --package ringcentral-video --area "Meeting toolbar" --language <alias>
entrypoints --package ringcentral-video --area "More menu" --language <alias>
```

It asserts:

- exit code `0`
- `Language: es`
- localized title and purpose markers for
  `ringcentral.video.toolbar.audio-menu`
- localized title and purpose markers for
  `ringcentral.video.toolbar.video-menu`
- fallback title and purpose markers for `ringcentral.video.toolbar.audio`
- localized title and purpose markers for
  `ringcentral.video.more.background`
- fallback title and purpose markers for `ringcentral.video.more.recording`

`test_entrypoints_language_uses_package_local_metadata_without_runtime_voice_validation`
continues to guard the provider boundary. It monkeypatches runtime voice helper
calls to fail if invoked, then proves `entrypoints --language` uses package-local
metadata inspection without checking runtime voice availability.

## Commands Run Or Expected

Inspection commands run while preparing this handoff:

```powershell
git status --short
rg -n "audio-menu|video-menu|more\.background|Spanish|es-MX|Language: es|Meeting toolbar" tests/unit/test_cli.py
Get-ChildItem docs\agent-handoffs | Sort-Object Name | Select-Object -Last 8 | Format-Table -AutoSize
Get-Content -Raw docs\agent-handoffs\cycle-141-implementation.md
git diff -- tests/unit/test_cli.py
Get-Content tests\unit\test_cli.py | Select-Object -Skip 730 -First 150
Get-Content -Raw docs\agent-handoffs\cycle-142-demand-analysis.md
Get-Content -Raw docs\agent-handoffs\cycle-142-risk-scan.md
```

Focused verification run:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_entrypoints_language_normalizes_spanish_alias_for_display_metadata tests\unit\test_cli.py::test_entrypoints_language_uses_package_local_metadata_without_runtime_voice_validation
```

Expected and observed:

```text
4 passed
```

Recommended final hygiene for the implementation owner:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py
.\.venv\Scripts\ruff.exe check --no-cache tests\unit\test_cli.py
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
git diff --check
git status --short
```

Expected:

- The focused Cycle142 CLI tests pass.
- The broader CLI unit file passes if the surrounding worktree is otherwise
  healthy.
- Ruff reports no style errors in `tests/unit/test_cli.py`.
- `localization-report --require-complete` remains green for required Spanish
  package localization without making optional entrypoint display metadata
  required.
- `git diff --check` reports no whitespace errors.
- `git status --short` shows only intended test/handoff files plus known
  concurrent artifacts such as `.coverage`.

## Boundaries

This is a tests-only implementation plus this handoff document.

Do not change:

- `packages/ringcentral-video.yaml`
- `src/ai_presenter/cli.py`
- `src/ai_presenter/packages/models.py`
- `src/ai_presenter/packages/localization_status.py`
- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/runtime/voice.py`
- Spanish `questionAliases`, Q&A prompts, Q&A answers, demo narration,
  `openSteps`, cleanup modes, routes, `questionPolicy`, providers, profiles,
  or durable localization counts

Do not reinterpret this guard as runtime Spanish voice support. It proves
package-local CLI inspection behavior only.

Do not reinterpret localized CLI display output as question-routing behavior.
Cycle141 owns the matcher boundary, and `localizedTitles.es` /
`localizedPurposes.es` must remain display/inspection metadata rather than
entrypoint match candidates.

Do not make optional Spanish entrypoint display metadata part of
`--require-complete`. Spanish optional `localizedTitles.es` and
`localizedPurposes.es` remain partial at the Cycle140 `8/27` state.

Do not claim live RingCentral Video acceptance, local SAPI/Piper/fake speech
Spanish support, bind-speaker readiness, device switching, camera switching,
background selection, Blur selection, or private settings inspection from these
tests.

## Next Cycle Recommendation

Keep building adjacent guardrails without changing behavior:

- Consider a compact README or lifecycle doc assertion that the CLI inspection
  examples remain package-local and marker-based.
- Keep marker-centered assertions for future display metadata expansion so
  Spanish copy edits do not create unnecessary CLI test churn.
- Avoid broadening the Cycle142 test into runtime matching, provider readiness,
  or live RingCentral acceptance.

Keep package YAML, source behavior, matcher behavior, aliases, provider/profile
logic, localization counts, durable docs, and unrelated dirty artifacts
unchanged.
