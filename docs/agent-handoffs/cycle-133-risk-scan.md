# Cycle 133 Risk Scan: Entrypoint Language Inspection And Spanish Expansion

Date: 2026-05-16
Cycle: 133
Scope: risk scan only for adding CLI `entrypoints --language` inspection, or
continuing Spanish localized entrypoint content expansion. This file is the
only intended edit for this task. Do not edit source code, tests, package YAML,
profiles, generated artifacts, staging, or commits from this scan.

## Current Baseline

Cycle131 added optional `OperationEntrypoint.localizedTitles` and
`localizedPurposes` maps, plus `title_for_language()` and
`purpose_for_language()` helpers. These fields are package-local display copy:
they are not matcher input, not routing input, not provider capability data, and
not a runtime voice declaration.

Cycle132 seeded Spanish display copy for exactly two RingCentral Video
entrypoints:

- `ringcentral.video.overview`
- `ringcentral.video.top.network-quality`

Spanish package localization remains complete for the required demo/Q&A
contract, and localized title/purpose coverage is optional report data. The
current report expectation is `localizedTitles.es present on 2/27 entrypoints`
and `localizedPurposes.es present on 2/27 entrypoints`. That is not full
Spanish entrypoint coverage.

The CLI `entrypoints` command currently lists canonical English titles and has
no `--language` option. `localization-report --language` already uses
package-local language strings, while `voices`, `doctor --language`, `demo`,
and `controller` language flags participate in runtime voice/provider support.

The worktree currently has `.coverage` modified. Treat it as generated,
unrelated state. Do not stage it for this cycle.

## Primary Risks

### Package Language Versus Runtime Voice Support

Risk: adding `entrypoints --language es` could be mistaken for proof that every
profile can speak Spanish, or that Piper/SAPI/local profiles support Spanish.

Guardrails:

- Define `entrypoints --language` as package metadata inspection only.
- Do not call `resolve_voice_settings()`, voice validation, provider readiness,
  or speech asset checks from the `entrypoints` command.
- Accept package-local language keys even if they are not runtime voice choices.
- Keep provider support claims in `voices`, `doctor`, `demo`, and controller
  checks, not in package inspection.

### Localized Purpose On Safety-Sensitive Operations

Risk: Spanish purpose copy can make risky surfaces sound more executable,
especially for meeting information, notes/transcript, recording, invite/link,
share, leave, mute/camera toggles, chat privacy, participant identity, and
report issue.

Guardrails:

- Keep `questionPolicy: answerOnly`, `openSteps`, cleanup behavior,
  `presenterNotes`, Q&A answers, and aliases unchanged during content expansion.
- For answer-only or privacy-sensitive entrypoints, localized purpose must be
  explanatory and bounded. It should not say or imply that AiPresenter reads,
  copies, exposes, announces, starts, records, shares, leaves, mutes, unmutes,
  changes camera state, diagnoses causes, or identifies people by default.
- Q&A-first safety answers must continue to win over entrypoint fallback copy.
- Localized title/purpose text must not become matcher, alias, controller, or
  interrupt input unless a separate diagnostics cycle owns that change.

### Default CLI Output Churn

Risk: adding inspection support could change the default `entrypoints` output,
breaking existing tests, scripts, or operator muscle memory.

Guardrails:

- With no `--language`, output must remain byte-for-byte compatible with the
  current shape: `- {id}: {title} [{area}]`.
- `--area` filtering behavior must remain case-insensitive against canonical
  area text.
- If `--language` is provided, display the localized title when present and the
  canonical title when absent.
- Do not show localized purpose by default. If purpose inspection is needed,
  make it a separate explicit mode in a later cycle so the current command
  stays compact.
- The command should not print readiness, safety, or operability claims unless
  the output design explicitly includes tested fields such as
  `questionPolicy`/`openSteps`.

### Overclaiming Spanish Completeness

Risk: because Spanish required localization passes, further entrypoint copy may
be described as "fully localized" even though only 2/27 entrypoint titles and
purposes are localized today.

Guardrails:

- Say "Spanish package demo/Q&A localization is complete" only for the current
  required localization contract.
- Say "Spanish entrypoint display copy is partial" unless all 27 localized
  titles and all 27 localized purposes are intentionally authored and tested.
- Keep localized title/purpose counts separate from required demo/Q&A counts.
- Do not claim live RingCentral acceptance, production readiness, or local
  Spanish voice support from package content, CLI inspection, or unit tests.

### Staging `.coverage`

Risk: verification or local test runs can leave `.coverage` modified and it may
be accidentally staged with source, tests, or package content.

Guardrails:

- Use `--no-cov` or `--override-ini addopts= -p no:cacheprovider` for focused
  verification when coverage output is irrelevant.
- Run `git status --short` before handoff and before any staging/commit in an
  implementation cycle.
- Do not stage `.coverage`. If cleanup is needed, it should be explicitly
  scoped and approved separately.

## No-Go Conditions

Do not accept Cycle133 implementation work if any of these are true:

- `entrypoints --language` uses runtime voice normalization or rejects a
  package-local language solely because no provider can speak it.
- Default `entrypoints` output changes when `--language` is omitted.
- `--language` changes area filtering, entrypoint ordering, package loading, or
  exit behavior for existing valid packages.
- Localized title/purpose fields participate in matching, alias indexes,
  diagnostics matching, controller routing, safety gating, or interrupt creation
  without a separately reviewed matcher/safety design.
- A safety-sensitive Spanish purpose implies reading private chat, identifying
  participants, exposing meeting IDs/links/dial-in/encryption values, starting
  notes/transcription/recording, sharing screen/content, leaving a meeting, or
  changing mic/camera state by default.
- Any `questionPolicy`, `openSteps`, cleanup route, locator target, aliases,
  Q&A safety answer, presenter note, or related entrypoint reference changes as
  part of a localized display-copy expansion.
- `localizedTitles.es` / `localizedPurposes.es` counts are folded into
  `--require-complete` silently, or Spanish is called complete without naming
  which coverage dimension is complete.
- Tests require real OpenAI credentials, network access, audio devices, a live
  RingCentral window, or local Spanish SAPI/Piper support.
- `.coverage` or other unrelated worktree changes are staged or committed.

## Must-Have Tests

For CLI `entrypoints --language`:

- Existing default-output test proves `entrypoints --package ... --area ...`
  remains unchanged without `--language`.
- Inline temp package test proves `--language es` displays
  `localizedTitles.es` when present.
- Inline temp package test proves a package-local language with no runtime voice
  support, such as `de`, is accepted for display and falls back per package
  metadata rules.
- Missing localized title falls back to the canonical title without pretending
  the entrypoint is localized.
- Real RingCentral package test, if scoped, proves the two Cycle132 pilot
  entrypoints display Spanish titles and unseeded entrypoints remain canonical.
- CLI tests verify `--language` does not show localized purpose, readiness, or
  operability claims unless those fields are explicitly designed and tested.

For Spanish content expansion:

- Package assertions name every newly seeded entrypoint and assert exact
  `localizedTitles.es` and `localizedPurposes.es` values.
- A coverage test updates localized title/purpose counts by exactly the number
  of newly seeded entrypoints while required Spanish demo/Q&A localization stays
  complete.
- Answer-rendering tests prove seeded entrypoints use Spanish title and purpose,
  and unseeded entrypoints keep the existing fallback behavior.
- Q&A precedence tests prove authored `localizedAnswers.es` still beat
  entrypoint fallback copy.
- Matcher-boundary tests prove Spanish text present only in localized
  title/purpose does not create a match.
- Safety tests prove Spanish prompts for recording, notes/transcript, chat
  privacy, screen share, meeting information, invite/link, leave,
  mute/unmute/camera, reactions/raise hand, and participant identity remain
  non-operable where they are non-operable today.
- Controller tests prove answer-only responses do not create interrupt steps.
- Provider-boundary tests or existing coverage prove Spanish remains
  OpenAI-backed for runtime speech and still fails on local unsupported profiles.

Suggested focused verification for an implementation owner:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_controller.py
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting toolbar"
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting toolbar" --language es
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
git diff --check
git status --short
```

Expected status must not include staged `.coverage`, runtime Spanish support
claims, or live RingCentral acceptance claims.

## Recommendation

Proceed with `entrypoints --language` first if the next cycle wants low-risk
operator visibility. Keep it title-only, package-local, and default-output
preserving.

Proceed with Spanish content expansion only as a small authored slice. Favor
low-risk explanatory entrypoints before privacy-sensitive or state-changing
surfaces, and require safety/Q&A/matcher tests before accepting any expansion.
Do not broaden matching or `--require-complete` semantics in the same cycle.
