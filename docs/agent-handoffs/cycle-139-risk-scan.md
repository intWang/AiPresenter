# Cycle 139 Risk Scan: Safe Spanish Display Metadata And Runtime Boundary

Date: 2026-05-17
Cycle: 139
Scope: risk scan only for the next optimization. This handoff is the only intended edit. Do not change source, tests, package YAML, durable docs, generated artifacts, staging, commits, or `.coverage` in this scan.

## Baseline Read

Current repo signals after Cycle 138:

- Spanish required package localization is complete for RingCentral Video: `51/51` demo narration steps, `12/12` Q&A questions, and `12/12` Q&A answers.
- Spanish package-owned aliases are broad but curated: `questionAliases.es` covers `26/27` entrypoints with `69` aliases.
- Optional Spanish entrypoint display metadata is still partial: `localizedTitles.es` and `localizedPurposes.es` are present on `5/27` entrypoints.
- Package-local CLI language aliases now normalize known runtime aliases for `entrypoints` and `localization-report`: `Spanish` and `es-MX` resolve to package key `es`, while unknown package-only keys such as `de` remain raw.
- `entrypoints --package ringcentral-video --language es` and alias forms such as `--language Spanish` remain package-local metadata inspection. They do not validate provider readiness, voice assets, controller/demo launch, or live RingCentral Video acceptance.
- Runtime Spanish is supported only with OpenAI-backed speech profiles, such as `profiles/ringcentral-video-openai.example.yaml`.
- Fake, local SAPI, Piper, `windows-sapi`, `windows-sapi-en`, and `windows-sapi-zh` routes must continue to reject Spanish before runtime.
- Spanish local SAPI/Piper support and live RingCentral Video Spanish acceptance remain unproven until a separate implementation and dated acceptance run prove them.

One durable-doc wrinkle: `docs/knowledge/language-lifecycle.md` still describes `entrypoints --language <lang>` as a raw key lookup in its general lifecycle section, while Cycle 138 made known aliases canonical for package-local inspection. If a docs slice is chosen, update that narrow sentence without expanding support claims.

## Recommended Safe Scope

Safest next optimization: a tiny Spanish optional entrypoint display metadata wedge for non-final-action menu surfaces only, with exact count updates from `5/27` to `8/27`.

Recommended entrypoints:

- `ringcentral.video.toolbar.audio-menu`
- `ringcentral.video.toolbar.video-menu`
- `ringcentral.video.more.background`

Safe wording rules:

- Keep RingCentral UI labels literal where operators must find them: `Microphone`, `Speaker`, `Leave computer audio`, `Use phone audio`, `More audio settings`, `More video settings`, `Background`, `Blur`, and `Settings`.
- Describe these as menu or settings navigation surfaces, not proof of selected devices, active camera state, active blur state, or safe custom assets.
- For audio/video menu copy, explicitly avoid changing microphone, speaker, camera, computer audio, phone audio, or deeper settings unless the user asks and visible context is verified.
- For background copy, frame blur and virtual backgrounds as privacy/appearance options, but avoid claiming blur is currently selected or custom uploaded backgrounds are safe to inspect.
- Keep the slice to exactly these three entrypoints. Do not combine it with runtime, provider, Q&A, alias, matching, or acceptance work.

Acceptable alternate safe slice:

- Docs-only cleanup that reconciles the Cycle 138 package-local alias normalization wording in `docs/knowledge/language-lifecycle.md`, README examples, and current handoff guidance.
- Keep the docs language precise: known runtime language aliases normalize to package keys for inspection; unknown package keys remain raw; this is still not runtime validation.

Performance/cache work is not the best next slice unless a concrete repeated-load hotspot is identified first. If selected anyway, keep it private, local to one derived index, and prove structural parity rather than using wall-clock thresholds.

## Explicit No-Go Areas

Do not include any of the following in the next small optimization:

- Runtime provider expansion for Spanish local SAPI or Piper.
- Any claim that Spanish works with local voice routes, offline voice assets, fake providers, or bind-speaker profiles.
- Any claim that OpenAI-backed Spanish runtime support proves RingCentral virtual microphone routing, local speaker playback, or live meeting acceptance.
- Any live acceptance-run entry unless a real current manual or automated run happened and was recorded with date, environment, route, steps, and result.
- Display metadata for Meeting information, Report issue, Invite/Add coworkers, Participants, Chat, Share, Recording, Notes/Transcript, Leave/End, microphone toggle, camera toggle, Settings hub, or Select blur in this slice.
- Broad Spanish alias expansion, especially for action, content-reading, recording, notes/transcript, participants, invite, chat, share, reaction, hand raise, mic, camera, report issue, meeting information, or leave/end prompts.
- Changes to Q&A matching order, alias precedence, localized title/purpose match candidates, `questionPolicy`, `_can_operate`, interrupt creation, cleanup modes, or controller operation gating.
- Making optional `localizedTitles.es` or `localizedPurposes.es` part of `--require-complete`.
- Treating `entrypoints --language es`, `--language Spanish`, or `--language es-MX` as a runtime preflight.
- Refactoring package loading, profile loading, OpenAI provider construction, local SAPI/Piper asset checks, controller startup, or demo launch while doing display metadata or docs polish.
- Staging, committing, deleting, regenerating, or touching `.coverage`.

## Risk Assessment By Focus Area

### Privacy-Sensitive RingCentral Surfaces

Risk: high if the next optimization touches Meeting information, Invite/Add coworkers, Participants, Chat, Share, Recording, Notes/Transcript, Reactions, Raise hand, Report issue, Settings, Leave/End, or any side panel that can expose private content.

These surfaces can expose meeting IDs, invite links, names, emails, chat messages, shared content, recording/transcript artifacts, account details, device labels, visible feedback, or meeting-ending controls. Copy and alias edits can accidentally imply AiPresenter reads, copies, sends, starts, stops, diagnoses, or changes live meeting state.

Safe rule: explain where a control lives and what the surface is for. Do not read private values, infer attendee identity, click final actions, upload content, change persistent preferences, or alter live meeting state unless a separately reviewed flow owns confirmation, cleanup, and tests.

### Device Menu Wording

Risk: medium-high. Audio and video menus are useful Spanish display metadata targets, but device menus may reveal private device names and can change local audio/video routing.

Safe wording should call them recovery/navigation menus. It should not claim AiPresenter can choose the correct microphone, switch speaker output, leave computer audio, use phone audio, pick a camera, diagnose hardware, or read device names by default. If the copy names deeper settings, keep it as a route description and preserve the "no change unless asked" boundary.

### Background Settings Wording

Risk: medium. Background controls are privacy-positive when used for blur, but they also expose room context, custom image/video assets, mirror settings, and durable preferences.

Safe wording should say Background is the path to blur and virtual background options. It should not claim the real room is hidden, custom uploads are safe, blur is active, or the presenter may inspect uploaded assets. Avoid adding display metadata for `ringcentral.video.settings.background.blur` in this slice because that entrypoint performs an actual selection action.

### Runtime And Language Overclaiming

Risk: high. Spanish now spans three separate concepts:

- required package localization is complete;
- package-local aliases and optional display metadata exist;
- runtime speech is OpenAI-only.

Do not compress this into "Spanish is fully supported." That would overclaim optional entrypoint display metadata, local SAPI/Piper, fake profiles, and live RingCentral acceptance. Keep `localization-report` and `entrypoints` language normalization separate from `demo`, `controller`, `doctor`, and provider readiness.

### Brittle Docs Count Tests

Risk: medium. Count guards are useful because package facts are easy to misstate, but they become noisy if they lock broad prose, README examples, or historical handoffs.

Safe pattern: compute counts from package models, then assert compact facts in current durable docs only. If the next content wedge moves Spanish optional display metadata from `5/27` to `8/27`, update source-backed tests and durable docs together. Do not edit old handoffs just to reconcile old counts.

### Performance And Cache Risks

Risk: medium-high around package loading, localization reports, entrypoint rendering, diagnostics, and question matching. A cache can silently change fallback behavior, alias order, Q&A-first precedence, safety gating, or lazy provider boundaries.

Performance work should preserve:

- Q&A-first routing before entrypoint aliases.
- Package-owned alias match order.
- Localized display metadata as rendering/inspection only.
- Known alias normalization for package-local inspection, while unknown package keys remain raw.
- `entrypoints --language` as package-only lookup that does not load runtime voice providers.
- OpenAI-positive and local-profile-negative Spanish voice validation.
- Diagnostics output shape for expected counts and substring-risk summaries.

Do not add process-global caches, file-mtime caches, or raw prompt-answer memoization without a dedicated technical scan and cache invalidation rule.

## Verification Requirements

For the recommended three-entrypoint Spanish display metadata wedge:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_spanish_entrypoint_copy_pilot_is_present tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_complete_spanish_package tests\unit\test_material_packages.py::test_ringcentral_spanish_display_metadata_counts_match_durable_docs tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_cli.py::test_localization_report_normalizes_spanish_language_aliases tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_entrypoints_language_normalizes_spanish_alias_for_display_metadata tests\unit\test_questions.py::test_ringcentral_spanish_entrypoint_answer_uses_localized_pilot_copy
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language Spanish
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --language es
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --language es-MX
.\.venv\Scripts\python.exe -m ruff check --no-cache packages tests
git diff --check
git status --short
```

Expected status: only the intended implementation files for that later cycle should be modified, plus any pre-existing `.coverage` modification left untouched and unstaged.

For docs-only alias-normalization wording cleanup:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_spanish_display_metadata_counts_match_durable_docs tests\unit\test_cli.py::test_localization_report_normalizes_spanish_language_aliases tests\unit\test_cli.py::test_entrypoints_language_normalizes_spanish_alias_for_display_metadata tests\unit\test_cli.py::test_entrypoints_language_uses_package_local_metadata_without_runtime_voice_validation
rg -n "raw language-key|package-local|runtime voice|Spanish|es-MX|SAPI|Piper|live RingCentral" README.md docs\knowledge\language-lifecycle.md docs\knowledge\ringcentral-video\source-index.md docs\knowledge\ringcentral-video\runtime-safety-routing.md
git diff --check
git status --short
```

For performance/cache work, this risk scan is not enough. The next owner should first write a technical scan with a concrete hotspot, then add parity tests before changing internals. Minimum verification should include:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_diagnostics.py tests\unit\test_cli.py::test_localization_report_does_not_load_voice_asset_providers tests\unit\test_cli.py::test_entrypoints_language_uses_package_local_metadata_without_runtime_voice_validation tests\unit\test_cli.py::test_demo_openai_profile_accepts_spanish_dry_run tests\unit\test_cli.py::test_demo_rejects_spanish_local_profile_before_runtime
.\.venv\Scripts\python.exe -m ruff check --no-cache src tests
git diff --check
git status --short
```

For any runtime voice/provider, controller, demo, or RingCentral safety-routing change:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests
.\.venv\Scripts\python.exe -m ruff check --no-cache .
.\.venv\Scripts\python.exe -m mypy --no-incremental src tests
.\.venv\Scripts\ai-presenter.exe doctor --profile profiles/ringcentral-video-openai.example.yaml --package ringcentral-video --flow meeting-control-map-demo --language es --require-localization
.\.venv\Scripts\ai-presenter.exe demo --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
git diff --check
git status --short
```

Expected result: OpenAI-backed Spanish checks remain accepted where applicable, and local Spanish routes still reject before runtime with a profile voice compatibility error.

## Residual Risks

- Spanish optional entrypoint display metadata remains partial at `5/27` until a later implementation changes package YAML, tests, and durable docs together.
- Spanish aliases and Q&A prompts are curated package knowledge, not general Spanish semantic action understanding.
- Known package-local CLI aliases now normalize through presenter language alias rules, so future runtime alias-table changes can affect inspection command canonicalization.
- Unknown package language keys still produce raw package lookup reports and can show all-zero coverage without being runtime errors.
- OpenAI-backed Spanish runtime support depends on configured OpenAI profile behavior and does not prove virtual microphone routing, local speaker playback, or RingCentral audio acceptance.
- Local SAPI/Piper Spanish support is absent; adding it needs provider, voice asset, profile, docs, and acceptance work.
- Live RingCentral route behavior remains mostly unaccepted, especially side panels, More-menu ordering, top-bar coordinates, modal cleanup, media controls, share, notes, recording, reactions, raise hand, invite, chat, participants, and device/background settings.
- Count tests can prevent stale docs, but overbroad assertions can make harmless wording edits painful.
- Performance optimizations can hide safety regressions if they change cache invalidation, match order, lazy provider loading, or fallback rendering.
- `.coverage` is already modified in the worktree during this scan. Leave it unmodified and unstaged.

## Recommendation

For Cycle 139, choose the three-entrypoint Spanish optional display metadata wedge only if the copy stays navigation-focused and privacy-bound. Otherwise, choose the docs-only alias-normalization cleanup. Avoid runtime/provider work, sensitive RingCentral surfaces, broad Spanish alias expansion, live acceptance claims, and cache/performance refactors unless a separate technical scan proves the need first.
