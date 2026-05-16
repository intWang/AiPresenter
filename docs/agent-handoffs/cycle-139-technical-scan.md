# Cycle 139 Technical Scan: Package Language Alias Docs Guard

Date: 2026-05-17

## Scope

Read-only technical scan for a small Cycle139 implementation slice. This scan
owns only this handoff file.

Worktree baseline:

- `.coverage` is already modified and must remain untouched and unstaged.
- Do not stage or commit unless a later owner explicitly asks.
- Do not change runtime provider behavior, voice provider routing, package YAML,
  live RingCentral acceptance claims, or broad localization semantics.

Areas considered:

- Safe Spanish display metadata wedge.
- Post-alias-normalization CLI tests and docs.
- Package loading and test-speed hygiene.
- RingCentral knowledge docs.
- Language/tone tests.

## Recommendation

Implement one small post-alias-normalization docs/test slice: update the durable
language lifecycle guidance so it matches Cycle138 CLI behavior, and add a
focused doc guard that prevents the stale "raw language-key lookup" wording from
returning.

Target behavior to document:

- `localization-report --language Spanish` resolves to package key `es`.
- `entrypoints --language es-MX` resolves to package key `es`.
- Unknown package-only keys such as `de` remain accepted as raw lookup keys for
  package inspection.
- These commands remain package-local inspection only; they do not validate
  runtime voice support, local SAPI/Piper assets, controller/demo execution, or
  live RingCentral Video acceptance.

This is cleaner than another Spanish display metadata wedge because the current
Spanish optional display metadata state is already intentionally partial at
`5/27`, and changing package YAML would expand product knowledge. It is safer
than package-loading optimization because there is a concrete docs drift from
Cycle138, while performance work would need deeper parity coverage. It is also
smaller than language/tone behavior work because CLI behavior is already tested
and passing.

## Evidence From Scan

Cycle138 implemented the behavior in `src/ai_presenter/cli.py`:

- `resolve_package_language_key()` calls `normalize_presenter_language()` for
  known presenter language aliases.
- `entrypoints()` and `localization_report()` use that helper.
- Unknown values fall back to the stripped raw key.

Focused verification from this scan:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_localization_report_normalizes_spanish_language_aliases tests\unit\test_cli.py::test_entrypoints_language_normalizes_spanish_alias_for_display_metadata tests\unit\test_cli.py::test_entrypoints_language_uses_package_local_metadata_without_runtime_voice_validation tests\unit\test_material_packages.py::test_ringcentral_spanish_display_metadata_counts_match_durable_docs
```

Result: `4 passed in 1.30s`.

Manual CLI probes:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language Spanish
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting top bar" --language es-MX
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language de
```

Observed results:

- `Spanish` printed `Language: es` and complete Spanish package coverage:
  `51/51` demo steps, `12/12` Q&A questions, `12/12` Q&A answers,
  `questionAliases.es` on `26/27` entrypoints with `69` aliases, and
  `localizedTitles.es` / `localizedPurposes.es` on `5/27` entrypoints.
- `es-MX` for `entrypoints` printed `Language: es`, showed localized Spanish
  display metadata for seeded top-bar entries, and preserved fallback metadata
  for unseeded entries.
- `de` printed `Language: de`, reported `0/51` demo steps and no unsupported
  presenter language error, proving raw unknown package keys still work.

Docs drift found:

- `docs/knowledge/language-lifecycle.md` still says
  `entrypoints --language <lang>` performs a raw language-key lookup.
- The same section says the command prints `Language: <key>` using the key the
  author provided.
- That was accurate before Cycle138 but is now incomplete: known aliases are
  canonicalized before package lookup and output.

Current docs already aligned enough:

- `README.md` explains package-local entrypoint metadata inspection separately
  from runtime voice support and live RingCentral acceptance.
- `docs/knowledge/ringcentral-video/source-index.md` and
  `runtime-safety-routing.md` keep Spanish package coverage, OpenAI-only runtime
  support, and local SAPI/Piper/live acceptance boundaries separate.

## Exact Files For Implementation

Primary docs:

- `docs/knowledge/language-lifecycle.md`

Focused test:

- `tests/unit/test_cli.py`

Optional docs polish, only if the wording stays tiny:

- `README.md`

Implementation handoff:

- `docs/agent-handoffs/cycle-139-implementation.md`

Do not touch:

- `.coverage`
- `packages/ringcentral-video.yaml`
- `src/ai_presenter/cli.py`
- `src/ai_presenter/runtime/voice.py`
- provider modules, controller runtime, desktop automation, diagnostics, live
  acceptance docs, or generated artifacts

## Implementation Notes

In `docs/knowledge/language-lifecycle.md`, update the Entrypoint display
metadata inspection boundary from raw-only wording to alias-aware wording.

Suggested replacement shape:

```markdown
- `entrypoints --language <lang>` is package-local inspection. Known presenter
  language aliases such as `Spanish`, `es-MX`, and `zh-CN` normalize to their
  canonical package keys before lookup.
- Unknown package-only keys remain raw package metadata lookup keys, so future
  package-local languages are not blocked by runtime voice support.
- The command prints `Language: <key>` using the resolved package key.
```

Also mention the same alias behavior for `localization-report`, either in the
Package localization complete section or a short shared note near the lifecycle
evidence bullets. Keep the runtime boundary wording intact.

Recommended test in `tests/unit/test_cli.py`:

```python
def test_package_language_alias_normalization_is_documented() -> None:
    lifecycle_text = Path("docs/knowledge/language-lifecycle.md").read_text(
        encoding="utf-8"
    )

    assert cli.resolve_package_language_key("Spanish") == "es"
    assert cli.resolve_package_language_key("es-MX") == "es"
    assert cli.resolve_package_language_key("zh-CN") == "zh"
    assert cli.resolve_package_language_key("de") == "de"
    assert "raw language-key lookup" not in lifecycle_text
    assert "known presenter language aliases" in lifecycle_text
    assert "Unknown package-only keys remain raw" in lifecycle_text
    assert "resolved package key" in lifecycle_text
```

If README is touched, add only one sentence near the package localization
commands:

```markdown
Known presenter language aliases such as `Spanish` and `es-MX` normalize to
canonical package keys for package inspection; unknown keys remain raw
package-local lookup keys.
```

Do not make README the primary source of truth; keep the lifecycle doc canonical.

## Test Strategy

Focused red/green command:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_package_language_alias_normalization_is_documented tests\unit\test_cli.py::test_localization_report_normalizes_spanish_language_aliases tests\unit\test_cli.py::test_entrypoints_language_normalizes_spanish_alias_for_display_metadata tests\unit\test_cli.py::test_localization_report_keeps_unknown_package_language_key_raw
```

Docs/count guard:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_spanish_display_metadata_counts_match_durable_docs
```

Manual probes:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language Spanish
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting top bar" --language es-MX
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language de
rg -n "raw language-key lookup|known presenter language aliases|Unknown package-only keys remain raw|resolved package key|runtime voice support|live RingCentral Video acceptance|SAPI|Piper" docs\knowledge\language-lifecycle.md README.md
git diff --check
git status --short
```

Expected status: only the intended docs/test/implementation-handoff files plus
the pre-existing `.coverage` modification.

## Edge Cases

- Do not reject unknown package keys such as `de`; package inspection remains
  more permissive than runtime voice.
- Do not imply `entrypoints --language Spanish` validates runtime Spanish
  support. It only inspects package metadata after resolving the key.
- Do not claim Spanish display metadata is complete; it remains partial at
  `5/27` titles and `5/27` purposes.
- Do not change `--require-complete`; optional display metadata and aliases are
  still diagnostic, not completion gates.
- Do not expand Spanish aliases, Q&A, narration, or entrypoint display metadata.
- Do not change language/tone normalization tables, controller dropdowns, voice
  catalogs, doctor runtime checks, or provider compatibility.
- If README is updated, keep the wording concise and subordinate to
  `docs/knowledge/language-lifecycle.md`.
- Keep tests no-coverage using `--override-ini addopts= -p no:cacheprovider` so
  `.coverage` is not rewritten.

## Rollback

Rollback is local to the docs/test slice:

```powershell
git diff -- docs\knowledge\language-lifecycle.md tests\unit\test_cli.py README.md docs\agent-handoffs\cycle-139-implementation.md
git checkout -- docs\knowledge\language-lifecycle.md tests\unit\test_cli.py README.md docs\agent-handoffs\cycle-139-implementation.md
```

Only run checkout for files the implementation owner actually changed and wants
to discard. Do not use broad reset or checkout commands, and do not touch
`.coverage`.
