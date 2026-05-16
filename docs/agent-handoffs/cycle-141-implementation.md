# Cycle 141 Implementation Handoff: Spanish Display Metadata Routing Guard

Date: 2026-05-17
Cycle: 141
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Scope: implementation handoff only. This handoff documents the current
tests-only Cycle141 implementation already present in `tests/unit/test_questions.py`
and adds no source, package, or test changes.

## Objective

Document the Cycle141 guard proving the Cycle140 Spanish optional display
metadata for three RingCentral Video entrypoints remains display/rendering data,
not query-matching data.

The guarded Cycle140 entrypoints are:

- `ringcentral.video.toolbar.audio-menu`
- `ringcentral.video.toolbar.video-menu`
- `ringcentral.video.more.background`

The intended behavior is:

- Spanish package-owned `questionAliases.es` still route to these entrypoints.
- Once routed, Spanish answers render each entrypoint's `localizedTitles.es`
  and `localizedPurposes.es`.
- Spanish safety/metadata fragments that appear only inside
  `localizedPurposes.es` do not create new matches.

## Files Changed

Observed implementation file:

- `tests/unit/test_questions.py`
  - Added `test_ringcentral_spanish_alias_routes_render_optional_display_metadata`.
  - Added `test_ringcentral_spanish_display_metadata_fragments_do_not_create_matches`.
  - Uses the real `packages/ringcentral-video.yaml` package, not a synthetic
    fixture.

Documentation file added by this handoff:

- `docs/agent-handoffs/cycle-141-implementation.md`

Concurrent worktree state observed before this handoff:

- `.coverage` was already modified.
- `tests/unit/test_questions.py` was already modified with the Cycle141 tests.
- `docs/agent-handoffs/cycle-141-demand-analysis.md`,
  `docs/agent-handoffs/cycle-141-risk-scan.md`, and
  `docs/agent-handoffs/cycle-141-technical-scan.md` were already untracked.

Treat those as other workers' edits. Do not revert, normalize, stage, or claim
ownership of them from this documentation pass.

## Test Intent

Cycle141 closes the risk left after Cycle140's display-copy pilot: localized
Spanish entrypoint display metadata should improve answer copy after a valid
alias match, but it should not expand Spanish routing.

The positive test verifies all three Cycle140 entrypoints through real
RingCentral Spanish aliases:

| Question | Expected entrypoint |
| --- | --- |
| `selector de microfono y altavoz` | `ringcentral.video.toolbar.audio-menu` |
| `menu de camara en la reunion` | `ringcentral.video.toolbar.video-menu` |
| `ubicacion de background en more` | `ringcentral.video.more.background` |

For each case, the response must use:

- `expected_entrypoint.localized_titles["es"]`
- `expected_entrypoint.localized_purposes["es"]`

The negative test verifies Spanish localized-only display tokens do not become
entrypoint matches. It derives each probe from the real `localizedTitles.es` and
`localizedPurposes.es` values, subtracts every token already present in package
entrypoint match candidates, and calls `_match_entrypoint()` directly so
unrelated Q&A answers cannot hide the matcher result.

## Exact Behavior Guarded

This implementation guards the separation between route inputs and display
outputs:

- `questionAliases.es` are allowed to route Spanish location/control questions.
- `localizedTitles.es` and `localizedPurposes.es` are allowed to render the
  answer after the entrypoint has already matched.
- `localizedPurposes.es` safety clauses are not aliases, not entrypoint fuzzy
  match candidates, and not operation permission signals.
- The three Cycle140 entrypoints remain covered without adding aliases,
  changing source matching behavior, or expanding optional metadata counts.

In practical terms, a future regression that starts indexing Spanish display
metadata into entrypoint match candidates or `_match_entrypoint()` should fail
the Cycle141 tests without relying on fallback wording.

## Commands Run Or Expected

Inspection commands run while preparing this handoff:

```powershell
git status --short
rg -n "Cycle141|questionAliases|localizedPurposes|localizedTitles|RingCentral Video|Cycle140|Spanish" tests/unit/test_questions.py
rg -n "def test_.*(alias|localized|RingCentral|Cycle140|Cycle141|safety|metadata|purpose)|Spanish|Cycle141" tests/unit/test_questions.py
rg --files docs/agent-handoffs
```

Focused verification run:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_spanish_alias_routes_render_optional_display_metadata tests\unit\test_questions.py::test_ringcentral_spanish_display_metadata_fragments_do_not_create_matches
```

Expected and observed: `6 passed`.

Main-session review adjustment after the first review:

- Added `test_ringcentral_spanish_display_metadata_is_not_part_of_match_candidates`
  so the guard checks the real package `entrypoint_match_candidates` and proves
  they are built from canonical `id`, `title`, `area`, `purpose`, and
  `title_or_id` token fields, not Spanish `localizedTitles.es` or
  `localizedPurposes.es`.
- Changed the negative matching guard to build queries from localized-only
  tokens after subtracting all existing package candidate tokens. This avoids
  false failures from legitimate product labels such as `Blur` and `video`.
- Removed the brittle assertion on the exact Spanish no-match fallback wording.
  The guard now checks `_match_entrypoint()` directly and asserts no entrypoint
  match.

Main-session rereview adjustment:

- Included score-relevant `title_or_id_tokens` in the real-package candidate
  assertion and localized-token exclusion check.
- Included `title_or_id_tokens` in the all-package token subtraction used by
  the localized-only negative probe.
- Kept the negative probe at `_match_entrypoint()` level to avoid unrelated Q&A
  responses being mistaken for entrypoint no-match behavior.

Focused verification after the review adjustment:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_spanish_alias_routes_render_optional_display_metadata tests\unit\test_questions.py::test_ringcentral_spanish_display_metadata_is_not_part_of_match_candidates tests\unit\test_questions.py::test_ringcentral_spanish_display_metadata_fragments_do_not_create_matches tests\unit\test_questions.py::test_localized_entrypoint_title_alone_does_not_create_a_match
```

Expected and observed: `6 passed`.

Recommended final hygiene for the implementation owner:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py
.\.venv\Scripts\ruff.exe check --no-cache tests\unit\test_questions.py
git diff --check
git status --short
```

Expected:

- The focused Cycle141 tests pass.
- The broader questions unit file passes if the surrounding worktree is
  otherwise healthy.
- Ruff reports no style errors in `tests/unit/test_questions.py`.
- `git diff --check` reports no whitespace errors.
- `git status --short` shows only intended test/handoff files plus known
  concurrent artifacts such as `.coverage`.

## Boundaries

This is a tests-only implementation plus this handoff document.

Do not change:

- `packages/ringcentral-video.yaml`
- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/packages/models.py`
- `src/ai_presenter/cli.py`
- Spanish `questionAliases`, Q&A prompts, Q&A answers, demo narration,
  `openSteps`, cleanup modes, routes, `questionPolicy`, providers, profiles,
  or durable localization counts

Do not reinterpret this guard as live RingCentral Video acceptance. It proves
local package/matcher behavior only.

Do not make `localizedTitles` or `localizedPurposes` part of required Spanish
localization. They remain optional display/inspection metadata, currently
partial at the Cycle140 `8/27` state.

Do not claim Spanish local SAPI/Piper/fake/bind-speaker runtime support from
these tests. Runtime voice support remains outside this cycle.

## Next Cycle Recommendation

Use the next cycle to broaden adjacent coverage without changing behavior:

- Add or confirm CLI display tests that `entrypoints --language es`,
  `--language Spanish`, and `--language es-MX` show localized/fallback markers
  for these entries.
- Keep package YAML, source matching, aliases, routes, operation eligibility,
  and localization counts unchanged.
- Run the focused questions, material-package, CLI, ruff, and whitespace checks
  together before any handoff is marked ready.
