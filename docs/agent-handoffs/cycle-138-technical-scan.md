# Cycle 138 Technical Scan: Package-Language Alias CLI Normalization

Date: 2026-05-16

## Scope

Read-only scan for a technically clean small Cycle138 slice. This scan changed
only this handoff file.

Baseline constraints:

- `.coverage` is already modified in the worktree; leave it untouched.
- Do not stage or commit unless a later owner explicitly asks.
- Avoid broad refactors, runtime/provider changes, package YAML churn, live
  RingCentral acceptance claims, or generated artifact updates.

Areas inspected:

- Spanish display metadata and package localization CLI output.
- CLI language/tone normalization paths.
- Question-answer localization and tone tests.
- Package-localization report internals.
- RingCentral knowledge docs and README boundary wording.
- Focused test speed for relevant CLI/voice checks.

## Recommendation

Implement one small CLI consistency slice: normalize known presenter language
aliases for package-local language commands while preserving unknown raw package
keys.

Target behavior:

- `localization-report --language Spanish` and `--language es-MX` should inspect
  canonical package key `es`, matching the existing runtime voice alias behavior.
- `entrypoints --language Spanish` and `--language es-MX` should show the same
  localized/fallback Spanish title and purpose metadata as `--language es`.
- Unknown package-only keys such as `de` should remain accepted as raw package
  localization keys so future package-local languages are not blocked merely
  because runtime voice does not support them.
- The output should print the resolved key, e.g. `Language: es`, to avoid the
  current misleading all-zero `Language: Spanish` report.

This is cleaner than another Spanish YAML/display-metadata expansion because
Cycle136 already moved optional Spanish entrypoint display metadata to `5/27`
and Cycle137 clarified the docs boundary. It is also safer than performance or
runtime work because it keeps behavior inside pure package inspection commands
and reuses existing language normalization semantics.

## Evidence From Scan

Current mismatch observed:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language Spanish
```

exits `0` but reports zero coverage for `Language: Spanish`, including `0/51`
demo steps, `0/12` Q&A questions, `0/12` Q&A answers, and no Spanish
entrypoint display metadata. The equivalent `--language es` command reports the
expected complete Spanish package state: `51/51`, `12/12`, `12/12`,
`questionAliases.es` on `26/27` entrypoints with `69` aliases, and
`localizedTitles.es` / `localizedPurposes.es` on `5/27` entrypoints.

Similarly:

```powershell
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting top bar" --language Spanish
```

prints fallback English display metadata for Network quality and Views, while
`--language es` correctly prints `Calidad de red` and `Diseño de vista`.

The mismatch exists because `demo`, `controller`, `doctor`, and `voices` use
`PresenterVoiceSettings` / presenter language alias helpers, while
`entrypoints` and `localization-report` currently pass the raw language string
straight into package-local dictionaries.

Relevant current code:

- `src/ai_presenter/cli.py`: `entrypoints()` strips `language` into
  `language_filter` without normalization.
- `src/ai_presenter/cli.py`: `localization_report()` passes `language` directly
  to `build_localization_status()`.
- `src/ai_presenter/runtime/voice.py`: presenter language aliases already
  normalize `Spanish`, `es-ES`, and `es-MX` to `es`; `zh-CN` to `zh`; and
  `ja-JP` to `ja`.

Focused test speed is acceptable for this slice. A no-coverage focused pytest
probe for the existing Spanish localization report, entrypoints output, and
voice alias normalization took about `2.60s`:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_voice.py::test_voice_settings_normalize_language_aliases
```

RingCentral durable docs are already aligned with the current Spanish state:

- `docs/knowledge/language-lifecycle.md` says Spanish required package
  localization is complete, optional entrypoint display metadata is partial at
  `5/27`, and runtime Spanish requires OpenAI-backed speech.
- `docs/knowledge/ringcentral-video/source-index.md` has the same `5/27`,
  `26/27`, and `69 aliases` counts.
- `docs/knowledge/ringcentral-video/runtime-safety-routing.md` keeps Spanish
  local SAPI/Piper and live acceptance as future work.
- `README.md` already distinguishes package-local `entrypoints --language es`
  inspection from runtime voice/provider validation.

## Exact Files For Implementation

Primary source:

- `src/ai_presenter/cli.py`

Focused tests:

- `tests/unit/test_cli.py`

Optional docs polish:

- `README.md`

Implementation handoff:

- `docs/agent-handoffs/cycle-138-implementation.md`

Do not touch:

- `.coverage`
- `packages/ringcentral-video.yaml`
- `src/ai_presenter/runtime/voice.py`
- `src/ai_presenter/packages/localization_status.py`
- provider, controller, desktop automation, diagnostics, or live acceptance
  files

## Implementation Notes

Add a small helper in `src/ai_presenter/cli.py`, near `resolve_voice_settings()`:

```python
def resolve_package_language_key(language: str) -> str:
    value = language.strip()
    try:
        return normalize_presenter_language(value)
    except ValueError:
        return value
```

Import `normalize_presenter_language` from `ai_presenter.runtime.voice`.

Use the helper only in package-local inspection/reporting commands:

- In `entrypoints()`, set `language_filter` to
  `None if language is None else resolve_package_language_key(language)`.
- In `localization_report()`, pass
  `language=resolve_package_language_key(language)` to
  `build_localization_status()`.

Do not use `PresenterVoiceSettings` here. These commands inspect package keys,
not runtime voice support. They should normalize known aliases for convenience
but keep raw unknown keys available for package-only localization inspection.

README polish is optional but useful. If included, add one sentence near the
localization commands, for example:

```markdown
Known runtime language aliases such as `Spanish`, `es-MX`, and `zh-CN`
normalize to package keys for these inspection commands; unknown keys remain
raw package-local lookup keys.
```

Keep the README caveat that `entrypoints --language ...` does not validate
runtime voice support, local SAPI/Piper assets, controller/demo execution, or
live RingCentral Video acceptance.

## Test Strategy

Add failing tests first in `tests/unit/test_cli.py`:

- `test_localization_report_normalizes_spanish_language_aliases`
  - Invoke `localization-report --package ringcentral-video --language Spanish`.
  - Assert exit code `0`.
  - Assert `Language: es`.
  - Assert `Localization report: 51/51 demo steps`.
  - Assert `questionAliases.es present on 26/27 entrypoints (69 aliases)`.
  - Assert `localizedTitles.es present on 5/27 entrypoints`.

- `test_entrypoints_language_normalizes_spanish_alias_for_display_metadata`
  - Invoke `entrypoints --package ringcentral-video --area "Meeting top bar" --language es-MX`.
  - Assert `Language: es`.
  - Assert `Calidad de red` and `Diseño de vista`.
  - Assert localized markers for Network quality and Views.
  - Assert Meeting information remains fallback.

- `test_localization_report_keeps_unknown_package_language_key_raw`
  - Invoke `localization-report --package ringcentral-video --language de`.
  - Assert exit code `0`.
  - Assert `Language: de`.
  - Assert `Localization report: 0/51 demo steps`.
  - Assert no `Invalid value` or `Unsupported presenter language` text.

Suggested focused red/green command:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_localization_report_normalizes_spanish_language_aliases tests\unit\test_cli.py::test_entrypoints_language_normalizes_spanish_alias_for_display_metadata tests\unit\test_cli.py::test_localization_report_keeps_unknown_package_language_key_raw
```

Regression command:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_entrypoints_language_uses_package_local_metadata_without_runtime_voice_validation tests\unit\test_cli.py::test_demo_openai_profile_accepts_spanish_dry_run tests\unit\test_cli.py::test_demo_rejects_spanish_local_profile_before_runtime tests\unit\test_voice.py::test_voice_settings_normalize_language_aliases tests\unit\test_voice.py::test_presenter_spanish_language_aliases_are_public_and_canonical
```

Manual CLI probes:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language Spanish
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es-MX --require-complete
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language de
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting top bar" --language Spanish
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting top bar" --language es-MX
```

Static checks:

```powershell
.\.venv\Scripts\python.exe -m ruff check src\ai_presenter\cli.py tests\unit\test_cli.py
rg -n "Spanish|es-MX|zh-CN|package-local|runtime voice|SAPI|Piper|live RingCentral" README.md src\ai_presenter\cli.py tests\unit\test_cli.py docs\knowledge\language-lifecycle.md docs\knowledge\ringcentral-video\source-index.md docs\knowledge\ringcentral-video\runtime-safety-routing.md
git diff --check
git status --short
```

Expected status: only intended Cycle138 implementation files plus the
pre-existing `.coverage` modification.

## Edge Cases

- Do not reject `de`, `fr`, or other unknown package-local keys in
  `localization-report` or `entrypoints`; package inspection should remain more
  permissive than runtime voice.
- Do not change `--require-complete` semantics. It should still fail only when
  required demo narration or Q&A localization is incomplete for the resolved
  package key.
- Do not add Spanish aliases, display metadata, Q&A, narration, or YAML counts
  in this slice.
- Do not claim Spanish optional entrypoint display metadata is complete; it
  remains partial at `5/27`.
- Do not describe `entrypoints --language Spanish` as runtime validation. It is
  package-local metadata inspection only.
- Do not alter `demo`, `controller`, `doctor`, or `voices` runtime language
  behavior except through shared imports if necessary.
- Keep known alias normalization canonical in output. Printing `Language: es`
  after `--language Spanish` is preferable because the report lines use package
  keys such as `questionAliases.es`.
- Preserve `entrypoints` fallback markers for unseeded Spanish display metadata,
  especially Meeting information and Report issue.

## Rollback

Rollback is small and local:

```powershell
git diff -- src\ai_presenter\cli.py tests\unit\test_cli.py README.md docs\agent-handoffs\cycle-138-implementation.md
git checkout -- src\ai_presenter\cli.py tests\unit\test_cli.py README.md docs\agent-handoffs\cycle-138-implementation.md
```

Only run the checkout command for files the implementation owner actually
changed and wants to discard. Do not use broad reset/checkout commands, and do
not touch `.coverage`.
