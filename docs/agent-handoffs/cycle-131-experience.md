# Cycle 131 Experience Packet: Localized Entrypoint Display Copy

Date: 2026-05-16
Cycle: 131
Scope: experience synthesis only. This packet summarizes the cycle for future
agents and should not be read as live acceptance evidence.

## Product Lesson

Cycle131 clarified that entrypoints are not only internal automation routes.
They are also a user-facing answer surface. Once Spanish users can ask where a
meeting control is, a Spanish label alone is not enough if the answer continues
with English purpose prose.

The product lesson is: aliases help users get matched; they should not become
the long-term content model for visible answer copy. Cycle130's Spanish
`questionAliases.es` label fallback was useful because it reduced an obvious
English-title leak, but Cycle131 showed the durable contract needs explicit
localized display fields for entrypoint title and purpose.

The right product boundary is narrow: "localized entrypoint answer copy now has
a schema and rendering fallback contract." It is not "RingCentral Video Spanish
acceptance is complete."

## Reusable Technical Pattern

Use optional localized display maps on the model, then keep the fallback logic
close to the data object:

- `localizedTitles` and `localizedPurposes` are optional maps on
  `OperationEntrypoint`.
- `title_for_language(language)` and `purpose_for_language(language)` trim
  localized values and fall back to canonical English `title` / `purpose` when
  the localized value is missing or blank.
- Runtime answer rendering asks the entrypoint for display text instead of
  duplicating fallback logic at each call site.
- Spanish still keeps the Cycle130 alias-label fallback when no
  `localizedTitles.es` value exists.
- Localized title/purpose values are display-only for this cycle. They do not
  enter fuzzy matching, alias indexes, operation routing, safety gating,
  controller interrupts, or package YAML content.
- Localization reports may show optional localized entrypoint copy coverage,
  but required localization completeness remains demo narration plus Q&A
  question/answer coverage.

This is the pattern to reuse for future localized display fields: optional
schema, strict unknown-key validation retained, helper-based fallback, rendering
only first, and separate optional coverage reporting.

## Guardrails For Future Localized Entrypoints

- Add model fields before adding package YAML keys. `CamelModel` forbids unknown
  fields, so YAML-first migration will break package loading.
- Keep localized display fields optional unless the product explicitly chooses a
  migration plan for all entrypoints and languages.
- Do not silently fold localized entrypoint title/purpose into
  `required_localization_complete`; report them separately unless the contract
  changes.
- Do not use localized title/purpose for matching in the same move unless
  duplicate, substring, alias-overlap, and risky-control diagnostics are
  expanded first.
- Preserve Q&A-first behavior for safety/support prompts. Authored localized
  answers remain the safer surface for recording, transcript, invite, leave,
  meeting information, chat privacy, participant-name, mute/camera, raise-hand,
  and similar prompts.
- Keep safety gating based on stable operation metadata. Localized prose should
  not become the only source for risky-action detection.
- Treat `packages/ringcentral-video.yaml` edits as product-content work, not a
  mechanical translation pass. Review `questionPolicy`, `openSteps`,
  `presenterNotes`, aliases, related entrypoint ids, and Q&A answers whenever
  package YAML changes.
- Keep default CLI and acceptance draft output English unless a language option
  is deliberately designed and tested.
- Keep ordinary tests local and offline. Do not require OpenAI credentials,
  network calls, live audio, or a live RingCentral window for display-copy proof.
- Leave `.coverage` and unrelated dirty worktree changes unstaged and
  unexplained as product evidence.

## Do Not Claim Yet

- Do not claim Spanish entrypoint answers are fully localized across
  RingCentral Video. No package YAML localized title/purpose content was added
  in Cycle131.
- Do not claim RingCentral Video Spanish acceptance is complete. Unit tests and
  dry CLI checks are not live acceptance.
- Do not claim local Spanish voice support. Spanish remains proven only for
  OpenAI-backed speech profiles unless a later provider cycle changes that.
- Do not claim fake, Piper, generic SAPI, English SAPI, or Chinese SAPI profiles
  support Spanish.
- Do not claim live RingCentral UI behavior, live OpenAI synthesis, audio
  quality, or local voice availability from this cycle.
- Do not claim localized title/purpose improves matching. Cycle131 intentionally
  kept those fields out of matcher and routing surfaces.

## Current Diff Summary

At synthesis time, the worktree showed implementation changes in:

- `src/ai_presenter/packages/models.py`
- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/packages/localization_status.py`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_questions.py`
- `tests/unit/test_cli.py`

It also showed `.coverage` modified. Treat that as unrelated/generated state
unless a future owner explicitly scopes it.

The diff summary was 373 source/test insertions and 2 deletions across the
tracked source/test files, plus a binary `.coverage` modification.

## Suggested Next-Cycle Options

1. Run final implementation verification and review.
   Execute the broader focused pytest selection, ruff, CLI localization reports,
   `git diff --check`, and `git status --short`. This is the highest-value next
   step because Cycle131 implementation notes say full requested verification
   still needed to be run before final acceptance.

2. Seed a tiny RingCentral Spanish localized entrypoint-copy pilot.
   Add `localizedTitles.es` and `localizedPurposes.es` for one or two safe
   entrypoints only, preferably one passive/answer-only control and one
   low-risk executable control. Do not bulk-translate all 27 entrypoints.

3. Add Spanish safety-focused answer tests around localized copy.
   Prove Q&A precedence and `can_operate=False` behavior for risky prompts still
   hold when localized entrypoint display copy exists.

4. Design optional CLI inspection for localized entrypoint display.
   Consider an explicit `entrypoints --language` view so package authors can
   inspect localized labels/purposes without changing default English output.

5. Plan broader content localization only after the pilot.
   A full RingCentral entrypoint localized title/purpose pass should be a
   reviewed content cycle with glossary decisions, not a schema clean-up task.

## Verification Commands Worth Reusing

Focused implementation checks:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_cli.py -q --no-cov
.\.venv\Scripts\ruff check --no-cache src tests
```

Risk-scan broader local check:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_controller.py tests\unit\test_cli.py tests\unit\test_diagnostics.py
```

Localization and provider boundary checks:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter.exe voices --profile profiles\ringcentral-video-openai.example.yaml --language es
.\.venv\Scripts\ai-presenter.exe voices --profile ringcentral-video-bind-speaker --language es
```

Worktree hygiene:

```powershell
git diff --check
git status --short
```

Expected interpretation:

- Focused unit tests can prove schema parsing, display rendering, fallback, and
  report behavior.
- CLI localization reports can prove required localization counts did not drift.
- Voice checks can preserve the OpenAI-backed Spanish boundary and local-profile
  rejection boundary.
- None of these commands prove live RingCentral acceptance, audio quality, or
  local Spanish voice availability.
