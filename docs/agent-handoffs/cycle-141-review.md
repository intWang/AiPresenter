# Cycle 141 Test Review: Spanish Display Metadata Routing Guard

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Scope: review of the current tests-only diff around the Cycle140 Spanish
optional display metadata guard. This review writes only this handoff document.

## Findings

### [P2] Guard remains sample-based and does not directly prove all Cycle140 display metadata is excluded from matching

The new positive cases in `tests/unit/test_questions.py:353` prove existing
Spanish `questionAliases.es` still route to the three Cycle140 entrypoints and
that answer rendering then uses `localizedTitles.es` and
`localizedPurposes.es`. The new negative cases in
`tests/unit/test_questions.py:390` prove three localized-purpose fragments do
not route today.

That is useful coverage, but it is still an indirect black-box guard. It does
not directly assert that the three Cycle140 entries' match candidates exclude
Spanish-only display tokens, and it does not exercise localized title text or
the full localized purpose strings as no-match prompts. A future regression
that indexes only full localized titles/purposes, or only title display text,
could plausibly slip past this exact diff while still making optional display
metadata route some Spanish questions.

Existing generic coverage reduces the blast radius:
`test_localized_entrypoint_title_alone_does_not_create_a_match()` and
`test_entrypoint_localized_title_and_purpose_do_not_affect_match_candidates()`
already cover the broader model boundary. The gap is that the Cycle141 diff
does not add the stronger real-entrypoint candidate-token assertion requested
by the Cycle141 demand/technical handoffs for the three Cycle140 entries.

### [P3] Negative cases pin the current unaccented Spanish no-match copy

`tests/unit/test_questions.py:411` asserts `No encontre` in the response. That
does confirm the Spanish fallback path, and it matches existing suite style, but
it also adds another assertion on the current unaccented spelling. If the
Spanish no-match copy is later corrected to use a diacritic, this display-only
metadata guard would fail for a copy-edit reason unrelated to routing.

A less brittle guard would keep the routing assertions as the primary proof and
either compare against the shared Spanish fallback source intentionally, or
assert that the English fallback is absent without hard-pinning the unaccented
wording in another display-metadata test.

## Verification

Inspected:

- `git diff -- tests/unit/test_questions.py`
- `src/ai_presenter/packages/models.py`
- `src/ai_presenter/runtime/questions.py`
- `packages/ringcentral-video.yaml`
- `docs/agent-handoffs/cycle-141-demand-analysis.md`
- `docs/agent-handoffs/cycle-141-risk-scan.md`
- `docs/agent-handoffs/cycle-141-technical-scan.md`
- `docs/agent-handoffs/cycle-141-implementation.md`

Focused tests run:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_spanish_alias_routes_render_optional_display_metadata tests\unit\test_questions.py::test_ringcentral_spanish_display_metadata_fragments_do_not_create_matches tests\unit\test_material_packages.py::test_entrypoint_localized_title_and_purpose_do_not_affect_match_candidates tests\unit\test_material_packages.py::test_material_package_normalizes_latin_diacritics_for_matching
```

Result: `8 passed in 1.58s`.

Whitespace check:

```powershell
git diff --check
```

Result: exit 0. Git printed the existing LF-to-CRLF warning for
`tests/unit/test_questions.py`, but no whitespace errors.

Workspace notes:

- Pre-existing `.coverage` remained modified.
- `tests/unit/test_questions.py` remained the only tracked source/test diff.
- Concurrent untracked Cycle141 handoff docs were present; I did not modify or
  revert them.

## Main-Session Resolution

Both findings were addressed after this review:

- The guard now includes
  `test_ringcentral_spanish_display_metadata_is_not_part_of_match_candidates`,
  which checks the real RingCentral Video package candidates for the three
  Cycle140 entrypoints. It asserts candidate tokens come from canonical `id`,
  `title`, `area`, `purpose`, and `title_or_id` token fields and that
  Spanish-only display metadata tokens are absent.
- The negative matching test no longer pins the current Spanish fallback text.
  It derives localized-only query tokens after subtracting all package candidate
  tokens, including `title_or_id` tokens, then calls `_match_entrypoint()`
  directly and asserts no entrypoint match.

Post-resolution focused verification:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_spanish_alias_routes_render_optional_display_metadata tests\unit\test_questions.py::test_ringcentral_spanish_display_metadata_is_not_part_of_match_candidates tests\unit\test_questions.py::test_ringcentral_spanish_display_metadata_fragments_do_not_create_matches tests\unit\test_questions.py::test_localized_entrypoint_title_alone_does_not_create_a_match
```

Result: `6 passed`.
