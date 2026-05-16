# Cycle 136 Risk Scan: Spanish Boundary And RingCentral Safety

Date: 2026-05-16
Cycle: 136
Scope: risk scan only for the next small optimization after Cycle135. This
handoff is the only intended edit. Do not change source, tests, package YAML,
durable docs, generated artifacts, staging, commits, or `.coverage` in this
scan.

## Baseline Read

Cycle135 added a durable-doc count drift guard for Spanish optional entrypoint
display metadata. Current repo signals still separate four things that future
work must not merge:

- Required Spanish package localization is complete for demo narration and Q&A:
  `51/51` demo steps, `12/12` Q&A questions, and `12/12` Q&A answers.
- Spanish package-owned location/query aliases are broad:
  `questionAliases.es` covers `26/27` RingCentral Video entrypoints with `69`
  aliases.
- Optional Spanish entrypoint display metadata remains partial:
  `localizedTitles.es` and `localizedPurposes.es` cover only `2/27`
  entrypoints.
- Runtime Spanish is supported only with OpenAI-backed speech profiles. Local
  SAPI, Piper, fake, and bind-speaker routes must still reject Spanish before
  runtime. Live RingCentral Spanish acceptance has not been proven.

Important current tests and docs already protect these boundaries:

- `tests/unit/test_material_packages.py` validates the two-entry Spanish
  display-copy pilot and the durable-doc count guard.
- `tests/unit/test_cli.py` covers localization report counts, package-local
  `entrypoints --language`, Spanish OpenAI dry-run acceptance, and local Spanish
  rejection.
- `tests/unit/test_questions.py` covers Spanish alias routing, unaccented
  prompts, Q&A-first safety precedence, and non-operable sensitive prompts.
- `docs/knowledge/language-lifecycle.md`,
  `docs/knowledge/ringcentral-video/privacy-matrix.md`, and
  `docs/knowledge/ringcentral-video/runtime-safety-routing.md` carry the
  maintainer boundaries for package localization, runtime voice support, and
  privacy-sensitive RingCentral controls.

## Recommended Safe Scope

Safest next optimization: add a tiny operator-facing inspection/doc improvement
that makes existing boundaries more discoverable without changing behavior.

Recommended slice:

- Add a README example for
  `ai-presenter entrypoints --package ringcentral-video --language es`, but do
  not include exact `2/27` counts in README.
- Wording should say the command inspects package-local localized/fallback
  entrypoint display copy only.
- Explicitly say it does not validate runtime voice support, local SAPI/Piper
  assets, provider readiness, controller operation, or live RingCentral
  acceptance.
- Keep the example near the existing `entrypoints` and `localization-report`
  command examples.

Acceptable alternate small scope: add a very small Spanish display-copy wedge
only for low-risk explanatory surfaces:

- Preferred entrypoints: `ringcentral.video.top.views`,
  `ringcentral.video.toolbar.more`, and `ringcentral.video.more.settings`.
- Acceptable with careful wording: `ringcentral.video.toolbar.video-menu`,
  `ringcentral.video.toolbar.audio-menu`, and
  `ringcentral.video.more.background`.
- Copy should describe opening or reviewing UI, not changing state. Preserve
  visible RingCentral labels such as `Views`, `More`, `Settings`,
  `Background`, `Blur`, `Gallery view`, and `Full screen`.
- If package YAML changes, update optional display metadata counts, durable-doc
  count mentions, CLI/package tests, and answer-rendering expectations in the
  same cycle.

Best engineering-hygiene scope if no user-visible text is desired:

- Strengthen only one narrow assertion around count drift or package-local
  inspection, using loaded package models rather than YAML grep.
- Keep historical handoffs out of count guards.
- Do not redefine `--require-complete`.

## Explicit No-Go Areas

Do not include any of the following in a small optimization unless a separate
cycle owns safety design, tests, and acceptance criteria:

- Any runtime provider expansion for Spanish local SAPI or Piper.
- Any live RingCentral Video acceptance claim or acceptance-run entry unless a
  real dated run was performed.
- Changes to `validate_profile_voice`, `resolve_speech_provider_name`,
  `PresenterVoiceSettings`, `voices`, or doctor runtime language semantics.
- Changes to `runtime.questions` matching order, alias precedence, Q&A
  precedence, `questionPolicy`, `_can_operate`, or interrupt creation.
- Broad Spanish alias expansion, especially action or content-reading prompts.
- Making `localizedTitles.es` or `localizedPurposes.es` part of
  `--require-complete`.
- Treating `entrypoints --language es` as a voice, provider, or live demo
  preflight.
- Refactoring package routing, package resolution, or packaged/repo path lookup
  while doing content/doc polish.
- Staging, committing, deleting, regenerating, or touching `.coverage`.

Avoid adding display copy in this small slice for privacy-sensitive or
state-changing RingCentral surfaces:

- `ringcentral.develop.video.start`
- `ringcentral.video.top.meeting-info`
- `ringcentral.video.top.report-issue`
- `ringcentral.video.main.add-coworkers`
- `ringcentral.video.toolbar.audio`
- `ringcentral.video.toolbar.video`
- `ringcentral.video.toolbar.share`
- `ringcentral.video.toolbar.invite`
- `ringcentral.video.toolbar.participants`
- `ringcentral.video.toolbar.chat`
- `ringcentral.video.toolbar.react`
- `ringcentral.video.toolbar.raise-hand`
- `ringcentral.video.more.recording`
- `ringcentral.video.more.notes`
- `ringcentral.video.toolbar.leave`
- `ringcentral.video.settings.background.blur`

These are not forbidden forever. They are no-go for a tiny optimization because
they touch meeting IDs, links, names, chat content, visible reactions, recording,
notes/transcripts, screen sharing, media state, invite flows, or destructive
meeting state.

## Risk Assessment By Focus Area

### Privacy-Sensitive RingCentral Surfaces

Risk: high if the next change touches Chat, Participants, Invite/Add coworkers,
Meeting information, Share, Notes/Transcript, Recording, Reactions, Raise hand,
or Leave.

The package currently has strong Q&A and `answerOnly` boundaries for many
sensitive prompts, but some location routes remain operable for ordinary panel
opening, such as Participants and Chat. A content change can look harmless while
making a prompt sound like AiPresenter reads names, messages, invite links, or
meeting details by default.

Safe rule: package copy may describe where a control lives. It must not say the
presenter reads, copies, sends, starts, stops, records, shares, invites,
identifies, diagnoses, or changes meeting state unless the flow explicitly owns
that action and tests cover it.

### Language And Runtime Confusion

Risk: high around CLI wording. Spanish has three different meanings in the repo:

- package localization completeness;
- package-local query/display metadata;
- runtime presenter voice support.

Only the OpenAI-backed route supports Spanish runtime speech. A README, CLI, or
doctor wording tweak could accidentally imply local SAPI/Piper support or live
readiness. `doctor --require-localization --localization-language es` can pass
package localization independently from `--language es` voice compatibility;
keep that distinction visible.

### Overclaiming Docs

Risk: medium-high. Existing durable docs have good caveats, but README is a
likely place for accidental compression. Avoid phrases such as "Spanish is fully
localized", "Spanish works locally", "Spanish demo accepted", or "all Spanish
entrypoints are localized".

Safer claims:

- "Spanish required package localization is complete for demo narration and
  Q&A."
- "Spanish optional entrypoint display copy is partial."
- "`entrypoints --language es` inspects package-local localized/fallback
  display metadata."
- "Spanish runtime speech requires an OpenAI-backed profile."
- "Live RingCentral acceptance requires dated evidence."

### Brittle Tests

Risk: medium. Cycle135 intentionally added a doc count guard. It is valuable,
but package content changes will now fail if durable count mentions are stale.
That is desired. The brittle part would be extending the guard to README prose
or historical `docs/agent-handoffs`, where old counts are expected.

Do not add tests that assert whole paragraphs or long README blocks. Prefer
source-backed counts from `build_localization_status()` and compact snippets.

### CLI UX Regressions

Risk: medium. The CLI has several related language flags:

- `--language` for runtime presenter voice selection.
- `--localization-language` for package coverage checks.
- `entrypoints --language` for raw package-local metadata lookup.

A small UX polish can regress import hygiene, provider validation boundaries, or
error clarity. `entrypoints --language` must remain lightweight and must not
load runtime voice providers or reject package-only languages. `demo` and
`controller` must continue to validate Spanish local-profile incompatibility
before runtime.

### Package Routing Regressions

Risk: medium-high if aliases, localized title/purpose fields, or question
matching are touched. Spanish aliases are intentionally routeable through the
package alias index even when the selected runtime voice is English. Localized
display metadata must remain answer-rendering/inspection only; it must not
become a match candidate or alter alias ordering.

Preserve Q&A-first behavior. Safety questions for chat/participant privacy,
screen-share content, recording, notes/transcript, reactions, and hand raising
must beat broad entrypoint alias matches.

## Test And Verification Requirements

For a README-only inspection example:

```powershell
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --language es
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_entrypoints_language_uses_package_local_metadata_without_runtime_voice_validation tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package
rg -n "fully localized|live acceptance|SAPI|Piper|OpenAI|package-local|entrypoints --package ringcentral-video --language es|runtime voice|provider" README.md docs\knowledge\language-lifecycle.md docs\knowledge\ringcentral-video\source-index.md
git diff --check
git status --short
```

For Spanish display-copy package changes:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_spanish_entrypoint_copy_pilot_is_present tests\unit\test_material_packages.py::test_ringcentral_spanish_display_metadata_counts_match_durable_docs tests\unit\test_material_packages.py::test_entrypoint_localized_title_and_purpose_do_not_affect_match_candidates tests\unit\test_material_packages.py::test_entrypoint_title_and_purpose_counts_do_not_gate_required_localization
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_cli.py::test_localization_report_require_complete_passes_for_spanish_package tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_entrypoints_language_uses_package_local_metadata_without_runtime_voice_validation
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_spanish_location_questions_match_package_aliases_without_legacy_table tests\unit\test_questions.py::test_ringcentral_spanish_safety_questions_stay_qa_first_with_aliases tests\unit\test_questions.py::test_ringcentral_spanish_unaccented_location_questions_match_curated_aliases tests\unit\test_questions.py::test_ringcentral_spanish_unaccented_safety_questions_stay_qa_first
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --language es
git diff --check
git status --short
```

For any CLI language/runtime wording or behavior change:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_demo_openai_profile_accepts_spanish_dry_run tests\unit\test_cli.py::test_controller_openai_profile_accepts_spanish_dry_run tests\unit\test_cli.py::test_demo_rejects_spanish_local_profile_before_runtime tests\unit\test_cli.py::test_doctor_require_localization_accepts_spanish_runtime_language tests\unit\test_cli.py::test_doctor_openai_profile_accepts_spanish_runtime_language tests\unit\test_cli.py::test_localization_report_does_not_load_voice_asset_providers
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py tests\unit\test_runtime_factory.py tests\unit\test_diagnostics.py
.\.venv\Scripts\ai-presenter.exe doctor --profile profiles/ringcentral-video-openai.example.yaml --package ringcentral-video --flow meeting-control-map-demo --language es --require-localization
.\.venv\Scripts\ai-presenter.exe demo --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
git diff --check
git status --short
```

Expected provider boundary: OpenAI-backed Spanish checks pass when environment
requirements are satisfied or mocked by tests. Local bind-speaker Spanish dry
run rejects before runtime with a profile voice compatibility error.

For package routing or sensitive-surface changes:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_controller.py tests\unit\test_diagnostics.py
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
git diff --check
git status --short
```

Run full verification if implementation touches shared matching, runtime voice,
controller interrupts, package loading, or package execution:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests
.\.venv\Scripts\python.exe -m ruff check --no-cache .
.\.venv\Scripts\python.exe -m mypy --no-incremental src tests
git diff --check
git status --short
```

## Residual Risks

- Live RingCentral behavior remains mostly unaccepted since early observations;
  locator confidence, modal cleanup, More-menu ordering, side panels, and
  participant-state variants still require manual acceptance before being
  described as proven.
- Spanish package localization is complete for required demo/Q&A text, but
  broad Spanish action-safety matching for Notes/Transcript-style prompts is
  not a general semantic parser. Authored Spanish Q&A safety prompts and aliases
  are the current protection.
- Optional Spanish entrypoint display copy is intentionally partial. Adding more
  copy increases count-maintenance work and the chance of overclaiming.
- Q&A alias substring diagnostics currently report an INFO summary. That is an
  expected guardrail, not proof that every future alias is safe.
- Terminal rendering may display mojibake for non-ASCII package strings on some
  Windows code pages. Review YAML and tests with UTF-8-aware tooling before
  changing localized copy.
- `.coverage` is already modified in the worktree during this scan. Leave it
  unmodified and unstaged.

## Recommendation

Choose the README/package-local inspection example as the next small
optimization. It is visible, low-risk, and reinforces the exact boundary that
currently matters most: Spanish package metadata is inspectable, Spanish
runtime speech is OpenAI-only, and live RingCentral acceptance is still a
separate evidence gate.

If the next owner instead needs package-content progress, keep it to a
three-entry low-risk display-copy wedge, update counts in the same change, and
run the focused package, CLI, and Spanish routing tests above. Do not touch
privacy-sensitive RingCentral surfaces, runtime provider routing, or question
matching in that content slice.
