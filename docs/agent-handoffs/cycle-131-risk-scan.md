# Cycle 131 Risk Scan: Entrypoint Localized Answer Copy

Date: 2026-05-16
Cycle: 131
Scope: risk scan only for adding entrypoint `localizedTitle` /
`localizedPurpose` support, or an equivalent Spanish answer-copy improvement.
This file is the only intended edit for this task. Do not edit source code,
tests, package YAML, profiles, durable docs, generated artifacts, staging, or
commits from this scan.

## Executive Boundary

Cycle128 established Spanish as complete package localization but not runtime
support. Cycle129 promoted Spanish only for OpenAI-backed speech profiles.
Cycle130 improved Spanish entrypoint answer labels by reusing the first
`questionAliases.es` alias, while leaving entrypoint purpose text in English.

Cycle131 should stay narrower than "full Spanish localization." The likely
product goal is to stop Spanish entrypoint fallback answers from sounding like
mixed-language output, for example:

```text
panel de participantes: Open participant list and meeting people controls.
```

The safest implementation shape is either:

- add explicit `localizedTitle` and `localizedPurpose` fields to
  `OperationEntrypoint`, use them only for answer rendering when present, and
  leave matching, routing, `questionPolicy`, and `openSteps` untouched; or
- add authored Spanish Q&A answers for the high-value prompts that currently
  fall through to entrypoint fallback, without broad schema work.

No live RingCentral acceptance is proven by this risk scan, by package
localization counts, or by unit tests.

## Current State Observed

- The package model is strict: `CamelModel` sets `extra="forbid"`, so adding
  `localizedTitle` or `localizedPurpose` to package YAML requires a schema
  migration in `src/ai_presenter/packages/models.py`.
- `OperationEntrypoint` currently has `title`, `area`, `purpose`,
  `questionPolicy`, `openSteps`, `presenterNotes`, and `questionAliases`.
- Entrypoint matching uses `title`, `area`, `purpose`, package-owned
  `questionAliases`, and legacy aliases. There is no localized title/purpose
  field in the match index today.
- Cycle130 changed answer rendering only: Spanish labels may come from
  `questionAliases.es`, while purpose text still comes from English
  `entrypoint.purpose`.
- Spanish localization report currently passes with `51/51` demo steps,
  `12/12` Q&A questions, `12/12` Q&A answers, and
  `questionAliases.es` on `26/27` entrypoints with `69` aliases.
- Diagnostics currently report `156` package-owned aliases with no
  cross-entrypoint duplicates, based on all package-owned alias languages.
- Spanish runtime support remains OpenAI-backed only. Local SAPI/Piper Spanish
  support remains out of scope and unproven.

## Primary Risks

### Schema Migration Risk

Risk: adding `localizedTitle` / `localizedPurpose` to YAML before adding model
fields will break package loading because unknown keys are forbidden.

Guardrails:

- Add model fields before any package YAML uses them.
- Keep fields optional with empty defaults, for example `dict[str, str]`.
- Preserve existing package loading for packages that omit the new fields.
- Keep model aliases camelCase and avoid renaming existing `title` or `purpose`.
- Do not include localized title/purpose in entrypoint matching unless that is
  an explicit matcher-design change with its own alias-overlap diagnostics.

### Localization Count Drift

Risk: localization status keeps reporting Spanish complete even if new
entrypoint localized fields are absent, or starts failing all existing language
reports because it suddenly requires new fields across every entrypoint.

Guardrails:

- Decide whether entrypoint localized title/purpose is required localization or
  optional answer polish before touching counts.
- If required, extend `LocalizationStatusReport` with separate entrypoint copy
  counts rather than folding them into demo/Q&A counts silently.
- Keep existing Spanish report expectations stable unless the cycle explicitly
  updates the contract from `51/51`, `12/12`, `12/12`, and `26/27`.
- For languages with intentionally partial entrypoint aliases, such as Japanese
  `13/27`, do not force complete entrypoint localizedTitle/purpose coverage
  unless that language is part of the scope.

### Package YAML Scale

Risk: `packages/ringcentral-video.yaml` is large and safety-sensitive. Bulk
adding localized fields across 27 entrypoints can accidentally change
`questionPolicy`, `openSteps`, `relatedEntrypointIds`, alias order, or safety
notes.

Guardrails:

- Treat YAML changes as product-content edits, not mechanical translation.
- Review any YAML diff for movement or changes in `questionPolicy`, `openSteps`,
  `presenterNotes`, `questionAliases`, `relatedEntrypointIds`, and Q&A answers.
- Prefer a small pilot set of entrypoints if the implementation can fall back
  safely when localized purpose is absent.
- Preserve English UI control names when they are actual RingCentral labels;
  translate explanatory prose around them.

### Stale Docs And Overclaims

Risk: README, lifecycle docs, handoffs, or runbooks start saying Spanish is
fully localized, locally supported, accepted, or live validated because
entrypoint copy is now Spanish.

Guardrails:

- Durable docs should only be updated in a docs-owned cycle.
- Keep wording to "Spanish entrypoint answer copy improved" or
  "Spanish fallback answers can use localized entrypoint copy."
- Continue saying Spanish runtime is OpenAI-backed only unless provider work
  changes that.
- Do not claim live acceptance without a dated acceptance run that records
  profile, provider, flow/question, audio, UI state, and result.

### Mixed-Language Claims

Risk: tests pass because the prefix is Spanish, while purpose text, answer-only
explanations, no-match text, or safety disclaimers remain English.

Guardrails:

- Tests should assert both title/label and purpose/prose behavior.
- Accept English product names and UI labels only when intentionally
  UI-label-preserving.
- If localized purpose is missing, answer rendering should either fall back in a
  clearly documented way or use a neutral Spanish fallback that does not pretend
  to be fully localized.

### Safety Answer-Only Controls

Risk: localized entrypoint copy makes risky operations sound more actionable, or
new localized fields accidentally get reused for matching and route risky
prompts around existing Q&A-first safety answers.

Guardrails:

- Preserve `questionPolicy: answerOnly`, `_RISKY_ENTRYPOINT_WORDS`,
  missing-`openSteps` behavior, and controller interrupt gating.
- Do not let localized title/purpose become executable intent.
- Keep Q&A-first matching for recording, notes/transcript, invite, share,
  mute/unmute, camera toggle, raise hand/reactions, leave, meeting information,
  chat privacy, and participant-name prompts.
- Add safety tests in Spanish if localized purpose text changes the answer
  wording for these controls.

### Preserving Cycles128-130 Behavior

Risk: a cleaner localization model regresses the boundaries proven in the last
three cycles.

Guardrails:

- Cycle128 boundary: package localization counts do not imply live/runtime
  acceptance.
- Cycle129 boundary: Spanish still runs only on OpenAI-backed speech profiles;
  fake, Piper, and SAPI profiles still reject Spanish.
- Cycle130 boundary: non-Spanish entrypoint answer labels still use canonical
  titles, and Spanish label improvement does not broaden to Chinese/Japanese
  without a deliberate requirement.
- No tests should require real OpenAI credentials, network access, live audio,
  or a live RingCentral window for ordinary answer-copy proof.

## No-Go Conditions

Do not accept Cycle131 work if any of these are true:

- Package YAML includes `localizedTitle` or `localizedPurpose` before the
  strict Pydantic model supports those fields.
- Localization reports still say Spanish is complete while newly required
  Spanish entrypoint title/purpose coverage is missing.
- Localization reports fail existing Chinese/Japanese/Spanish contracts because
  entrypoint copy counts were added without a migration plan.
- Localized title/purpose fields participate in matching without duplicate,
  substring, alias-overlap, and risky-control diagnostics.
- Any risky Spanish prompt becomes operable when its English/ZH/JA counterpart
  is answer-only or non-operable.
- Spanish succeeds on fake, Piper, generic SAPI, English SAPI, or Chinese SAPI
  profiles.
- Docs or handoffs claim full Spanish localization, local Spanish support, live
  RingCentral acceptance, or production readiness from unit tests or dry runs.
- Broad package YAML edits are made without focused review of safety fields and
  matcher-affecting fields.
- `.coverage` or unrelated worktree changes are staged as part of the cycle.

## Must-Have Tests

Before accepting an implementation, require focused tests for:

- Model migration: a package entrypoint can load with `localizedTitle.es` and
  `localizedPurpose.es`; old packages without those fields still load.
- Strict schema: unknown neighboring keys still fail so the migration does not
  weaken package validation.
- Spanish rendering: Spanish entrypoint fallback uses localized title and
  localized purpose when present, not English `title: purpose`.
- Partial fallback: missing `localizedPurpose.es` has an intentional, tested
  fallback that does not overclaim full localization.
- Non-Spanish preservation: English, Chinese, and Japanese entrypoint fallback
  labels and purpose text remain Cycle130-compatible unless explicitly changed.
- Q&A precedence: authored `localizedAnswers.es` still beats entrypoint fallback.
- Safety flags: risky Spanish controls remain `can_operate=False` and do not
  create a controller interrupt step.
- Matcher boundaries: adding localized title/purpose does not change alias
  precedence, longest-alias ordering, accent folding, or Q&A-first safety
  routing unless separately specified.
- Localization report: Spanish counts remain the current contract if the fields
  are optional, or include separate entrypoint localized title/purpose counts if
  they become required.
- Provider boundary: Spanish remains OpenAI-backed only; local profiles still
  reject Spanish before runtime.
- No live calls: tests use fake providers/runners and do not construct real
  OpenAI clients or touch live RingCentral windows.

Suggested focused verification:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_controller.py tests\unit\test_cli.py tests\unit\test_diagnostics.py
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe voices --profile profiles\ringcentral-video-openai.example.yaml --language es
.\.venv\Scripts\ai-presenter.exe voices --profile ringcentral-video-bind-speaker --language es
git diff --check
git status --short
```

Expected results depend on whether entrypoint copy is optional or required, but
they must not include live acceptance claims, local Spanish support, or unrelated
worktree changes.

## Recommendation

Proceed only with a small, explicit answer-copy boundary. If adding schema
fields, keep them optional and rendering-only first. Do not use localized
title/purpose as matcher input in the same cycle unless diagnostics and safety
tests are expanded. If the team wants lower risk, improve Spanish answer copy by
adding authored Q&A for the most common entrypoint prompts instead of migrating
the entrypoint schema immediately.
