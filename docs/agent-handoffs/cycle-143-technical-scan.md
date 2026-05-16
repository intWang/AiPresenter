# Cycle 143 Technical Scan

## Candidate

Docs-only guard aligning `README.md` and
`docs/knowledge/language-lifecycle.md` with the Cycle142 CLI marker contract:
`entrypoints --language` is package-local entrypoint display metadata
inspection. It prints the resolved package key, such as `Language: es`, and
labels title/purpose source as localized or fallback. It must not be described
as runtime Spanish readiness, matcher expansion, provider validation, voice
asset readiness, controller/demo execution, or live RingCentral acceptance.

## Current State Observed

- `README.md` already has an `entrypoints --package ringcentral-video
  --language es` example and says the command inspects localized and fallback
  entrypoint title/purpose metadata only.
- The README paragraph immediately after that still mixes in Spanish runtime
  and provider wording: `Spanish RingCentral Video package localization is
  complete, and --language es is runtime-selectable only with OpenAI-backed
  speech profiles.`
- `docs/knowledge/language-lifecycle.md` already has a dedicated
  `Entrypoint display metadata inspection` gate and states that
  `entrypoints --language <lang>` is package-local inspection.
- The lifecycle doc already documents package-key resolution, unknown raw keys,
  localized/fallback source markers, and the no-runtime-voice/provider boundary,
  but it does not explicitly tie the Spanish CLI contract to `Language: es` or
  the exact marker strings.
- `tests/unit/test_cli.py` contains the Cycle142 behavior guard:
  `test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy`,
  `test_entrypoints_language_normalizes_spanish_alias_for_display_metadata`,
  and
  `test_entrypoints_language_uses_package_local_metadata_without_runtime_voice_validation`.
- `tests/unit/test_cli.py::test_package_language_alias_normalization_is_documented`
  already checks lifecycle wording for package language key resolution.
- No README wording test exists yet.
- Initial status had a pre-existing modified `.coverage` artifact. Do not stage
  or revert it.

## Files To Touch

### `README.md`

Touch only the material demo / entrypoint inspection wording around the current
Spanish entrypoint display metadata example. Replace the prose after:

```powershell
.\.venv\Scripts\ai-presenter entrypoints --package ringcentral-video --language es
```

with this exact wording or a very close equivalent:

```markdown
This is package-local entrypoint display metadata inspection. With `--language
es`, the command prints `Language: es`, marks localized titles as `(title:
localized)`, marks localized purposes as `(localized)`, and marks canonical
title/purpose fallbacks as `(title: fallback)` and `(fallback)`. These markers
are display-source labels only. They are not evidence of runtime Spanish
readiness, matcher expansion, provider availability, local SAPI/Piper assets,
controller or demo execution, or live RingCentral Video acceptance.

Use `doctor --require-localization --localization-language ...` when checking
package localization keys that are separate from runtime presenter voice
support. The language lifecycle and promotion gates are documented in
`docs/knowledge/language-lifecycle.md`.
```

Remove the nearby sentence that ties this inspection example to runtime/provider
support:

```markdown
Spanish RingCentral Video package localization is complete, and `--language es`
is runtime-selectable only with OpenAI-backed speech profiles. Local SAPI and
Piper routes do not support Spanish yet.
```

Do not update the later voice compatibility paragraph unless the implementation
owner deliberately broadens the task. That paragraph is separate from the
entrypoints inspection contract and is backed by voice/profile tests.

### `docs/knowledge/language-lifecycle.md`

In gate 3, `Entrypoint display metadata inspection`, add one explicit Spanish
marker-contract paragraph after the `Evidence:` bullet and before
`Important boundary:`:

```markdown
   For Spanish inputs such as `es`, `Spanish`, and `es-MX`, the command
   displays `Language: es`. Each entrypoint line marks the title source with
   `(title: localized)` or `(title: fallback)`, and the following `purpose:`
   line ends in `(localized)` or `(fallback)`.
```

Then sharpen the boundary bullets so they include the support-claim guard:

```markdown
   - These markers are display-source labels only. They are not evidence of
     runtime Spanish readiness, matcher expansion, provider compatibility,
     voice asset availability, controller/demo execution, or live RingCentral
     Video acceptance.
```

Keep the existing Current Spanish State counts intact:

- `51/51` demo steps
- `12/12` Q&A questions
- `12/12` Q&A answers
- `questionAliases.es` on `26/27` entrypoints with `69` aliases
- `localizedTitles.es` on `8/27` entrypoints
- `localizedPurposes.es` on `8/27` entrypoints

Do not rewrite the real runtime voice state in this slice. The docs change is
about keeping `entrypoints --language` from being treated as evidence for that
state.

### `tests/unit/test_cli.py`

Add a focused docs guard near
`test_package_language_alias_normalization_is_documented`:

```python
def test_entrypoints_language_marker_contract_is_documented() -> None:
    readme_text = Path("README.md").read_text(encoding="utf-8")
    lifecycle_text = Path("docs/knowledge/language-lifecycle.md").read_text(
        encoding="utf-8"
    )
    normalized_readme_text = " ".join(readme_text.split())
    normalized_lifecycle_text = " ".join(lifecycle_text.split())

    assert "entrypoints --package ringcentral-video --language es" in readme_text
    for doc_text in (normalized_readme_text, normalized_lifecycle_text):
        assert "Language: es" in doc_text
        assert "(title: localized)" in doc_text
        assert "(title: fallback)" in doc_text
        assert "display-source labels only" in doc_text
        assert "not evidence of runtime Spanish readiness" in doc_text
        assert "matcher expansion" in doc_text
        assert "provider" in doc_text
        assert "live RingCentral Video acceptance" in doc_text

    assert (
        "Spanish RingCentral Video package localization is complete, and "
        "`--language es` is runtime-selectable"
        not in normalized_readme_text
    )
```

Keep `test_package_language_alias_normalization_is_documented` in place. It
guards key resolution wording and complements the new marker-contract test.

## Files Not To Touch

- `src/ai_presenter/cli.py`
- `src/ai_presenter/packages/models.py`
- `src/ai_presenter/packages/localization_status.py`
- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/runtime/voice.py`
- `packages/ringcentral-video.yaml`
- `profiles/*.yaml`
- RingCentral evidence or acceptance docs
- `.coverage`

If any source or package change seems necessary, pause and rescope. Cycle142
already verified the behavior; Cycle143 should only align durable docs and the
doc guard.

## Verification Commands

Focused docs and CLI marker tests:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_package_language_alias_normalization_is_documented tests\unit\test_cli.py::test_entrypoints_language_marker_contract_is_documented tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_entrypoints_language_normalizes_spanish_alias_for_display_metadata tests\unit\test_cli.py::test_entrypoints_language_uses_package_local_metadata_without_runtime_voice_validation
```

Adjacent package-count and matcher-boundary sentinels:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_spanish_display_metadata_counts_match_durable_docs tests\unit\test_material_packages.py::test_entrypoint_localized_title_and_purpose_do_not_affect_match_candidates tests\unit\test_questions.py::test_ringcentral_spanish_display_metadata_is_not_part_of_match_candidates tests\unit\test_questions.py::test_ringcentral_spanish_display_metadata_fragments_do_not_create_matches
```

Manual inspection smoke probes:

```powershell
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting toolbar" --language es
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting toolbar" --language Spanish
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "More menu" --language es-MX
```

Expected probe traits:

- Output includes `Language: es`.
- `ringcentral.video.toolbar.audio-menu` and
  `ringcentral.video.toolbar.video-menu` show localized title and purpose
  markers.
- `ringcentral.video.toolbar.audio` shows fallback title and purpose markers.
- `ringcentral.video.more.background` shows localized title and purpose markers.
- `ringcentral.video.more.recording` shows fallback title and purpose markers.

Final hygiene:

```powershell
.\.venv\Scripts\ruff.exe check --no-cache tests\unit\test_cli.py
git diff --check -- README.md docs/knowledge/language-lifecycle.md tests/unit/test_cli.py
git status --short
```

## No-Go Claims

- Do not claim `entrypoints --language es` proves Spanish runtime readiness.
- Do not claim localized entrypoint display metadata expands question matching.
- Do not claim provider, local SAPI/Piper, fake speech, voice asset, or
  bind-speaker support from CLI inspection output.
- Do not claim live RingCentral Video acceptance from CLI inspection output.
- Do not make optional `localizedTitles.es` or `localizedPurposes.es` part of
  `localization-report --require-complete`.
- Do not change Spanish aliases, Q&A, demo narration, localization counts,
  package YAML, profile YAML, or source behavior.
