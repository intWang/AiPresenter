# Cycle 138 Risk Scan: Spanish Boundary And Safe Optimization Scope

Date: 2026-05-16
Cycle: 138
Scope: risk scan only for the next small optimization. This handoff is the only intended edit. Do not change source, tests, package YAML, durable docs, generated artifacts, staging, commits, or `.coverage` in this scan.

## Baseline Read

Cycle 137 tightened the Spanish docs boundary without changing runtime behavior. Current repo signals remain:

- Spanish required package localization is complete for required RingCentral Video demo narration and Q&A: `51/51` demo steps, `12/12` Q&A questions, and `12/12` Q&A answers.
- Spanish package-owned aliases are broad but curated: `questionAliases.es` covers `26/27` RingCentral Video entrypoints with `69` aliases.
- Optional Spanish entrypoint display metadata is still partial: `localizedTitles.es` and `localizedPurposes.es` are present on `5/27` entrypoints.
- `entrypoints --package ringcentral-video --language es` is package-local metadata inspection only. It does not validate runtime voice support, provider readiness, controller/demo execution, local voice assets, or live RingCentral Video acceptance.
- Runtime Spanish output is supported only with OpenAI-backed speech profiles, such as `profiles/ringcentral-video-openai.example.yaml`.
- Fake, local SAPI, Piper, `windows-sapi`, `windows-sapi-en`, and `windows-sapi-zh` routes must still reject Spanish before runtime.
- Spanish local SAPI/Piper support and live RingCentral Video Spanish acceptance remain unproven until a separate implementation and dated acceptance run proves them.

The current live RingCentral evidence baseline is still thin: Cycle 003 produced a read-only empty-room observation for RingCentral Video `26.2.20.355`, and no executable RingCentral Video route is fully `Accepted` for live operation in the current knowledge package.

## Recommended Safe Scope

Safest next optimization: choose one small, non-runtime improvement that preserves the current boundaries.

Recommended slice:

- Add or refine tests around docs/count drift using source-backed package models, not paragraph snapshots.
- Keep the assertion limited to durable current docs such as `docs/knowledge/language-lifecycle.md`, `docs/knowledge/ringcentral-video/source-index.md`, and `docs/knowledge/ringcentral-video/runtime-safety-routing.md`.
- Assert only compact, high-value facts: Spanish required localization `51/51`, Q&A `12/12`, optional display metadata `5/27`, aliases `26/27` and `69`, and OpenAI-only runtime support.
- Keep historical handoffs, README prose, runbook checklists, and acceptance templates out of strict count tests unless the cycle explicitly owns them.

Acceptable alternate safe slice:

- A tiny performance hygiene change that caches or reuses existing package-derived indexes without changing schemas, matching order, rendered answers, diagnostics output, or provider validation.
- The performance work must prove behavior parity first with focused tests, then document the cache invalidation rule in the implementation handoff.

Acceptable docs-only slice:

- Clarify a current durable doc if wording still risks mixing package localization, optional display metadata, OpenAI runtime support, local voice support, and live acceptance.
- Do not add new acceptance evidence unless a real run happened.

## Explicit No-Go Areas

Do not include any of the following in the next small optimization:

- Runtime provider expansion for Spanish local SAPI or Piper.
- Any claim that Spanish works with local voice routes, offline voice assets, fake providers, or bind-speaker profiles.
- Any claim that OpenAI-backed Spanish runtime support proves live RingCentral readiness.
- Any live acceptance-run entry unless a real current manual or automated run was performed and recorded with date, environment, route, commands or manual steps, and result.
- Changes to `validate_profile_voice`, `resolve_speech_provider_name`, voice catalog behavior, doctor runtime language semantics, controller language options, or demo launch behavior.
- Changes to Q&A matching order, alias precedence, localized title/purpose match candidates, safety gating, interrupt creation, or `_can_operate`.
- Broad Spanish alias expansion, especially for action, content-reading, recording, notes/transcript, participants, invite, chat, share, reaction, hand raise, mic, camera, report issue, meeting information, or leave/end prompts.
- Making optional `localizedTitles.es` or `localizedPurposes.es` part of `--require-complete`.
- Treating `entrypoints --language es` as a runtime preflight.
- Refactoring package loading, profile loading, OpenAI provider construction, local SAPI/Piper asset checks, or controller startup while doing docs/count/performance polish.
- Staging, committing, deleting, regenerating, or touching `.coverage`.

## Risk Assessment By Focus Area

### Privacy-Sensitive RingCentral Surfaces

Risk: high if the next optimization touches Meeting information, Invite/Add coworkers, Participants, Chat, Share, Recording, Notes/Transcript, Reactions, Raise hand, Report issue, Settings, or Leave/End.

These surfaces can expose meeting IDs, invite links, names, emails, chat messages, shared content, recording/transcript artifacts, account or device details, visible feedback, or meeting-ending controls. A copy or alias change can accidentally imply AiPresenter reads, copies, sends, starts, stops, diagnoses, or changes live meeting state.

Safe rule: explain where a control lives and what it is for. Do not read private values, infer attendance or identity, click final actions, or change state unless a separately reviewed flow owns the action, privacy boundary, cleanup path, and tests.

### Spanish And Runtime Overclaiming

Risk: high. Spanish currently means three separate things:

- required package localization is complete;
- package-local aliases and optional display metadata exist;
- runtime speech is OpenAI-only.

Do not compress these into "Spanish is fully supported." That phrase would overclaim entrypoint display metadata, local voice routes, and live acceptance. Keep `doctor --require-localization --localization-language es` separate from `demo/controller --language es` voice compatibility.

### Brittle Docs Count Tests

Risk: medium. Count drift tests are useful because package facts are easy to misstate, but they become noisy if they assert long prose or historical artifacts.

Safe pattern: compute counts from package models, then assert short snippets in current durable docs. Avoid tests that lock whole paragraphs, README examples, old cycle handoffs, or wording that can be legitimately edited without changing package state.

### Performance Regressions

Risk: medium-high around package loading, question matching, diagnostics, and CLI startup. These areas build derived indexes for aliases, Q&A, localization reports, and entrypoint rendering. A faster path can silently change order, fallback behavior, or safety precedence.

Performance work should preserve:

- Q&A-first routing before entrypoint aliases.
- Package-owned alias match order.
- Localized display metadata as rendering/inspection only.
- `entrypoints --language` as a package-only lookup that does not load runtime voice providers.
- OpenAI-positive and local-profile-negative Spanish voice validation.
- Diagnostics output shape for expected counts and substring-risk summaries.

Prefer structural parity assertions over wall-clock thresholds unless a real benchmark harness is added.

## Verification Requirements

For docs/count drift guard changes:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_spanish_display_metadata_counts_match_durable_docs tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_cli.py::test_entrypoints_language_uses_package_local_metadata_without_runtime_voice_validation
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --language es
git diff --check
git status --short
```

For performance work in package localization, question routing, or CLI inspection:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_cli.py::test_localization_report_does_not_load_voice_asset_providers tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_entrypoints_language_uses_package_local_metadata_without_runtime_voice_validation
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_demo_openai_profile_accepts_spanish_dry_run tests\unit\test_cli.py::test_controller_openai_profile_accepts_spanish_dry_run tests\unit\test_cli.py::test_demo_rejects_spanish_local_profile_before_runtime
git diff --check
git status --short
```

For any runtime voice/provider, controller, demo, or safety-routing change, this risk scan is not enough. The next owner should write a separate technical plan, add focused failing tests first, and run at minimum:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests
.\.venv\Scripts\python.exe -m ruff check --no-cache .
.\.venv\Scripts\python.exe -m mypy --no-incremental src tests
.\.venv\Scripts\ai-presenter.exe doctor --profile profiles/ringcentral-video-openai.example.yaml --package ringcentral-video --flow meeting-control-map-demo --language es --require-localization
.\.venv\Scripts\ai-presenter.exe demo --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
git diff --check
git status --short
```

Expected status: only the intended files for that later cycle should be modified, plus any pre-existing `.coverage` modification left untouched and unstaged.

## Residual Risks

- Spanish optional entrypoint display metadata remains partial at `5/27`; future docs and tests must not describe all entrypoint display copy as localized.
- Spanish aliases and Q&A prompts are curated package knowledge, not general Spanish semantic action understanding.
- Authored Spanish safety Q&A prompts win through Q&A-first matching, but broad Spanish action-term expansion for sensitive Notes/Transcript-style prompts remains future work.
- OpenAI-backed Spanish runtime support depends on configured OpenAI profile behavior and does not prove virtual microphone routing, local speaker playback, or RingCentral audio acceptance.
- Local SAPI/Piper Spanish support is absent; adding it needs provider, voice asset, profile, docs, and acceptance work.
- Live RingCentral route behavior remains mostly unaccepted, especially side panels, More-menu ordering, top-bar coordinates, modal cleanup, media controls, share, notes, recording, reactions, raise hand, invite, chat, and participants.
- Count tests can prevent stale docs, but overbroad assertions can make harmless wording edits painful.
- Performance optimizations can hide safety regressions if they change cache invalidation, match order, or lazy provider loading.
- `.coverage` is already modified in the worktree during this scan. Leave it unmodified and unstaged.

## Recommendation

Choose a small source-backed docs/count guard or a behavior-preserving cache optimization as Cycle 138's next implementation. Keep it away from privacy-sensitive RingCentral surfaces, runtime Spanish provider promotion, package alias expansion, live acceptance claims, and broad CLI language semantics. If the next cycle needs anything beyond docs/count/performance hygiene, split it into its own technical scan and risk review first.
