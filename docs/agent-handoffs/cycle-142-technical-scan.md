# Cycle 142 Technical Scan: Spanish Entrypoint Marker Guard

Date: 2026-05-17
Scope: technical scan only. This handoff is the only file owned by this task.

## Worktree Note

- `git status --short` showed a pre-existing `.coverage` modification before
  this handoff was written. Leave it alone.
- Do not revert concurrent edits from other workers.
- During final verification, additional unowned changes were visible in
  `tests/unit/test_cli.py` plus untracked
  `docs/agent-handoffs/cycle-142-demand-analysis.md` and
  `docs/agent-handoffs/cycle-142-risk-scan.md`. Treat them as other workers'
  changes unless you explicitly own those files in the implementation turn.
- This cycle should add tests/docs guardrails for:
  `ai-presenter entrypoints --package ringcentral-video --language es`,
  `--language Spanish`, and `--language es-MX`.
- Do not change runtime question matching for this task.

## Current CLI Shape

- `src/ai_presenter/cli.py::resolve_package_language_key()` at lines 75-80
  strips the raw language string, normalizes known presenter language aliases
  through `normalize_presenter_language()`, and returns unknown package-only keys
  unchanged.
- `src/ai_presenter/cli.py::entrypoints()` at lines 261-304:
  - loads the package;
  - lowercases only the optional `--area` filter;
  - resolves `--language` through `resolve_package_language_key()`;
  - prints `Language: <resolved-key>`;
  - prints title markers from `entrypoint.localized_titles`;
  - prints purpose markers from `entrypoint.localized_purposes`;
  - falls back to canonical title/purpose display when the localized field is
    blank or absent.
- No source change is expected. The implementation target is a guard around
  current behavior, not new CLI behavior.

## Existing Tests To Build On

- `tests/unit/test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy`
  currently asserts `--language es` marker output across:
  - `Meeting top bar`;
  - `Meeting toolbar`;
  - `More menu`.
- `tests/unit/test_cli.py::test_entrypoints_language_normalizes_spanish_alias_for_display_metadata`
  currently parametrizes `Spanish` and `es-MX` for `Meeting toolbar` and checks
  `Language: es`, localized marker output for `audio-menu` / `video-menu`, and
  fallback marker output for direct `audio`.
- `tests/unit/test_cli.py::test_entrypoints_language_uses_package_local_metadata_without_runtime_voice_validation`
  monkeypatches runtime voice/profile/provider helpers to fail if
  `entrypoints --language` calls them. Keep this boundary.
- `tests/unit/test_cli.py::test_package_language_alias_normalization_is_documented`
  already checks `Spanish`, `es-MX`, `zh-CN`, and unknown `de` package-key
  normalization against `docs/knowledge/language-lifecycle.md`.
- `tests/unit/test_material_packages.py::test_ringcentral_spanish_display_metadata_counts_match_durable_docs`
  already keeps durable docs aligned with `localizedTitles.es` and
  `localizedPurposes.es` counts.
- `tests/unit/test_questions.py::test_ringcentral_spanish_display_metadata_is_not_part_of_match_candidates`
  and `test_ringcentral_spanish_display_metadata_fragments_do_not_create_matches`
  already protect the runtime matcher boundary. Do not duplicate this through
  CLI tests.

## Recommended Test Touch

Modify only `tests/unit/test_cli.py` unless the docs wording changes require a
small docs assertion.

Preferred narrow change:

- Rename or expand
  `test_entrypoints_language_normalizes_spanish_alias_for_display_metadata`.
- Parametrize the same marker assertions over all three public package
  inspection spellings: `es`, `Spanish`, and `es-MX`.
- Keep `test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy`
  if it is still valuable for cross-area coverage, or trim it only if the new
  test fully covers the same localized/fallback examples.

Recommended assertion shape:

```python
@pytest.mark.parametrize("language_arg", ["es", "Spanish", "es-MX"])
def test_entrypoints_spanish_language_aliases_preserve_display_markers(
    language_arg: str,
) -> None:
    result = CliRunner().invoke(
        app,
        [
            "entrypoints",
            "--package",
            "ringcentral-video",
            "--area",
            "Meeting toolbar",
            "--language",
            language_arg,
        ],
    )

    assert result.exit_code == 0
    assert "Language: es" in result.stdout
    assert (
        "- ringcentral.video.toolbar.audio: Microphone control "
        "[Meeting toolbar] (title: fallback)"
    ) in result.stdout
    assert "  purpose: Toggle mute and unmute in the live meeting. (fallback)" in result.stdout
    assert (
        "- ringcentral.video.toolbar.audio-menu: Menú de micrófono y altavoz "
        "[Meeting toolbar] (title: localized)"
    ) in result.stdout
    assert (
        "  purpose: Abre el menú de audio para revisar Microphone, Speaker, Leave "
        "computer audio, Use phone audio y More audio settings sin cambiar "
        "dispositivos ni leer datos privados. (localized)"
    ) in result.stdout
    assert (
        "- ringcentral.video.toolbar.video: Camera control "
        "[Meeting toolbar] (title: fallback)"
    ) in result.stdout
    assert (
        "- ringcentral.video.toolbar.video-menu: Menú de cámara "
        "[Meeting toolbar] (title: localized)"
    ) in result.stdout
    assert (
        "- ringcentral.video.toolbar.more: Más acciones "
        "[Meeting toolbar] (title: localized)"
    ) in result.stdout
    assert (
        "- ringcentral.video.toolbar.audio: Microphone control "
        "[Meeting toolbar] (title: fallback)"
    ) in result.stdout
    assert "Unsupported presenter language" not in result.output
    assert "Loaded voice" not in result.output
```

Optional docs assertion:

- Extend `test_package_language_alias_normalization_is_documented()` so it also
  asserts the durable lifecycle doc mentions:
  - `entrypoints --language <lang>` as package-local inspection;
  - `Spanish`, `es-MX`, and `zh-CN` as aliases;
  - `Language: <key>`;
  - `localized` source markers;
  - `fallback` source markers;
  - no runtime voice/provider validation.

Avoid exact README coupling unless README text is updated in the same cycle.
`docs/knowledge/language-lifecycle.md` is the better durable guard.

## Recommended Docs Touch

Primary durable docs:

- `docs/knowledge/language-lifecycle.md`
  - Keep the "Entrypoint display metadata inspection" section.
  - It already states that `entrypoints --language <lang>` is package-local
    inspection, aliases such as `Spanish`, `es-MX`, and `zh-CN` normalize to
    package keys, `Language: <key>` is printed, and `localized` / `fallback`
    markers describe display source.
  - If a docs change is needed, add only a compact example showing
    `--language es`, `--language Spanish`, and `--language es-MX` all print
    `Language: es`.

Secondary operator docs:

- `README.md`
  - Optional only. The current "Inspect package-local Spanish entrypoint display
    metadata" section documents the command and runtime boundary.
  - If touched, add one sentence that known aliases like `Spanish` and `es-MX`
    normalize to `Language: es`, and that each displayed title/purpose line is
    marked `localized` or `fallback`.

Do not edit historical handoffs to reconcile old wording.

## Files And Functions Not To Touch

- Do not edit `src/ai_presenter/runtime/questions.py`.
- Do not edit `src/ai_presenter/packages/models.py`.
- Do not edit `packages/ringcentral-video.yaml`.
- Do not add `localizedTitles` or `localizedPurposes` to
  `EntrypointMatchCandidate`.
- Do not broaden `_match_package_entrypoint_alias()` or `_score_entrypoint_match()`
  to inspect display metadata.
- Do not route `entrypoints --language` through `PresenterVoiceSettings`,
  `validate_cli_voice_profile()`, provider routing, voice assets, controller
  language choices, or live RingCentral Video acceptance.

## Verification Commands

Use no-coverage focused tests so the pre-existing `.coverage` change stays
untouched:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_entrypoints_language_normalizes_spanish_alias_for_display_metadata tests\unit\test_cli.py::test_entrypoints_language_uses_package_local_metadata_without_runtime_voice_validation tests\unit\test_cli.py::test_package_language_alias_normalization_is_documented
```

If the recommended test is renamed, replace the old test name with:

```powershell
tests\unit\test_cli.py::test_entrypoints_spanish_language_aliases_preserve_display_markers
```

Manual probes:

```powershell
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting toolbar" --language es
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting toolbar" --language Spanish
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting toolbar" --language es-MX
```

Expected manual-probe invariants:

- all three print `Language: es`;
- all three print localized markers for `audio-menu`, `video-menu`, and
  `toolbar.more`;
- all three print fallback markers for direct `audio`, direct `video`, and
  `more.notes`;
- no probe prints `Unsupported presenter language`, `Loaded voice`, provider
  output, or runtime acceptance language.

Final hygiene:

```powershell
.\.venv\Scripts\ruff.exe check --no-cache tests\unit\test_cli.py
git diff --check
git status --short
```

## Scan Verification Already Run

Focused existing guards:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_entrypoints_language_normalizes_spanish_alias_for_display_metadata tests\unit\test_cli.py::test_package_language_alias_normalization_is_documented
```

Result: `4 passed`; latest rerun reported `4 passed in 2.19s`.

Manual probes for `es`, `Spanish`, and `es-MX` all printed `Language: es` and
the same `Meeting toolbar` localized/fallback marker output.

## Pitfalls

- `Spanish` and `es-MX` are aliases for package inspection here; unknown
  package-only keys such as `de` must remain raw lookup keys.
- Title and purpose markers are independent. An entrypoint could theoretically
  have a localized title and fallback purpose, or the reverse.
- `entrypoints --language` output is not a runtime matcher contract. It is a
  human inspection surface for package display metadata.
- Spanish display metadata remains partial: current durable state is
  `localizedTitles.es` on `8/27` entrypoints and `localizedPurposes.es` on
  `8/27` entrypoints.
- Do not convert this guard into a runtime Spanish voice/provider test. Runtime
  Spanish is profile/provider-gated separately.
- Do not stage generated artifacts such as `.coverage`.
