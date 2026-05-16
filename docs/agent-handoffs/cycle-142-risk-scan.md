# Cycle 142 Risk Scan: Spanish CLI Entrypoint Display Inspection

Date: 2026-05-17
Cycle: 142
Scope: risk scan for the candidate task to add or harden CLI inspection tests
for Spanish entrypoint display metadata localized/fallback markers across
`es`, `Spanish`, and `es-MX`.

This scan owns only this handoff. Do not modify, revert, normalize, stage, or
claim source/test/package edits made by other workers.

## Read Basis

- CLI language resolution and entrypoint inspection:
  `src/ai_presenter/cli.py`
- Existing CLI display tests and concurrent test diff context:
  `tests/unit/test_cli.py`
- Package/display metadata model:
  `src/ai_presenter/packages/models.py`
- Localization status counters:
  `src/ai_presenter/packages/localization_status.py`
- Durable docs: `README.md`, `docs/knowledge/language-lifecycle.md`,
  `docs/knowledge/ringcentral-video/source-index.md`, and
  `docs/knowledge/ringcentral-video/runtime-safety-routing.md`
- Recent handoffs: Cycle 140 risk scan, Cycle 141 risk/technical/experience
  notes, and Cycle 141 implementation handoff

Initial `git status --short` showed a pre-existing modified `.coverage`
artifact. While this scan was in progress, a concurrent
`tests/unit/test_cli.py` modification appeared with Spanish entrypoint CLI
assertions. Treat that as another worker's implementation context; this risk
scan does not edit or revert it.

## Current State Observed

- `entrypoints --package ... --language <value>` is package-local inspection.
  It resolves known presenter language aliases through
  `resolve_package_language_key()`, so `Spanish` and `es-MX` normalize to
  package key `es`; unknown package-only keys remain raw lookup keys.
- When a language is supplied, the command prints `Language: <key>`, then each
  entrypoint title and purpose using `title_for_language()` and
  `purpose_for_language()`.
- The CLI marks each title and purpose field independently as `localized` when
  nonblank package-local metadata exists for that resolved key, otherwise
  `fallback`.
- Spanish required package localization remains complete for demo narration and
  Q&A, but optional Spanish entrypoint display metadata is intentionally partial
  at `localizedTitles.es` on `8/27` entrypoints and `localizedPurposes.es` on
  `8/27` entrypoints.
- Cycle 141 already guarded the matcher boundary: Spanish display metadata may
  render after a valid alias/Q&A/canonical match, but must not become query
  metadata or route eligibility.
- The candidate Cycle 142 task should therefore be CLI-display-only: prove the
  inspection output shows localized/fallback markers consistently for `es`,
  `Spanish`, and `es-MX` without changing source, package YAML, aliases,
  matcher behavior, providers, profiles, or live acceptance docs.

## Risk: Overclaiming Runtime Support

Risk: high if wording drifts.

`entrypoints --language es` can look like a runtime language preflight because
it accepts a language flag and prints Spanish display copy. It is not a runtime
preflight. The test and handoff wording must keep the boundary visible:

- It inspects package-local entrypoint display metadata.
- It does not instantiate narration or speech providers.
- It does not validate local SAPI, Piper, fake speech, bind-speaker output, or
  virtual microphone routing.
- It does not prove `demo --language es` or `controller --language es` works
  for any profile.

Acceptable claim: `Spanish` and `es-MX` normalize to the package key `es` for
entrypoint display inspection.

No-go claim: these CLI inspection tests prove Spanish runtime support, voice
availability, provider readiness, or live demo readiness.

## Risk: Brittle Stdout Assertions

Risk: medium-high.

CLI tests naturally assert stdout, but full-line Spanish copy assertions can be
fragile for reasons unrelated to the display contract:

- copy edits to Spanish purpose text can break tests even when marker behavior
  is correct;
- CRLF/LF churn can create noisy diffs in `tests/unit/test_cli.py`;
- broad `in stdout` checks can pass while the relevant entrypoint moved areas
  or only a title marker was checked;
- one large test with many exact strings makes the failure hard to diagnose.

Recommended guard shape:

- Keep assertions focused on entrypoint id, normalized language header,
  resolved area, and `(title: localized)` / `(title: fallback)` plus purpose
  `(localized)` / `(fallback)` markers.
- For exact Spanish strings, assert only the few lines needed to prove
  `title_for_language()` and `purpose_for_language()` are being used for a
  representative localized entrypoint.
- Include at least one fallback title and one fallback purpose in each alias
  path, or use a small helper that verifies marker pairs by entrypoint id.
- Avoid asserting the whole 27-entrypoint output order unless order is the
  explicit behavior under test.
- Prefer area-scoped invocations such as `Meeting toolbar`, `Meeting top bar`,
  or `More menu` so failures stay small and intentional.

The highest-value CLI contract for this cycle is not the exact prose. It is:
same resolved key, same localized/fallback marker semantics, no provider calls,
and no count/requiredness drift.

## Risk: Confusing Inspection With Matching

Risk: high.

The `entrypoints` command displays `localizedTitles.es` and
`localizedPurposes.es` for humans. That output must not be interpreted as a
query-matching contract.

No-go patterns:

- asserting that a string printed by `entrypoints --language es` is therefore a
  valid Spanish question;
- adding or changing `questionAliases.es` to make display-output tests pass;
- changing `src/ai_presenter/packages/models.py` so localized titles/purposes
  become `EntrypointMatchCandidate` tokens;
- changing `src/ai_presenter/runtime/questions.py` so the matcher consults
  `localized_titles`, `localized_purposes`, or CLI inspection output;
- using runtime `answer_question()` behavior to justify a CLI inspection-only
  task unless the assertion is explicitly a no-match boundary already covered
  by Cycle 141.

Keep the phrasing crisp: `questionAliases.es` are query metadata;
`localizedTitles.es` and `localizedPurposes.es` are display/inspection metadata.
Cycle 142 should not reopen matcher design.

## Risk: Optional Metadata Treated As Required

Risk: medium.

Spanish display metadata is partial by design. A test that requires every
entrypoint in the output to have localized title/purpose markers would silently
promote optional metadata into a required localization gate.

No-go patterns:

- changing `localization-report --require-complete` to require
  `localizedTitles.es` or `localizedPurposes.es`;
- asserting no fallback markers appear for Spanish entrypoints;
- describing Spanish as fully localized across entrypoint display metadata;
- updating package counts away from `8/27` unless a separate package-content
  cycle explicitly changes YAML;
- treating fallback markers as failure in `entrypoints --language es`,
  `--language Spanish`, or `--language es-MX`.

Good tests should prove both sides:

- a known Spanish-localized entrypoint prints localized title/purpose markers;
- a known unlocalized entrypoint still prints canonical fallback title/purpose
  markers;
- `Spanish` and `es-MX` show `Language: es` and the same marker contract as
  `es`.

## Risk: Provider And Live Acceptance Overclaims

Risk: high.

Provider and live acceptance boundaries are especially easy to blur because the
same word "Spanish" appears in package localization, runtime voice selection,
and live-demo readiness.

This candidate must not claim:

- local Spanish SAPI or Piper support;
- fake/local speech Spanish runtime support;
- bind-speaker or virtual microphone Spanish readiness;
- OpenAI provider availability beyond the existing profile-gated runtime
  support documented elsewhere;
- current-build RingCentral Video locator reliability;
- live acceptance for audio menu, video menu, More menu, Background, Settings,
  or any other route;
- device switching, camera switching, background selection, Blur selection, or
  private device/settings inspection.

Keep existing provider-boundary tests valuable but scoped: the CLI inspection
command should not call `resolve_voice_settings()`,
`validate_cli_voice_profile()`, `resolve_speech_provider_name()`, or
`check_voice_asset_availability()`. Passing that test means "no provider
inspection happened", not "providers are good".

## Recommended Implementation Shape

This should be a tests-only implementation if the concurrent
`tests/unit/test_cli.py` work is not already sufficient.

Preferred tests:

- Parameterize the display-inspection command over `es`, `Spanish`, and
  `es-MX`.
- Assert all three print `Language: es`.
- Assert a localized Cycle 140 entrypoint such as
  `ringcentral.video.toolbar.audio-menu`,
  `ringcentral.video.toolbar.video-menu`, or
  `ringcentral.video.more.background` shows localized title/purpose markers.
- Assert a known unlocalized entrypoint in the same area still shows fallback
  title/purpose markers.
- Retain or add a package-local synthetic test proving unknown language keys
  can inspect metadata without runtime voice validation.
- Keep the existing localization report tests separate; they are count guards,
  not CLI display marker guards.

Do not touch:

- `packages/ringcentral-video.yaml`
- `src/ai_presenter/cli.py`
- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/packages/models.py`
- provider/profile code
- acceptance docs or live evidence files

If source changes appear necessary for this candidate, pause and rescope. The
observed source already has the desired inspection semantics.

## Verification To Require

Run focused CLI tests without coverage/cache churn:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_entrypoints_language_normalizes_spanish_alias_for_display_metadata tests\unit\test_cli.py::test_entrypoints_language_uses_package_local_metadata_without_runtime_voice_validation
```

Run the adjacent package-count and matcher-boundary sentinels if the
implementation touches assertions around display metadata:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_spanish_display_metadata_counts_match_durable_docs tests\unit\test_material_packages.py::test_entrypoint_localized_title_and_purpose_do_not_affect_match_candidates tests\unit\test_questions.py::test_ringcentral_spanish_display_metadata_is_not_part_of_match_candidates
```

Manual CLI probes are useful as smoke checks, but they are still inspection
only:

```powershell
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting toolbar" --language es
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting toolbar" --language Spanish
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting toolbar" --language es-MX
```

Final hygiene:

```powershell
.\.venv\Scripts\ruff.exe check --no-cache tests\unit\test_cli.py
git diff --check
git status --short
```

Expected status after the implementation owner finishes: only intended
`tests/unit/test_cli.py` changes, this handoff if included in the same working
set, the pre-existing `.coverage` artifact if still dirty, and any clearly
unrelated concurrent handoffs. Source code and package YAML should remain
unchanged for Cycle 142.

## Go/No-Go Recommendation

Go, with tight scope.

This is a useful low-risk guard if it stays focused on CLI package-local
inspection: `es`, `Spanish`, and `es-MX` should resolve to the same package key
and show the expected localized/fallback marker contract.

No-go if the task changes source behavior, matcher behavior, aliases, package
YAML, required localization gates, provider/profile support, or live acceptance
claims. No-go if tests are written so broadly that normal Spanish copy edits
break them, or so narrowly that they never prove both localized and fallback
markers.
