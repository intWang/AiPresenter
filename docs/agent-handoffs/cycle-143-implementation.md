# Cycle 143 Implementation Handoff: Entrypoints Language Marker Docs

Date: 2026-05-17
Cycle: 143
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Scope: implementation handoff only. This handoff documents the Cycle143
docs/test contract already present in the worktree and adds no source, test, or
package changes.

## Objective

Document Cycle143's docs-only alignment for `entrypoints --language`.

The implemented contract keeps `entrypoints --package ringcentral-video
--language es` framed as package-local, marker-based display metadata
inspection. It is an inspection surface for optional entrypoint
`localizedTitles.<lang>` and `localizedPurposes.<lang>` after package language
key resolution. It is not runtime Spanish readiness, provider validation,
matcher expansion, controller/demo execution, voice asset readiness, or live
RingCentral Video acceptance.

## Files Changed

Observed implementation files:

- `README.md`
  - Replaced the looser package-local inspection paragraph with explicit marker
    wording.
  - States that `--language es` prints `Language: es`.
  - Defines localized title markers as `(title: localized)`.
  - Defines localized purpose markers as `(localized)`.
  - Defines canonical title/purpose fallback markers as `(title: fallback)` and
    `(fallback)`.
  - States these markers are display-source labels only and are not evidence of
    runtime Spanish readiness, matcher expansion, provider availability, local
    SAPI/Piper assets, controller/demo execution, or live RingCentral Video
    acceptance.
  - Removed the adjacent README sentence that tied the entrypoint inspection
    example to Spanish package localization completeness and OpenAI-backed
    runtime selectability.

- `docs/knowledge/language-lifecycle.md`
  - Added the Spanish marker contract to lifecycle gate 3,
    `Entrypoint display metadata inspection`.
  - Documents that Spanish inputs such as `es`, `Spanish`, and `es-MX` display
    `Language: es`.
  - Documents field-level markers for entrypoint title and following
    `purpose:` lines.
  - Tightened the boundary so marker output is explicitly not evidence of
    runtime Spanish readiness, matcher expansion, provider compatibility, voice
    asset availability, controller/demo execution, or live RingCentral Video
    acceptance.
  - Preserves the existing package-local language key boundary, including known
    presenter-language alias normalization and unknown raw package metadata
    lookup keys.

- `tests/unit/test_cli.py`
  - Added `test_entrypoints_language_marker_contract_is_documented`.
  - The guard checks README for the `entrypoints --package ringcentral-video
    --language es` command, `Spanish` / `es-MX` alias wording, `Language: es`,
    localized/fallback markers, and explicit runtime/provider/matcher/live
    boundaries.
  - The guard checks lifecycle for the more precise marker contract and
    display-source boundary.
  - The guard also asserts README does not reintroduce runtime-selectability or
    runtime-validation claims next to that inspection example.

Documentation file added by this handoff:

- `docs/agent-handoffs/cycle-143-implementation.md`

Concurrent worktree state observed before this handoff:

- `.coverage` was already modified.
- `README.md`, `docs/knowledge/language-lifecycle.md`, and
  `tests/unit/test_cli.py` were already modified with Cycle143 implementation
  changes.
- `docs/agent-handoffs/cycle-143-demand-analysis.md`,
  `docs/agent-handoffs/cycle-143-risk-scan.md`, and
  `docs/agent-handoffs/cycle-143-technical-scan.md` were already untracked.

Treat those as other workers' edits unless a later task explicitly says
otherwise. Do not revert, normalize, stage, or claim ownership of unrelated
dirty files from this handoff.

## Exact Doc Contract

README contract:

- The command example remains:

```powershell
.\.venv\Scripts\ai-presenter entrypoints --package ringcentral-video --language es
```

- The command is described as package-local entrypoint display metadata
  inspection.
- With `--language es`, the command prints `Language: es`.
- Localized titles are labeled `(title: localized)`.
- Localized purposes are labeled `(localized)`.
- Canonical title fallbacks are labeled `(title: fallback)`.
- Canonical purpose fallbacks are labeled `(fallback)`.
- The markers are display-source labels only.
- The markers are not evidence of runtime Spanish readiness, matcher
  expansion, provider availability, local SAPI/Piper assets, controller/demo
  execution, or live RingCentral Video acceptance.
- `doctor --require-localization --localization-language ...` remains the
  separate command for checking package localization keys apart from runtime
  presenter voice support.

Language lifecycle contract:

- `localizedTitles.<lang>` and `localizedPurposes.<lang>` remain optional
  package-local display metadata for entrypoint answer rendering and
  inspection.
- `entrypoints --language <lang>` is package-local inspection.
- Known presenter-language aliases such as `Spanish`, `es-MX`, and `zh-CN`
  normalize to canonical package keys before package-local inspection.
- Unknown package-only keys remain raw package metadata lookup keys, so future
  package-local languages are not blocked by runtime voice support.
- The command prints `Language: <key>` using the resolved package key.
- Spanish inputs `es`, `Spanish`, and `es-MX` display `Language: es`.
- Entrypoint title rows mark source with `(title: localized)` or
  `(title: fallback)`.
- The following `purpose:` line ends in `(localized)` or `(fallback)`.
- `localized` means nonblank package-local display copy was found for that
  field.
- `fallback` means canonical title or purpose copy was shown.
- These markers do not affect matching candidates, alias ordering, Q&A
  precedence, safety gating, controller interrupts, provider routing, voice
  assets, or live acceptance.

Test guard contract:

- `test_entrypoints_language_marker_contract_is_documented` is a documentation
  guard. It protects durable wording, not runtime behavior.
- It intentionally requires both README and lifecycle docs to mention the
  marker contract and runtime-boundary language.
- It intentionally prevents the README from reintroducing the nearby sentence
  that conflated the inspection example with Spanish runtime selectability.

## Tests Run Or Expected

Focused verification run while preparing this handoff:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_package_language_alias_normalization_is_documented tests\unit\test_cli.py::test_entrypoints_language_marker_contract_is_documented tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_entrypoints_language_normalizes_spanish_alias_for_display_metadata tests\unit\test_cli.py::test_entrypoints_language_uses_package_local_metadata_without_runtime_voice_validation
```

Observed:

```text
6 passed
```

Expected final hygiene for the implementation owner:

```powershell
git diff -- README.md docs\knowledge\language-lifecycle.md tests\unit\test_cli.py
git diff --check -- README.md docs\knowledge\language-lifecycle.md tests\unit\test_cli.py docs\agent-handoffs\cycle-143-implementation.md
git status --short
```

Expected status should show this handoff plus the intended Cycle143 docs/test
changes and any pre-existing unrelated dirty artifacts. It should not show
source, package YAML, provider/profile, voice asset, generated artifact, or
runtime behavior changes caused by this handoff.

## Boundaries

This handoff is documentation-focused. The only test change is a docs guard
that reads README/lifecycle text; it does not exercise or alter CLI behavior.

Do not change:

- `src/ai_presenter/cli.py`
- `src/ai_presenter/packages/models.py`
- `src/ai_presenter/packages/localization_status.py`
- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/runtime/voice.py`
- `packages/ringcentral-video.yaml`
- `profiles/*.yaml`
- CLI behavior tests in `tests/unit/test_cli.py`
- Spanish `questionAliases`, Q&A prompts, Q&A answers, demo narration,
  `localizedTitles.es`, `localizedPurposes.es`, `openSteps`, cleanup modes,
  routes, `questionPolicy`, providers, profiles, or durable localization counts
- generated artifacts such as `.coverage`

Do not claim from this cycle:

- Spanish local SAPI or Piper readiness.
- Fake speech Spanish support.
- Bind-speaker Spanish readiness.
- Provider compatibility beyond the separately documented OpenAI-backed runtime
  boundary.
- Query matcher expansion from localized entrypoint titles or purposes.
- `localization-report --require-complete` coverage for optional entrypoint
  display metadata.
- Controller or demo execution support from CLI inspection output.
- Live RingCentral Video acceptance.

`localizedTitles.es` and `localizedPurposes.es` remain optional, partial
display metadata. Fallback markers are expected inspection output, not a failed
localization state.

## Next Cycle Recommendation

Keep the next cycle narrow and evidence-centered:

- Prefer no further implementation unless wording drift appears again.
- If future docs mention `entrypoints --language`, keep the command labeled as
  package-local marker-based display metadata inspection.
- If optional Spanish display metadata expands beyond the current partial
  state, update count-backed docs and marker-centered tests together.
- If anyone wants to promote Spanish beyond the existing OpenAI-backed runtime
  boundary, make that a separate runtime/acceptance cycle with provider,
  profile, `doctor`, `voices`, demo/controller, and dated RingCentral evidence.

Avoid using Cycle143 as justification for source changes, matcher changes,
package YAML edits, provider/profile changes, or live-acceptance claims.
