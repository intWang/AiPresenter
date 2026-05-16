# Cycle 133 Experience Synthesis: Localized Entrypoint Inspection

Date: 2026-05-16

## Scope

This synthesis is for future agents continuing the AiPresenter localization
thread after Cycle133. It summarizes the product and technical lessons from the
read-only localized entrypoint inspection slice.

This handoff does not claim live acceptance, runtime voice support, or expanded
package localization coverage. Source, tests, packages, staging, and commits
were intentionally left untouched by this synthesis task.

## Product Lesson

Localized entrypoint display copy needed an inspection surface before it needed
more copy.

Cycle131 made optional `localizedTitles` and `localizedPurposes` possible.
Cycle132 proved the pattern on two low-risk RingCentral Video entrypoints:
`ringcentral.video.overview` and
`ringcentral.video.top.network-quality`. Before Cycle133, authors could see
coverage counts in `localization-report`, but they still had to inspect YAML or
exercise runtime answers to review the actual text.

Cycle133's useful product move was to make partial localization visible as
partial localization. The new CLI mode shows localized title and purpose copy
where present and makes fallback explicit where absent. That is better than
hiding partial state behind English-only inventory, and also better than
over-promising that Spanish entrypoint display copy is complete.

The lesson for future localization work: when the repo gains a new authored
metadata surface, add a boring read-only inspection path early. It gives package
authors and operators a shared review tool before content expansion creates
more review risk.

## Technical Pattern

Package-local CLI language flags must be treated as metadata selectors, not
runtime language or voice selectors.

For `entrypoints --language`, the language value should be a raw package lookup
key. It may be `es`, `de`, or another package-local key even if no runtime
profile, speech provider, SAPI voice, Piper model, or OpenAI voice path is
available for that language.

The command should use package model helpers such as:

- `OperationEntrypoint.title_for_language(language)`
- `OperationEntrypoint.purpose_for_language(language)`

It should not call runtime voice or provider helpers such as:

- `resolve_voice_settings()`
- `validate_cli_voice_profile()`
- `validate_profile_voice()`
- `resolve_speech_provider_name()`
- `check_voice_asset_availability()`

This keeps package metadata inspection aligned with `localization-report
--language`, not with `demo`, `controller`, `doctor --language`, or `voices`.

The implemented diff summary at handoff time showed:

- `.coverage` modified as generated/unrelated state.
- `src/ai_presenter/cli.py` changed for CLI behavior.
- `tests/unit/test_cli.py` changed for focused coverage.
- No package YAML changes.

## Output And UX Guardrails

Default output is the compatibility contract. With no `--language`,
`entrypoints` should keep the compact shape:

```text
- {entrypoint.id}: {entrypoint.title} [{entrypoint.area}]
```

Localized inspection output may be more verbose, but it must stay honest:

- Keep `--area` filtering behavior unchanged and applied before rendering.
- Show localized title and purpose only when nonblank localized values exist.
- Fall back to canonical English title and purpose when localized values are
  absent or blank.
- Mark source clearly, such as `localized` versus `fallback`.
- Do not print readiness, operability, provider, audio, or live acceptance
  claims.
- Do not imply that localized display copy changes matching, routing, safety
  gating, controller interrupts, aliases, or Q&A precedence.
- Keep purpose inspection explicitly framed as inspection, because purpose text
  can carry safety implications on privacy-sensitive or state-changing
  RingCentral surfaces.

There was a design tension during Cycle133: earlier scans recommended a
title-only first pass to reduce output noise, while implementation chose to
include purpose lines with explicit source markers. Future agents should accept
that implemented behavior as the current baseline, then document it clearly
rather than silently shrinking it without a product decision.

## Claims Still Unproven

- Spanish entrypoint display copy is still partial, not complete. The known
  Cycle132 state was `localizedTitles.es` and `localizedPurposes.es` on `2/27`
  entrypoints.
- Spanish package demo/Q&A localization completeness does not prove full
  Spanish entrypoint localization.
- CLI inspection does not prove local Spanish SAPI/Piper support.
- CLI inspection does not prove every profile can speak Spanish.
- CLI inspection does not prove live RingCentral Video acceptance.
- Unit tests do not prove network, audio-device, desktop automation, or live
  meeting behavior.
- Localized title and purpose fields remain display metadata unless a separate
  reviewed cycle changes matcher or routing semantics.
- `.coverage` was already modified and remains unrelated generated state.

## Suggested Cycle134 Options

1. Durable localization authoring docs.
   Update `docs/knowledge/language-lifecycle.md` or a linked authoring note to
   cover `localizedTitles`, `localizedPurposes`, `entrypoints --language`, the
   source markers, and the boundary between package-local metadata and runtime
   voice support. This is the best next step because Cycle133 shipped a visible
   behavior that future authors need to interpret correctly.

2. Add a small, low-risk Spanish entrypoint display-copy seed.
   Add one or two more explanatory, non-state-changing RingCentral entrypoints
   only after a fresh risk scan. Keep exact package assertions and Q&A fallback
   tests. Avoid recording, notes/transcript, meeting info, invite/link, share,
   leave, mute/camera toggles, chat privacy, and participant identity unless
   safety copy and tests are explicitly scoped.

3. Add a narrower CLI inspection refinement only if users report friction.
   Possible refinements include a compact/verbose toggle or clearer source
   labels. Do not change default no-language output. Do not remove purpose
   inspection casually, because it is now part of the localized inspection
   value proposition.

4. Broaden runtime language work only with live-support evidence.
   Runtime Spanish voice/provider behavior, controller UI language promotion,
   or local voice support should wait for explicit acceptance criteria and
   verification beyond package metadata.

## Verification Commands Worth Reusing

Focused CLI tests:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit\test_cli.py::test_entrypoints_lists_material_package_entrypoints_by_area tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_entrypoints_language_uses_package_local_metadata_without_runtime_voice_validation -q --no-cov
```

Full CLI unit file:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit\test_cli.py -q --no-cov
```

Default compact English output sample:

```powershell
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting top bar"
```

Localized inspection sample:

```powershell
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting top bar" --language es
```

Spanish localization contract check:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
```

Lint and worktree hygiene:

```powershell
.\.venv\Scripts\ruff check --no-cache src tests
git diff --check
git status --short
```

Use `--no-cov` or `--override-ini addopts= -p no:cacheprovider` for focused
verification when coverage output is not the target. Do not stage `.coverage`
unless a separate cleanup task explicitly owns it.
