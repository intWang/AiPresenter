# Cycle 144 Risk Scan: RingCentral Video Knowledge Wording Guard

Date: 2026-05-17
Cycle: 144
Scope: risk scan for a docs-only or docs-plus-guard cleanup around
RingCentral Video knowledge wording. The candidate should avoid overclaiming
live acceptance, runtime Spanish/provider readiness, privacy-safe inspection,
device/background changes, or optional metadata completeness.

This scan owns only this handoff. Do not modify source, tests, package YAML,
profiles, runbooks, durable knowledge docs, generated artifacts, or concurrent
work from other agents for this risk-scan task.

## Read Basis

- `README.md`
- `docs/knowledge/ai-presenter-maintenance.md`
- `docs/knowledge/language-lifecycle.md`
- `docs/knowledge/ringcentral-video/runtime-safety-routing.md`
- `docs/knowledge/ringcentral-video/privacy-matrix.md`
- `docs/knowledge/ringcentral-video/evidence-index.md`
- `docs/knowledge/ringcentral-video/locator-matrix.md`
- `docs/knowledge/ringcentral-video/validation-checklist-index.md`
- `docs/knowledge/ringcentral-video/acceptance-runs.md`
- Recent handoffs: Cycles 140 through 143 risk scans
- Current working-tree note: initial `git status --short` showed a
  pre-existing modified `.coverage` artifact. This scan does not edit or
  normalize it.

## Current State Observed

- README and lifecycle docs already describe `entrypoints --language es` as
  package-local display metadata inspection. The command can normalize
  `Spanish` and `es-MX` to package key `es`, but this is not runtime voice or
  live demo evidence.
- Spanish required package localization is complete for RingCentral Video demo
  narration and Q&A. Spanish runtime output is supported only through
  OpenAI-backed speech profiles.
- Fake, Piper, local SAPI, bind-speaker, and other local routes must still
  reject Spanish unless a separate implementation and provider evidence changes
  that boundary.
- Optional Spanish entrypoint display metadata remains partial:
  `localizedTitles.es` and `localizedPurposes.es` are documented as `8/27`.
  These fields are display/inspection metadata, not aliases, matcher inputs,
  operation permission, or `--require-complete` gates.
- Live RingCentral Video evidence remains limited. The knowledge docs record
  repo-tested or observed routes, but no executable route is broadly accepted
  for live operation without a dated acceptance run.
- Device and background surfaces are privacy-sensitive. Audio/video menus can
  expose selected device labels, levels, and preferences. Background settings
  can expose room imagery, custom assets, uploads, mirror settings, and
  appearance state.

## Candidate Shape

The safest next task is a wording cleanup in durable docs, README, or a narrow
test/doc guard that reinforces existing boundaries without changing product
behavior.

Good target outcomes:

- State that package-local inspection, runtime support, provider readiness, and
  live acceptance are separate gates.
- State that privacy-safe inspection may summarize allowlisted controls and
  generic states, but must not read private content or infer sensitive values.
- State that audio, video, and background documentation may explain where
  controls live, not switch devices, read labels, inspect room imagery, upload
  assets, or apply effects.
- State that optional localized title/purpose metadata can remain partial and
  fallback markers are expected display-source labels.
- Preserve the current OpenAI-only Spanish runtime boundary and local provider
  rejection boundary.

Out of scope:

- Source changes.
- Package YAML changes.
- Provider/profile changes.
- Alias, Q&A, matcher, controller, or interrupt behavior changes.
- New live RingCentral evidence unless a dated acceptance run is actually
  performed and recorded in the correct evidence file.
- Rewriting historical handoffs only to refresh old snapshots.

## Risk: Live Acceptance Overclaim

Risk: high.

The docs contain local tests, read-only observation, route confidence tables,
manual checklists, and runbook procedures. These can easily be mistaken for
current live acceptance.

No-go claims:

- "RingCentral Video routes are accepted" without a dated acceptance run.
- "Audio menu, video menu, More menu, Background, Settings, Notes, Invite,
  Participants, Chat, Share, reactions, or raise hand are live-safe."
- "The manual checklist proves acceptance."
- "A repo test, dry run, CLI inspection, or doctor check proves the current
  RingCentral build works."
- "Read-only UIA observation proves clicks, cleanup, or side effects are safe."

Safe wording:

- "Repo tests cover package shape and local behavior."
- "Cycle 003 is read-only observation evidence for one build, locale, DPI,
  bounds, and empty-room state."
- "Accepted live behavior requires a dated record in
  `docs/knowledge/ringcentral-video/acceptance-runs.md` with environment,
  route, steps, cleanup, result, and privacy notes."

## Risk: Spanish Runtime And Provider Readiness Overclaim

Risk: high.

Spanish appears in package coverage, display metadata inspection, query aliases,
runtime voice selection, and provider diagnostics. A cleanup can flatten those
into one misleading "Spanish is ready" claim.

No-go claims:

- "Spanish is supported" without the OpenAI-backed speech boundary.
- "`entrypoints --language es` proves Spanish runtime readiness."
- "`localization-report --require-complete` proves `demo --language es` or
  `controller --language es` works."
- "Spanish works with local SAPI, Piper, fake speech, bind-speaker, or virtual
  microphone routes."
- "Spanish has live RingCentral acceptance."

Safe wording:

- "Spanish required package localization is complete for RingCentral Video demo
  narration and Q&A."
- "Spanish package-owned aliases and Q&A can route curated Spanish prompts,
  including accent-insensitive Latin variants."
- "Spanish runtime output is profile-gated and currently OpenAI-backed only."
- "Local provider readiness and live RingCentral acceptance remain separate
  future evidence gates."

## Risk: Privacy-Safe Inspection Becomes Private Inspection

Risk: high.

The running-app scan and RingCentral observation guidance allow sanitized
control discovery. Wording drift could make that sound like permission to read
meeting content, account state, or device/environment details.

No-go claims:

- "Scan can safely inspect all visible text."
- "Screenshots are acceptable by default."
- "Device names, participant names, chat text, invite links, meeting IDs, notes,
  transcripts, captions, account labels, or report contents may be logged as
  evidence."
- "AiPresenter can infer policy, role, readiness, meeting appropriateness,
  privacy status, root cause, or room safety from visible UI alone."

Safe wording:

- "Prefer UI Automation and window metadata for first-pass evidence."
- "Record allowlisted product-control labels and generic states only."
- "Use screenshots only for a specific verification need with a privacy review
  path."
- "Redact or omit private meeting content, identifiers, account details, device
  labels, and custom assets."

## Risk: Device And Background Wording Becomes State Change

Risk: high.

Audio, video, and background controls are useful teaching surfaces but can alter
the meeting, reveal local hardware, or change the user's camera appearance.

No-go claims:

- "AiPresenter switches microphone, speaker, camera, computer audio, phone
  audio, HD settings, mirror settings, or video quality."
- "AiPresenter reads selected device names, audio levels, camera labels, or
  preview contents."
- "AiPresenter selects Blur, turns effects off, applies a background, uploads
  a custom asset, removes an asset, or checks whether the room is hidden."
- "Blur or virtual backgrounds guarantee privacy, compliance,
  confidentiality, or full room concealment."
- "Opening Settings proves devices, camera permission, background state, or
  quality are ready."

Safe wording:

- "Audio/video/background docs may explain where controls live and what
  categories exist."
- "Real device or background changes require explicit user request, visible
  option confirmation, clear side effects, and a recovery path."
- "Background effects can reduce room exposure but are not a privacy guarantee."
- "Custom images and thumbnails are private unless the user explicitly asks to
  inspect them and the visible context is verified."

## Risk: Optional Metadata Completeness Overclaim

Risk: medium-high.

Recent cycles added and guarded Spanish `localizedTitles.es` and
`localizedPurposes.es`. Those fields are intentionally optional and partial.

No-go claims:

- "Spanish is fully localized across entrypoint display metadata."
- "`fallback` means localization failed."
- "`--require-complete` checks localized entrypoint titles and purposes."
- "Localized titles or purposes are query aliases, route candidates, or
  operation eligibility signals."
- "Display metadata counts must be complete before package localization passes."

Safe wording:

- "Required package localization covers demo narration, Q&A questions, and Q&A
  answers."
- "Optional display metadata is useful for rendered answers and CLI inspection,
  and can remain partial."
- "`localized` and `fallback` markers are display-source labels only."
- "Query readiness comes from Q&A and curated `questionAliases`, not localized
  title/purpose display copy."

## Risk: Docs Guard Becomes Behavior Change

Risk: medium.

The candidate mentions "docs+guard", which can be useful if wording drift needs
a sentinel. It should not become a stealth product change.

Acceptable guard scope:

- A focused docs test or text assertion that a durable boundary sentence exists.
- A matcher-boundary test if and only if the existing localized title/purpose
  display-only invariant needs extra coverage.
- A CLI inspection test if and only if the change touches localized/fallback
  marker wording or examples.

No-go guard scope:

- Editing source behavior to make a test pass.
- Adding aliases or Q&A prompts.
- Changing package YAML counts.
- Changing provider compatibility or language normalization.
- Running or recording live acceptance as part of a docs wording cleanup.
- Making optional metadata required in tests.

## Suggested Safe Scope

Recommended scope for the implementation owner:

- Docs-only: one small wording cleanup in README, language lifecycle, runtime
  safety routing, privacy matrix, source index, or maintenance playbook.
- Or docs plus one narrow guard: a focused test that locks an existing boundary
  already expressed in source and docs.
- No package YAML, source, provider, profile, or live evidence changes.
- No new acceptance claims.
- No historical handoff rewrites except this Cycle144 handoff.

Preferred verification:

```powershell
git diff --check
git status --short
```

If a guard test is added, run only the focused test file or specific test names
for the touched boundary, then `git diff --check` and `git status --short`.
Do not require live RingCentral checks for a wording cleanup.

Expected status: only intended docs or focused guard files changed, plus any
pre-existing unrelated `.coverage` or concurrent handoff edits. Do not stage or
commit unrelated artifacts.

## Go/No-Go Recommendation

Go for a docs-only wording cleanup, and go cautiously for a docs-plus-guard
cleanup if the guard is narrow and proves an existing boundary.

No-go if the task changes source behavior, package YAML, aliases, Q&A, routes,
provider/profile support, optional-metadata requiredness, or live acceptance
evidence. No-go if wording claims live RingCentral acceptance, local Spanish
provider readiness, privacy-safe inspection of private content, automatic
device/background changes, or complete optional entrypoint display metadata.
